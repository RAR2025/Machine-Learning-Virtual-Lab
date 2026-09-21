function ModelSelection({ problemType, models, selected, onSelect, loading }) {
    if (!problemType) return null;

    return (
        <section>
            <h2>Model Selection</h2>
            <p className="muted">Problem type: <strong>{problemType}</strong></p>
            <div className="grid">
                {(models || []).map((m) => (
                    <div key={m.key} className="card" style={{ borderColor: selected === m.key ? "#3b82f6" : "#e2e8f0" }}>
                        <h3>{m.name}</h3>
                        <p className="muted">{m.description}</p>
                        <button disabled={loading || selected === m.key} onClick={() => onSelect(m.key)}>
                            {selected === m.key ? "Selected" : `Select ${m.name}`}
                        </button>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default ModelSelection;
