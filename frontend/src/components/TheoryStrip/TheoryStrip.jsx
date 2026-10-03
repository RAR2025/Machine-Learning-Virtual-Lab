import React from 'react';
import './TheoryStrip.css';
import { ALGORITHMS } from '../../data/algorithms';

export default function TheoryStrip({ activeAlgo, hyperparams }) {
  const algo = ALGORITHMS[activeAlgo];

  // Dynamic theoretical explanation based on current hyperparams
  const getDynamicTheory = () => {
    if (activeAlgo === 'knn') {
      const k = hyperparams.k ?? 3;
      if (k === 1) {
        return {
          title: 'Extreme Low K (K = 1)',
          impact: 'Generates 1-Nearest Neighbor Voronoi tessellation. The boundary wraps tightly around every single isolated outlier, causing high variance and maximum risk of overfitting.'
        };
      } else if (k >= 15) {
        return {
          title: 'High K (Smoothing & High Bias)',
          impact: 'A large neighborhood forces majority consensus. Minor local clusters and non-linear patterns get washed out, creating a flatter, higher-bias decision boundary.'
        };
      }
      return {
        title: `Balanced Neighborhood (K = ${k})`,
        impact: `Assigns class by polling ${k} nearest Euclidean neighbors with ${hyperparams.weights ?? 'uniform'} weighting. Produces locally adaptive piece-wise curves.`
      };
    }

    if (activeAlgo === 'svm') {
      const kernel = hyperparams.kernel ?? 'rbf';
      const c = hyperparams.c ?? 1.0;
      if (kernel === 'linear') {
        return {
          title: 'Linear Hyperplane w · x + b = 0',
          impact: `Constrained to a straight planar separator. Regularization C=${c} controls margin softness. Cannot separate non-linear distributions like concentric circles.`
        };
      } else if (kernel === 'rbf') {
        const gamma = hyperparams.gamma ?? 0.5;
        return {
          title: `RBF Gaussian Kernel (γ = ${gamma}, C = ${c})`,
          impact: `Maps 2D inputs to infinite-dimensional Hilbert space. High γ (${gamma}) contracts the bell curves into tight islands; lower γ allows smoother continuous manifolds.`
        };
      }
      return {
        title: 'Polynomial Kernel Separator',
        impact: `Computes dot products in high-degree polynomial space, generating parabolic or cubic boundary contours.`
      };
    }

    if (activeAlgo === 'dt') {
      const depth = hyperparams.max_depth ?? 4;
      return {
        title: `Decision Tree Cuts (Max Depth = ${depth})`,
        impact: `Partitions the plane using strictly axis-parallel orthogonal thresholds (X₁ ≤ θ or X₂ ≤ θ). Depth ${depth} allows up to ${Math.pow(2, depth)} rectangular sub-regions.`
      };
    }

    return {
      title: 'Classifier Theory',
      impact: algo.summary
    };
  };

  const dynamicInfo = getDynamicTheory();

  return (
    <footer className="vlab-theory-strip">
      {/* Column 1: Core Mathematical Model */}
      <div className="theory-column">
        <div className="theory-tag-row">
          <span className="theory-badge" style={{ color: algo.themeColor, borderColor: algo.borderColor }}>
            {algo.shortName} Foundation
          </span>
          <span className="theory-category">{algo.category}</span>
        </div>
        <div className="theory-body-text">{algo.summary}</div>
      </div>

      <div className="theory-divider"></div>

      {/* Column 2: Dynamic Hyperparameter Effect */}
      <div className="theory-column theory-column-highlight">
        <div className="theory-tag-row">
          <span className="theory-tag-live">Active Dynamics</span>
          <span className="theory-title-live">{dynamicInfo.title}</span>
        </div>
        <div className="theory-body-text">{dynamicInfo.impact}</div>
      </div>

      <div className="theory-divider"></div>

      {/* Column 3: Geometric Boundary Observation */}
      <div className="theory-column">
        <div className="theory-tag-row">
          <span className="theory-badge">Geometric Observation</span>
        </div>
        <div className="theory-body-text">
          {activeAlgo === 'knn' && 'Notice how the boundary adapts to point density. Watch isolated noise points create small circular boundary islands when K is small.'}
          {activeAlgo === 'svm' && 'Observe how the boundary maintains maximum distance (margin) from the nearest support vectors of each class.'}
          {activeAlgo === 'dt' && 'Notice that the boundary is exclusively composed of 90-degree horizontal and vertical step lines, never smooth diagonal curves.'}
        </div>
      </div>
    </footer>
  );
}
