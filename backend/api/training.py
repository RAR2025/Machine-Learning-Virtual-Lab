"""POST /api/train — train and compare encoding strategies."""
import datetime
import logging

from fastapi import APIRouter, HTTPException

from backend.core import experiments as exps
from backend.core import state as legacy_state
from backend.schemas import TrainRequest
from backend.services.encoding import loo, mestimate, onehot, target
from backend.services.encoding import embedding as embedding_enc
from backend.services.modeling.registry import canonical_key
from backend.services.splitting import make_split
from backend.utils.http import json_safe, resolve_confusion_url

logger = logging.getLogger("ml-virtual-lab")

router = APIRouter()

PRIMARY_ENCODINGS = ("onehot", "target", "loo", "embedding")


def _resolve_exp(request: TrainRequest):
    exp = exps.get_experiment(request.experiment_id)
    # legacy fallback: default experiment may have been loaded via old routes
    if not exps.is_loaded(exp) and exps.is_loaded(exps.get_experiment(None)) and exp.get("experiment_id") == "default":
        pass
    if not exps.is_loaded(exp):
        # allow legacy global
        if legacy_state.X_data is not None and exp.get("experiment_id") == "default":
            exp["X_data"] = legacy_state.X_data
            exp["y_data"] = legacy_state.y_data
            exp["dataset_id"] = legacy_state.dataset_id
            exp["problem_type"] = legacy_state.problem_type
            exp["appropriate_models"] = legacy_state.appropriate_models
            exp["selected_model"] = legacy_state.selected_model
    return exp


@router.post("/api/train")
def train_model(request: TrainRequest):
    exp = _resolve_exp(request)
    if not exps.is_loaded(exp):
        raise HTTPException(status_code=400, detail="No dataset loaded. Please POST /api/analyze first.")
    if len(exp["X_data"]) == 0:
        raise HTTPException(status_code=400, detail="Dataset is empty (0 rows). Clean or reload the dataset.")
    if not exp.get("selected_model") and not request.model:
        raise HTTPException(status_code=400, detail="No model in state. Please POST /api/analyze first.")

    try:
        y_check = exps.y_series(exp)
        if exp.get("problem_type") == "Classification" and y_check is not None:
            if int(y_check.nunique()) < 2:
                raise HTTPException(status_code=400, detail="Target has a single class after cleaning. Classification needs at least 2 classes.")
    except HTTPException:
        raise
    except Exception:
        pass

    encoding = (request.encoding or "all").lower().strip()
    problem = exp.get("problem_type") or "Classification"

    # Resolve model + split config (request overrides stored, then persisted)
    model_key = canonical_key(request.model or exp.get("selected_model"), problem)
    try:
        from backend.services.modeling.registry import resolve_model as _resolve
        _resolve(problem, model_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    exp["selected_model"] = model_key
    if request.test_size is not None:
        exp["test_size"] = float(request.test_size)
    if request.random_state is not None:
        exp["random_state"] = int(request.random_state)
    ts = float(exp.get("test_size", 0.2)); rs = int(exp.get("random_state", 42))
    if exp.get("experiment_id") == "default":
        legacy_state.selected_model = model_key

    # One shared split for fair comparison (BEFORE any target encoding).
    notes_shared: list = []
    split = make_split(exps.y_series(exp), test_size=ts, random_state=rs,
                       problem_type=problem, notes=notes_shared)
    exp["split"] = split
    exps.touch(exp)

    encodings = {
        "onehot": onehot.run_one_hot_encoding,
        "target": target.run_target_encoding,
        "loo": loo.run_loo_encoding,
        "embedding": embedding_enc.run_embedding_encoding,
        # legacy, hidden from primary UI but still callable
        "m_estimate": mestimate.run_m_estimate_encoding,
    }

    def run_one(key):
        fn = encodings[key]
        kwargs = dict(experiment_id=exp.get("experiment_id"), model=model_key,
                      test_size=ts, random_state=rs, split=split)
        # Embedding uses fixed lab defaults (dim=8, epochs=20); no UI tuning.
        item = fn(**kwargs)
        # attach shared-split note
        item.setdefault("notes", []).append(
            "Same train/test split reused for all encodings in this run (fair comparison)."
        )
        for n in notes_shared:
            if n not in item["notes"]:
                item["notes"].append(n)
        return item

    def meta_for(items):
        return {
            "experiment_id": exp.get("experiment_id"),
            "dataset_id": exp.get("dataset_id"),
            "dataset_name": exp.get("dataset_name"),
            "model": model_key,
            "problem_type": problem,
            "test_size": ts,
            "random_state": rs,
            "split": split,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }

    try:
        if encoding == "all":
            # Primary experiment (classification/Adult): onehot/target/loo/embedding.
            # Regression generic support: embedding MLP is classification-focused,
            # so the 4th slot uses legacy m-estimate (kept optional, hidden from
            # the primary classification UI).
            run_keys = PRIMARY_ENCODINGS
            if problem == "Regression":
                run_keys = ("onehot", "target", "loo", "m_estimate")
            results = []
            for key in run_keys:
                try:
                    results.append(run_one(key))
                except Exception as e:
                    logger.exception("Encoding '%s' failed", key)
                    results.append({
                        "encoding_name": key, "encoding_key": key,
                        "problem_type": problem, "selected_model": model_key,
                        "categorical_cols_encoded": [], "numerical_cols": [],
                        "encoded_applied": False,
                        "notes": [f"Encoding '{key}' failed: {str(e)}"],
                        "train_test_split": {"train_samples": split["train_samples"], "test_samples": split["test_samples"]},
                        "result": None, "error": str(e),
                    })
            payload = {"results": json_safe(resolve_confusion_url(results)),
                       "comparison": build_comparison(results),
                       "meta": meta_for(results)}
            exp["train_results"] = payload["results"]
            exp["train_meta"] = payload["meta"]
            exps.touch(exp)
            return payload
        elif encoding not in encodings:
            raise HTTPException(status_code=400, detail=f"Unknown encoding '{encoding}'. Choose from: all, onehot, target, loo, embedding")
        else:
            result = run_one(encoding)
            payload = {"results": json_safe(resolve_confusion_url(result)),
                       "comparison": build_comparison([result]),
                       "meta": meta_for([result])}
            exp["train_results"] = [result] if not isinstance(payload["results"], list) else payload["results"]
            exp["train_meta"] = payload["meta"]
            exps.touch(exp)
            return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Training failed")
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


def build_comparison(items):
    """Side-by-side metric table (no ranking/best labels)."""
    rows = []
    for it in items:
        r = (it or {}).get("result") or {}
        rows.append({
            "encoding": it.get("encoding_name"),
            "encoding_key": it.get("encoding_key"),
            "accuracy": r.get("Accuracy"),
            "precision": r.get("Precision"),
            "recall": r.get("Recall"),
            "f1": r.get("F1"),
            "n_features_out": it.get("n_features_out"),
            "ok": r is not None and bool(r),
            "error": it.get("error"),
        })
    # Factual range statement (no "best" claim)
    f1s = [x["f1"] for x in rows if isinstance(x.get("f1"), (int, float))]
    note = "Performance differences indicate how each representation affects the selected model."
    if f1s:
        note = (f"Across evaluated encodings, F1 ranged from {min(f1s):.4f} to {max(f1s):.4f}. " + note)
    return {"rows": rows, "note": note + " Same train/test split and same model configuration were used."}
