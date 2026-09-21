# Machine Learning Virtual Lab

An interactive virtual laboratory for learning and experimenting with the complete supervised machine learning workflow. Load a real UCI dataset, automatically detect whether the problem is **Classification** or **Regression**, clean the data, try different categorical encoding techniques, and compare model performance — all through a clean web UI with theory explained at every step.

## Project Structure

```
Machine-Learning-Virtual-Lab/
├── backend/                     # FastAPI + scikit-learn API
│   ├── __init__.py
│   ├── main.py                  # FastAPI server (CORS, state, routes)
│   ├── detector.py              # Problem-type detection + UCI ID extraction
│   ├── state.py                 # Global shared ML state
│   ├── clean.py                 # Data cleaning pipeline
│   ├── classify.py              # Target label encoding
│   ├── models.py                # Model registry (Logistic/Linear Regression)
│   ├── encodingcommon.py        # Shared train/test + pipeline workflow
│   ├── onehotencoding.py        # One-Hot Encoding
│   ├── targetencoding.py        # Target Encoding
│   ├── looencoding.py           # Leave-One-Out Encoding
│   ├── mestimateencoding.py     # M-Estimate Encoding
│   ├── classificationmodel.py   # Classification evaluation
│   └── regressionmodel.py       # Regression evaluation
├── frontend/                    # React (Vite) UI
│   ├── src/
│   │   ├── App.jsx              # Root component / orchestration
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── Aim.jsx
│   │   │   ├── CodeInput.jsx        # Dataset code input
│   │   │   ├── AnalyzeSection.jsx   # Problem-type results + preview
│   │   │   ├── CleaningSection.jsx  # Cleaning + results
│   │   │   ├── ModelSelection.jsx   # Model + theory
│   │   │   ├── EncodingSection.jsx  # Encoding buttons + metrics
│   │   │   ├── DataTable.jsx        # Generic table renderer
│   │   │   └── Conclusion.jsx
│   │   ├── services/api.js      # API client library
│   │   └── data/experimentData.js  # Static educational content
│   ├── index.html
│   ├── vite.config.js           # React plugin + API proxy
│   └── package.json
├── requirements.txt
├── plan.md
├── LICENSE
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite |
| Backend | Python 3, FastAPI, Uvicorn |
| ML / Data | Pandas, NumPy, scikit-learn, category_encoders |
| Dataset source | UCI Machine Learning Repository (`ucimlrepo`) |

## Setup

### Backend

```bash
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running

### 1. Start the backend

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

API server starts at `http://localhost:8000`

### 2. Start the frontend (in a second terminal)

```bash
cd frontend
npm run dev
```

Web app opens at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend on port `8000`.

## Usage

1. **Enter dataset code** — paste Python code referencing a UCI dataset ID, e.g. `from ucimlrepo import fetch_ucirepo; dataset = fetch_ucirepo(id=275)`.
2. **Analyze** — the app fetches the dataset and detects the problem type (Classification vs Regression), the target column, and shows a preview of the data.
3. **Clean** — removes missing/duplicate rows, normalizes strings, and encodes categorical targets.
4. **Model selection** — displays the recommended model with its theory.
5. **Encode & train** — choose One-Hot, Target, Leave-One-Out, or M-Estimate encoding and compare evaluation metrics.

## API Endpoints

### `POST /api/analyze`

Analyzes a UCI dataset and detects the problem type.

**Request:**
```json
{
  "code": "from ucimlrepo import fetch_ucirepo\n\nheart_disease = fetch_ucirepo(id=45)\nX = heart_disease.data.features\ny = heart_disease.data.targets"
}
```

**Response:**
```json
{
  "dataset_id": 45,
  "target_column": "num",
  "target_dtype": "int64",
  "unique_target_values": 5,
  "problem_type": "Classification",
  "reason": "Numeric target has relatively few unique values.",
  "num_features": 13,
  "num_samples": 303,
  "appropriate_models": ["LogisticRegression"],
  "selected_model": "LogisticRegression",
  "X_head": [ { "...": "..." } ],
  "y_head": [ { "num": 0 } ]
}
```

### `POST /api/clean`

Cleans the currently loaded dataset (removes NaN and duplicate rows, normalizes strings, encodes categorical targets).

**Response:**
```json
{
  "dataset_id": 45,
  "problem_type": "Classification",
  "target_encoded": true,
  "X_shape_before": [303, 13],
  "y_shape_before": [303, 1],
  "nan_rows_removed": 0,
  "duplicate_rows_removed": 6,
  "X_shape_after": [297, 13],
  "y_shape_after": [297, 1],
  "encoded_column": "num",
  "class_mapping": { "0": 0, "1": 1 },
  "num_classes": 5,
  "X_clean_head": [ { "...": "..." } ]
}
```

### `POST /api/train`

Trains and evaluates the selected model under a given encoding technique.

**Request:**
```json
{ "encoding": "onehot" }
```

`encoding` accepts `"onehot"`, `"target"`, `"loo"`, `"m_estimate"`, or `"all"` (returns a comparison of all four).

**Classification response:**
```json
{
  "encoding_name": "One-Hot Encoding",
  "problem_type": "Classification",
  "selected_model": "LogisticRegression",
  "categorical_cols_encoded": ["sex", "cp"],
  "train_test_split": { "train_samples": 221, "test_samples": 56 },
  "result": {
    "Encoding": "One-Hot Encoding",
    "Accuracy": 0.7857,
    "Precision": 0.74,
    "Recall": 0.7857,
    "F1": 0.76,
    "ConfusionMatrix": [ [44, 4], [8, 0] ],
    "Classes": [0, 1]
  }
}
```

**Regression response** (same wrapper, different metrics):
```json
{
  "encoding_name": "One-Hot Encoding",
  "problem_type": "Regression",
  "selected_model": "LinearRegression",
  "result": {
    "Encoding": "One-Hot Encoding",
    "R2": 0.3974,
    "MSE": 1.5,
    "RMSE": 1.22,
    "MAE": 0.94
  }
}
```

### `GET /api/health`

Health check with current state.

**Response:**
```json
{
  "status": "ok",
  "dataset_loaded": true,
  "dataset_id": 275,
  "problem_type": "Regression",
  "selected_model": "LinearRegression"
}
```

### `POST /api/reset`

Clears all in-memory dataset state so a fresh dataset can be loaded. The frontend calls this automatically on every page load/refresh, so reloading the app resets the backend to a clean state.

**Response:**
```json
{
  "status": "ok",
  "dataset_loaded": false,
  "dataset_id": null,
  "problem_type": null
}
```

> **Note:** The backend keeps its loaded dataset in memory (single-dataset, single-user model). Calling `/api/analyze` a second time for a different dataset is rejected until `/api/reset` is invoked. Refreshing the web app triggers this reset automatically.

## Evaluation Metrics

- **Classification:** Accuracy, Precision, Recall, F1 Score + Confusion Matrix.
- **Regression:** R² Score, MSE, RMSE, MAE.

## License

See [LICENSE](LICENSE).
