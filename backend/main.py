from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.detector import extract_dataset_id, detect_problem_type
from backend.clean import clean_dataset
from backend import state
from backend.models import get_model_names
import pandas as pd

app = FastAPI(title="Auto ML Problem Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DatasetRequest(BaseModel):
    code: str


class TrainRequest(BaseModel):
    encoding: str = "all"


def _get_appropriate_models(problem_type):
    return get_model_names(problem_type)


@app.post("/api/analyze")
def analyze_dataset(request: DatasetRequest):
    code = request.code.strip()

    if not code:
        raise HTTPException(status_code=400, detail="Code field cannot be empty.")

    parsed_id = extract_dataset_id(code)

    if parsed_id is None:
        raise HTTPException(
            status_code=400,
            detail="Could not find a valid UCI dataset ID. Expected format: fetch_ucirepo(id=275)",
        )

    if state.X_data is None or state.dataset_id is None:
        try:
            from ucimlrepo import fetch_ucirepo

            dataset = fetch_ucirepo(id=parsed_id)

            state.X_data = dataset.data.features
            state.y_data = dataset.data.targets
            state.dataset_id = parsed_id

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching dataset: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset already loaded. Please use the other endpoints "
                f"(e.g. /api/clean) on the current dataset (id={state.dataset_id})."
            ),
        )

    try:
        result = detect_problem_type(state.y_data)

        state.problem_type = result["problem_type"]
        state.appropriate_models = _get_appropriate_models(result["problem_type"])

        if state.appropriate_models:
            state.selected_model = state.appropriate_models[0]

        target_name = (
            state.y_data.columns[0]
            if isinstance(state.y_data, pd.DataFrame)
            else "Unknown"
        )

        return {
            "dataset_id": state.dataset_id,
            "target_column": target_name,
            "target_dtype": result.get("target_dtype", str(state.y_data.dtypes)),
            "unique_target_values": int(
                result.get("unique_values", state.y_data.nunique())
            ),
            "problem_type": result["problem_type"],
            "reason": result["reason"],
            "num_features": state.X_data.shape[1],
            "num_samples": state.X_data.shape[0],
            "appropriate_models": state.appropriate_models,
            "selected_model": state.selected_model,
            "X_head": state.X_data.head().to_dict(orient="records"),
            "y_head": state.y_data.head().to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing dataset: {str(e)}"
        )


@app.post("/api/clean")
def clean_dataset_route():
    if state.X_data is None or state.y_data is None:
        raise HTTPException(
            status_code=400,
            detail="No dataset loaded. Please POST /api/analyze first.",
        )

    try:
        result = clean_dataset(state.X_data, state.y_data)

        state.X_data = result["X"]
        state.y_data = result["y"]

        if result["problem_type"] == "Classification":
            state.problem_type = "Classification"
            state.appropriate_models = _get_appropriate_models("Classification")
        elif result["problem_type"] == "Regression":
            state.problem_type = "Regression"
            state.appropriate_models = _get_appropriate_models("Regression")

        if state.selected_model not in state.appropriate_models:
            state.selected_model = (
                state.appropriate_models[0] if state.appropriate_models else None
            )

        response = {
            "dataset_id": state.dataset_id,
            "problem_type": state.problem_type,
            "target_encoded": result["target_encoded"],
            "X_shape_before": result["X_shape_before"],
            "y_shape_before": result["y_shape_before"],
            "nan_rows_removed": result["nan_rows_removed"],
            "duplicate_rows_removed": result["duplicate_rows_removed"],
            "X_shape_after": result["X_shape_after"],
            "y_shape_after": result["y_shape_after"],
            "unique_target_values": result["unique_target_values"],
            "X_clean_head": state.X_data.head().to_dict(orient="records"),
            "y_clean_head": state.y_data.head().to_dict(orient="records"),
        }

        if result["target_encoded"]:
            response["encoded_column"] = result["encoded_column"]
            response["class_mapping"] = result["class_mapping"]
            response["num_classes"] = result["num_classes"]

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error cleaning dataset: {str(e)}"
        )


@app.post("/api/train")
def train_model(request: TrainRequest):
    if state.X_data is None or state.y_data is None:
        raise HTTPException(
            status_code=400,
            detail="No dataset loaded. Please POST /api/analyze first.",
        )

    if not state.selected_model:
        raise HTTPException(
            status_code=400,
            detail="No model in state. Please POST /api/analyze first.",
        )

    encoding = request.encoding.lower().strip()

    from backend import onehotencoding
    from backend import targetencoding
    from backend import looencoding
    from backend import mestimateencoding

    encodings = {
        "onehot": onehotencoding.run_one_hot_encoding,
        "target": targetencoding.run_target_encoding,
        "loo": looencoding.run_loo_encoding,
        "m_estimate": mestimateencoding.run_m_estimate_encoding,
    }

    try:
        if encoding == "all":
            return [
                onehotencoding.run_one_hot_encoding(),
                targetencoding.run_target_encoding(),
                looencoding.run_loo_encoding(),
                mestimateencoding.run_m_estimate_encoding(),
            ]

        if encoding not in encodings:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown encoding '{encoding}'. Choose from: all, onehot, target, loo, m_estimate",
            )

        return encodings[encoding]()

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "dataset_loaded": state.X_data is not None,
        "dataset_id": state.dataset_id,
        "problem_type": state.problem_type,
        "selected_model": state.selected_model,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)