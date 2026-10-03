import React, { useState } from 'react';
import './RightPanel.css';

export default function RightPanel({
  metrics,
  isTraining,
  activeAlgo,
  collapsed,
  onToggleCollapse
}) {
  const [tooltip, setTooltip] = useState(null);
  const hasMetrics = Boolean(metrics);

  if (collapsed) return null;

  return (
    <aside className="vlab-panel vlab-panel-right">
      <div className="panel-header">
        <div className="panel-title">
          <span>Live Metrics</span>
        </div>
        <button
          className="panel-collapse-trigger"
          onClick={onToggleCollapse}
          title="Collapse Metrics (Right Panel)"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      <div className="panel-content">
        {/* 1. Accuracy Big Metric */}
        <div className="clean-metric-card">
          <div className="card-top-row">
            <span className="card-label">Accuracy</span>
            <span className="card-badge">Train</span>
          </div>
          <div className="accuracy-val-row">
            <span className="accuracy-big-val">
              {hasMetrics ? `${(metrics.accuracy * 100).toFixed(1)}%` : '—'}
            </span>
          </div>
          <div className="mini-progress-track">
            <div
              className="mini-progress-fill"
              style={{ width: hasMetrics ? `${metrics.accuracy * 100}%` : '0%' }}
            ></div>
          </div>
        </div>

        {/* 2. Precision / Recall / F1 */}
        <div className="metrics-triad">
          <div className="triad-item">
            <span className="triad-label">Precision</span>
            <span className="triad-val">{hasMetrics ? (metrics.precision ?? 0).toFixed(2) : '—'}</span>
          </div>
          <div className="triad-item">
            <span className="triad-label">Recall</span>
            <span className="triad-val">{hasMetrics ? (metrics.recall ?? 0).toFixed(2) : '—'}</span>
          </div>
          <div className="triad-item">
            <span className="triad-label">F1-Score</span>
            <span className="triad-val">{hasMetrics ? (metrics.f1 ?? 0).toFixed(2) : '—'}</span>
          </div>
        </div>

        {/* 3. Confusion Matrix */}
        <div className="clean-metric-card">
          <div className="card-top-row">
            <div className="title-with-info">
              <span className="card-label">Confusion Matrix</span>
              <button
                type="button"
                className="info-bubble-btn"
                onMouseEnter={() => setTooltip('cm')}
                onMouseLeave={() => setTooltip(null)}
                title="Confusion Matrix details"
              >
                i
              </button>
            </div>
            {tooltip === 'cm' && (
              <div className="control-floating-tooltip">
                Diagonal cells represent correctly classified points (True Positives & True Negatives).
              </div>
            )}
          </div>

          {hasMetrics && metrics.confusionMatrix ? (
            <div className="compact-cm">
              <div className="cm-header-lbl"></div>
              <div className="cm-header-lbl">Pred A</div>
              <div className="cm-header-lbl">Pred B</div>

              <div className="cm-row-lbl">True A</div>
              <div className="cm-cell hit">{metrics.confusionMatrix[0]?.[0] ?? 0}</div>
              <div className="cm-cell miss">{metrics.confusionMatrix[0]?.[1] ?? 0}</div>

              <div className="cm-row-lbl">True B</div>
              <div className="cm-cell miss">{metrics.confusionMatrix[1]?.[0] ?? 0}</div>
              <div className="cm-cell hit">{metrics.confusionMatrix[1]?.[1] ?? 0}</div>
            </div>
          ) : (
            <div className="cm-placeholder">Ready to evaluate</div>
          )}
        </div>

        {/* 4. Bias-Variance Estimator */}
        <div className="clean-metric-card">
          <div className="card-top-row">
            <div className="title-with-info">
              <span className="card-label">Bias-Variance</span>
              <button
                type="button"
                className="info-bubble-btn"
                onMouseEnter={() => setTooltip('bv')}
                onMouseLeave={() => setTooltip(null)}
                title="Bias-Variance Tradeoff details"
              >
                i
              </button>
            </div>
            {tooltip === 'bv' && (
              <div className="control-floating-tooltip">
                Indicates model complexity tradeoff: High Bias (underfitting) vs High Variance (overfitting).
              </div>
            )}
          </div>

          <div className="bv-container">
            <div className="bv-line-labels">
              <span>Bias (Underfit)</span>
              <span>Variance (Overfit)</span>
            </div>
            <div className="bv-track-bar">
              <div
                className="bv-pin"
                style={{
                  left: hasMetrics && metrics.varianceScore !== undefined
                    ? `${Math.min(95, Math.max(5, metrics.varianceScore * 100))}%`
                    : '50%'
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
