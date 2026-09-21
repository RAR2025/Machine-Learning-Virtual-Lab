"""System routes: health, reset, confusion images, SPA fallback."""
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.core import experiments as exps
from backend.core import state
from backend.core.config import (
    CONFUSION_PREFIX,
    CONFUSION_SUFFIX,
    FRONTEND_DIR,
    PROJECT_ROOT,
)

router = APIRouter()


@router.get("/api/health")
def health_check(experiment_id: str | None = None):
    exp = exps.get_experiment(experiment_id)
    base = exps.summary(exp)
    # legacy fields for old frontend
    return {
        "status": "ok",
        **base,
        "dataset_loaded": base["dataset_loaded"],
        "dataset_id": base["dataset_id"],
        "problem_type": base["problem_type"],
        "selected_model": base["selected_model"],
        "num_samples": base["num_samples"],
        "num_features": base["num_features"],
    }


@router.post("/api/reset")
def reset_state(experiment_id: str | None = None):
    """Clear the loaded dataset so a new one can be analyzed."""
    if experiment_id:
        exps.reset_experiment(experiment_id)
        return {"status": "ok", "dataset_loaded": False, "experiment_id": experiment_id}
    exps.reset_experiment(None)
    try:
        state.reset()
    except Exception:
        pass
    return {"status": "ok", "dataset_loaded": False}


@router.get("/api/confusion/{file_name}")
def get_confusion_image(file_name: str):
    """Serves a saved confusion-matrix heatmap PNG for display in the frontend."""
    if not file_name.startswith(CONFUSION_PREFIX) or not file_name.endswith(CONFUSION_SUFFIX):
        raise HTTPException(status_code=400, detail="Invalid file name.")

    # Guard against path traversal (quote-stripped names only).
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name.")

    for base in (PROJECT_ROOT, os.getcwd()):
        path = os.path.join(base, file_name)
        if os.path.isfile(path):
            return FileResponse(path, media_type="image/png")

    raise HTTPException(
        status_code=404,
        detail=f"Confusion matrix image not found: {file_name}",
    )


@router.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve the built React frontend. Falls back to index.html for SPA routing."""
    # Never shadow API routes (safety if router order changes).
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found.")
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not built. Run 'npm run build' in the frontend directory.")
