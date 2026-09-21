"""POST /api/analyze — fetch a UCI dataset and detect the problem type."""
from fastapi import APIRouter, HTTPException

import pandas as pd

from backend.core import experiments as exps
from backend.core import state as legacy_state
from backend.schemas import DatasetRequest
from backend.services.analysis import profile_dataset
from backend.services.detection import detect_problem_type, extract_dataset_id
from backend.services.modeling.registry import canonical_key, get_available_models, get_model_names
from backend.utils.http import json_safe

router = APIRouter()


@router.post("/api/analyze")
def analyze_dataset(request: DatasetRequest):
    code = (request.code or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Code field cannot be empty.")

    parsed_id = extract_dataset_id(code)
    if parsed_id is None:
        raise HTTPException(
            status_code=400,
            detail="Could not find a valid UCI dataset ID. Expected format: fetch_ucirepo(id=2)",
        )

    # Resolve experiment: reuse provided id or create a fresh one so users
    # never overwrite each other. Legacy callers without an id share "default"
    # with the old single-dataset guard.
    if request.experiment_id:
        exp = exps.get_experiment(request.experiment_id)
    else:
        exp = exps.get_experiment(None)

    if exps.is_loaded(exp) and exp.get("dataset_id") is not None:
        if exp.get("dataset_id") == parsed_id:
            try:
                result = detect_problem_type(exps.y_series(exp))
                prof = profile_dataset(exp["X_data"], exp["y_data"],
                                       dataset_id=exp.get("dataset_id"),
                                       dataset_name=exp.get("dataset_name"))
                return json_safe({
                    "experiment_id": exp.get("experiment_id"),
                    **prof,
                    "target_column": prof["target_column"],
                    "target_dtype": result.get("target_dtype", "unknown"),
                    "unique_target_values": int(result.get("unique_values", 0)),
                    "target_classes": list(prof.get("class_distribution", {}).keys()),
                    "problem_type": result["problem_type"],
                    "reason": result["reason"],
                    "appropriate_models": exp.get("appropriate_models", []),
                    "available_models": get_available_models(result["problem_type"]),
                    "selected_model": exp.get("selected_model"),
                    "X_head": exp["X_data"].head().to_dict(orient="records"),
                    "y_head": exp["y_data"].head().to_dict(orient="records") if isinstance(exp["y_data"], pd.DataFrame) else [],
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error analyzing dataset: {str(e)}")
        # Different id in the same experiment -> require explicit reset/new experiment
        if not request.experiment_id:
            raise HTTPException(
                status_code=400,
                detail=(f"Dataset already loaded (id={exp.get('dataset_id')}). POST /api/reset first to load a different dataset."),
            )
        # Different experiment id reusing same record: fall through to (re)load.

    try:
        from ucimlrepo import fetch_ucirepo
        dataset = fetch_ucirepo(id=parsed_id)
        features = dataset.data.features
        targets = dataset.data.targets
        if features is None or targets is None or len(features) == 0:
            raise ValueError("Fetched dataset is empty.")
        try:
            ds_name = getattr(getattr(dataset, "metadata", None), "name", None) or getattr(dataset, "name", None) or f"UCI #{parsed_id}"
        except Exception:
            ds_name = f"UCI #{parsed_id}"
        exp["X_data"] = features
        exp["y_data"] = targets
        exp["dataset_id"] = parsed_id
        exp["dataset_name"] = str(ds_name)
        exp["split"] = None
        exp["clean_report"] = None
        exp["train_results"] = None
        exps.touch(exp)
        # keep legacy proxies in sync for old routes/tests
        if exp.get("experiment_id") == "default":
            legacy_state.X_data = features
            legacy_state.y_data = targets
            legacy_state.dataset_id = parsed_id
    except HTTPException:
        raise
    except Exception as e:
        exps.reset_experiment(exp.get("experiment_id"))
        raise HTTPException(status_code=500, detail=f"Error fetching dataset: {str(e)}")

    try:
        result = detect_problem_type(exp["y_data"])
        exp["problem_type"] = result["problem_type"]
        exp["appropriate_models"] = get_model_names(result["problem_type"])
        default_model = "logistic_regression" if result["problem_type"] == "Classification" else "linear_regression"
        exp["selected_model"] = canonical_key(exp["appropriate_models"][0] if exp["appropriate_models"] else default_model, result["problem_type"])
        exps.touch(exp)
        if exp.get("experiment_id") == "default":
            legacy_state.problem_type = exp["problem_type"]
            legacy_state.appropriate_models = exp["appropriate_models"]
            legacy_state.selected_model = exp["selected_model"]

        prof = profile_dataset(exp["X_data"], exp["y_data"],
                               dataset_id=parsed_id, dataset_name=exp.get("dataset_name"))
        return json_safe({
            "experiment_id": exp.get("experiment_id"),
            **prof,
            "target_column": prof["target_column"],
            "target_dtype": result.get("target_dtype", "unknown"),
            "unique_target_values": int(result.get("unique_values", 0)),
            "target_classes": list(prof.get("class_distribution", {}).keys()),
            "problem_type": result["problem_type"],
            "reason": result["reason"],
            "appropriate_models": exp["appropriate_models"],
            "available_models": get_available_models(result["problem_type"]),
            "selected_model": exp["selected_model"],
            "X_head": exp["X_data"].head().to_dict(orient="records"),
            "y_head": exp["y_data"].head().to_dict(orient="records") if isinstance(exp["y_data"], pd.DataFrame) else [],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing dataset: {str(e)}")
