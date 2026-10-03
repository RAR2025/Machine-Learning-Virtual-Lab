# ML Virtual Lab — Master Build Plan

> **Concept:** Decision Boundary Playground — A single-screen, no-scroll, real-time interactive virtual lab where students draw data points on a canvas and watch KNN / SVM / Decision Tree decision boundaries animate live, with live metrics on the right and contextual theory below.

---

## Project Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React 19 + Vite 8 | Already set up, fast HMR |
| Styling | Vanilla CSS (custom design system) | Full control, no framework bloat |
| Canvas | HTML5 Canvas API (raw, no lib) | Real-time boundary drawing |
| Backend | FastAPI + Python | sklearn for boundary/metrics computation |
| ML Compute | scikit-learn | KNN, SVM, Decision Tree |
| Charts | Custom SVG (no chart lib) | Lightweight, animated, no dep |

---

## Final UI Layout (1 Screen, No Scroll)

```
+---------------------------------------------------------------------+
| MLVlab           [KNN] [SVM] [Decision Tree]      v1.0  Team X      |  <- TOPBAR (56px)
+--------------+------------------------------+----------------------+
|              |                              |                      |
|  LEFT PANEL  |      CENTER CANVAS           |   RIGHT PANEL        |
|  (280px)     |      (flex-grow)             |   (300px)            |
|              |                              |                      |
|  Algorithm   |  Interactive drawing area    |  Live Accuracy Gauge |
|  Card with   |  - Click = add point         |  Confusion Matrix    |
|  active glow |  - Right-click = class 2     |  Metric bars         |
|              |  - Decision boundary         |  (Precision/Recall   |
|  Hyperparams |    renders in realtime       |   F1 / AUC)          |
|  Sliders     |  - Animated fill gradient    |                      |
|              |  - Point sparkle on add      |  Bias-Variance       |
|  Dataset     |                              |  Indicator           |
|  Presets     |  [Clear] [Run] [Demo]        |                      |
|              |                              |  Point Count         |
|  Theory Tip  |                              |  Class Distribution  |
|              |                              |                      |
+--------------+------------------------------+----------------------+
|  BOTTOM THEORY STRIP (~140px fixed)                                 |
|  Contextual explanation: WHY this boundary looks the way it does    |
|  Changes dynamically based on selected algo + current params        |
+---------------------------------------------------------------------+
```

---

## Design System

### Theme: Light Mode — Contrast + ML/AI Vibe

```
Background:       #F0F4FF  (cool near-white, not paper white)
Surface:          #FFFFFF
Surface Alt:      #F7F9FF
Border:           #E2E8F7
Text Primary:     #0D1321  (near-black, readable)
Text Secondary:   #4A5680
Text Muted:       #8892B0

Accent Blue:      #3B6EF8  (primary CTA, active states)
Accent Purple:    #7C3AED  (SVM theme)
Accent Teal:      #0EA5E9  (KNN theme)
Accent Orange:    #F97316  (Decision Tree theme)

Gradient Hero:    linear-gradient(135deg, #3B6EF8 0%, #7C3AED 100%)
Gradient Glow:    radial-gradient(ellipse, rgba(59,110,248,0.12) 0%, transparent 70%)

Class 1 Color:    #3B6EF8  (blue points)
Class 2 Color:    #F97316  (orange points)

Boundary Overlay: Semi-transparent filled regions (blue 15% / orange 15% alpha)

Font:             'Inter' (Google Fonts) — weights 400, 500, 600, 700
Code Font:        'JetBrains Mono' (param values, metrics)
```

### Algo Color Coding
- **KNN** -> Teal `#0EA5E9` — slider glow teal
- **SVM** -> Purple `#7C3AED` — slider glow purple
- **Decision Tree** -> Orange `#F97316` — slider glow orange

---

## Phase Breakdown

---

### Phase 0 — Foundation & Design System
**Goal:** Skeleton HTML + CSS design system only. No JS logic. Verify layout renders correctly.

