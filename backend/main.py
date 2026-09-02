from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.detector import extract_dataset_id, detect_problem_type
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


@app.post("/api/analyze")
def analyze_dataset(request: DatasetRequest):
    code = request.code.strip()

    if not code:
        raise HTTPException(status_code=400, detail="Code field cannot be empty.")

    dataset_id = extract_dataset_id(code)

    if dataset_id is None:
        raise HTTPException(
            status_code=400,
            detail="Could not find a valid UCI dataset ID. Expected format: fetch_ucirepo(id=275)",
        )

    try:
        from ucimlrepo import fetch_ucirepo

        dataset = fetch_ucirepo(id=dataset_id)

        X = dataset.data.features
        y = dataset.data.targets

        result = detect_problem_type(y)

        target_name = y.columns[0] if isinstance(y, pd.DataFrame) else "Unknown"

        return {
            "dataset_id": dataset_id,
            "target_column": target_name,
            "target_dtype": result.get("target_dtype", str(y.dtypes)),
            "unique_target_values": int(result.get("unique_values", y.nunique())),
            "problem_type": result["problem_type"],
            "reason": result["reason"],
            "num_features": X.shape[1],
            "num_samples": X.shape[0],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dataset: {str(e)}")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
