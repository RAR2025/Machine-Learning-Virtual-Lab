import React from 'react';
import './RightPanel.css';

export default function RightPanel({
  metrics,
  isTraining,
  activeAlgo
}) {
  const hasMetrics = Boolean(metrics);

  return (
    <aside className="vlab-panel vlab-panel-right">
      <div className="panel-header">
        <div className="panel-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          <span>Live Metrics & Evaluation</span>
        </div>
        <span className="badge badge-subtle">
          <span className={`badge-dot ${hasMetrics ? 'live' : ''}`}></span>
          {hasMetrics ? 'Evaluated' : 'Awaiting Fit'}
        </span>
      </div>

      <div className="panel-content">
        {/* 1. Accuracy Radial / Score Card */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-name">Classification Accuracy</span>
            <span className="metric-tag">Training Set</span>
          </div>
          <div className="accuracy-display">
            <div className="accuracy-number">
              {hasMetrics ? `${(metrics.accuracy * 100).toFixed(1)}%` : '—'}
            </div>
            <div className="accuracy-progress-bar">
              <div 
                className="accuracy-fill" 
                style={{ width: hasMetrics ? `${metrics.accuracy * 100}%` : '0%' }}
              ></div>
            </div>
          </div>
        </div>

        {/* 2. Secondary Metrics (Precision, Recall, F1) */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-name">Classification Report</span>
          </div>
          <div className="sub-metrics-grid">
            <div className="sub-metric-box">
              <span className="sub-metric-label">Precision</span>
              <span className="sub-metric-val">
                {hasMetrics ? (metrics.precision ?? 0).toFixed(2) : '—'}
              </span>
            </div>
            <div className="sub-metric-box">
              <span className="sub-metric-label">Recall</span>
              <span className="sub-metric-val">
                {hasMetrics ? (metrics.recall ?? 0).toFixed(2) : '—'}
              </span>
            </div>
            <div className="sub-metric-box">
              <span className="sub-metric-label">F1 Score</span>
              <span className="sub-metric-val">
                {hasMetrics ? (metrics.f1 ?? 0).toFixed(2) : '—'}
              </span>
            </div>
          </div>
        </div>

        {/* 3. Confusion Matrix Slot */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-name">Confusion Matrix</span>
          </div>
          {hasMetrics && metrics.confusionMatrix ? (
            <div className="cm-table">
              <div className="cm-row cm-header-row">
                <span className="cm-cell empty-cell"></span>
                <span className="cm-cell col-label">Pred A</span>
                <span className="cm-cell col-label">Pred B</span>
              </div>
              <div className="cm-row">
                <span className="cm-cell row-label">True A</span>
                <span className="cm-cell val-cell true-positive">
                  {metrics.confusionMatrix[0]?.[0] ?? 0}
                </span>
                <span className="cm-cell val-cell false-negative">
                  {metrics.confusionMatrix[0]?.[1] ?? 0}
                </span>
              </div>
              <div className="cm-row">
                <span className="cm-cell row-label">True B</span>
                <span className="cm-cell val-cell false-positive">
                  {metrics.confusionMatrix[1]?.[0] ?? 0}
                </span>
                <span className="cm-cell val-cell true-negative">
                  {metrics.confusionMatrix[1]?.[1] ?? 0}
                </span>
              </div>
            </div>
          ) : (
            <div className="cm-empty">
              <span>Matrix generates upon model training</span>
            </div>
          )}
        </div>

        {/* 4. Bias-Variance Tradeoff Meter */}
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-name">Bias-Variance Estimator</span>
            <span className="metric-tag">{activeAlgo.toUpperCase()}</span>
          </div>
          <div className="bias-variance-meter">
            <div className="bv-scale">
              <span className="bv-label-left">High Bias<br/><small>(Underfitting)</small></span>
              <span className="bv-label-center">Optimal Balance</span>
              <span className="bv-label-right">High Variance<br/><small>(Overfitting)</small></span>
            </div>
            <div className="bv-track">
              <div 
                className="bv-indicator"
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
