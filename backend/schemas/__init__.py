"""Pydantic request schemas for the HTTP API."""

from typing import Optional

from pydantic import BaseModel, Field


class DatasetRequest(BaseModel):
    code: str
    experiment_id: Optional[str] = None


class SplitRequest(BaseModel):
    experiment_id: Optional[str] = None
    test_size: float = Field(default=0.2, ge=0.05, le=0.5)
    random_state: int = Field(default=42, ge=0, le=99999)


class TrainRequest(BaseModel):
    encoding: str = "all"
    experiment_id: Optional[str] = None
    model: Optional[str] = None
    test_size: Optional[float] = Field(default=None, ge=0.05, le=0.5)
    random_state: Optional[int] = Field(default=None, ge=0, le=99999)


class ModelSelectRequest(BaseModel):
    experiment_id: Optional[str] = None
    model: str
