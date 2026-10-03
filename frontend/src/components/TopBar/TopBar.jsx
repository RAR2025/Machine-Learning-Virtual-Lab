import React, { useState } from 'react';
import './TopBar.css';
import { ALGORITHMS } from '../../data/algorithms';
import GuideModal from './GuideModal';

export default function TopBar({
  activeAlgo,
  points,
  autoTrain,
  setAutoTrain,
  onResetPoints,
  isTraining,
  onTrain,
  leftCollapsed,
  setLeftCollapsed,
  rightCollapsed,
  setRightCollapsed,
  theoryCollapsed,
  setTheoryCollapsed
}) {
  const [showInfoModal, setShowInfoModal] = useState(false);
  const currentAlgo = ALGORITHMS[activeAlgo];
  const countA = points.filter((p) => p.label === 0).length;
  const countB = points.filter((p) => p.label === 1).length;

  return (
    <>
      <header className="vlab-topbar">
        {/* Left Section: Panel Toggle & Minimal Brand */}
        <div className="topbar-left">
          <button
            className={`btn-icon-toggle ${!leftCollapsed ? 'active-toggle' : ''}`}
            onClick={() => setLeftCollapsed(!leftCollapsed)}
            title={leftCollapsed ? 'Expand Controls (Left Panel)' : 'Collapse Controls (Left Panel)'}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="9" y1="3" x2="9" y2="21"></line>
            </svg>
          </button>

          <div className="brand-lockup">
            <span className="brand-title">ML-VLab</span>
            <span className="brand-dot">/</span>
            <span className="brand-sub">Decision Boundary</span>
          </div>
        </div>

        {/* Center Section: High-contrast Algo Pill & Counters */}
        <div className="topbar-center">
          {/* Active Algorithm Pill */}
          <div className="algo-badge-pill" style={{ '--pill-accent': currentAlgo.themeColor }}>
            <span className="pill-dot"></span>
            <span className="pill-name">{currentAlgo.shortName}</span>
          </div>

          {/* Minimalist Data Counters */}
          <div className="dataset-counter">
            <span className="cnt-item">
              <span className="cnt-dot a-dot"></span>
              <b>{countA}</b>
            </span>
            <span className="cnt-divider"></span>
            <span className="cnt-item">
              <span className="cnt-dot b-dot"></span>
              <b>{countB}</b>
            </span>
            <span className="cnt-divider"></span>
            <span className="cnt-total">Total: <b>{points.length}</b></span>
          </div>
        </div>

        {/* Right Section: Actions & Guide Modal */}
        <div className="topbar-right">
          {/* Auto-Train Toggle */}
          <label className="toggle-wrapper" title="Automatically re-compute boundary on change">
            <input
              type="checkbox"
              checked={autoTrain}
              onChange={(e) => setAutoTrain(e.target.checked)}
            />
            <span className="toggle-switch"></span>
            <span className="toggle-text">Auto-Train</span>
          </label>

          {/* Compute Boundary Button */}
          <button
            className="btn btn-primary"
            onClick={onTrain}
            disabled={isTraining || points.length === 0}
          >
            {isTraining ? (
              <>
                <span className="btn-spinner"></span>
                <span>Fitting...</span>
              </>
            ) : (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Fit Model</span>
              </>
            )}
          </button>

          {/* Reset */}
          <button
            className="btn btn-outline"
            onClick={onResetPoints}
            disabled={points.length === 0}
            title="Reset Canvas"
          >
            Clear
          </button>

          {/* Info / Mind Concept Modal Button */}
          <button
            className="btn-icon-toggle"
            onClick={() => setShowInfoModal(true)}
            title="Virtual Lab Concept Guide (Click to read)"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </button>

          {/* Right Panel Toggle */}
          <button
            className={`btn-icon-toggle ${!rightCollapsed ? 'active-toggle' : ''}`}
            onClick={() => setRightCollapsed(!rightCollapsed)}
            title={rightCollapsed ? 'Expand Metrics (Right Panel)' : 'Collapse Metrics (Right Panel)'}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="15" y1="3" x2="15" y2="21"></line>
            </svg>
          </button>
        </div>
      </header>

      {/* Info / Guide Walkthrough Modal */}
      <GuideModal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
      />
    </>
  );
}