**Files to create:**
- `frontend/src/main.jsx` — ReactDOM mount
- `frontend/src/index.css` — Full design system (tokens, layout, typography, components)
- `frontend/src/App.jsx` — Static shell: topbar + 3-column layout + bottom strip (all hardcoded placeholders)
- `frontend/index.html` — Title, Google Fonts import, meta tags

**Acceptance criteria:**
- Page loads, shows correct 3-column + topbar + theory strip layout
- No scroll visible on 1080p screen
- Color tokens match design spec above
- Inter font loading correctly
- Layout is responsive down to 1280px wide

---

### Phase 1 — Interactive Canvas Engine
**Goal:** The center canvas is fully interactive — user can draw points, clear them, see them rendered with class colors and sparkle animations.

**Files to create:**
- `frontend/src/components/Canvas.jsx` — Main canvas component
- `frontend/src/hooks/useCanvas.js` — Canvas setup, resize observer, DPR scaling
- `frontend/src/hooks/usePoints.js` — Point state management (add, remove, clear, class toggle)
- `frontend/src/utils/canvasDraw.js` — Drawing primitives: drawPoint(), drawGrid(), clearCanvas(), animatePoint()

**Key behaviors:**
- Left-click on canvas -> add Class 1 point (blue filled circle, 8px radius)
- Right-click on canvas -> add Class 2 point (orange filled circle)
- Click existing point -> remove it
- Points animate in with a ripple/sparkle effect on placement
- Canvas auto-resizes with window resize (ResizeObserver)
- Canvas renders at device pixel ratio for crisp rendering
- Bottom-left shows live count: "Class 1: N  |  Class 2: M"
- [Clear Canvas] button wipes all points with a fade animation
- [Demo: Moons] [Demo: Blobs] [Demo: XOR] presets auto-populate sample points

**Canvas data model:**
```js
// Point shape
{ x: Number,  // canvas-normalized 0..1
  y: Number,  // canvas-normalized 0..1
  class: 0|1, // 0=blue, 1=orange
  id: String  // uuid for keying
}
```
> IMPORTANT: Store x/y as normalized 0..1 values (not pixel coords) so canvas resize does not break points.

---

### Phase 2 — Left Panel: Algorithm Selector + Hyperparameters
**Goal:** Left panel is fully interactive. User picks an algo; hyperparameter sliders appear. Selecting an algo triggers a color-themed glow on the panel.

**Files to create:**
- `frontend/src/components/LeftPanel.jsx` — Algorithm cards + param sliders
- `frontend/src/components/AlgoCard.jsx` — Single algo selector card (active glow state)
- `frontend/src/components/ParamSlider.jsx` — Labeled slider with live value display
- `frontend/src/context/LabContext.jsx` — Global lab state (selectedAlgo, params, points, boundary, metrics)

**Algorithm configs (defined as data, not hardcoded):**

```js
// frontend/src/data/algorithms.js
export const ALGORITHMS = {
  knn: {
    label: 'K-Nearest Neighbors',
    color: '#0EA5E9',
    params: [
      { key: 'k', label: 'K (Neighbors)', min: 1, max: 25, step: 1, default: 5 },
      { key: 'metric', label: 'Distance Metric', type: 'select',
        options: ['euclidean', 'manhattan', 'minkowski'], default: 'euclidean' }
    ]
  },
  svm: {
    label: 'Support Vector Machine',
    color: '#7C3AED',
    params: [
      { key: 'C', label: 'C (Regularization)', min: 0.01, max: 10, step: 0.01, default: 1.0 },
      { key: 'kernel', label: 'Kernel', type: 'select',
        options: ['linear', 'rbf', 'poly'], default: 'rbf' },
      { key: 'gamma', label: 'Gamma', min: 0.01, max: 5, step: 0.01, default: 0.5 }
    ]
  },
  decision_tree: {
    label: 'Decision Tree',
    color: '#F97316',
    params: [
      { key: 'max_depth', label: 'Max Depth', min: 1, max: 15, step: 1, default: 3 },
      { key: 'criterion', label: 'Criterion', type: 'select',
        options: ['gini', 'entropy'], default: 'gini' },
      { key: 'min_samples_split', label: 'Min Samples Split', min: 2, max: 20, step: 1, default: 2 }
    ]
  }
}
```

