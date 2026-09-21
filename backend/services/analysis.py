"""Dataset profiling for the Analyze stage."""
import numpy as np
import pandas as pd


def _col_missing(s: pd.Series) -> int:
    try:
        return int(s.isna().sum())
    except Exception:
        return 0


def profile_dataset(X: pd.DataFrame, y, dataset_id=None, dataset_name=None) -> dict:
    y_col = y.columns[0] if isinstance(y, pd.DataFrame) else getattr(y, "name", "target")
    y_s = y.iloc[:, 0] if isinstance(y, pd.DataFrame) else y

    cat_cols = X.select_dtypes(include=["object", "category", "bool", "string"]).columns.tolist()
    num_cols = X.select_dtypes(include=["number"]).columns.tolist()

    # class distribution (top 20 to bound size)
    try:
        vc = y_s.value_counts(dropna=False).head(20)
        class_dist = {str(k): int(v) for k, v in vc.items()}
    except Exception:
        class_dist = {}

    # missing summary
    missing_per_col = {}
    for c in list(X.columns):
        missing_per_col[str(c)] = _col_missing(X[c])
    missing_per_col[str(y_col)] = _col_missing(y_s)
    total_cells = int(X.size) + int(y_s.size) if len(X) else 0
    missing_cells = int(sum(missing_per_col.values()))

    # cardinality + top category per categorical
    cardinality = {}
    cat_detail = {}
    for c in cat_cols:
        try:
            vc = X[c].value_counts(dropna=True)
            n_unique = int(X[c].nunique(dropna=True))
            top = str(vc.index[0]) if len(vc) else None
            top_freq = int(vc.iloc[0]) if len(vc) else 0
            cardinality[str(c)] = n_unique
            cat_detail[str(c)] = {
                "unique": n_unique,
                "top": top,
                "top_freq": top_freq,
                "missing": int(X[c].isna().sum()),
            }
        except Exception:
            cardinality[str(c)] = 0
            cat_detail[str(c)] = {"unique": 0, "top": None, "top_freq": 0, "missing": 0}

    # numerical summary
    num_summary = {}
    for c in num_cols:
        try:
            s = pd.to_numeric(X[c], errors="coerce")
            num_summary[str(c)] = {
                "min": float(s.min()) if s.notna().any() else None,
                "max": float(s.max()) if s.notna().any() else None,
                "mean": float(s.mean()) if s.notna().any() else None,
                "median": float(s.median()) if s.notna().any() else None,
                "std": float(s.std()) if s.notna().any() else None,
                "missing": int(s.isna().sum()),
            }
        except Exception:
            continue

    # balance flag
    balanced = None
    balance_note = None
    if len(class_dist) == 2:
        vals = list(class_dist.values())
        ratio = min(vals) / max(vals) if max(vals) else 0
        balanced = bool(ratio >= 0.4)
        balance_note = (
            "Reasonably balanced" if balanced
            else "Imbalanced — prefer F1 / ROC-AUC / PR over raw accuracy."
        )

    return {
        "dataset_id": dataset_id,
        "dataset_name": dataset_name,
        "rows": int(X.shape[0]),
        "columns": int(X.shape[1]),
        "num_samples": int(X.shape[0]),
        "num_features": int(X.shape[1]),
        "numerical_columns": [str(c) for c in num_cols],
        "categorical_columns": [str(c) for c in cat_cols],
        "numerical_count": len(num_cols),
        "categorical_count": len(cat_cols),
        "target_column": str(y_col),
        "class_distribution": class_dist,
        "missing_per_column": missing_per_col,
        "missing_cells": missing_cells,
        "total_cells": total_cells,
        "cardinality": cardinality,
        "categorical_detail": cat_detail,
        "numerical_summary": num_summary,
        "balanced": balanced,
        "balance_note": balance_note,
    }
