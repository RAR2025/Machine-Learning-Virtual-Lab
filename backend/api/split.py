"""Train/test split configuration (must happen BEFORE target encoding)."""
from fastapi import APIRouter, HTTPException

from backend.core import experiments as exps
from backend.schemas import SplitRequest
from backend.services.splitting import make_split

router = APIRouter()


@router.post("/api/split")
def configure_split(body: SplitRequest):
    exp = exps.get_experiment(body.experiment_id)
    if not exps.is_loaded(exp):
        raise HTTPException(status_code=400, detail="No dataset loaded. Please POST /api/analyze first.")
    notes: list = []
    try:
        rec = make_split(exps.y_series(exp), test_size=float(body.test_size),
                         random_state=int(body.random_state),
                         problem_type=exp.get("problem_type") or "Classification",
                         notes=notes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    exp["test_size"] = float(body.test_size)
    exp["random_state"] = int(body.random_state)
    exp["split"] = rec
    exp["train_results"] = None
    exps.touch(exp)
    return {"experiment_id": exp.get("experiment_id"), "split": rec, "notes": notes,
            "message": "Split configured BEFORE encoding. Target encoders will fit on training data only."}
