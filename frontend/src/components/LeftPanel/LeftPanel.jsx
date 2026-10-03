import React from 'react';
import './LeftPanel.css';
import AlgoSelector from './AlgoSelector';
import HyperparamControls from './HyperparamControls';
import { ALGORITHMS } from '../../data/algorithms';

export default function LeftPanel({
  activeAlgo,
  setActiveAlgo,
  hyperparams,
  onChangeParam,
  onTrain,
  isTraining,
  pointsCount
}) {
  const currentAlgo = ALGORITHMS[activeAlgo];

  return (
    <aside className="vlab-panel vlab-panel-left">
      <div className="panel-header">
        <div className="panel-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <line x1="4" y1="21" x2="4" y2="14"></line>
            <line x1="4" y1="10" x2="4" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12" y2="3"></line>
            <line x1="20" y1="21" x2="20" y2="16"></line>
            <line x1="20" y1="12" x2="20" y2="3"></line>
            <line x1="1" y1="14" x2="7" y2="14"></line>
            <line x1="9" y1="8" x2="15" y2="8"></line>
            <line x1="17" y1="16" x2="23" y2="16"></line>
          </svg>
          <span>Model & Parameters</span>
        </div>
        <span className="badge badge-subtle">{currentAlgo.shortName}</span>
      </div>

      <div className="panel-content">
        {/* 1. Algorithm Selection Cards */}
        <div className="section-block">
          <div className="section-subtitle">Select Classifier</div>
          <AlgoSelector
            activeAlgo={activeAlgo}
            onSelectAlgo={setActiveAlgo}
          />
        </div>

        {/* 2. Dynamic Hyperparameter Tuning */}
        <div className="section-block">
          <HyperparamControls
            activeAlgo={activeAlgo}
            hyperparams={hyperparams}
            onChangeParam={onChangeParam}
          />
        </div>

        {/* 3. Mathematical Formula Snippet */}
        <div className="section-block">
          <div className="section-subtitle">Optimization Objective</div>
          <div className="formula-box">
            <code>{currentAlgo.mathFormula}</code>
          </div>
        </div>

        {/* 4. Fit Model Primary Action */}
        <div className="left-panel-footer">
          <button
            className={`btn btn-primary btn-full ${isTraining ? 'btn-loading' : ''}`}
            onClick={onTrain}
            disabled={isTraining || pointsCount === 0}
          >
            {isTraining ? (
              <>
                <span className="spinner"></span>
                <span>Calculating Boundary...</span>
              </>
            ) : (
              <>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Compute Decision Boundary</span>
              </>
            )}
          </button>
          {pointsCount === 0 && (
            <div className="footer-warning">Draw points on canvas to train</div>
          )}
        </div>
      </div>
    </aside>
  );
}
