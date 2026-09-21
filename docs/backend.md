# Backend Documentation

FastAPI backend for the Machine-Learning Virtual Lab. It fetches real UCI
datasets, detects classification vs regression, cleans the data, trains one
model under four categorical-encoding strategies, and serves the results
(including confusion-matrix images) to the React frontend.

- **Stack:** FastAPI, Uvicorn, Pydantic, pandas, scikit-learn,
  `category_encoders`, matplotlib/seaborn, `ucimlrepo`, PyTorch (embedding
  encoder), pytest
- **Experiment 1:** Adult Income (UCI id=2) is the primary dataset; the API
  stays generic for other UCI ids. Primary encodings for classification are
  One-Hot, Target, Leave-One-Out and Embedding-Based (PyTorch). M-Estimate
  remains as an optional legacy encoder (used as the 4th slot for regression,
  hidden from the primary classification UI).
- **Entry point:** `uvicorn backend.main:app` (serves API + built frontend)
- **Python requirements:** see `requirements.txt` at the repo root

---

## 1. Folder structure

```text
backend/
├── main.py                  # Thin entry point: re-exports `backend.api.app`
├── api/                     # HTTP layer — one module per concern
│   ├── __init__.py          # create_app(), CORS, router wiring
│   ├── analyze.py           # POST /api/analyze (experiment-aware, rich profile)
│   ├── cleaning.py          # POST /api/clean (experiment-aware)
│   ├── training.py          # POST /api/train (model/split/embedding options)
│   ├── models.py            # GET /api/models, POST /api/models/select
│   ├── split.py             # POST /api/split (stratified, stored per experiment)
│   ├── experiment.py        # GET /api/visualizations/dataset, GET /api/experiment/results
│   └── system.py            # GET /api/health, POST /api/reset,
│                            # GET /api/confusion/{file}, SPA fallback
├── core/                    # Shared fundamentals
│   ├── config.py            # PROJECT_ROOT, FRONTEND_DIR, CORS, app meta
│   ├── experiments.py       # Per-experiment in-memory store (experiment_id-keyed)
│   └── state.py             # Legacy proxies to the "default" experiment (backward compat)
├── schemas/                 # Pydantic request models
│   └── __init__.py          # DatasetRequest, SplitRequest, TrainRequest, ModelSelectRequest
├── services/                # Business logic (no HTTP code here)
│   ├── cleaning.py          # clean_dataset() pipeline
│   ├── detection.py         # detect_problem_type(), extract_dataset_id()
│   ├── analysis.py          # profile_dataset() — cardinality, class dist, num summary
│   ├── splitting.py         # make_split() — stratified, materialised indices
│   ├── visualization_dataset.py  # dataset_charts() — chart-ready JSON
│   ├── encoding/
│   │   ├── common.py        # run_workflow(), shared-split, dim/sparsity reporting
│   │   ├── onehot.py        # One-Hot Encoding runner
│   │   ├── target.py        # Target Encoding runner (train-fit only)
│   │   ├── loo.py           # Leave-One-Out Encoding runner (train-fit only)
│   │   ├── embedding.py     # PyTorch trainable embeddings + MLP (classification)
│   │   └── mestimate.py     # Legacy optional encoder (regression fallback)
├── tests/
│   └── test_lab.py          # pytest: detection, cleaning, split, encodings,
│                            # leakage proof, embedding vocab, isolation, comparison
│   ├── evaluation/
│   │   ├── classification.py# accuracy/precision/recall/F1 + heatmap PNG
│   │   └── regression.py    # R2/MSE/RMSE/MAE
│   └── modeling/
│       ├── registry.py      # model registry (resolve/get names)
│       └── target.py        # encode_target() — label-encode the target
├── utils/
│   └── http.py              # json_safe(), resolve_confusion_url(),
│                            # dataset_summary()
```

**Layering rule:** `api/` may import from `core/`, `schemas/`,
`services/`, `utils/`. `services/` may import from `core/` and sibling
services, but never from `api/`. Always import the canonical paths
(e.g. `from backend.services.cleaning import clean_dataset`).

---

## 2. Request flow (happy path)

```text
POST /api/analyze  ──▶ fetch UCI dataset ──▶ detect problem type ──▶ state
POST /api/clean    ──▶ clean_dataset() ──▶ update state ──▶ rich report
POST /api/train    ──▶ run_workflow × encoding ──▶ metrics + PNG ──▶ frontend
POST /api/reset    ──▶ clear state (load a different dataset afterwards)
```

