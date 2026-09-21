const STEPS = ["Dataset", "Analyze", "Clean", "Problem", "Model", "Split", "Encoding", "Train", "Evaluate", "Compare", "Conclusion"];

export default function WorkflowStepper({ current }) {
  return (
    <section aria-label="Experiment workflow">
      <h2>Experiment Workflow</h2>
      <ol style={{ display: "flex", flexWrap: "wrap", gap: 8, listStyle: "none", padding: 0, margin: 0 }}>
        {STEPS.map((s, i) => {
          const done = i < current;
          const active = i === current;
          return (
            <li key={s} style={{
              padding: "6px 12px", borderRadius: 999,
              background: done ? "#dcfce7" : active ? "#dbeafe" : "#f1f5f9",
              border: `1px solid ${done ? "#86efac" : active ? "#93c5fd" : "#e2e8f0"}`,
              fontSize: "0.85rem", fontWeight: active ? 700 : 400,
              color: done ? "#166534" : active ? "#1d4ed8" : "#475569",
            }}>
              {done ? `✓ ${i + 1}. ${s}` : `${i + 1}. ${s}`}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
