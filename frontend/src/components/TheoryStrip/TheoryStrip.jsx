import React from 'react';
import './TheoryStrip.css';
import { ALGORITHMS } from '../../data/algorithms';

export default function TheoryStrip({
  activeAlgo,
  hyperparams,
  collapsed,
  onToggleCollapse
}) {
  const algo = ALGORITHMS[activeAlgo];

  // Dynamic theoretical explanation based on current hyperparams
  const getDynamicTheory = () => {
    if (activeAlgo === 'knn') {
      const k = hyperparams.k ?? 3;
      if (k === 1) {
        return {
          title: 'K = 1 (Voronoi Tessellation)',
          impact: 'Wraps tightly around every single isolated outlier. Maximum variance, high risk of overfitting.'
        };
      } else if (k >= 15) {
        return {
          title: `K = ${k} (Broad Neighborhood Averaging)`,
          impact: 'Large neighborhood forces broad consensus. Smoother decision boundary, higher bias.'
        };
      }
      return {
        title: `K = ${k} (${hyperparams.weights ?? 'uniform'} weights)`,
        impact: `Assigns class by polling ${k} nearest Euclidean neighbors. Generates adaptive local curves.`
      };
    }

    if (activeAlgo === 'svm') {
      const kernel = hyperparams.kernel ?? 'rbf';
      const c = hyperparams.c ?? 1.0;
      if (kernel === 'linear') {
        return {
          title: `Linear Hyperplane (C = ${c})`,
          impact: 'Constrained to a straight separator. Soft margin C controls tolerance to misclassified points.'
        };
      } else if (kernel === 'rbf') {
        const gamma = hyperparams.gamma ?? 0.5;
        return {
          title: `RBF Gaussian Kernel (γ = ${gamma}, C = ${c})`,
          impact: 'Maps 2D inputs to Hilbert space. High γ creates tight boundary islands around points.'
        };
      }
      return {
        title: 'Polynomial Kernel',
        impact: 'Computes dot products in high-degree polynomial feature space.'
      };
    }

    if (activeAlgo === 'dt') {
      const depth = hyperparams.max_depth ?? 4;
      return {
        title: `Axis Cuts (Max Depth = ${depth})`,
        impact: 'Partitions space using strictly horizontal and vertical 90-degree threshold cuts.'
      };
    }

    return {
      title: 'Classifier Theory',
      impact: algo.summary
    };
  };

  const dynamicInfo = getDynamicTheory();

  if (collapsed) {
    return (
      <footer className="vlab-theory-strip minimized" onClick={onToggleCollapse}>
        <div className="minimized-strip-content">
          <span className="minimized-title">Theory & Geometric Intuition: <b>{algo.name}</b></span>
          <span className="expand-hint">Click to expand ▲</span>
        </div>
      </footer>
    );
  }

  return (
    <footer className="vlab-theory-strip">
      <div className="theory-header-bar">
        <div className="theory-header-left">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2a9 9 0 0 1 9 9c0 3.1-1.5 5.8-3.9 7.4l-.1.1v2.5a1 1 0 0 1-1 1h-8a1 1 0 0 1-1-1v-2.5l-.1-.1A9 9 0 0 1 12 2z"></path>
          </svg>
          <span className="theory-main-title">Theory & Geometric Observations</span>
        </div>
        <button
          className="theory-minimize-btn"
          onClick={onToggleCollapse}
          title="Minimize Theory Panel"
        >
          Minimize ▼
        </button>
      </div>

      <div className="theory-columns-grid">
        {/* Column 1: Core Foundation */}
        <div className="theory-col">
          <span className="col-tag">01. Principle</span>
          <p className="col-desc">{algo.summary}</p>
        </div>

        {/* Column 2: Active Dynamics */}
        <div className="theory-col highlight">
          <span className="col-tag">02. Active Dynamics — {dynamicInfo.title}</span>
          <p className="col-desc">{dynamicInfo.impact}</p>
        </div>

        {/* Column 3: Geometric Observation */}
        <div className="theory-col">
          <span className="col-tag">03. What to Observe</span>
          <p className="col-desc">
            {activeAlgo === 'knn' && 'Notice how the boundary adapts to point density. Watch isolated noise points create small circular islands when K is small.'}
            {activeAlgo === 'svm' && 'Observe how the boundary maintains maximum distance (margin) from the nearest support vectors of each class.'}
            {activeAlgo === 'dt' && 'Notice that the boundary is exclusively composed of 90-degree horizontal and vertical step lines, never smooth curves.'}
          </p>
        </div>
      </div>
    </footer>
  );
}
