import React from 'react';
import { ALGORITHMS } from '../../data/algorithms';
import './LeftPanel.css';

export default function AlgoSelector({ activeAlgo, onSelectAlgo }) {
  return (
    <div className="algo-segmented-control">
      {Object.values(ALGORITHMS).map((algo) => {
        const isSelected = activeAlgo === algo.id;
        return (
          <button
            key={algo.id}
            type="button"
            className={`algo-tab-btn ${isSelected ? 'active' : ''}`}
            onClick={() => onSelectAlgo(algo.id)}
            style={{
              '--tab-accent': algo.themeColor,
            }}
            title={algo.name}
          >
            <span className="algo-tab-indicator"></span>
            <span className="algo-tab-name">{algo.shortName}</span>
          </button>
        );
      })}
    </div>
  );
}
