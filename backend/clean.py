import pandas as pd

from backend.detector import detect_problem_type
from backend.classify import encode_target


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

    # ---------------------------------
    # 2. Clean string columns in X
    # ---------------------------------
    for column in X.select_dtypes(include=["object", "string"]).columns:
        X[column] = (
            X[column]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # ---------------------------------
    # 3. Clean string columns in y
    # ---------------------------------
    if isinstance(y, pd.DataFrame):
        for column in y.select_dtypes(include=["object", "string"]).columns:
            y[column] = (
                y[column]
                .astype("string")
                .str.strip()
                .str.lower()
            )
    else:
        if y.dtype == "object" or pd.api.types.is_string_dtype(y):
            y = (
                y.astype("string")
                .str.strip()
                .str.lower()
            )

    # ---------------------------------
    # 4. Convert empty strings to NaN
    # ---------------------------------
    X = X.replace(r"^\s*$", pd.NA, regex=True)
    y = y.replace(r"^\s*$", pd.NA, regex=True)

    # ---------------------------------
    # 5. Combine X and y
    # ---------------------------------
    data = pd.concat([X, y], axis=1)

    rows_before = len(data)

    # ---------------------------------
    # 6. Remove rows containing NaN
    # ---------------------------------
    data = data.dropna()

    nan_rows_removed = rows_before - len(data)

    # ---------------------------------
    # 7. Remove duplicate rows
    # ---------------------------------
    rows_before_duplicates = len(data)

    data = data.drop_duplicates()

    duplicate_rows_removed = (
        rows_before_duplicates - len(data)
    )

    # ---------------------------------
    # 8. Separate X and y
    # ---------------------------------
    X_clean = data[X.columns].copy()

    if isinstance(y, pd.DataFrame):
        y_clean = data[y.columns].copy()
    else:
        y_clean = data[y.name].copy()

    # ---------------------------------
    # 9. Detect problem type
    # ---------------------------------
    problem = detect_problem_type(y_clean)

    # ---------------------------------
    # 10. Prepare result
    # ---------------------------------
    result = {
        "X_shape_before": list(original_X_shape),
        "y_shape_before": list(original_y_shape),

        "nan_rows_removed": int(nan_rows_removed),
        "duplicate_rows_removed": int(duplicate_rows_removed),

        "X_shape_after": list(X_clean.shape),
        "y_shape_after": list(y_clean.shape),

        "X": X_clean,
        "y": y_clean,

        "problem_type": problem["problem_type"],
        "target_encoded": False,
    }

    # ---------------------------------
    # 11. Classification target encoding
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