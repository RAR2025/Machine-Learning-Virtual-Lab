import DataTable from "./DataTable";

function AnalyzeSection({ analysis }) {
    if (!analysis) return null;
    const types = {};
    (analysis.categorical_columns || []).forEach((c) => { types[c] = "cat"; });
    (analysis.numerical_columns || []).forEach((c) => { types[c] = "num"; });
    const binary = analysis.problem_type === "Classification" && Object.keys(analysis.class_distribution || {}).length === 2;

    return (
        <section>
            <h2>Dataset Analysis</h2>
            <div className="stats">
                <div className="stat"><span>Dataset</span><strong>{analysis.dataset_name || `UCI #${analysis.dataset_id}`}</strong><em>id={analysis.dataset_id}</em></div>
                <div className="stat"><span>Samples</span><strong>{(analysis.rows ?? analysis.num_samples)?.toLocaleString()}</strong></div>
                <div className="stat"><span>Features</span><strong>{analysis.columns ?? analysis.num_features}</strong><em>{analysis.categorical_count} cat · {analysis.numerical_count} num</em></div>
                <div className="stat"><span>Problem type</span><strong>{analysis.problem_type}{binary ? " · Binary" : ""}</strong><em>{analysis.reason}</em></div>
                <div className="stat"><span>Target</span><strong>{analysis.target_column}</strong><em>{analysis.target_dtype} · {analysis.unique_target_values} uniques</em></div>
                <div className="stat"><span>Missing cells</span><strong>{analysis.missing_cells?.toLocaleString()} / {analysis.total_cells?.toLocaleString()}</strong><em>{analysis.balance_note}</em></div>
            </div>

            <details>
                <summary>Class distribution</summary>
                <table className="dense">
                    <thead><tr><th>Class</th><th>Count</th></tr></thead>
                    <tbody>{Object.entries(analysis.class_distribution || {}).map(([k, v]) => <tr key={k}><td>{k}</td><td>{v?.toLocaleString()}</td></tr>)}</tbody>
                </table>
            </details>
            <details>
                <summary>Categorical features — cardinality &amp; top value</summary>
                <table className="dense">
                    <thead><tr><th>Column</th><th>Unique</th><th>Top</th><th>Top freq</th><th>Missing</th></tr></thead>
                    <tbody>{Object.entries(analysis.categorical_detail || {}).map(([c, d]) => <tr key={c}><td>{c}</td><td>{d.unique}</td><td>{d.top}</td><td>{d.top_freq}</td><td>{d.missing}</td></tr>)}</tbody>
                </table>
            </details>
            <details>
                <summary>Numerical features — summary statistics</summary>
                <table className="dense">
                    <thead><tr><th>Column</th><th>Min</th><th>Max</th><th>Mean</th><th>Median</th><th>Std</th></tr></thead>
                    <tbody>{Object.entries(analysis.numerical_summary || {}).map(([c, d]) => <tr key={c}><td>{c}</td><td>{d.min?.toFixed?.(2)}</td><td>{d.max?.toFixed?.(2)}</td><td>{d.mean?.toFixed?.(2)}</td><td>{d.median?.toFixed?.(2)}</td><td>{d.std?.toFixed?.(2)}</td></tr>)}</tbody>
                </table>
            </details>
            <details>
                <summary>Data preview</summary>
                <DataTable data={analysis.X_head} types={types} />
                <h4>Target preview</h4>
                <DataTable data={analysis.y_head} />
            </details>
        </section>
    );
}

export default AnalyzeSection;
