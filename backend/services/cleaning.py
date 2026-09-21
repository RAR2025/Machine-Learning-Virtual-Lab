"""Robust dataset-cleaning pipeline for UCI datasets.

Goals:
  * Kill placeholder junk (".", "?", "NA", "n/a", "null", "--", ...) in
    categoricals *before* it can fragment encodings.
  * Handle numeric sentinels (-999, inf), comma/percent formatted numbers,
    unicode noise, datetime-like columns.
  * Preserve data: impute feature gaps (median / mode) instead of dropping
    every row with a NaN; only rows with a missing *target* are dropped.
  * Reduce encoder pain: drop constant / mostly-empty columns, group rare
    categories into "other", cap extreme numeric outliers (IQR).
  * Report everything so the frontend can show what happened.
"""

import re
import unicodedata
import warnings

import numpy as np
import pandas as pd

from backend.services.detection import detect_problem_type
from backend.services.modeling.target import encode_target


# ---------------------------------------------------------------------------
# Placeholder / missing-value tokens (compared AFTER normalisation:
# unicode-NFKC, strip, collapse whitespace, lowercase).
# ---------------------------------------------------------------------------
MISSING_TOKENS = {
    "",
    ".",
    "..",
    "...",
    "....",
    ".....",
    "?",
    "??",
    "???",
    "-",
    "--",
    "---",
    "----",
    "na",
    "n/a",
    "n\\a",
    "n.a",
    "n.a.",
    "n a",
    "nan",
    "nat",
    "none",
    "null",
    "nil",
    "missing",
    "unknown",
    "undef",
    "undefined",
    "not defined",
    "no value",
    "not available",
    "not applicable",
    "nil.",
    "null.",
    "none.",
    "missing.",
    "unknown.",
    "#na",
    "#n/a",
    "#null",
    "#missing",
    "#div/0!",
    "#value!",
    "*",
    "**",
    "***",
    "#",
    "##",
    "-999",
    "-9999",
    "-99999",
}

# Strings made ONLY of these punctuation chars (short ones) are placeholders:
# ".", "..", "?.", "--", "##", "**", "//", etc. Real values such as
# "st. louis" or "e-mail" always contain other characters and are kept.
_PUNCT_ONLY_RE = re.compile(r"^[.\?\-_\*#/\\|~]+$")

# Numeric sentinel values that mean "missing" in the wild.
NUMERIC_SENTINELS = {-999.0, -9999.0, -99999.0}

# Tuning knobs for the pipeline.
MAX_COLUMN_MISSING_RATIO = 0.5   # drop feature columns missing more than this
NUMERIC_COERCE_THRESHOLD = 0.7   # convert object col to numeric if >=70% parses
DATETIME_PARSE_THRESHOLD = 0.7   # convert object col to datetime if >=70% parses
RARE_MIN_COUNT = 2               # categories rarer than this (and <1%) -> "other"
RARE_MIN_FRAC = 0.01
RARE_MIN_UNIQUES = 10            # only group when a column has >10 categories

# Single-char tokens that double as legitimate binary categories in UCI
# sets (Credit Approval's +/- target). They are treated as missing only
# when they are NOT load-bearing: if the token is frequent (>5% of the
# column) it is kept as a real category instead of being wiped out.
_LOAD_BEARING_TOKENS = {"-", "+"}
_LOAD_BEARING_MIN_FRAC = 0.05
# Characters stripped from the *ends* of string values (stray wrappers).
_STRIP_CHARS = " .\"'`;:,\u200b\u200c\u200d\ufeff"


# ---------------------------------------------------------------------------
# String normalisation helpers
# ---------------------------------------------------------------------------
def _unicode_clean(s: pd.Series) -> pd.Series:
    """NFKC-normalise, kill NBSP / zero-width chars, collapse whitespace."""
    s = s.astype("string")
    try:
        s = s.str.normalize("NFKC")
    except Exception:
        s = s.map(
            lambda v: unicodedata.normalize("NFKC", v) if isinstance(v, str) else v
        ).astype("string")
    s = s.str.replace("\u00a0", " ", regex=False)
    s = s.str.replace("[\u200b\u200c\u200d\ufeff]", "", regex=True)
    s = s.str.replace(r"\s+", " ", regex=True)
    return s


