import React, { useState } from 'react';
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
  pointsCount,
  collapsed,
  onToggleCollapse
}) {
  const [showFormula, setShowFormula] = useState(false);
  const currentAlgo = ALGORITHMS[activeAlgo];

  if (collapsed) return null;

  return (
    <aside className="vlab-panel vlab-panel-left">
      <div className="panel-header">
        <div className="panel-title">
          <span>Classifier Config</span>
        </div>
        <button
          className="panel-collapse-trigger"
          onClick={onToggleCollapse}
          title="Collapse Panel (Shift+Left)"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
      </div>

      <div className="panel-content">
        {/* 1. Algorithm Selector Tabs */}
        <div className="panel-section">
          <div className="section-label-row">
            <span className="section-label">Algorithm</span>
          </div>
          <AlgoSelector
            activeAlgo={activeAlgo}
            onSelectAlgo={setActiveAlgo}
          />
        </div>

        {/* 2. Parameters */}
        <div className="panel-section">
          <div className="section-label-row">
            <span className="section-label">Hyperparameters</span>
          </div>
          <HyperparamControls
            activeAlgo={activeAlgo}
            hyperparams={hyperparams}
            onChangeParam={onChangeParam}
          />
        </div>

        {/* 3. Mathematical Formula (Collapsible on demand) */}
        <div className="panel-section">
          <button
            type="button"
            className="formula-toggle-btn"
            onClick={() => setShowFormula(!showFormula)}
          >
            <span>Math Formulation</span>
            <span className="formula-arrow">{showFormula ? '▲' : '▼'}</span>
          </button>
          {showFormula && (
            <div className="formula-drawer">
              <code>{currentAlgo.mathFormula}</code>
            </div>
          )}
        </div>

        {/* 4. Fit Action */}
        <div className="panel-bottom-action">
          <button
            className="btn btn-primary btn-block"
            onClick={onTrain}
            disabled={isTraining || pointsCount === 0}
          >
            {isTraining ? 'Computing Boundary...' : 'Run & Draw Boundary'}
          </button>
        </div>
      </div>
    </aside>
  );
}
