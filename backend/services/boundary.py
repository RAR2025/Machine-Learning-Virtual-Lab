"""Phase 3 + Phase 8 — Core sklearn logic for POST /api/boundary.

Steps:
  1. Convert points -> X (N, 2), y (N,) numpy arrays.
  2. Build + train model per algo + hyperparams.
  3. Predict a resolution x resolution meshgrid over [0, 1] x [0, 1] (vectorized).
  4. Score on the training set (accuracy / precision / recall / f1 / confusion matrix).
  5. Compute bias-variance heuristic in [0, 1] (0 = high bias, 1 = high variance).
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from backend.schemas.boundary import BoundaryRequest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_float(params: Dict[str, Any], *keys: str, default: float) -> float:
    for k in keys:
        if k in params and params[k] is not None:
            try:
                return float(params[k])
            except (TypeError, ValueError):
                continue
    return default


def _get_int(params: Dict[str, Any], *keys: str, default: int) -> int:
    for k in keys:
        if k in params and params[k] is not None:
            try:
                return int(float(params[k]))
            except (TypeError, ValueError):
                continue
    return default


def _get_str(params: Dict[str, Any], *keys: str, default: str) -> str:
    for k in keys:
        if k in params and params[k] is not None:
            v = str(params[k]).strip().lower()
            if v:
                return v
    return default


# ---------------------------------------------------------------------------
# Model construction (Phase 8: cap / sanitize all hyperparams)
# ---------------------------------------------------------------------------

def build_model(algo: str, hyperparams: Dict[str, Any], n_samples: int):
    """Instantiate the sklearn classifier for *algo*."""
    params = dict(hyperparams or {})

    if algo == "knn":
        k = _get_int(params, "k", "n_neighbors", "n-neighbors", default=5)
        # Edge case: k > total points -> cap to total points (and >= 1).
        k = max(1, min(k, max(1, n_samples)))
        # Keep k odd for binary ties when possible (but never exceed n_samples).
        metric = _get_str(params, "metric", default="euclidean")
        if metric not in ("euclidean", "manhattan", "minkowski"):
            metric = "euclidean"
        weights = _get_str(params, "weights", default="uniform")
        if weights not in ("uniform", "distance"):
            weights = "uniform"
        p = 2
        if metric == "manhattan":
            p = 1
        model = KNeighborsClassifier(n_neighbors=k, metric=metric, weights=weights, p=p)
        model_info = {"k": k, "n_neighbors": k, "metric": metric, "weights": weights}
        return model, model_info

    if algo == "svm":
        kernel = _get_str(params, "kernel", default="rbf")
        if kernel not in ("linear", "rbf", "poly", "sigmoid"):
            kernel = "rbf"
        C = _get_float(params, "C", "c", "regularization", default=1.0)
        C = float(min(max(C, 0.01), 100.0))
        gamma = _get_str(params, "gamma", default="__float__")  # sentinel
        # gamma may be numeric or 'scale'/'auto'
        raw_gamma = params.get("gamma", params.get("g", 0.5))
        try:
            gamma_val = float(raw_gamma)  # type: ignore[arg-type]
            gamma_val = float(min(max(gamma_val, 0.01), 10.0))
        except (TypeError, ValueError):
            gamma_val = "scale" if str(raw_gamma).lower() in ("scale", "auto", "") else 0.5
        _ = gamma  # keep linters quiet; gamma_val is authoritative
        model = SVC(kernel=kernel, C=C, gamma=gamma_val)  # type: ignore[arg-type]
        model_info = {"kernel": kernel, "C": C, "c": C, "gamma": gamma_val}
        return model, model_info

    # algo == "dt"
    max_depth = params.get("max_depth", params.get("maxDepth", 4))
    try:
        max_depth_int = int(float(max_depth)) if max_depth is not None else 4  # type: ignore[arg-type]
    except (TypeError, ValueError):
        max_depth_int = 4
    max_depth_int = int(min(max(max_depth_int, 1), 20))
    criterion = _get_str(params, "criterion", default="gini")
    if criterion not in ("gini", "entropy", "log_loss"):
        criterion = "gini"
    min_split = _get_int(params, "min_samples_split", "minSamplesSplit", default=2)
    min_split = int(min(max(min_split, 2), max(2, n_samples)))
    model = DecisionTreeClassifier(
        max_depth=max_depth_int,
        criterion=criterion,
        min_samples_split=min_split,
        random_state=42,
    )
    model_info = {
        "max_depth": max_depth_int,
        "criterion": criterion,
        "min_samples_split": min_split,
        "tree_depth": max_depth_int,
    }
    return model, model_info


# ---------------------------------------------------------------------------
# Bias-variance heuristic -> float in [0, 1]
# ---------------------------------------------------------------------------

def variance_heuristic(algo: str, model_info: Dict[str, Any]) -> Tuple[float, str, str]:
    """Return (score, label, explanation). 0 = high bias, 1 = high variance."""
    if algo == "knn":
        k = int(model_info.get("k", 5))
        if k <= 1:
            return 0.9, "High Variance", (
                f"K={k} memorizes single neighbours; wiggly boundary that overfits noise."
            )
        if k <= 7:
            return 0.5, "Balanced", (
                f"K={k} balances local detail with smoothing; good bias-variance trade-off."
            )
        if k <= 15:
            return 0.3, "High Bias leaning", (
                f"K={k} over-smooths; broad consensus washes out local structure."
            )
        return 0.12, "High Bias", (
            f"K={k} heavily underfits; nearly the majority-class everywhere."
        )
    if algo == "svm":
        C = float(model_info.get("C", 1.0))
        gamma = model_info.get("gamma", 0.5)
        try:
            g = float(gamma)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            g = 0.5
        if C < 0.1 or g < 0.05:
            return 0.15, "High Bias", (
                f"C={C}, gamma={gamma}: soft margin / wide kernel underfits the data."
            )
        if C > 5 or g > 2.0:
            return 0.88, "High Variance", (
                f"C={C}, gamma={gamma}: hard margin / tight kernel islands overfit points."
            )
        return 0.5, "Balanced", (
            f"C={C}, gamma={gamma}: margin and kernel width trade off well."
        )
    # dt
    depth = int(model_info.get("max_depth", 4))
    if depth <= 1:
        return 0.1, "High Bias", (
            f"max_depth={depth} is a decision stump; single axis-aligned cut underfits."
        )
    if depth > 8:
        return 0.9, "High Variance", (
            f"max_depth={depth} grows staircases around individual points; overfits."
        )
    if depth <= 5:
        return 0.5, "Balanced", (
            f"max_depth={depth} partitions structure without memorizing noise."
        )
    return 0.7, "Variance leaning", (
        f"max_depth={depth} is expressive; watch for fragmented regions."
    )


# ---------------------------------------------------------------------------
# Main entry: fit + grid + metrics
# ---------------------------------------------------------------------------

def compute_boundary(req: BoundaryRequest) -> Dict[str, Any]:
    """Train on req.points and return the full response payload dict."""
    n = len(req.points)
    X = np.array([[p.x, p.y] for p in req.points], dtype=float).reshape(n, 2)
    y = np.array([p.label for p in req.points], dtype=int).reshape(n,)

    model, model_info = build_model(req.algo, req.hyperparams, n_samples=n)
    res = int(req.resolution)

    t0 = time.perf_counter()
    model.fit(X, y)
    fit_ms = (time.perf_counter() - t0) * 1000.0

    # Vectorized meshgrid prediction (no Python loops) — <200ms for 60x60.
    lin = np.linspace(0.0, 1.0, res)
    xx, yy = np.meshgrid(lin, lin)
    flat = np.c_[xx.ravel(), yy.ravel()]
    Z = model.predict(flat).reshape(res, res)
    grid = Z.astype(int).tolist()

    # Training-set metrics (guard single-class / tiny sets with zero_division=0).
    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred, labels=[0, 1]).tolist()
    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, zero_division=0))
    rec = float(recall_score(y, y_pred, zero_division=0))
    f1 = float(f1_score(y, y_pred, zero_division=0))

    var_score, var_label, var_expl = variance_heuristic(req.algo, model_info)

    # Extra model introspection for plan.md model_info.
    try:
        if req.algo == "svm" and hasattr(model, "n_support_"):
            model_info["n_support_vectors"] = int(np.sum(model.n_support_))  # type: ignore[attr-defined]
            model_info["n_support_per_class"] = [int(v) for v in model.n_support_]  # type: ignore[attr-defined]
        if req.algo == "dt" and hasattr(model, "get_depth"):
            model_info["actual_depth"] = int(model.get_depth())  # type: ignore[attr-defined]
            model_info["n_leaves"] = int(model.get_n_leaves())  # type: ignore[attr-defined]
    except Exception:
        pass

    support = {
        "class_0": int(int(np.sum(y == 0))),
        "class_1": int(int(np.sum(y == 1))),
    }

    payload: Dict[str, Any] = {
        # Flat (frontend) fields
        "grid": grid,
        "resolution": res,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "confusion_matrix": cm,
        "variance_score": float(var_score),
        "fit_time_ms": float(fit_ms),
        # Nested (plan.md) aliases
        "x_range": [0.0, 1.0],
        "y_range": [0.0, 1.0],
        "metrics": {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "confusion_matrix": cm,
            "support": support,
        },
        "model_info": model_info,
        "bias_variance": {
            "label": var_label,
            "score": float(var_score),
            "explanation": var_expl,
        },
    }
    return payload


__all__ = ["build_model", "variance_heuristic", "compute_boundary"]
