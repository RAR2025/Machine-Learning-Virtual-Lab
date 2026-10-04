"""Phase 3 — Pydantic schemas for POST /api/boundary.

Supports both naming conventions:
  * Member-2 / frontend contract: points[{x,y,label}], algo, hyperparams, resolution
  * plan.md contract:          points[{x,y,class}], algorithm, params, grid_resolution

Responses carry flat fields (frontend) plus nested aliases (plan.md):
  metrics / model_info / bias_variance / x_range / y_range.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, Field
from pydantic import field_validator


class Point(BaseModel):
    """Single canvas point, coordinates normalized to [0, 1]."""

    model_config = {"populate_by_name": True}

    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x in [0, 1]")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y in [0, 1]")
    label: int = Field(
        ...,
        ge=0,
        le=1,
        description="Class label 0 or 1",
        validation_alias=AliasChoices("label", "class", "cls", "class_label"),
    )

    @field_validator("label", mode="before")
    @classmethod
    def _coerce_label(cls, v: Any) -> Any:
        # Accept bools / numeric strings gracefully.
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, str):
            s = v.strip()
            if s in ("0", "1"):
                return int(s)
        return v


AlgoName = Literal["knn", "svm", "dt"]


class BoundaryRequest(BaseModel):
    """Request body for POST /api/boundary."""

    model_config = {"populate_by_name": True}

    points: List[Point] = Field(..., min_length=2, description="Canvas points")
    algo: str = Field(
        ...,
        description="Algorithm: 'knn' | 'svm' | 'dt' ('decision_tree' accepted as alias)",
        validation_alias=AliasChoices("algo", "algorithm"),
    )
    hyperparams: Dict[str, Any] = Field(
        default_factory=dict,
        description="Algorithm hyperparameters",
        validation_alias=AliasChoices("hyperparams", "params"),
    )
    resolution: int = Field(
        default=60,
        ge=10,
        le=200,
        description="Grid resolution (N x N)",
        validation_alias=AliasChoices("resolution", "grid_resolution"),
    )

    @field_validator("algo", mode="before")
    @classmethod
    def _normalize_algo(cls, v: Any) -> Any:
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("decision_tree", "decisiontree", "tree", "dt"):
                return "dt"
            if s in ("knn", "k-nn", "kneighbors"):
                return "knn"
            if s in ("svm", "svc"):
                return "svm"
            return s
        return v

    @field_validator("algo")
    @classmethod
    def _check_algo(cls, v: str) -> str:
        if v not in ("knn", "svm", "dt"):
            raise ValueError("algo must be one of 'knn' | 'svm' | 'dt'")
        return v


class BoundaryResponse(BaseModel):
    """Response body for POST /api/boundary."""

    grid: List[List[int]]
    resolution: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: List[List[int]]
    variance_score: float = Field(
        ..., ge=0.0, le=1.0, description="0 = high bias/underfit, 1 = high variance/overfit"
    )
    fit_time_ms: float

    # --- plan.md nested aliases (optional, for spec compatibility) ---
    x_range: Optional[List[float]] = None
    y_range: Optional[List[float]] = None
    metrics: Optional[Dict[str, Any]] = None
    model_info: Optional[Dict[str, Any]] = None
    bias_variance: Optional[Dict[str, Any]] = None


__all__ = ["Point", "BoundaryRequest", "BoundaryResponse"]
