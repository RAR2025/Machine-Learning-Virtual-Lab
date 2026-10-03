import React from 'react';
import './TopBar.css';
import { ALGORITHMS } from '../../data/algorithms';

export default function TopBar({
  activeAlgo,
  points,
  autoTrain,
  setAutoTrain,
  onResetPoints,
  isTraining,
  onTrain
}) {
  const currentAlgo = ALGORITHMS[activeAlgo];
  const countA = points.filter(p => p.label === 0).length;
  const countB = points.filter(p => p.label === 1).length;

  return (
    <header className="vlab-topbar">
      {/* Brand & Identity */}
      <div className="topbar-brand">
        <div className="brand-logo-icon">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="6" cy="6" r="3" />
            <circle cx="18" cy="6" r="3" />
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="18" r="3" />
            <line x1="9" y1="6" x2="15" y2="6" />
            <line x1="6" y1="9" x2="6" y2="15" />
            <line x1="18" y1="9" x2="18" y2="15" />
            <line x1="9" y1="18" x2="15" y2="18" />
            <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
          </svg>
        </div>
        <div className="brand-meta">
          <div className="brand-title">
            <span>ML</span>-VLab
            <span className="brand-badge">Playground</span>
          </div>
          <div className="brand-tagline">Real-Time Decision Boundary & Bias-Variance Lab</div>
        </div>
      </div>

      {/* Center Status Indicators */}
      <div className="topbar-center">
        {/* Point Counters */}
        <div className="stats-pill">
          <span className="stats-dot class-a-dot"></span>
          <span className="stats-label">Class A:</span>
          <span className="stats-value">{countA}</span>
          <span className="stats-divider">|</span>
          <span className="stats-dot class-b-dot"></span>
          <span className="stats-label">Class B:</span>
          <span className="stats-value">{countB}</span>
          <span className="stats-divider">|</span>
          <span className="stats-label">Total:</span>
          <span className="stats-total">{points.length}</span>
        </div>

        {/* Active Algorithm Indicator */}
        <div 
          className="active-algo-badge"
          style={{
            backgroundColor: currentAlgo.bgColor,
            borderColor: currentAlgo.borderColor,
            color: currentAlgo.themeColor
          }}
        >
          <span className="algo-indicator-dot" style={{ backgroundColor: currentAlgo.themeColor }}></span>
          <span className="algo-name">{currentAlgo.shortName}</span>
          <span className="algo-mode-tag">{currentAlgo.badgeText}</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="topbar-actions">
        {/* Auto Train Toggle */}
        <label className="toggle-control" title="Automatically re-compute boundary when points or hyperparams change">
          <input 
            type="checkbox" 
            checked={autoTrain} 
            onChange={(e) => setAutoTrain(e.target.checked)} 
          />
          <span className="toggle-slider"></span>
          <span className="toggle-label">Auto-Train</span>
        </label>

        {/* Manual Run / Compute Button */}
        <button 
          className={`btn btn-primary btn-sm ${isTraining ? 'btn-loading' : ''}`}
          onClick={onTrain}
          disabled={isTraining || (countA === 0 && countB === 0)}
          title="Compute Decision Boundary"
        >
          {isTraining ? (
            <>
              <span className="spinner"></span>
              <span>Fitting...</span>
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>Fit Model</span>
            </>
          )}
        </button>

        {/* Reset Canvas Button */}
        <button 
          className="btn btn-outline btn-sm"
          onClick={onResetPoints}
          disabled={points.length === 0}
          title="Clear all points"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="1 4 1 10 7 10"></polyline>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
          <span>Reset</span>
        </button>
      </div>
    </header>
  );
}
