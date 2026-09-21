"""HTTP-layer helpers: JSON safety, confusion-image URLs, state summaries."""

import datetime as _datetime
from urllib.parse import quote

import numpy as np
import pandas as pd

from backend.core import state


def json_safe(value):
    """Convert a value to a JSON-compatible type, replacing NaN/Inf with None."""
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if value is None:
        return None
    if value is pd.NA or value is pd.NaT:
        return None
    try:
        if pd.isna(value) and not isinstance(value, (str, bytes)):
            return None
    except Exception:
        pass
    if isinstance(value, (float, np.floating)) and (
        np.isnan(value) or np.isinf(value)
    ):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, _datetime.datetime, _datetime.date)):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        try:
            return bytes(value).decode("utf-8", errors="replace")
        except Exception:
            return None
    return value


def resolve_confusion_url(payload):
    """Turn each result's ConfusionImage file name into a servable URL."""
    items = payload if isinstance(payload, list) else [payload]

    for item in items:
        if not isinstance(item, dict):
            continue
        result = item.get("result")
        if isinstance(result, dict) and result.get("ConfusionImage"):
            file_name = result["ConfusionImage"]
            result["ConfusionImageUrl"] = (
                f"/api/confusion/{quote(file_name)}"
            )

    return payload


def dataset_summary():
    target_name = (
        state.y_data.columns[0]
        if isinstance(state.y_data, pd.DataFrame)
        else getattr(state.y_data, "name", "Unknown")
    )
    return {
        "dataset_id": state.dataset_id,
        "target_column": target_name,
        "num_features": state.X_data.shape[1] if state.X_data is not None else 0,
        "num_samples": state.X_data.shape[0] if state.X_data is not None else 0,
        "problem_type": state.problem_type,
        "appropriate_models": state.appropriate_models,
        "selected_model": state.selected_model,
    }
