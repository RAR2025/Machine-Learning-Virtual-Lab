"""Backward-compatible global state.

New code should use backend.core.experiments.get_experiment(experiment_id).
This module proxies the "default" experiment so existing imports
(state.X_data, state.reset(), ...) keep working.
"""
import pandas as pd

from backend.core import experiments as _exps


def _default():
    return _exps.get_experiment(None)


# Module-level attribute access is provided via __getattr__ (PEP 562).
def __getattr__(name):
    if name in ("X_data", "y_data", "dataset_id", "problem_type",
                "appropriate_models", "selected_model"):
        return _default().get(name)
    raise AttributeError(name)


def __setattr__(name, value):
    if name in ("X_data", "y_data", "dataset_id", "problem_type",
                "appropriate_models", "selected_model"):
        _default()[name] = value
    else:
        globals()[name] = value


def reset():
    _exps.reset_experiment(None)


def is_loaded():
    return _exps.is_loaded(_default())


def y_series():
    return _exps.y_series(_default())


def summary():
    return _exps.summary(_default())
