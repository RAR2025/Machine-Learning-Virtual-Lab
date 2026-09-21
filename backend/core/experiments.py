"""Per-experiment in-memory store.

Replaces the old process-global singleton with an experiment_id-keyed dict
so User A cannot overwrite User B's dataset. The legacy module-level
proxies (X_data, y_data, ...) are kept for backward compatibility and
point at the "default" experiment.
"""
import time
import uuid
import pandas as pd

DEFAULT_EXPERIMENT_ID = "default"

_experiments: dict = {}


def _new_record(experiment_id: str) -> dict:
    return {
        "experiment_id": experiment_id,
        "created_at": time.time(),
        "updated_at": time.time(),
        "X_data": None,
        "y_data": None,
        "dataset_id": None,
        "dataset_name": None,
        "problem_type": None,
        "appropriate_models": [],
        "selected_model": None,
        # Train/test split config + materialised indices
        "test_size": 0.2,
        "random_state": 42,
        "split": None,  # dict with train_idx/test_idx/stratified
        "clean_report": None,
        "train_results": None,
        "train_meta": None,
    }


def get_experiment(experiment_id: str | None) -> dict:
    eid = (experiment_id or DEFAULT_EXPERIMENT_ID).strip() or DEFAULT_EXPERIMENT_ID
    if eid not in _experiments:
        _experiments[eid] = _new_record(eid)
    return _experiments[eid]


def create_experiment() -> dict:
    eid = uuid.uuid4().hex[:12]
    _experiments[eid] = _new_record(eid)
    return _experiments[eid]


def reset_experiment(experiment_id: str | None) -> dict:
    eid = (experiment_id or DEFAULT_EXPERIMENT_ID).strip() or DEFAULT_EXPERIMENT_ID
    _experiments[eid] = _new_record(eid)
    return _experiments[eid]


def reset_all() -> None:
    _experiments.clear()


def is_loaded(exp: dict) -> bool:
    return exp.get("X_data") is not None and exp.get("y_data") is not None


def y_series(exp: dict):
    y_data = exp.get("y_data")
    if y_data is None:
        return None
    if isinstance(y_data, pd.DataFrame):
        return y_data.iloc[:, 0]
    return y_data


def summary(exp: dict) -> dict:
    X = exp.get("X_data")
    return {
        "experiment_id": exp.get("experiment_id"),
        "dataset_loaded": is_loaded(exp),
        "dataset_id": exp.get("dataset_id"),
        "dataset_name": exp.get("dataset_name"),
        "problem_type": exp.get("problem_type"),
        "selected_model": exp.get("selected_model"),
        "num_samples": X.shape[0] if X is not None else 0,
        "num_features": X.shape[1] if X is not None else 0,
    }


def touch(exp: dict) -> None:
    exp["updated_at"] = time.time()
