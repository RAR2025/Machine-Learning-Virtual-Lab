const ENCODINGS = [
  { key: "onehot", name: "One-Hot Encoding" },
  { key: "target", name: "Target Encoding" },
  { key: "loo", name: "Leave-One-Out Encoding" },
  { key: "embedding", name: "Embedding-Based Encoding" },
];

function fmt(v) { return typeof v === "number" ? v.toFixed(4) : (v ?? "-"); }

export default function EncodingSection({ onTrain, trainMap, loading, trainingKey, splitReady }) {
  const trained = ENCODINGS.filter((e) => trainMap[e.key]?.result);

  return (
    <section>
      <h2>Encoding &amp; Training</h2>
      {!splitReady && <p className="muted">Configure the train/test split first.</p>}
      {ENCODINGS.map((e) => {
        const item = trainMap[e.key];
        const busy = loading && trainingKey === e.key;
        return (
          <div key={e.key} className="card" style={{ marginBottom: 12 }}>
            <h3>{e.name}</h3>
            <button disabled={loading || !splitReady} onClick={() => onTrain(e.key)}>
              {busy ? "Training..." : item ? "Retrain" : "Train"}
            </button>
            {busy && <p className="muted">Training model, please wait…</p>}
            {item && <EncodingResult item={item} />}
          </div>
        );
      })}

      {trained.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>Comparison</h3>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead><tr><th>Encoding</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>Features out</th></tr></thead>
              <tbody>
                {trained.map((e) => {
                  const item = trainMap[e.key];
                  const r = item.result;
                  return (
                    <tr key={e.key}><td>{item.encoding_name}</td><td>{fmt(r.Accuracy)}</td><td>{fmt(r.Precision)}</td><td>{fmt(r.Recall)}</td><td>{fmt(r.F1)}</td><td>{item.n_features_out ?? "-"}</td></tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="muted">Performance differences indicate how each representation affects the selected model. Same train/test split and same model configuration were used.</p>
        </div>
      )}
    </section>
  );
}

function EncodingResult({ item }) {
  if (!item?.result) return <p className="muted">Failed: {item?.error}</p>;
  const r = item.result;
  const prev = item.encoded_preview;
  return (
    <div style={{ marginTop: 12 }}>
      <p className="muted">Model: {item.selected_model} | Train: {item.train_test_split?.train_samples} | Test: {item.train_test_split?.test_samples} | Features in→out: {item.n_features_in}→{item.n_features_out}</p>
      <div className="results-grid">
        {[["Accuracy", r.Accuracy], ["Precision", r.Precision], ["Recall", r.Recall], ["F1", r.F1]].map(([k, v]) => (
          <div key={k} className="metric"><div className="label">{k}</div><div className="value">{fmt(v)}</div></div>
        ))}
      </div>
      {(r.TP != null) && <p className="muted">TP={r.TP} TN={r.TN} FP={r.FP} FN={r.FN}</p>}
      {prev && (
        <div style={{ marginTop: 12 }}>
          <h4>Encoded data preview (df.head() — what the model saw)</h4>
          <div style={{ overflowX: "auto" }}>
            <table>
              <thead><tr>{prev.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
              <tbody>
                {prev.rows.map((row, i) => (
                  <tr key={i}>{row.map((v, j) => <td key={j}>{v}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted">Showing {prev.shown_rows} of {prev.total_rows} rows × {prev.columns.length} of {prev.total_columns} columns{prev.hidden_columns > 0 ? ` (+${prev.hidden_columns} more columns)` : ""}.</p>
        </div>
      )}
      {r.ConfusionImageUrl && <img src={r.ConfusionImageUrl} alt={`Confusion Matrix - ${item.encoding_name}`} style={{ maxWidth: "100%", borderRadius: 8, marginTop: 12 }} />}
    </div>
  );
}