State is a per-experiment in-memory dict (`backend/core/experiments.py`)
keyed by `experiment_id` (auto-created on `/api/analyze`, isolated per user;
`reset_all()`/per-experiment reset supported). Each record holds `X_data`,
`y_data`, `dataset_id/name`, `problem_type`, `appropriate_models`,
`selected_model`, `test_size/random_state/split`, `clean_report`,
`train_results/meta`. `backend/core/state.py` keeps legacy proxies to the
`"default"` experiment so old callers/tests keep working. Pass
`experiment_id` on every request; omit it only for single-user legacy use.
One shared split is materialised per run and reused by all encoders (fair
comparison, leakage-safe: target/LOO/embedding vocabularies fit on train only,
test mapped via frozen train state with `<UNK>` handling).

---

## 3. API reference

Base URL in dev: `http://localhost:8000` (Vite proxies `/api` there).

### POST `/api/analyze`

Body: `{ "code": "fetch_ucirepo(id=275)" }` — the UCI id is extracted with
`extract_dataset_id()` (regex for `fetch_ucirepo(id=<int>)`).

- First call fetches via `ucimlrepo`, stores features/targets in state,
  detects the problem type and picks the default model.
- Re-posting the **same** id is idempotent (returns the current summary).
- A **different** id while state is loaded → `400`; call `/api/reset` first.

Success response (abridged):

```json
{
  "dataset_id": 275,
  "target_column": "cnt",
  "target_dtype": "int64",
  "unique_target_values": 200,
  "problem_type": "Regression",
  "reason": "Numeric target contains many unique values.",
  "num_features": 12,
  "num_samples": 731,
  "appropriate_models": ["LinearRegression"],
  "selected_model": "LinearRegression",
  "X_head": [ { "...": "..." } ],
  "y_head": [ { "...": "..." } ]
}
```

### POST `/api/clean`

No body. Runs `clean_dataset()` (see §4), replaces state `X_data`/`y_data`,
re-resolves the model list for the detected problem type.

Response includes the legacy fields the frontend renders
(`X_shape_before/after`, `nan_rows_removed`, `duplicate_rows_removed`,
`target_encoded`, `class_mapping`, …) **plus** the pipeline diagnostics:

| Field | Meaning |
| ----- | ------- |
| `placeholder_cells_found` (+ `_in_X`, `_in_Y`) | `"."`, `"?"`, `"NA"`, `"n/a"`, `"null"`, … cells neutralised |
| `sentinel_cells_found` | numeric `-999`/`±inf` cells neutralised |
| `rows_dropped_target_missing` | rows dropped for missing target (targets are never imputed) |
| `imputed_cells`, `numeric_imputed`, `categorical_imputed` | median/mode imputations applied to features |
| `columns_dropped` | sparse (>50% missing) + constant columns removed |
| `numeric_coerced` | `"1,000"`/`"45%"`-style columns converted to numeric |
| `datetime_converted` | datetime-like columns converted to epoch seconds |
| `rare_grouped` | `{col: n_cats}` merged into `"other"` |
| `outliers_capped` | numeric feature cells winsorized at 1.5×IQR |
| `warnings` | human-readable list of drops/actions |

### POST `/api/train`

Body: `{ "encoding": "all" | "onehot" | "target" | "loo" | "m_estimate" }`.

- `"all"` runs all four encoders; **failures are isolated** — a broken
  encoder yields an item with `result: null` + `error`/`notes` instead of
  failing the whole request.
- Each item: `encoding_name`, `problem_type`, `selected_model`,
  `categorical_cols_encoded`, `numerical_cols`, `encoded_applied`, `notes`,
  `train_test_split`, `result` (metrics + `ConfusionImageUrl` for
  classification).

### GET `/api/health`

`{ "status": "ok", "dataset_loaded": …, "dataset_id": …, "problem_type": …,
"selected_model": …, "num_samples": …, "num_features": … }`.

### POST `/api/reset`

Clears state. Required before analyzing a different dataset id.

### GET `/api/confusion/{file_name}`

