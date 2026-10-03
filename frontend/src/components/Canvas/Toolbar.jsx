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
      {/* 1. Draw Mode Segmented Buttons */}
      <div className="tool-segment">
        <button
          className={`segment-btn ${activeClass === 0 && !isEraser ? 'active class-a' : ''}`}
          onClick={() => {
            setActiveClass(0);
            setIsEraser(false);
          }}
          title="Draw Class A points (Blue)"
        >
          <span className="dot a-dot"></span>
          <span>Class A</span>
        </button>

        <button
          className={`segment-btn ${activeClass === 1 && !isEraser ? 'active class-b' : ''}`}
          onClick={() => {
            setActiveClass(1);
            setIsEraser(false);
          }}
          title="Draw Class B points (Orange)"
        >
          <span className="dot b-dot"></span>
          <span>Class B</span>
        </button>

        <button
          className={`segment-btn ${isEraser ? 'active eraser' : ''}`}
          onClick={() => setIsEraser(!isEraser)}
          title="Eraser tool (Click/drag to delete points)"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
          <span>Erase</span>
        </button>
      </div>

      <div className="toolbar-v-divider"></div>

      {/* 2. Compact Dataset Presets */}
      <div className="preset-cluster">
        <span className="cluster-label">Preset:</span>
        {Object.values(DATASET_PRESETS).map((p) => (
          <button
            key={p.id}
            className="chip-btn"
            onClick={() => onLoadPreset(p.id)}
            title={p.tagline}
          >
            {p.name}
          </button>
        ))}
      </div>

      <div className="toolbar-v-divider"></div>

      {/* 3. Actions: Undo, Clear, Grid */}
      <div className="action-cluster">
        <button
          className="icon-action-btn"
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo last point (Ctrl+Z)"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 7v6h6"></path>
            <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
          </svg>
        </button>

        <button
          className="icon-action-btn"
          onClick={onClear}
          title="Clear all points"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <button
          className={`icon-action-btn ${showGrid ? 'active-grid' : ''}`}
          onClick={() => setShowGrid(!showGrid)}
          title="Toggle Grid Lines"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="3" y1="15" x2="21" y2="15"></line>
            <line x1="9" y1="3" x2="9" y2="21"></line>
            <line x1="15" y1="3" x2="15" y2="21"></line>
          </svg>
        </button>
      </div>

      {/* 4. Live Coordinate Monitor */}
      <div className="coord-monitor">
        {hoverCoord ? (
          <span>X₁: <b>{hoverCoord.x.toFixed(2)}</b>, X₂: <b>{hoverCoord.y.toFixed(2)}</b></span>
        ) : (
          <span className="coord-idle">Click or drag to place data</span>
        )}
      </div>
    </div>
  );
}
