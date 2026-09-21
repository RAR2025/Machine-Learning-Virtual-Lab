import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from backend.core import state
from backend.core import experiments as exps
from backend.services.evaluation import classification as classification_eval
from backend.services.evaluation import regression as regression_eval
from backend.services.modeling.registry import canonical_key, resolve_model
from backend.services.splitting import make_split


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

    if not transformers:
        raise ValueError("No usable feature columns left for training.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def _safe_split(X, y, problem_type, notes):
    """Stratified split for classification, with graceful fallback.

    Stratification crashes when a class has fewer than 2 members; fall back
    to an unstratified split and record a note instead of failing the run.
    """
    from sklearn.model_selection import train_test_split
    stratify = y if problem_type == "Classification" else None
    try:
        return train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )
    except ValueError:
        if stratify is not None:
            notes.append(
                "Stratified split was not possible (a class has too few "
                "samples); fell back to an unstratified split."
            )
            from sklearn.model_selection import train_test_split as tts
            return tts(X, y, test_size=0.2, random_state=42)
        raise


def _resolve_experiment_data(experiment_id):
    if experiment_id:
        exp = exps.get_experiment(experiment_id)
        if exps.is_loaded(exp):
            return exp, exp["X_data"], exps.y_series(exp), exp.get("problem_type"), exp.get("selected_model")
    # fallback to legacy default state
    X = state.X_data
    y = state.y_series()
    return None, X, y, state.problem_type, state.selected_model


def run_workflow(encoding_name, make_encoder, experiment_id=None, model=None,
                 test_size=None, random_state=None, split=None):
    exp, X, y, problem_type, selected_model = _resolve_experiment_data(experiment_id)

    if X is None or len(X) == 0:
        raise ValueError("No dataset loaded. Please POST /api/analyze first.")

    if y is None or len(y) == 0:
        raise ValueError("No target loaded. Please POST /api/analyze first.")

    if len(X.columns) == 0:
        raise ValueError("No feature columns left to train on.")

    if problem_type is None:
        from backend.services.detection import detect_problem_type
        problem_type = detect_problem_type(y)["problem_type"]

    if problem_type == "Classification" and int(pd.Series(np.asarray(y)).nunique()) < 2:
        raise ValueError(
            "Target has a single class. Classification needs at least 2 classes."
        )

    categorical_cols, numerical_cols = get_categorical_numerical_cols(X)

    notes = []

    if not categorical_cols:
        notes.append(
            f"{encoding_name}: dataset has no categorical columns, so no "
            "encoding was applied. The model was trained on the numerical "
            "features directly."
        )

    # Resolve split: reuse provided indices (fair comparison) or build new.
    ts = float(test_size) if test_size is not None else float((exp or {}).get("test_size", 0.2) or 0.2)
    rs = int(random_state) if random_state is not None else int((exp or {}).get("random_state", 42) or 42)
    model_key = model or (exp or {}).get("selected_model") or selected_model

    # Align y to X's index so category_encoders sees matching indexes
    # (cleaning leaves non-contiguous indexes after row drops).
    y_aligned = pd.Series(np.asarray(y), index=X.index)
    if split is not None and split.get("train_idx") and split.get("test_idx"):
        train_idx = np.asarray(split["train_idx"], dtype=int)
        test_idx = np.asarray(split["test_idx"], dtype=int)
        # guard against stale indices
        n = len(X)
        train_idx = train_idx[(train_idx >= 0) & (train_idx < n)]
        test_idx = test_idx[(test_idx >= 0) & (test_idx < n)]
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_aligned.iloc[train_idx], y_aligned.iloc[test_idx]
        split_info = {
            "train_samples": int(len(train_idx)),
            "test_samples": int(len(test_idx)),
            "test_size": float(split.get("test_size", ts)),
            "random_state": int(split.get("random_state", rs)),
            "stratified": bool(split.get("stratified", False)),
        }
    else:
        split_rec = make_split(y, test_size=ts, random_state=rs,
                               problem_type=problem_type, notes=notes)
        train_idx = np.asarray(split_rec["train_idx"], dtype=int)
        test_idx = np.asarray(split_rec["test_idx"], dtype=int)
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_aligned.iloc[train_idx], y_aligned.iloc[test_idx]
        split_info = {
            "train_samples": split_rec["train_samples"],
            "test_samples": split_rec["test_samples"],
            "test_size": split_rec["test_size"],
            "random_state": split_rec["random_state"],
            "stratified": split_rec["stratified"],
        }
        split = split_rec

    encoder = make_encoder(categorical_cols)

    preprocessor = build_preprocessor(encoder, categorical_cols, numerical_cols)

    estimator = resolve_model(problem_type, model_key)

    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", estimator)]
    )

    eid = (exp or {}).get("experiment_id") if exp is not None else (experiment_id or "default")
    if problem_type == "Classification":
        result = classification_eval.evaluate_model(
            pipeline, X_train, X_test, y_train, y_test, encoding_name,
            experiment_id=eid,
        )
    else:
        result = regression_eval.evaluate_model(
            pipeline, X_train, X_test, y_train, y_test, encoding_name
        )

    # Feature dimension for reporting.
    n_features_in = None
    n_features_out = None
    try:
        Xt_train = pipeline.named_steps["preprocessor"].transform(X_train)
        import numpy as _np
        n_features_in = int(X_train.shape[1])
        n_features_out = int(_np.asarray(Xt_train).shape[1])
    except Exception:
        Xt_train = None

    # Encoded preview (df.head): what the model actually saw.
    encoded_preview = None
    try:
        arr = np.asarray(Xt_train)
        if arr is None:
            raise ValueError("no transformed data")
        try:
            cat_enc = pipeline.named_steps["preprocessor"].named_transformers_.get("categorical")
            if cat_enc is not None and hasattr(cat_enc, "get_feature_names_out"):
                cat_names = list(cat_enc.get_feature_names_out(categorical_cols))
            else:
                cat_names = list(categorical_cols)
            names = cat_names + list(numerical_cols)
            if len(names) != arr.shape[1]:
                names = [f"f{i}" for i in range(arr.shape[1])]
        except Exception:
            names = [f"f{i}" for i in range(arr.shape[1])]
        total_cols = len(names)
        show = min(total_cols, 12)
        head = arr[:5, :show]
        encoded_preview = {
            "columns": [str(c) for c in names[:show]],
            "rows": [[round(float(v), 4) for v in row] for row in head],
            "total_columns": int(total_cols),
            "hidden_columns": int(total_cols - show),
            "total_rows": int(arr.shape[0]),
            "shown_rows": int(min(5, arr.shape[0])),
        }
    except Exception:
        encoded_preview = None

    try:
        model_name = canonical_key(model_key, problem_type)
    except Exception:
        model_name = model_key

    return {
        "encoding_name": encoding_name,
        "encoding_key": encoding_name.lower().replace(" ", "_").replace("-", "_"),
        "problem_type": problem_type,
        "selected_model": selected_model if model_key is None else model_key,
        "model_key": model_name,
        "categorical_cols_encoded": categorical_cols,
        "numerical_cols": numerical_cols,
        "encoded_applied": bool(categorical_cols),
        "notes": notes,
        "train_test_split": split_info,
        "n_features_in": n_features_in,
        "n_features_out": n_features_out,
        "encoded_preview": encoded_preview,
        "result": result,
    }
