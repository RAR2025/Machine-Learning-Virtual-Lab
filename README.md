# Machine Learning Virtual Lab

An interactive virtual laboratory for learning and experimenting with the complete supervised machine learning workflow. Load a real UCI dataset, automatically detect whether the problem is **Classification** or **Regression**, clean the data, configure the train/test split, pick a model, try different categorical encoding techniques, and compare performance — all through a clean web UI with theory explained at every step.

Primary lab dataset: **Adult Income (UCI id=2)**. The API stays generic for other UCI ids.

## Project Structure

```
Machine-Learning-Virtual-Lab/
├── backend/                      # FastAPI API (layered: api / core / services)
│   ├── main.py                   # Thin entry point (uvicorn backend.main:app)
│   ├── api/                      # HTTP layer — one module per concern
│   │   ├── __init__.py           # create_app(), CORS, router wiring
│   │   ├── analyze.py            # POST /api/analyze
│   │   ├── cleaning.py           # POST /api/clean
│   │   ├── training.py           # POST /api/train (onehot/target/loo/embedding)
│   │   ├── models.py             # GET /api/models, POST /api/models/select
│   │   ├── split.py              # POST /api/split
│   │   └── system.py             # GET /api/health, POST /api/reset,
│   │                             # GET /api/confusion/{file}, SPA fallback
│   ├── core/
│   │   ├── config.py             # Paths, CORS, app meta
│   │   ├── experiments.py        # Per-experiment store (experiment_id-keyed)
│   │   └── state.py              # Legacy proxies to "default" experiment
│   ├── schemas/                  # Pydantic request models
│   ├── services/
│   │   ├── analysis.py           # Dataset profiling
│   │   ├── cleaning.py           # 12-stage clean_dataset() pipeline
│   │   ├── detection.py          # Problem-type detection + UCI ID extraction
│   │   ├── splitting.py          # Stratified split (materialised indices)
│   │   ├── encoding/
│   │   │   ├── common.py         # Shared ColumnTransformer + Pipeline workflow
│   │   │   ├── onehot.py         # One-Hot Encoding
│   │   │   ├── target.py         # Target Encoding (train-fit only)
│   │   │   ├── loo.py            # Leave-One-Out Encoding (train-fit only)
│   │   │   ├── embedding.py      # PyTorch trainable embeddings + MLP
│   │   │   └── mestimate.py      # M-Estimate (legacy; 4th slot for regression)
│   │   ├── evaluation/
│   │   │   ├── classification.py # Accuracy/Precision/Recall/F1 + heatmap PNG
│   │   │   └── regression.py     # R²/MSE/RMSE/MAE
│   │   └── modeling/
│   │       ├── registry.py       # Model registry (Logistic / Linear Regression)
│   │       └── target.py         # Target label-encoding
│   ├── utils/http.py             # json_safe(), confusion URL helpers
│   └── tests/test_lab.py         # pytest suite (detection, cleaning, split,
│                                 # encodings, leakage, isolation, comparison)
├── frontend/                     # React (Vite) UI
│   ├── src/
│   │   ├── App.jsx               # Root orchestration (experiment_id, models, split, train)
│   │   ├── main.jsx              # ReactDOM bootstrap
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── Aim.jsx
│   │   │   ├── WorkflowStepper.jsx
│   │   │   ├── CodeInput.jsx         # Dataset code input (Adult default)
│   │   │   ├── AnalyzeSection.jsx    # Problem-type results + preview
│   │   │   ├── CleaningSection.jsx   # Cleaning report + diagnostics
│   │   │   ├── ModelSelection.jsx    # Model cards + theory
│   │   │   ├── TrainTestSplit.jsx    # test_size / random_state config
│   │   │   ├── EncodingSection.jsx   # Encoding buttons + metrics + comparison
│   │   │   ├── DataTable.jsx         # Paginated table renderer
│   │   │   └── Conclusion.jsx
│   │   ├── services/api.js       # analyzeCode, cleanData, trainModel,
│   │   │                         # listModels, selectModel, configureSplit
│   │   └── data/experimentData.js# Static educational content/theory
│   ├── index.html
│   ├── vite.config.js            # React plugin + /api → localhost:8000 proxy
│   └── package.json              # scripts: dev, build, lint, preview
├── docs/
│   ├── README.md                 # Docs index
│   ├── backend.md                # Backend deep-dive
│   └── frontend.md               # Frontend deep-dive
├── scripts/                      # E2E helpers (e2e_uci.py + reports)
├── requirements.txt
├── LICENSE
└── README.md
```

Layering rule: `api/` may import from `core/`, `schemas/`, `services/`, `utils/`. `services/` never imports from `api/`.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, plain CSS |
| Backend | Python 3, FastAPI, Uvicorn, Pydantic |
| ML / Data | Pandas, NumPy, scikit-learn, category_encoders, PyTorch (embedding encoder), matplotlib/seaborn (confusion heatmaps) |
| Dataset source | UCI Machine Learning Repository (`ucimlrepo`) |
| Tests | pytest (`backend/tests/test_lab.py`) |

## Running

### 1. Backend (from repo root)

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

### 2. Frontend (dev)

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `http://localhost:8000`, so the backend must be running.

### 3. Production build (backend serves the UI)

```bash
cd frontend
npm run build
cd ..
python -m uvicorn backend.main:app --port 8000
```

The backend serves `frontend/dist` with an `index.html` SPA fallback.

## Usage