**Interactions:**
- Clicking algo card -> active state (colored left border, glow, param sliders animate in)
- Slider drag -> param value updates live in state
- Param value displayed numerically next to slider track
- "Run" button at bottom of left panel (or auto-run toggle)
- Hovering algo card -> subtle lift/shadow

---

### Phase 3 — Backend: Boundary Computation API
**Goal:** FastAPI backend receives points + algo + params, returns a 2D grid of predictions (for boundary rendering) + classification metrics.

**Files to create:**
- `backend/api/__init__.py` — Rewrite: register only new routes
- `backend/api/boundary.py` — `POST /api/boundary` endpoint
- `backend/schemas/__init__.py` — Pydantic models: BoundaryRequest, BoundaryResponse
- `backend/services/boundary.py` — Core sklearn logic
- `backend/core/config.py` — Update (remove old references)

**API Contract:**

```
POST /api/boundary
Body:
{
  "points": [{"x": 0.3, "y": 0.6, "class": 0}, ...],
  "algorithm": "knn" | "svm" | "decision_tree",
  "params": { "k": 5 },
  "grid_resolution": 60
}

Response:
{
  "grid": [[0, 1, 0, ...], ...],
  "x_range": [0.0, 1.0],
  "y_range": [0.0, 1.0],
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.91,
    "recall": 0.93,
    "f1": 0.92,
    "confusion_matrix": [[TP, FP], [FN, TN]],
    "support": { "class_0": 15, "class_1": 14 }
  },
  "model_info": {
    "n_support_vectors": 4,
    "tree_depth": 3,
    "k": 5
  },
  "bias_variance": {
    "label": "High Variance",
    "explanation": "..."
  }
}
```

**Backend logic (services/boundary.py):**
- Train sklearn model on user normalized points
- Predict on grid_resolution x grid_resolution meshgrid
- Return 2D grid array
- Compute metrics using sklearn on training points
- Bias-variance: heuristic from model params
- Minimum point guard: require >= 3 points per class before running

**Error handling:**
- < 3 points per class -> 422 with detail message
- Only 1 class present -> 422 with detail message

---

### Phase 4 — Boundary Rendering on Canvas
**Goal:** Frontend sends points to backend, receives grid, renders the colored decision boundary overlay on canvas with smooth animation.

**Files to create/modify:**
- `frontend/src/utils/boundaryRenderer.js` — Grid to Canvas rendering logic
- `frontend/src/hooks/useBoundary.js` — API call + debounce + render trigger
- `frontend/src/services/api.js` — computeBoundary(points, algo, params) fetch call

**Rendering logic:**
- Receive grid[row][col] -> each cell is a colored pixel block
- Class 0 region: rgba(59, 110, 248, 0.15) blue tint
- Class 1 region: rgba(249, 115, 22, 0.15) orange tint
- Boundary line (transition pixels): 1.5px stroke in algo accent color
- Render order: boundary fill -> boundary line -> data points (always on top)
- On boundary update: fade-in new boundary over 300ms (requestAnimationFrame)
- Support Vectors (SVM): circled highlights around SVs

**Trigger strategy:**
- Auto-run mode (default ON): debounce 400ms after any point add/remove or param change
- Manual run mode: only trigger on "Run" button click
- Pulsing ring on canvas edge while API call is in flight

---

### Phase 5 — Right Panel: Live Metrics Dashboard
**Goal:** Right panel shows animated metrics that update whenever boundary recomputes.

