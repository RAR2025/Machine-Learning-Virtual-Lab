"""Phase 3 + Phase 8 — POST /api/boundary endpoint."""
from fastapi import APIRouter, HTTPException

from backend.schemas.boundary import BoundaryRequest, BoundaryResponse
from backend.services.boundary import compute_boundary

router = APIRouter(tags=["boundary"])


@router.post("/api/boundary", response_model=BoundaryResponse)
def post_boundary(req: BoundaryRequest) -> BoundaryResponse:
    """Train the selected model and return the prediction grid + metrics.

    Edge cases (Phase 8):
      * < 2 points total -> 422
      * only 1 class present -> 422 (model cannot learn a boundary)
      * k > N is capped inside the service layer, not rejected
    """
    labels = {p.label for p in req.points}
    if len(req.points) < 2:
        raise HTTPException(
            status_code=422, detail="Need at least 2 points to fit a model."
        )
    if len(labels) < 2:
        raise HTTPException(
            status_code=422,
            detail="Need points from both classes (0 and 1) to fit a decision boundary.",
        )

    try:
        payload = compute_boundary(req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=500, detail=f"Boundary computation failed: {exc}"
        ) from exc

    return BoundaryResponse(**payload)


__all__ = ["router", "post_boundary"]
