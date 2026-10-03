import React from 'react';
import { ALGORITHMS } from '../../data/algorithms';
import './LeftPanel.css';

export default function HyperparamControls({
  activeAlgo,
  hyperparams,
  onChangeParam
}) {
  const algo = ALGORITHMS[activeAlgo];

  if (!algo || !algo.controls) return null;

  return (
    <div className="hyperparam-section">
      <div className="section-subtitle">Hyperparameter Tuning</div>

      <div className="controls-stack">
        {algo.controls.map((ctrl) => {
          // Check conditional display (e.g. gamma only when kernel is rbf/poly)
          if (ctrl.showIf && !ctrl.showIf(hyperparams)) {
            return null;
          }

          const currentValue = hyperparams[ctrl.id] ?? algo.defaultParams[ctrl.id];

          return (
            <div key={ctrl.id} className="control-card">
              <div className="control-label-row">
                <span className="control-label">{ctrl.label}</span>
                <span className="control-val">
                  {typeof currentValue === 'number'
                    ? Number.isInteger(currentValue)
                      ? currentValue
                      : currentValue.toFixed(2)
                    : currentValue}
                </span>
              </div>

              {ctrl.type === 'slider' && (
                <div className="slider-wrapper">
                  <input
                    type="range"
                    className="range-slider"
                    min={ctrl.min}
                    max={ctrl.max}
                    step={ctrl.step}
                    value={currentValue}
                    onChange={(e) =>
                      onChangeParam(ctrl.id, parseFloat(e.target.value))
                    }
                  />
                  <div className="slider-limits">
                    <span>{ctrl.min}</span>
                    <span>{ctrl.max}</span>
                  </div>
                </div>
              )}

              {ctrl.type === 'select' && (
                <select
                  className="select-control"
                  value={currentValue}
                  onChange={(e) => onChangeParam(ctrl.id, e.target.value)}
                >
                  {ctrl.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              )}

              {ctrl.description && (
                <div className="control-desc">{ctrl.description}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