Serves `confusion_matrix_*.png` files written to the project root.
Rejects anything not matching `confusion_matrix_*.png` and blocks path
traversal (`/`, `\`, `..`).

### GET `/{full_path:path}` (catch-all, registered last)

Serves the built React app from `frontend/dist` (falls back to
`index.html` for SPA routing; `404` with a build hint if not built).

---

## 4. Cleaning pipeline (`services/cleaning.py`)

`clean_dataset(X, y)` — pure function (copies inputs), 12 stages:

1. **Validate** — single target column only.
2. **Tidy column names** — strip whitespace, dedupe.
3. **String normalisation** — Unicode NFKC, NBSP/zero-width removal,
   whitespace collapse, lowercase; stray leading/trailing `.`/`'"` stripped
   (`"m."`→`"m"`, lone `"."`→ missing) while inner dots (`"st. louis"`) stay.
4. **Placeholders → NA** — `MISSING_TOKENS` (`"."`, `"?"`, `"na"`, `"n/a"`,
   `"null"`, `"--"`, …) + punctuation-only strings (`".?"`, `"##"`).
   Load-bearing guard: a frequent `-`/`+` (>5% of the column) is kept as a
   real binary category (Credit Approval's `+/-` target) instead of being
   wiped out.
5. **Numeric recovery** — `"1,000"`, `"$12"`, `"45%"` coerced when ≥70% of a
   column parses; datetime-like columns (≥70% parse) become epoch seconds.
6. **Numeric sentinels → NA** — `-999`/`-9999`/`-99999`, `±inf`.
7. **Sparse columns dropped** (>50% missing), then **imputation**:
   numeric→median, categorical→mode. Missing *targets* are never imputed.
8. **Rows with missing target dropped** (+ residual-NA safety net).
9. **Constant columns dropped**; **rare categories → `"other"`**
   (cols with >10 uniques, cats below `max(2, 1%)`); **outliers capped**
   (1.5×IQR winsorization, features only).
10. **Duplicates dropped**; empty-result and single-class guards raise
    descriptive `ValueError`s.
11. **Problem re-detection** + target label-encoding for classification.
12. **Rich report dict** (shapes, counts, per-column maps, warnings).

Tuning knobs live at the top of the module (`MAX_COLUMN_MISSING_RATIO`,
`NUMERIC_COERCE_THRESHOLD`, `RARE_MIN_COUNT/FRAC`, …).

---

## 5. Detection, encodings, models

- **Detection** (`services/detection.py`): object/string/category/bool
  targets → Classification; numeric targets with ≤20 uniques or <5% unique
  ratio → Classification, else Regression. `analyze_code()` is a legacy
  plain-text helper.
- **Encodings** (`services/encoding/`): every runner delegates to
  `run_workflow()` in `common.py`, which splits columns
  (categorical vs numeric), builds a `ColumnTransformer`
  (encoder + `StandardScaler`, `remainder="drop"`), and trains via a
  `Pipeline`. Train/test split is stratified for classification with an
  automatic unstratified fallback (recorded in `notes`) when a class is too
  small to stratify.
- **Models** (`services/modeling/registry.py`): Classification →
  `LogisticRegression(max_iter=1000, class_weight="balanced")`;
  Regression → `LinearRegression`. `resolve_model()` / `get_model_names()`.
- **Evaluation**: classification reports Accuracy/Precision/Recall/F1
  (`zero_division=0`) + confusion-matrix heatmap PNG saved to the project
  root with a sanitised filename; regression reports R2/MSE/RMSE/MAE.

### Adding a new encoding

1. Create `backend/services/encoding/<name>.py` with a `run_<name>_encoding()`
   function calling `run_workflow("Display Name", make_encoder)`.
2. Register it in `backend/api/training.py`'s `encodings` dict (+ the `"all"`
   loop) and add the button/label in the frontend `EncodingSection`.

### Adding a new model

Add a factory to `CLASSIFIERS`/`REGRESSORS` in
`backend/services/modeling/registry.py` — it is picked up by
`get_model_names()` (analyze/clean responses) automatically.

---

## 6. Run & develop

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- Interactive API docs: `http://localhost:8000/docs`
- Frontend dev server (`frontend/`, `npm run dev`) proxies `/api` to the
  backend; production serves `frontend/dist` from the backend itself.
- `backend/core/config.py` holds `PROJECT_ROOT`, `FRONTEND_DIR`,
  `CORS_ORIGINS`, app title/version.
- Logging: training failures are logged via the `ml-virtual-lab` logger;
  route handlers translate exceptions to `HTTPException(400/500)`.
