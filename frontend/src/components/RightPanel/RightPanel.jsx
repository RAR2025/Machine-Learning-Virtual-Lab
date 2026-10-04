import './RightPanel.css';
import ConfusionMatrix from './ConfusionMatrix';
import MetricsGauge from './MetricsGauge';

export default function RightPanel({
  metrics,
  isTraining,
  collapsed,
  onToggleCollapse
}) {
  const hasMetrics = Boolean(metrics);
  const accuracy = hasMetrics ? metrics.accuracy : 0;
  const varianceScore = hasMetrics ? Math.min(1, Math.max(0, metrics.varianceScore ?? 0.5)) : 0.5;
  const biasVarianceLabel = varianceScore >= 0.65 ? 'High variance · Overfitting' : varianceScore <= 0.35 ? 'High bias · Underfitting' : 'Balanced complexity';

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
        {/* 1. Accuracy radial gauge */}
        <div className="clean-metric-card">
          <div className="card-top-row">
            <span className="card-label">Accuracy</span>
            <span className="card-badge">Train</span>
          </div>
          <MetricsGauge value={accuracy} isLoading={isTraining} />
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
          <div className="card-top-row"><span className="card-label">Confusion Matrix</span><span className="card-hint">hover cells</span></div>

          {hasMetrics && metrics.confusionMatrix ? (
            <ConfusionMatrix matrix={metrics.confusionMatrix} />
          ) : (
            <div className="cm-placeholder">Ready to evaluate</div>
          )}
        </div>

        {/* 4. Bias-Variance Estimator */}
        <div className="clean-metric-card">
          <div className="card-top-row"><span className="card-label">Bias-Variance</span><span className="card-hint">complexity</span></div>

          <div className="bv-container">
            <div className="bv-line-labels">
              <span>Bias (Underfit)</span>
              <span>Variance (Overfit)</span>
            </div>
            <div className="bv-track-bar" title={biasVarianceLabel} aria-label={biasVarianceLabel}>
              <div
                className="bv-pin"
                style={{
                  left: `${Math.min(95, Math.max(5, varianceScore * 100))}%`
                }}
              >
                <span className="bv-tooltip">{biasVarianceLabel}</span>
              </div>
            </div>
            <div className="bv-status">{biasVarianceLabel}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
