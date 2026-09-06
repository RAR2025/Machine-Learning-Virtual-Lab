import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from backend import state
from backend import classificationmodel
from backend import regressionmodel
from backend.models import resolve_model


def get_categorical_numerical_cols(X):
    categorical_cols = X.select_dtypes(
        include=["object", "category", "bool", "string"]
    ).columns.tolist()
    numerical_cols = X.select_dtypes(include=["number"]).columns.tolist()
    return categorical_cols, numerical_cols


def build_preprocessor(encoder, categorical_cols, numerical_cols):
    transformers = []

    if categorical_cols:
        transformers.append(("categorical", encoder, categorical_cols))

    if numerical_cols:
        transformers.append(("numerical", StandardScaler(), numerical_cols))

    return ColumnTransformer(transformers=transformers)


def run_workflow(encoding_name, make_encoder):
    X = state.X_data

    if X is None:
        raise ValueError("No dataset loaded. Please POST /api/analyze first.")

    y = state.y_series()

    if y is None:
        raise ValueError("No target loaded. Please POST /api/analyze first.")

    problem_type = state.problem_type

    if problem_type is None:
        from backend.detector import detect_problem_type
        problem_type = detect_problem_type(y)["problem_type"]

    categorical_cols, numerical_cols = get_categorical_numerical_cols(X)

    if not categorical_cols:
        raise ValueError(
            f"{encoding_name}: dataset has no categorical columns to encode."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=(y if problem_type == "Classification" else None)
    )

    encoder = make_encoder(categorical_cols)

    preprocessor = build_preprocessor(encoder, categorical_cols, numerical_cols)

    estimator = resolve_model(problem_type, state.selected_model)

    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", estimator)]
    )

    if problem_type == "Classification":
        result = classificationmodel.evaluate_model(
            pipeline, X_train, X_test, y_train, y_test, encoding_name
        )
    else:
        result = regressionmodel.evaluate_model(
            pipeline, X_train, X_test, y_train, y_test, encoding_name
        )

    return {
        "encoding_name": encoding_name,
        "problem_type": problem_type,
        "selected_model": state.selected_model,
        "categorical_cols_encoded": categorical_cols,
        "numerical_cols": numerical_cols,
        "train_test_split": {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        },
        "result": result,
    }