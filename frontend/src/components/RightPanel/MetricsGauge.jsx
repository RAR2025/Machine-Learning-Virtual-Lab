const RADIUS = 42;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function MetricsGauge({ value, isLoading }) {
  const percentage = Math.max(0, Math.min(1, Number(value) || 0));
  const dashOffset = CIRCUMFERENCE * (1 - percentage);
  const gaugeColor = percentage >= 0.8 ? '#16A34A' : percentage >= 0.6 ? '#EA580C' : '#DC2626';

  return (
    <div className="accuracy-gauge" aria-label={`Accuracy ${Math.round(percentage * 100)} percent`}>
      <svg className="accuracy-gauge-svg" viewBox="0 0 108 108" role="img">
        <circle className="gauge-track" cx="54" cy="54" r={RADIUS} />
        <circle
          className="gauge-value"
          cx="54"
          cy="54"
          r={RADIUS}
          stroke={gaugeColor}
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={dashOffset}
        />
      </svg>
      <div className="gauge-center">
        <strong>{isLoading ? '...' : `${(percentage * 100).toFixed(1)}%`}</strong>
        <span>accuracy</span>
      </div>
    </div>
  );
}
