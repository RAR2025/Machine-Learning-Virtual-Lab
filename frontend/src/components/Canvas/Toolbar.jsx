import React from 'react';
import './Toolbar.css';
import { DATASET_PRESETS } from '../../data/presets';

export default function Toolbar({
  activeClass,
  setActiveClass,
  isEraser,
  setIsEraser,
  onClear,
  onUndo,
  canUndo,
  onLoadPreset,
  showGrid,
  setShowGrid,
  hoverCoord
}) {
  return (
    <div className="canvas-toolbar">
      {/* Placement Mode Tools */}
      <div className="toolbar-group">
        <span className="toolbar-label">Draw Mode:</span>
        
        {/* Class A (Blue) */}
        <button
          className={`tool-btn ${activeClass === 0 && !isEraser ? 'active class-a-active' : ''}`}
          onClick={() => {
            setActiveClass(0);
            setIsEraser(false);
          }}
          title="Place Class 0 points (Blue)"
        >
          <span className="tool-circle class-a-circle"></span>
          <span>Class A</span>
        </button>

        {/* Class B (Orange) */}
        <button
          className={`tool-btn ${activeClass === 1 && !isEraser ? 'active class-b-active' : ''}`}
          onClick={() => {
            setActiveClass(1);
            setIsEraser(false);
          }}
          title="Place Class 1 points (Orange)"
        >
          <span className="tool-circle class-b-circle"></span>
          <span>Class B</span>
        </button>

        {/* Eraser */}
        <button
          className={`tool-btn ${isEraser ? 'active eraser-active' : ''}`}
          onClick={() => setIsEraser(!isEraser)}
          title="Click points to erase them"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
          <span>Erase</span>
        </button>
      </div>

      <div className="toolbar-divider"></div>

      {/* Dataset Presets */}
      <div className="toolbar-group">
        <span className="toolbar-label">Presets:</span>
        {Object.values(DATASET_PRESETS).map((preset) => (
          <button
            key={preset.id}
            className="preset-btn"
            onClick={() => onLoadPreset(preset.id)}
            title={preset.tagline}
          >
            {preset.name}
          </button>
        ))}
      </div>

      <div className="toolbar-divider"></div>

      {/* History & Canvas Options */}
      <div className="toolbar-group">
        {/* Undo */}
        <button 
          className="tool-btn-icon" 
          onClick={onUndo} 
          disabled={!canUndo}
          title="Undo last point (Ctrl+Z)"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 7v6h6"></path>
            <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
          </svg>
        </button>

        {/* Clear */}
        <button 
          className="tool-btn-icon" 
          onClick={onClear} 
          title="Clear all points"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* Grid Toggle */}
        <button 
          className={`tool-btn-icon ${showGrid ? 'active-icon' : ''}`} 
          onClick={() => setShowGrid(!showGrid)}
          title="Toggle Grid Lines"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="3" y1="15" x2="21" y2="15"></line>
            <line x1="9" y1="3" x2="9" y2="21"></line>
            <line x1="15" y1="3" x2="15" y2="21"></line>
          </svg>
        </button>
      </div>

      {/* Live Coordinate Tag */}
      <div className="toolbar-coord">
        {hoverCoord ? (
          <span>X₁: <b>{hoverCoord.x.toFixed(2)}</b>, X₂: <b>{hoverCoord.y.toFixed(2)}</b></span>
        ) : (
          <span className="coord-hint">Click or drag to place points</span>
        )}
      </div>
    </div>
  );
}
