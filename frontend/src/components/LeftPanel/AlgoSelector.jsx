import React from 'react';
import { ALGORITHMS } from '../../data/algorithms';
import './LeftPanel.css';

export default function AlgoSelector({ activeAlgo, onSelectAlgo }) {
  return (
    <div className="algo-selector-list">
      {Object.values(ALGORITHMS).map((algo) => {
        const isSelected = activeAlgo === algo.id;
        return (
          <button
            key={algo.id}
            type="button"
            className={`algo-card ${isSelected ? 'selected' : ''}`}
            onClick={() => onSelectAlgo(algo.id)}
            style={{
              '--card-theme': algo.themeColor,
              '--card-bg': algo.bgColor,
              '--card-border': algo.borderColor,
            }}
          >
            <div className="algo-card-top">
              <div className="algo-card-icon">
                {algo.id === 'knn' && (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <circle cx="19" cy="5" r="2"></circle>
                    <circle cx="5" cy="19" r="2"></circle>
                    <line x1="12" y1="12" x2="19" y2="5" strokeDasharray="2 2"></line>
                    <line x1="12" y1="12" x2="5" y2="19" strokeDasharray="2 2"></line>
                  </svg>
                )}
                {algo.id === 'svm' && (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="4" y1="20" x2="20" y2="4" strokeWidth="2.5"></line>
                    <line x1="2" y1="16" x2="16" y2="2" strokeDasharray="3 3"></line>
                    <line x1="8" y1="22" x2="22" y2="8" strokeDasharray="3 3"></line>
                  </svg>
                )}
                {algo.id === 'dt' && (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="4" r="2"></circle>
                    <circle cx="6" cy="14" r="2"></circle>
                    <circle cx="18" cy="14" r="2"></circle>
                    <line x1="12" y1="6" x2="6" y2="12"></line>
                    <line x1="12" y1="6" x2="18" y2="12"></line>
                  </svg>
                )}
              </div>
              <div className="algo-card-heading">
                <span className="algo-card-title">{algo.name}</span>
                <span className="algo-card-badge">{algo.badgeText}</span>
              </div>
            </div>
            <p className="algo-card-summary">{algo.summary}</p>
          </button>
        );
      })}
    </div>
  );
}
