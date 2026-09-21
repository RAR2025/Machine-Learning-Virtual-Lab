"""POST /api/clean — run the cleaning pipeline on the loaded dataset."""
from fastapi import APIRouter, Body, HTTPException

from backend.core import experiments as exps
from backend.core import state as legacy_state
from backend.schemas import DatasetRequest
from backend.services.cleaning import clean_dataset
from backend.services.modeling.registry import canonical_key, get_available_models, get_model_names
from backend.utils.http import json_safe

router = APIRouter()


@router.post("/api/clean")
def clean_dataset_route(body: DatasetRequest | None = Body(default=None)):
    experiment_id = (body.experiment_id if body else None)
    exp = exps.get_experiment(experiment_id)
    if not exps.is_loaded(exp):
        raise HTTPException(status_code=400, detail="No dataset loaded. Please POST /api/analyze first.")
    try:
        result = clean_dataset(exp["X_data"], exp["y_data"])
        exp["X_data"] = result["X"]
        exp["y_data"] = result["y"]
        if result["problem_type"] == "Classification":
            exp["problem_type"] = "Classification"
            exp["appropriate_models"] = get_model_names("Classification")
        elif result["problem_type"] == "Regression":
            exp["problem_type"] = "Regression"
            exp["appropriate_models"] = get_model_names("Regression")
        # normalise selected model to canonical key
        try:
            exp["selected_model"] = canonical_key(exp.get("selected_model"), exp["problem_type"])
        except Exception:
            exp["selected_model"] = "logistic_regression" if exp["problem_type"] == "Classification" else "linear_regression"
        if exp.get("selected_model") not in ("logistic_regression", "linear_regression"):
            exp["selected_model"] = "logistic_regression" if exp["problem_type"] == "Classification" else "linear_regression"
        exp["split"] = None  # cleaning invalidates any prior split
        exp["clean_report"] = {k: v for k, v in result.items() if k not in ("X", "y")}
        exps.touch(exp)
        if exp.get("experiment_id") == "default":
            legacy_state.X_data = result["X"]
            legacy_state.y_data = result["y"]
            legacy_state.problem_type = exp["problem_type"]
            legacy_state.appropriate_models = exp["appropriate_models"]
            legacy_state.selected_model = exp["selected_model"]

        # Before/after snapshot for the Cleaning Report UI
        before_rows = int(result["X_shape_before"][0])
        after_rows = int(result["X_shape_after"][0])
        response = {
            "experiment_id": exp.get("experiment_id"),
            "dataset_id": exp.get("dataset_id"),
            "dataset_name": exp.get("dataset_name"),
            "problem_type": exp["problem_type"],
            "available_models": get_available_models(exp["problem_type"]),
            "selected_model": exp["selected_model"],
            "target_encoded": result["target_encoded"],
            "X_shape_before": result["X_shape_before"],
            "y_shape_before": result["y_shape_before"],
            "nan_rows_removed": result["nan_rows_removed"],
            "duplicate_rows_removed": result["duplicate_rows_removed"],
            "placeholder_cells_found": result.get("placeholder_cells_found", 0),
            "placeholder_cells_in_X": result.get("placeholder_cells_in_X", 0),
            "placeholder_cells_in_y": result.get("placeholder_cells_in_y", 0),
            "sentinel_cells_found": result.get("sentinel_cells_found", 0),
            "rows_dropped_target_missing": result.get("rows_dropped_target_missing", 0),
            "residual_na_rows_removed": result.get("residual_na_rows_removed", 0),
            "imputed_cells": result.get("imputed_cells", 0),
            "numeric_imputed": result.get("numeric_imputed", {}),
            "categorical_imputed": result.get("categorical_imputed", {}),
            "columns_dropped": result.get("columns_dropped", []),
            "sparse_columns_dropped": result.get("sparse_columns_dropped", []),
            "constant_columns_dropped": result.get("constant_columns_dropped", []),
            "numeric_coerced": result.get("numeric_coerced", []),
            "datetime_converted": result.get("datetime_converted", []),
            "rare_grouped": result.get("rare_grouped", {}),
            "outliers_capped": result.get("outliers_capped", 0),
            "outliers_per_column": result.get("outliers_per_column", {}),
            "warnings": result.get("warnings", []),
            "X_shape_after": result["X_shape_after"],
            "y_shape_after": result["y_shape_after"],
            "unique_target_values": result["unique_target_values"],
            "cleaning_summary": {
                "rows_before": before_rows,
                "rows_after": after_rows,
                "rows_removed": int(before_rows - after_rows),
                "columns_before": int(result["X_shape_before"][1]),
                "columns_after": int(result["X_shape_after"][1]),
                "missing_cells_handled": int(result.get("placeholder_cells_found", 0) + result.get("sentinel_cells_found", 0) + result.get("imputed_cells", 0)),
            },
            "X_clean_head": json_safe(exp["X_data"].head().to_dict(orient="records")),
            "y_clean_head": json_safe(exp["y_data"].head().to_dict(orient="records")) if hasattr(exp["y_data"], "head") else [],
        }
        if result["target_encoded"]:
            response["encoded_column"] = result["encoded_column"]
            response["class_mapping"] = result["class_mapping"]
            response["num_classes"] = result["num_classes"]
        return json_safe(response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning dataset: {str(e)}")