**Files to create:**
- `frontend/src/components/RightPanel.jsx`
- `frontend/src/components/AccuracyGauge.jsx` — SVG arc gauge (0-100%)
- `frontend/src/components/ConfusionMatrix.jsx` — 2x2 TP/TN/FP/FN grid
- `frontend/src/components/MetricBar.jsx` — Animated Precision/Recall/F1 bar
- `frontend/src/components/BiasVarianceChip.jsx` — Overfit/Balanced/Underfit pill
- `frontend/src/components/ClassDistribution.jsx` — SVG donut (no lib)

**Accuracy Gauge:**
- SVG arc, 0-100%, value in center
- Color: < 60% red, 60-80% yellow, > 80% green
- Animates on CSS stroke-dashoffset transition

**Bias-Variance Heuristic:**
```
KNN:   K=1 -> High Variance | K=3-7 -> Balanced | K>15 -> High Bias
SVM:   C<0.1 -> High Bias   | C>5   -> High Variance  | else Balanced
DT:    depth=1 -> High Bias | depth>8 -> High Variance | else Balanced
```

---

### Phase 6 — Bottom Theory Strip
**Goal:** Theory strip dynamically explains the current algo behavior based on selected params.

**Files to create:**
- `frontend/src/components/TheoryStrip.jsx`
- `frontend/src/data/theory.js`

**Strip layout (fixed ~140px height, never scrolls):**
- Left: Algorithm name + formula badge
- Center: Dynamic explanation text (fades on change)
- Right: "Key Intuition" callout box (static per algo)

---

### Phase 7 — Demo Presets & UX Polish
**Goal:** Pre-populated dataset shapes + all interaction refinements + loading states.

**Preset shapes (all return Array of {x, y, class}):**
- generateMoons(n=40) — two interleaved half-circles (great for SVM RBF)
- generateBlobs(n=40) — two Gaussian clusters (great for KNN/DT)
- generateXOR(n=40) — XOR pattern (shows linear SVM fails)
- generateCircles(n=40) — concentric circles (RBF kernel demo)
- generateSpiral(n=40) — interleaved spirals (DT depth demo)

**UX polish checklist:**
- [ ] Topbar: Logo SVG + wordmark + algo chips + version badge
- [ ] Algo cards: hover scale(1.01), active left-border glow
- [ ] Sliders: custom styled thumb, colored track fill from left
- [ ] Canvas: crosshair cursor, dot grid background (20px pitch)
- [ ] Points: inner highlight circle for 3D look
- [ ] Loading state: canvas edge pulses with algo color
- [ ] Empty state: hint text on canvas
- [ ] Keyboard shortcuts: C=clear, R=run, 1/2/3=switch algo
- [ ] Error toast: bottom-center, auto-dismiss 3s
- [ ] Tooltips on metric labels

---

### Phase 8 — Backend Hardening & Integration
**Goal:** Backend is robust, handles all edge cases, CORS configured, proxy working.

**Checklist:**
- [ ] CORS: allow http://localhost:5173 in config.py
- [ ] Vite proxy: /api -> http://localhost:8000
- [ ] Pydantic guards all inputs
- [ ] All errors return { "detail": "..." }
- [ ] Numpy vectorized meshgrid (no Python loops)
- [ ] Target response time < 200ms for 60x60 grid

---

### Phase 9 — Final Visual Polish & Professional Touches
**Goal:** Lab looks like a real professional tool, not a student project.

**Checklist:**
- [ ] Logo: SVG atom/network icon top-left + MLVlab wordmark
- [ ] Topbar: frosted glass backdrop-filter: blur()
- [ ] Consistent shadow system across panels
- [ ] All state changes: 200ms ease transitions
- [ ] Canvas: subtle dot grid on background
- [ ] Active algo glow: box-shadow with algo color
- [ ] Boundary: bilinear interpolation for smooth edges
- [ ] Metric count-up animation on first appearance
- [ ] README.md: project description, setup, team credits

