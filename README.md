# ML Virtual Lab: Decision Boundary Playground

An interactive, single-screen real-time Machine Learning Virtual Laboratory for visualizing classification decision boundaries, understanding algorithm geometric behavior, and exploring the Bias-Variance tradeoff.

## Key Features

- **Single Screen, 0-Scroll Layout**: Fully reactive 3-panel workspace + synchronized bottom educational theory strip.
- **Interactive High-DPI Canvas**: Real-time point drawing, drag-to-paint, eraser, undo (`Ctrl+Z`), and classic dataset presets (Two Moons, Concentric Circles, Linear, XOR).
- **Core Algorithms Supported**:
  - **K-Nearest Neighbors (KNN)**: Adjustable K neighbors, distance weighting, and distance metrics.
  - **Support Vector Machine (SVM)**: RBF, Linear, and Polynomial kernels with regularization $C$ and $\gamma$.
  - **Decision Tree**: Tree depth limit (orthogonal axis cuts), splitting criterion (Gini / Entropy).
- **Live Metrics Dashboard**: Real-time classification accuracy, precision, recall, F1, confusion matrix, and bias-variance estimator.
- **Dynamic Theory Engine**: Real-time mathematical intuition and geometric observation tips tailored to active algorithm and hyperparameter states.

---

## Architecture & Layout

```
+--------------------------------------------------------------------------+
| TopBar (54px) — Brand Logo | Point Counters | Algo Badge | Auto-Train    |
+-------------------+----------------------------------+-------------------+
| [Left Panel 290px]| [Center Canvas: flex-grow]       | [Right 300px]     |
| - Algo Cards      | - Interactive drawing            | - Accuracy Gauge  |
| - Hyperparam      | - High-DPI Retina resolution     | - Precision/Recall|
|   Sliders/Selects | - Live decision boundary mesh    | - Confusion Matrix|
| - Formula Snippet | - Presets & coordinate grid      | - Bias-Variance   |
+-------------------+----------------------------------+-------------------+
| Bottom Strip (136px) — Educational Theory & Geometric Observations       |
+--------------------------------------------------------------------------+
```

---

## Tech Stack

- **Frontend**: React 19, Vite 8, Vanilla CSS (Design system with CSS custom properties), HTML5 Canvas API
- **Backend**: FastAPI, scikit-learn, numpy, uvicorn

---

## Getting Started

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn backend.main:app --port 8000 --reload
```

Interactive API docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Phase Roadmap

- **Phase 0–2 (Foundation)**: Design tokens, 1-screen shell, high-DPI canvas engine, algorithm controls.
- **Phase 3 & 8 (Backend Lead)**: FastAPI `POST /api/boundary`, meshgrid inference, scikit-learn pipeline.
- **Phase 4 & 5 (Visualization Lead)**: Canvas boundary heatmap overlay & SVG metrics dashboard.
- **Phase 6 & 7 (Theory & Presets Lead)**: Educational theory engine & toy dataset generators.
- **Phase 9 (All Members)**: Demo polish and presentation readiness.