def _normalize_string_series(s: pd.Series) -> pd.Series:
    """Strip wrappers, collapse whitespace, lowercase. Keeps inner dots."""
    s = _unicode_clean(s)
    s = s.str.strip()
    # Stray leading/trailing periods/quotes ("m." -> "m", "'red'" -> "red").
    # A lone "." / "..." becomes "" and is treated as missing downstream.
    s = s.str.strip(_STRIP_CHARS).str.strip()
    s = s.str.replace(r"\s+", " ", regex=True)
    s = s.str.lower()
    s = s.str.strip(_STRIP_CHARS).str.strip()
    return s


def _missing_mask(s: pd.Series) -> pd.Series:
    """Boolean mask of placeholder-token cells in an already-normalised series."""
    mask = s.isin(MISSING_TOKENS)
    remaining = s[~mask & s.notna()]
    if len(remaining):
        punct = remaining.str.match(r"^[.\?\-_\*#/\\|~]+$").fillna(False)
        short = (remaining.str.len() <= 10).fillna(False)
        punct = punct & short
        mask.loc[punct[punct].index] = True
    return mask.fillna(False)


def _clean_string_series(s: pd.Series) -> tuple[pd.Series, int]:
    """Normalise a string column; placeholder tokens -> NA.

    Returns (cleaned_series, placeholder_cells_found).
    """
    s = _normalize_string_series(s)
    mask = _missing_mask(s)
    # Load-bearing guard: a frequent "-" / "+" is a real binary category
    # (e.g. Credit Approval's +/- target), not a placeholder. Unmask it
    # instead of wiping out half the column.
    n = len(s)
    if n:
        for tok in _LOAD_BEARING_TOKENS:
            tok_cells = s == tok
            n_tok = int(tok_cells.sum())
            if n_tok / n > _LOAD_BEARING_MIN_FRAC and bool(mask[tok_cells].all()):
                mask = mask & ~tok_cells
    found = int(mask.sum())
    s = s.mask(mask, pd.NA)
    s = s.replace(r"^\s*$", pd.NA, regex=True)
    return s, found


def _clean_string_frame(df: pd.DataFrame) -> int:
    """Clean every string-like column of df in place. Returns placeholder cells."""
    total = 0
    for column in df.select_dtypes(include=["object", "string", "category"]).columns:
        cleaned, found = _clean_string_series(df[column])
        df[column] = cleaned
        total += found
    return total


# ---------------------------------------------------------------------------
# Numeric / datetime recovery
# ---------------------------------------------------------------------------
def _coerce_numeric_like(df: pd.DataFrame) -> list:
    """Convert object/string cols that are really numbers ("1,000", "45%").

    Returns the list of converted column names.
    """
    converted = []
    for column in df.select_dtypes(include=["object", "string"]).columns:
        raw = df[column].astype("string")
        s = raw.str.strip()
        # drop thousand-separators, currency symbols, trailing % (keep value)
        s = s.str.replace(",", "", regex=False)
        s = s.str.replace(r"^[$\u20b9\u20ac\u00a3\u00a5]", "", regex=True)
        s = s.str.replace(r"%$", "", regex=True).str.strip()
        coerced = pd.to_numeric(s, errors="coerce")
        non_na = df[column].notna().sum()
        if non_na == 0:
            continue
        if int(coerced.notna().sum()) / int(non_na) >= NUMERIC_COERCE_THRESHOLD:
            df[column] = coerced
            converted.append(column)
    return converted


