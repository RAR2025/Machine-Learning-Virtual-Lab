function CodeInput({ code, setCode, onAnalyze, loading }) {
    return (
        <section>
            <h2>Dataset</h2>
            <p className="muted">
                Paste a UCI fetch command, e.g. <code>fetch_ucirepo(id=2)</code> (Adult Income).
                {" "}Don't know the ID? Browse the full archive, open a dataset, and copy its numeric ID.
            </p>
            <a
                href="https://archive.ics.uci.edu/datasets"
                target="_blank"
                rel="noopener noreferrer"
                className="link-button"
            >
                Explore UCI Datasets ↗
            </a>
            <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="fetch_ucirepo(id=2)"
                rows={3}
                disabled={loading}
            />
            <div style={{ display: "flex", gap: 8 }}>
                <button onClick={onAnalyze} disabled={loading || !code.trim()}>
                    {loading ? "Analyzing..." : "Analyze Dataset"}
                </button>
            </div>
        </section>
    );
}

export default CodeInput;
