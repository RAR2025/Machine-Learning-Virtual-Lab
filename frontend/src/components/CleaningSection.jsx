function formatShape(shape) {
    if (Array.isArray(shape) && shape.length === 2) {
        return `${shape[0]} samples × ${shape[1]} features`;
    }
    if (typeof shape === "number") {
        return `${shape} samples`;
    }
    return "unknown";
}

function CleaningSection({ result, onClean, loading, disabled }) {
    return (
        <section>
            <h2>Data Cleaning</h2>
            <button onClick={onClean} disabled={loading || disabled}>
                {loading ? "Cleaning..." : "Clean Dataset"}
            </button>
            {result && (
                <div className="result">
                    <h3>Cleaning Report</h3>
                    <p>Before: <strong>{formatShape(result.X_shape_before)}</strong> | After: <strong>{formatShape(result.X_shape_after)}</strong> (removed {result.cleaning_summary?.rows_removed} rows)</p>
                    <p>NaN rows removed: {result.nan_rows_removed}, duplicates: {result.duplicate_rows_removed}, imputed cells: {result.imputed_cells}, outliers capped: {result.outliers_capped}.</p>
                    <p>Columns removed: {(result.columns_dropped || []).join(", ") || "none"}.</p>
                    {result.target_encoded && <p>Target encoded: {result.encoded_column} ({result.num_classes} classes) {JSON.stringify(result.class_mapping)}</p>}
                    <details><summary>Advanced diagnostics</summary>
                        <p className="muted">Placeholders→NA: {result.placeholder_cells_found}, sentinels: {result.sentinel_cells_found}, target-missing rows: {result.rows_dropped_target_missing}.</p>
                        <p className="muted">Warnings: {(result.warnings || []).join(" | ") || "none"}</p>
                    </details>
                </div>
            )}
        </section>
    );
}

export default CleaningSection;