def _convert_datetime_like(df: pd.DataFrame) -> list:
    """Convert object/string cols that parse as datetimes to unix seconds.

    Encoders can't consume raw datetimes, so we materialise them as numeric
    epoch seconds (NaT -> NaN, imputed later). Returns converted columns.
    """
    converted = []
    for column in df.select_dtypes(include=["object", "string"]).columns:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                dt = pd.to_datetime(df[column], errors="coerce")
            except Exception:
                continue
        non_na = df[column].notna().sum()
        if non_na == 0:
            continue
        if int(dt.notna().sum()) / int(non_na) >= DATETIME_PARSE_THRESHOLD:
            epoch = (dt - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
            df[column] = epoch.astype("float64")
            converted.append(column)
    return converted


def _replace_numeric_sentinels(df: pd.DataFrame) -> int:
    """Turn sentinel numbers (-999, +/-inf) in numeric cols into NA."""
    cells = 0
    for column in df.select_dtypes(include=["number"]).columns:
        col = df[column]
        mask = col.isin(list(NUMERIC_SENTINELS))
        try:
            mask = mask | col.isin([np.inf, -np.inf])
        except Exception:
            pass
        n = int(mask.sum())
        if n:
            df[column] = col.mask(mask, np.nan)
            cells += n
    return cells


# ---------------------------------------------------------------------------
# Column hygiene
# ---------------------------------------------------------------------------
def _tidy_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names and dedupe (append _1, _2 ...)."""
    seen: dict = {}
    new_cols = []
    for col in df.columns:
        name = str(col).strip().replace("\u00a0", " ") or "column"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        new_cols.append(name)
    df.columns = new_cols
    return df


def _drop_sparse_columns(X: pd.DataFrame) -> tuple[list, dict]:
    """Drop all-missing or mostly-missing (>50%) feature columns."""
    dropped = []
    missing_ratio = {}
    for column in list(X.columns):
        ratio = float(X[column].isna().mean()) if len(X) else 0.0
        missing_ratio[str(column)] = round(ratio, 4)
        if ratio >= 1.0 or ratio > MAX_COLUMN_MISSING_RATIO:
            X.drop(columns=[column], inplace=True)
            dropped.append(str(column))
    return dropped, missing_ratio


def _drop_constant_columns(X: pd.DataFrame) -> list:
    """Drop zero-variance feature columns (useless for every encoder/model)."""
    dropped = []
    for column in list(X.columns):
        try:
            if int(X[column].nunique(dropna=True)) <= 1:
                X.drop(columns=[column], inplace=True)
                dropped.append(str(column))
        except Exception:
            continue
    return dropped


def _impute_features(X: pd.DataFrame) -> tuple[int, dict, dict]:
    """Median-impute numerics, mode-impute categoricals. Returns counts."""
    total = 0
    numeric_imputed: dict = {}
    categorical_imputed: dict = {}
    for column in X.columns:
        missing = int(X[column].isna().sum())
        if not missing:
            continue
        if pd.api.types.is_numeric_dtype(X[column]):
            median = X[column].median()
            if pd.isna(median):
                continue
            X[column] = X[column].fillna(median)
            total += missing
            numeric_imputed[str(column)] = missing
        else:
            try:
                mode = X[column].mode(dropna=True)
            except Exception:
                mode = pd.Series(dtype=object)
            if len(mode) == 0:
                continue
            X[column] = X[column].fillna(mode.iloc[0])
            total += missing
            categorical_imputed[str(column)] = missing
    return total, numeric_imputed, categorical_imputed


def _group_rare_categories(X: pd.DataFrame) -> dict:
    """Fold ultra-rare categories into "other" to tame one-hot dimensionality.

    Only applies to columns with >10 distinct values; a category is rare when
    its count < max(RARE_MIN_COUNT, ceil(RARE_MIN_FRAC * n_rows)).
    Returns {column: n_distinct_categories_merged}.
    """
    grouped: dict = {}
    n = len(X)
    if n == 0:
        return grouped
    min_count = max(RARE_MIN_COUNT, int(np.ceil(RARE_MIN_FRAC * n)))
    for column in X.select_dtypes(include=["object", "string", "category"]).columns:
        try:
            uniques = int(X[column].nunique(dropna=True))
        except Exception:
            continue
        if uniques <= RARE_MIN_UNIQUES:
            continue
        counts = X[column].value_counts(dropna=True)
        rare = counts[counts < min_count].index.tolist()
        if not rare:
            continue
        X[column] = X[column].mask(X[column].isin(rare), "other")
        grouped[str(column)] = len(rare)
    return grouped


def _cap_outliers(X: pd.DataFrame) -> tuple[int, dict]:
    """Winsorize numeric features at 1.5*IQR bounds. Returns (cells, per-col)."""
    total = 0
    per_col: dict = {}
    for column in X.select_dtypes(include=["number"]).columns:
        s = X[column]
        try:
            q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
        except Exception:
            continue
        iqr = q3 - q1
        if not np.isfinite(iqr) or iqr == 0:
            continue
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        capped = int(((s < lo) | (s > hi)).sum())
        if capped:
            X[column] = s.clip(lower=lo, upper=hi)
            total += capped
            per_col[str(column)] = capped
    return total, per_col


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def clean_dataset(X, y):
    # ---------------------------------
    # 1. Validate target
    # ---------------------------------
    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError(
                "This application currently supports only one target column."
            )

    # Make copies so original data is not modified
    X = X.copy()
    y = y.copy()

    original_X_shape = X.shape
    original_y_shape = y.shape
    dtypes_before = {str(c): str(X[c].dtype) for c in X.columns}

    if isinstance(y, pd.DataFrame):
        y_frame = y
        y_is_frame = True
    else:
        # Work with a 1-col frame internally so Series targets get the same
        # cleaning path; convert back at split time.
        y_is_frame = False
        y_frame = y.to_frame()

    _tidy_column_names(X)
    _tidy_column_names(y_frame)

    # ---------------------------------
    # 2. Normalise strings + "." / placeholder tokens -> NA
    # ---------------------------------
    placeholder_cells_x = _clean_string_frame(X)
    placeholder_cells_y = _clean_string_frame(y_frame)

    X = X.replace(r"^\s*$", pd.NA, regex=True)
    y_frame = y_frame.replace(r"^\s*$", pd.NA, regex=True)

    # ---------------------------------
    # 3. Recover numeric / datetime columns hiding as strings
    # ---------------------------------
    numeric_coerced = _coerce_numeric_like(X)
    numeric_coerced_y = _coerce_numeric_like(y_frame)
    datetime_converted = _convert_datetime_like(X)

    # ---------------------------------
    # 4. Numeric sentinels (-999, inf) -> NA
    # ---------------------------------
    sentinel_cells = _replace_numeric_sentinels(X) + _replace_numeric_sentinels(y_frame)

    # ---------------------------------
    # 5. Drop hopeless feature columns (>50% missing), impute the rest
    # ---------------------------------
    sparse_dropped, missing_ratio = _drop_sparse_columns(X)
    imputed_cells, numeric_imputed, categorical_imputed = _impute_features(X)

    # ---------------------------------
    # 6. Missing targets -> drop rows (targets are never imputed)
    # ---------------------------------
    data = pd.concat([X, y_frame], axis=1)
    rows_before = len(data)
    target_col = list(y_frame.columns)[0]
    rows_dropped_target = int(data[target_col].isna().sum())
    data = data.dropna(subset=[target_col])
    # Final safety net: nothing in X should still be NA after imputation.
    residual_na_rows = int(data[X.columns].isna().any(axis=1).sum()) if len(X.columns) else 0
    data = data.dropna(subset=list(X.columns)) if len(X.columns) else data
    nan_rows_removed = rows_before - len(data)

    # ---------------------------------
    # 7. Column hygiene on the surviving rows
    # ---------------------------------
    X_tmp = data[X.columns].copy() if len(X.columns) else data.iloc[:, 0:0].copy()
    constant_dropped = _drop_constant_columns(X_tmp)
    rare_grouped = _group_rare_categories(X_tmp)
    outliers_capped, outliers_per_col = _cap_outliers(X_tmp)
    data = pd.concat([X_tmp, data[[target_col]]], axis=1)

    # ---------------------------------
    # 8. Remove duplicate rows
    # ---------------------------------
    rows_before_duplicates = len(data)
    data = data.drop_duplicates()
    duplicate_rows_removed = rows_before_duplicates - len(data)

    if len(data) == 0:
        raise ValueError(
            "Cleaning removed all rows. The dataset is empty after removing "
            "missing targets, sparse columns and duplicates."
        )
    if len(X_tmp.columns) == 0:
        raise ValueError(
            "Cleaning removed all feature columns (all missing, constant or "
            "sparse). Nothing left to train on."
        )

    # ---------------------------------
    # 9. Separate X and y
    # ---------------------------------
    X_clean = data[X_tmp.columns].copy()
    y_clean = data[[target_col]].copy()
    if not y_is_frame:
        y_clean = y_clean.iloc[:, 0]

    # ---------------------------------
    # 10. Detect problem type
    # ---------------------------------
    problem = detect_problem_type(y_clean)
    if problem["problem_type"] == "Classification":
        n_classes = int(y_clean.nunique().iloc[0] if isinstance(y_clean, pd.DataFrame) else y_clean.nunique())
        if n_classes < 2:
            raise ValueError(
                "Cleaning left a single class in the target. "
                "Classification needs at least 2 classes."
            )

    # ---------------------------------
    # 11. Prepare result (old keys preserved for the frontend)
    # ---------------------------------
    warnings: list = []
    for col in sparse_dropped:
        warnings.append(f"Column '{col}' dropped: mostly missing.")
    for col in constant_dropped:
        warnings.append(f"Column '{col}' dropped: constant (zero variance).")

    result = {
        "X_shape_before": list(original_X_shape),
        "y_shape_before": list(original_y_shape),

        "nan_rows_removed": int(nan_rows_removed),
        "duplicate_rows_removed": int(duplicate_rows_removed),

        "placeholder_cells_found": int(placeholder_cells_x + placeholder_cells_y),
        "placeholder_cells_in_X": int(placeholder_cells_x),
        "placeholder_cells_in_y": int(placeholder_cells_y),
        "sentinel_cells_found": int(sentinel_cells),
        "rows_dropped_target_missing": int(rows_dropped_target),
        "residual_na_rows_removed": int(residual_na_rows),

        "imputed_cells": int(imputed_cells),
        "numeric_imputed": {k: int(v) for k, v in numeric_imputed.items()},
        "categorical_imputed": {k: int(v) for k, v in categorical_imputed.items()},

        "columns_dropped": [str(c) for c in (sparse_dropped + constant_dropped)],
        "sparse_columns_dropped": [str(c) for c in sparse_dropped],
        "constant_columns_dropped": [str(c) for c in constant_dropped],
        "numeric_coerced": [str(c) for c in numeric_coerced],
        "datetime_converted": [str(c) for c in datetime_converted],
        "rare_grouped": {k: int(v) for k, v in rare_grouped.items()},
        "outliers_capped": int(outliers_capped),
        "outliers_per_column": {k: int(v) for k, v in outliers_per_col.items()},
        "dtypes_before": dtypes_before,
        "dtypes_after": {str(c): str(X_clean[c].dtype) for c in X_clean.columns},
        "warnings": warnings,

        "X_shape_after": list(X_clean.shape),
        "y_shape_after": list(y_clean.shape),

        "X": X_clean,
        "y": y_clean,

        "problem_type": problem["problem_type"],
        "target_encoded": False,
    }

    # ---------------------------------
    # 12. Classification target encoding
    # ---------------------------------
    if problem["problem_type"] == "Classification":
        encoded = encode_target(y_clean)
        result["target_encoded"] = True
        result["y"] = encoded["y_encoded"]
        result["encoded_column"] = encoded["encoded_column"]
        result["class_mapping"] = encoded["class_mapping"]
        result["num_classes"] = encoded["num_classes"]
        result["unique_target_values"] = encoded["unique_target_values"]
    else:
        result["unique_target_values"] = int(
            y_clean.nunique().iloc[0]
            if isinstance(y_clean, pd.DataFrame)
            else y_clean.nunique()
        )

    return result