1. **Enter dataset code** — e.g. `from ucimlrepo import fetch_ucirepo; dataset = fetch_ucirepo(id=2)` (Adult Income).
2. **Analyze** — fetches the dataset, detects Classification vs Regression, profiles cardinality/class distribution, picks the default model, and returns an `experiment_id`.
3. **Clean** — 12-stage pipeline: string normalisation, placeholder/sentinel handling (`?`, `NA`, `-999`, …), numeric coercion (`1,000`, `45%`), datetime → epoch, sparse/constant column drops, median/mode imputation (targets never imputed), rare-category grouping, IQR winsorization, dedupe, target label-encoding.
4. **Model selection** — Classification → Logistic Regression; Regression → Linear Regression (single supported model per problem type).
5. **Train/test split** — configure `test_size` / `random_state` (stratified for classification with automatic fallback). One shared split is materialised per run and reused by all encoders for a fair comparison.
6. **Encode & train** — run One-Hot, Target, Leave-One-Out, or Embedding-Based individually, or `"all"` for a side-by-side comparison. Encoders fit on train only (no leakage; `<UNK>` handling for unseen categories).
7. **Conclusion** — compare metrics and the generated comparison note (F1 range + shared-split statement).

> Every request accepts an optional `experiment_id`. It isolates users/datasets in memory (`backend/core/experiments.py`). Omit it only for single-user/legacy use.

## API Endpoints

Base URL (dev): `http://localhost:8000` — full reference in [`docs/backend.md`](docs/backend.md).

| Method & path | Purpose |
|---------------|---------|
| `POST /api/analyze` | Fetch UCI dataset, detect problem type, return profile + `experiment_id` |
| `POST /api/clean` | Run cleaning pipeline on the loaded experiment |
| `GET /api/models` | List available models for the problem type |
| `POST /api/models/select` | Select the model for the experiment |
| `POST /api/split` | Configure `test_size` / `random_state` (before encoding) |
| `POST /api/train` | Train under one encoding or `"all"`; returns `{results, comparison, meta}` |
| `GET /api/health` | Status + loaded-dataset summary |
| `POST /api/reset` | Clear one experiment (or `default`) so a new dataset can be loaded |
| `GET /api/confusion/{file}` | Serve a saved confusion-matrix PNG |

### `POST /api/analyze`

**Request:**

```json
{ "code": "from ucimlrepo import fetch_ucirepo\ndataset = fetch_ucirepo(id=2)", "experiment_id": null }
```

**Response (abridged):**

```json
{
  "experiment_id": "a1b2c3d4e5f6",
  "dataset_id": 2,
  "target_column": "income",
  "target_dtype": "object",
  "unique_target_values": 2,
  "problem_type": "Classification",
  "reason": "Categorical target …",
  "num_features": 14,
  "num_samples": 48842,
  "appropriate_models": ["LogisticRegression"],
  "available_models": [{ "key": "logistic_regression", "name": "Logistic Regression" }],
  "selected_model": "logistic_regression",
  "X_head": [{ "...": "..." }],
  "y_head": [{ "income": "<=50K" }]
}
```

Re-posting the **same** id is idempotent. A **different** id in the same experiment → `400`; call `/api/reset` (or use a new `experiment_id`).

### `POST /api/clean`

```json
{ "experiment_id": "a1b2c3d4e5f6", "code": "" }
```

Returns shapes before/after, NaN/duplicate counts, `target_encoded` / `class_mapping`, plus diagnostics (`placeholder_cells_found`, `imputed_cells`, `columns_dropped`, `rare_grouped`, `outliers_capped`, `warnings`, …).

### `POST /api/split`

```json
{ "experiment_id": "a1b2c3d4e5f6", "test_size": 0.2, "random_state": 42 }
```

### `POST /api/train`

```json
{ "encoding": "all", "experiment_id": "a1b2c3d4e5f6", "model": "logistic_regression", "test_size": 0.2, "random_state": 42 }
```

`encoding`: `"onehot" | "target" | "loo" | "embedding" | "m_estimate" | "all"`. Classification primary set is `onehot/target/loo/embedding`; regression uses `m_estimate` as the 4th slot. Failures are isolated per encoding (`result: null` + `error`/`notes`).

**Classification item (abridged):**

```json
{
  "encoding_name": "One-Hot Encoding",
  "encoding_key": "onehot",
  "problem_type": "Classification",
  "selected_model": "logistic_regression",
  "categorical_cols_encoded": ["workclass", "education"],
  "train_test_split": { "train_samples": 39000, "test_samples": 9000 },
  "result": { "Encoding": "One-Hot Encoding", "Accuracy": 0.85, "Precision": 0.74, "Recall": 0.61, "F1": 0.67, "ConfusionImageUrl": "/api/confusion/confusion_matrix_....png" }
}
```

**Regression item:** `{ "Encoding": "…", "R2": 0.39, "MSE": 1.5, "RMSE": 1.22, "MAE": 0.94 }`.

`comparison` is a side-by-side table (`rows` + factual F1-range `note`); `meta` carries model/split/timestamp.

### `GET /api/health` / `POST /api/reset`

```json
{ "status": "ok", "dataset_loaded": true, "dataset_id": 2, "problem_type": "Classification", "selected_model": "logistic_regression" }
```

## Evaluation Metrics

- **Classification:** Accuracy, Precision, Recall, F1 (`zero_division=0`) + confusion-matrix heatmap PNG.
- **Regression:** R², MSE, RMSE, MAE.

## Tests & Scripts

```bash
pytest backend/tests/test_lab.py -v   # from repo root
python scripts/e2e_uci.py             # end-to-end UCI run (see scripts/e2e_report.md)
```

## Docs

- [`docs/backend.md`](docs/backend.md) — folder structure, request flow, API reference, cleaning stages, encodings/models, run guide.
- [`docs/frontend.md`](docs/frontend.md) — components, screen flow/state, API service, run & build.

## License

See [LICENSE](LICENSE).