---

## Final File Tree

```
Machine-Learning-Virtual-Lab/
├── requirements.txt
├── README.md
├── .gitignore
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py          # create_app(), CORS, routes
│   │   ├── boundary.py          # POST /api/boundary
│   │   └── system.py            # GET /api/health, SPA fallback
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── schemas/
│   │   └── __init__.py          # BoundaryRequest, BoundaryResponse
│   ├── services/
│   │   ├── __init__.py
│   │   └── boundary.py          # sklearn KNN/SVM/DT + grid computation
│   └── utils/
│       ├── __init__.py
│       └── http.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── index.css             # Full design system
│       ├── App.jsx               # Layout shell + LabContext provider
│       ├── context/
│       │   └── LabContext.jsx
│       ├── hooks/
│       │   ├── useCanvas.js
│       │   ├── usePoints.js
│       │   └── useBoundary.js
│       ├── components/
│       │   ├── TopBar.jsx
│       │   ├── LeftPanel.jsx
│       │   ├── AlgoCard.jsx
│       │   ├── ParamSlider.jsx
│       │   ├── Canvas.jsx
│       │   ├── RightPanel.jsx
│       │   ├── AccuracyGauge.jsx
│       │   ├── ConfusionMatrix.jsx
│       │   ├── MetricBar.jsx
│       │   ├── BiasVarianceChip.jsx
│       │   ├── ClassDistribution.jsx
│       │   └── TheoryStrip.jsx
│       ├── data/
│       │   ├── algorithms.js
│       │   ├── presets.js
│       │   └── theory.js
│       ├── services/
│       │   └── api.js
│       └── utils/
│           ├── canvasDraw.js
│           └── boundaryRenderer.js
└── docs/
    ├── plan.md
    ├── README.md
    └── context/
        └── ml-syllabus.txt
```

---

## Phase Execution Context Block

When giving AI commands per phase, paste this at the top:

```
Context: ML Virtual Lab — Decision Boundary Playground
Stack: React 19 + Vite, Vanilla CSS, FastAPI + sklearn
Constraint: Single screen, no scroll, light mode, Inter font
Design: bg=#F0F4FF accent=#3B6EF8 | KNN=#0EA5E9 | SVM=#7C3AED | DT=#F97316
See: docs/plan.md for full spec

Task: Build [Phase N — Name] per docs/plan.md
```

---

## Development Order & Dependencies

```
Phase 0 (Foundation)
  Phase 1 (Canvas Engine)
    Phase 2 (Left Panel + Context) <-- parallel with Phase 3
    Phase 3 (Backend API)          <-- parallel with Phase 2
      Phase 4 (Boundary Rendering) <-- needs Phase 1 + 3
        Phase 5 (Right Panel)      <-- needs Phase 4
          Phase 6 (Theory Strip)   <-- needs Phase 2
            Phase 7 (Presets + Polish)
              Phase 8 (Backend Hardening)
                Phase 9 (Final Polish)
```

---

## Updated requirements.txt

```
fastapi>=0.115.0
uvicorn>=0.34.0
pydantic>=2.0.0
numpy>=1.26.0
scikit-learn>=1.4.0
```

Removed: torch, pandas, matplotlib, seaborn, category_encoders, ucimlrepo

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Boundary computation | Backend (sklearn) | JS ML libs limited; sklearn gives accurate SVM/KNN |
| Grid resolution | 60x60 | Fast compute + smooth render |
| Point storage | Normalized 0..1 | Survives canvas resize |
| State management | React Context | No Redux needed; simple single-page state |
| Charts | Custom SVG | No bundle weight, full animation control |
| Auto-run debounce | 400ms | Feels instant, avoids API flood |
| Language | Plain JS (no TS) | Faster team prototyping |

---

*Last updated: October 2026 — Team ML VLab*
