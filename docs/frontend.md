# Frontend Documentation

React virtual-lab UI that walks a student through the full supervised-learning
experiment: enter a UCI dataset → analyze → clean → compare encodings.

- **Stack:** React 19, Vite 8, plain CSS (`index.css`, `App.css`), no UI kit
- **Dev server:** `npm run dev` (Vite, proxies `/api` → `http://localhost:8000`)
- **Production:** `npm run build` → `frontend/dist`, served by the FastAPI
  backend's SPA fallback (see `docs/backend.md` §3)

---

## 1. Folder structure

```text
frontend/
├── index.html               # Vite entry HTML (mounts #root)
├── vite.config.js           # React plugin + dev proxy for /api
├── package.json             # scripts: dev, build, lint, preview
└── src/
    ├── main.jsx             # ReactDOM bootstrap (StrictMode) + index.css
    ├── App.jsx              # 12-step orchestration (experiment_id, split, models, train)
    ├── App.css / index.css  # Plain CSS only (responsive + print-friendly)
    ├── services/
    │   └── api.js           # analyzeCode, cleanData, trainModel (+model/split/
    │                        # embedding opts), listModels, selectModel,
    │                        # configureSplit, getDatasetCharts,
    │                        # getExperimentResults, getHealth, resetExperiment
    ├── data/
    │   └── experimentData.js# All teaching copy: aim, dataset, one_hot,
    │                        # target/loo/embedding theory, mini example,
    │                        # split/evaluation/comparison notes
    └── components/
        ├── Header.jsx       # Title bar
        ├── Aim.jsx          # Experiment 1 aim + introduction
        ├── WorkflowStepper.jsx  # 12-step progress indicator
        ├── CodeInput.jsx    # Adult-default UCI textarea + Analyze
        ├── AnalyzeSection.jsx  # Dataset cards, class dist, cat/num summaries
        ├── DatasetVisualization.jsx  # SVG: target, missing, cardinality,
        │                       # top-cats, histogram, boxplot, cat-vs-target, heatmap
        ├── CleaningSection.jsx # Cleaning Report + expandable diagnostics
        ├── ModelSelection.jsx  # Selectable models (logreg default, RF, tree)
        ├── TrainTestSplit.jsx  # 70/80/90 + random_state, stratified display
        ├── EncodingSection.jsx # 4 primary encodings + Run All, theory,
        │                       # mini example, metrics, ROC/PR, dims, sparsity,
        │                       # embedding history + PCA projection
        ├── charts.jsx       # Dependency-free SVG primitives (no chart lib)
        ├── Conclusion.jsx   # Conclusion generated from actual results
        └── DataTable.jsx    # Paginated table, column-type badges, missing flags
```

---

## 2. Screen flow & state (`App.jsx`)

Sections render top-to-bottom as a lab worksheet; each section appears once
its data exists (`AnalyzeSection`/`ModelSelection` return `null` until then).

```text
CodeInput ──analyze──▶ AnalyzeSection ──clean──▶ CleaningSection
      │                                              │
      └────────── problem_type ──▶ ModelSelection ◀──┘
                                         │
EncodingSection ──train(encoding)──▶ metric cards + confusion images
Conclusion (static)
```

State (all in `App`):

| State | Set by | Resets when |
| ----- | ------ | ----------- |
| `code` | textarea | — |
| `analysis` | `handleAnalyze` → `analyzeCode(code)` | new analyze |
| `cleaningResults` | `handleClean` → `cleanData()` | new analyze |
| `trainingResults` | `handleTrain(enc)` → `trainModel(enc)` | new analyze |
| `loading` (`''`/`analyze`/`clean`/`train`) | around each call | `finally` |
| `error` | any caught `Error` | next action |

`handleTrain(encoding)` accepts one of `onehot | target | loo | m_estimate`
(single-encoding response object). `trainingResults` may also be an array
(the backend's `"all"` mode) — `EncodingSection` renders both shapes.

---

## 3. Components

- **`Header`** — static title bar.
- **`Aim`** — renders `experimentInfo.aim` + `introduction`.
- **`CodeInput`** (`code`, `setCode`, `onAnalyze`, `loading`) — textarea for
  e.g. `fetch_ucirepo(id=275)` (Bike Sharing); Analyze disabled while loading
  or when the trimmed code is empty.
- **`AnalyzeSection`** (`analysis`) — cards for problem type, reason, target
  column, shape, unique target values; `DataTable` previews of `X_head`,
  `y_head` (first 5 rows from the backend).
- **`DataTable`** (`data`) — generic table; empty/non-array → *"No data to
  display."*; numbers formatted (`toLocaleString` for ints, 4 decimals).
- **`CleaningSection`** (`result`, `onClean`, `loading`) — theory + steps
  from `experimentInfo.cleaning`; result shows features shape before/after,
  NaN rows removed, duplicate rows removed, and — when `target_encoded` —
  the encoded column, class count and `class_mapping` JSON. (The backend also
  returns richer diagnostics — placeholders, imputations, dropped columns,
  outliers — which this section can be extended to display.)
- **`ModelSelection`** (`problemType`) — picks the classification vs
  regression card from `experimentInfo` (model name, theory, advantages).
- **`EncodingSection`** (`onTrain`, `results`, `loading`) — four buttons with
  tooltip descriptions (`ENCODING_LABELS`); each result card shows model +
  train/test sizes, a metric grid (Accuracy/Precision/Recall/F1 when
  `result.ConfusionMatrix` exists, else R2/MSE/RMSE/MAE), the
  `ConfusionImageUrl` image when present, and the no-categorical note when
  `encoded_applied` is false. Failed `"all"`-mode items (`result: null`)
  render nothing.
- **`Conclusion`** — static `experimentInfo.conclusion` text.

---

## 4. API service (`services/api.js`)

```js
import { analyzeCode, cleanData, trainModel, getHealth } from './services/api';
```

- `API_BASE_URL = ""` — same-origin; in dev Vite proxies `/api` to the
  backend, in production the backend serves the built SPA itself.
- `handle(response)` — throws `Error(detail)` using the backend's
  `body.detail` for non-2xx responses (surfaced in `App`'s error banner).
- `analyzeCode(code)` → `POST /api/analyze { code }`
- `cleanData()` → `POST /api/clean` (empty body)
- `trainModel(encoding)` → `POST /api/train { encoding }`
- `getHealth()` → `GET /api/health` (available; not currently wired into UI)

---

## 5. Static content (`data/experimentData.js`)

`experimentInfo` holds all teaching copy in one place: `aim`,
`introduction`, `classification` (`title`, `theory`, `model`,
`advantages[]`), `regression` (same shape), `cleaning` (`theory`,
`steps[]`), `conclusion`. Edit text here — no component changes needed.

> Note: `cleaning.steps` currently describes "dropping rows with missing
> values"; the backend now imputes feature gaps (median/mode) and only drops
> rows with missing targets — update this copy if you want the theory to
> match the implementation exactly.

---

## 6. Run & build

```bash
cd frontend
npm install
npm run dev      # dev server (uses vite.config.js /api proxy)
npm run build    # outputs frontend/dist
npm run lint     # eslint
npm run preview  # preview the production build
```

- Backend must run on `http://localhost:8000` for the dev proxy
  (`vite.config.js` → `server.proxy['/api']`).
- Production: after `npm run build`, start the backend — it serves
  `frontend/dist` with `index.html` fallback for SPA routes.
- Styling lives in `src/index.css` + `src/App.css` (classes used across
  components: `theory`, `card`, `grid`, `results-grid`, `metric`,
  `step-list`, `muted`, `error`, `encoding-buttons`).
