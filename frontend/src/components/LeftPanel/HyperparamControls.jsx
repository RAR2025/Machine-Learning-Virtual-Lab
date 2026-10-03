import React, { useState } from 'react';
import { ALGORITHMS } from '../../data/algorithms';
import './LeftPanel.css';

export default function HyperparamControls({
  activeAlgo,
  hyperparams,
  onChangeParam
}) {
  const algo = ALGORITHMS[activeAlgo];
  const [activeTooltip, setActiveTooltip] = useState(null);

  if (!algo || !algo.controls) return null;

  return (
    <div className="hyperparam-container">
      <div className="controls-stack">
        {algo.controls.map((ctrl) => {
          if (ctrl.showIf && !ctrl.showIf(hyperparams)) {
            return null;
          }

          const currentValue = hyperparams[ctrl.id] ?? algo.defaultParams[ctrl.id];
          const hasTooltip = Boolean(ctrl.description);
          const isTooltipOpen = activeTooltip === ctrl.id;

          return (
            <div key={ctrl.id} className="control-row-card">
              <div className="control-header-line">
                <div className="label-with-info">
                  <span className="control-title">{ctrl.label}</span>
                  {hasTooltip && (
                    <button
                      type="button"
                      className="info-bubble-btn"
                      onClick={() => setActiveTooltip(isTooltipOpen ? null : ctrl.id)}
                      onMouseEnter={() => setActiveTooltip(ctrl.id)}
                      onMouseLeave={() => setActiveTooltip(null)}
                      title="Learn what this hyperparameter does"
                    >
                      i
                    </button>
                  )}
                </div>

                <span className="control-value-chip">
                  {typeof currentValue === 'number'
                    ? Number.isInteger(currentValue)
                      ? currentValue
                      : currentValue.toFixed(2)
                    : currentValue}
                </span>
              </div>

              {/* Minimal floating tooltip on hover/click */}
              {isTooltipOpen && hasTooltip && (
                <div className="control-floating-tooltip">
                  {ctrl.description}
                </div>
              )}

              {/* Slider Input */}
              {ctrl.type === 'slider' && (
                <div className="slider-box">
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
                  <div className="slider-bounds">
                    <span>{ctrl.min}</span>
                    <span>{ctrl.max}</span>
                  </div>
                </div>
              )}

              {/* Select Input */}
              {ctrl.type === 'select' && (
                <select
                  className="clean-select"
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
            </div>
          );
        })}
      </div>
    </div>
  );
}
