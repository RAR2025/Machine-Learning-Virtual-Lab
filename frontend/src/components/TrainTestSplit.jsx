import { useState } from "react";

export default function TrainTestSplit({ split, testSize, randomState, onApply, loading, disabled }) {
  const [ts, setTs] = useState(testSize ?? 0.2);
  const [rs, setRs] = useState(randomState ?? 42);
  return (
    <section>
      <h2>Train / Test Split</h2>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "end" }}>
        <label>Train size: <select value={String(ts)} onChange={(e) => setTs(Number(e.target.value))} disabled={disabled || loading}>
          <option value="0.3">70% train / 30% test</option>
          <option value="0.2">80% train / 20% test</option>
          <option value="0.1">90% train / 10% test</option>
        </select></label>
        <label>Random state: <input type="number" value={rs} min={0} max={99999} onChange={(e) => setRs(Number(e.target.value))} disabled={disabled || loading} style={{ width: 100 }} /></label>
        <button disabled={disabled || loading} onClick={() => onApply(ts, rs)}>Apply split (test {(ts * 100).toFixed(0)}%)</button>
      </div>
      {split && <p className="muted" style={{ marginTop: 8 }}>Training samples: {split.train_samples} | Testing samples: {split.test_samples} | Random state: {split.random_state} | Stratified: {String(split.stratified)}</p>}
    </section>
  );
}
