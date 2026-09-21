"""Model registry + selection routes."""
from fastapi import APIRouter, HTTPException

from backend.core import experiments as exps
from backend.core import state as legacy_state
from backend.schemas import ModelSelectRequest
from backend.services.modeling.registry import canonical_key, get_available_models, resolve_model

router = APIRouter()


@router.get("/api/models")
def list_models(experiment_id: str | None = None, problem_type: str | None = None):
    exp = exps.get_experiment(experiment_id)
    pt = problem_type or exp.get("problem_type") or legacy_state.problem_type or "Classification"
    if pt not in ("Classification", "Regression"):
        pt = "Classification"
    return {"problem_type": pt, "models": get_available_models(pt),
            "selected_model": exp.get("selected_model")}


@router.post("/api/models/select")
def select_model(body: ModelSelectRequest):
    exp = exps.get_experiment(body.experiment_id)
    pt = exp.get("problem_type") or legacy_state.problem_type or "Classification"
    try:
        key = canonical_key(body.model, pt)
        resolve_model(pt, key)  # validates
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    exp["selected_model"] = key
    exp["split"] = None  # model change does not invalidate split, but clear train cache
    exp["train_results"] = None
    exps.touch(exp)
    if exp.get("experiment_id") == "default":
        legacy_state.selected_model = key
    info = next((m for m in get_available_models(pt) if m.get("key") == key), {"key": key})
    return {"experiment_id": exp.get("experiment_id"), "selected_model": key, "model": info}
