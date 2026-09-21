import { useMemo, useState } from "react";

function DataTable({ data, pageSize = 8, maxCols = 12, types = {} }) {
    const [page, setPage] = useState(0);
    const columns = useMemo(() => Object.keys(data?.[0] || {}).slice(0, maxCols), [data, maxCols]);
    const totalCols = data?.[0] ? Object.keys(data[0]).length : 0;

    if (!data || !Array.isArray(data) || data.length === 0) {
        return <p className="muted">No data to display.</p>;
    }
    const pages = Math.max(1, Math.ceil(data.length / pageSize));
    const rows = data.slice(page * pageSize, page * pageSize + pageSize);

    return (
        <div>
            <div style={{ overflowX: "auto" }}>
                <table>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th key={col}>{col}
                                    {types[col] && <span className="muted" style={{ marginLeft: 6, fontWeight: 400 }}>({types[col]})</span>}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, i) => (
                            <tr key={i}>
                                {columns.map((col) => (
                                    <td key={col}>{formatCell(row[col])}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {totalCols > maxCols && <p className="muted">Showing {maxCols} of {totalCols} columns (sample). Total model input width is reported separately.</p>}
            <div className="muted" style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8 }}>
                <button type="button" disabled={page === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>Prev</button>
                <span>Page {page + 1} / {pages} ({data.length} rows)</span>
                <button type="button" disabled={page + 1 >= pages} onClick={() => setPage((p) => Math.min(pages - 1, p + 1))}>Next</button>
            </div>
        </div>
    );
}

function formatCell(value) {
    if (value === null || value === undefined) {
        return <span className="muted">- (missing)</span>;
    }
    if (typeof value === "number") {
        return Number.isInteger(value)
            ? value.toLocaleString()
            : value.toFixed(4);
    }
    return String(value);
}

export default DataTable;
