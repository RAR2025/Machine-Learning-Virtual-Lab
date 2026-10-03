import React, { useState } from 'react';
import './GuideModal.css';

export default function GuideModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('steps'); // 'steps' | 'algorithms' | 'shortcuts'

  if (!isOpen) return null;

  return (
    <div className="guide-modal-backdrop" onClick={onClose}>
      <div className="guide-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="guide-modal-header">
          <div className="guide-header-left">
            <div className="guide-header-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <div>
              <div className="guide-header-title">Virtual Lab User Guide & Experiment Manual</div>
              <div className="guide-header-desc">
                Step-by-step workflow, algorithm theory, and interactive control guide
              </div>
            </div>
          </div>
          <button className="guide-close-btn" onClick={onClose} title="Close guide (Esc)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="guide-tabs-bar">
          <button
            className={`guide-tab-item ${activeTab === 'steps' ? 'active' : ''}`}
            onClick={() => setActiveTab('steps')}
          >
            <span>1. Step-by-Step Workflow</span>
          </button>
          <button
            className={`guide-tab-item ${activeTab === 'algorithms' ? 'active' : ''}`}
            onClick={() => setActiveTab('algorithms')}
          >
            <span>2. Algorithm Fundamentals</span>
          </button>
          <button
            className={`guide-tab-item ${activeTab === 'shortcuts' ? 'active' : ''}`}
            onClick={() => setActiveTab('shortcuts')}
          >
            <span>3. Controls & Shortcuts</span>
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="guide-modal-body">
          {activeTab === 'steps' && (
            <div className="guide-steps-list">
              {/* Step 1 */}
              <div className="step-card">
                <div className="step-badge">Step 01</div>
                <div className="step-content">
                  <div className="step-title">Supply 2D Training Data</div>
                  <div className="step-text">
                    You can place custom points manually on the canvas or load benchmark synthetic distributions:
                  </div>
                  <ul className="step-bullets">
                    <li>
                      <b>Draw Mode:</b> Toggle between <b>Class A</b> (Blue points) and <b>Class B</b> (Orange points) on the canvas toolbar. Click or drag to add points.
                    </li>
                    <li>
                      <b>Starter Presets:</b> Click <b>Two Moons</b> (interlocking non-linear manifolds), <b>Concentric Circles</b> (radial classification), <b>Linearly Separable</b> (two gaussian clusters), or <b>XOR</b> (diagonal 4-quadrant benchmark).
                    </li>
                  </ul>
                </div>
              </div>

              {/* Step 2 */}
              <div className="step-card">
                <div className="step-badge">Step 02</div>
                <div className="step-content">
                  <div className="step-title">Select a Classification Algorithm</div>
                  <div className="step-text">
                    Use the <b>Left Panel</b> to choose which machine learning classifier you want to examine:
                  </div>
                  <div className="step-subgrid">
                    <div className="subgrid-card">
                      <span className="card-mini-tag knn-tag">KNN</span>
                      <p>Non-parametric lazy learner. Classifies based on majority vote of the nearest Euclidean neighbors.</p>
                    </div>
                    <div className="subgrid-card">
                      <span className="card-mini-tag svm-tag">SVM</span>
                      <p>Finds the optimal separating hyperplane with maximum margin. Supports Linear, RBF, and Polynomial kernels.</p>
                    </div>
                    <div className="subgrid-card">
                      <span className="card-mini-tag dt-tag">Decision Tree</span>
                      <p>Hierarchical decision rules. Partitions space with strictly orthogonal (axis-parallel) threshold cuts.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="step-card">
                <div className="step-badge">Step 03</div>
                <div className="step-content">
                  <div className="step-title">Tune Hyperparameters & Watch Live Boundary Reaction</div>
                  <div className="step-text">
                    Move the parameter sliders in real time and observe the visual contour changes:
                  </div>
                  <ul className="step-bullets">
                    <li>
                      <b>KNN:</b> Change $K$ (e.g. $K=1$ produces tightly wound Voronoi islands around single noise points; large $K=15$ smooths the boundary curve).
                    </li>
                    <li>
                      <b>SVM:</b> Adjust Regularization $C$ (soft vs hard margin) and RBF $\gamma$ (gamma radius of influence for support vectors).
                    </li>
                    <li>
                      <b>Decision Tree:</b> Adjust <b>Max Depth</b> to watch tree growth from a single decision stump into fine-grained rectangular partitions.
                    </li>
                  </ul>
                </div>
              </div>

              {/* Step 4 */}
              <div className="step-card">
                <div className="step-badge">Step 04</div>
                <div className="step-content">
                  <div className="step-title">Analyze Live Metrics & Confusion Matrix</div>
                  <div className="step-text">
                    The <b>Right Panel</b> computes evaluation metrics in real time:
                  </div>
                  <ul className="step-bullets">
                    <li>
                      <b>Classification Accuracy:</b> Overall percentage of correctly classified points.
                    </li>
                    <li>
                      <b>Precision, Recall & F1-Score:</b> Detailed classification efficacy for both Class A and Class B.
                    </li>
                    <li>
                      <b>Confusion Matrix:</b> Displays True Positives (green), False Positives/Negatives (red), and True Negatives.
                    </li>
                  </ul>
                </div>
              </div>

              {/* Step 5 */}
              <div className="step-card">
                <div className="step-badge">Step 05</div>
                <div className="step-content">
                  <div className="step-title">Examine the Bias-Variance Tradeoff & Theory Strip</div>
                  <div className="step-text">
                    Look at the bottom <b>Theory & Observations</b> bar to see dynamic mathematical principles and real-time guidance explaining <i>why</i> the boundary looks the way it does.
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'algorithms' && (
            <div className="guide-algo-details">
              {/* KNN Section */}
              <div className="algo-deep-dive">
                <div className="dive-header">
                  <span className="dive-pill knn-pill">K-Nearest Neighbors (KNN)</span>
                  <span className="dive-type">Instance-Based / Non-Parametric</span>
                </div>
                <p className="dive-text">
                  KNN does not construct an explicit internal model during training; it stores all training points in memory. When predicting an unseen query point, it computes Euclidean distance to all samples, identifies the K closest neighbors, and takes a majority vote.
                </p>
                <div className="dive-insight">
                  <b>Key Insight for Lab Demonstrations:</b> Setting $K=1$ generates Voronoi cells where every point has 100% training accuracy but extreme variance. Increasing $K$ introduces inductive bias and produces smoother, more robust decision curves.
                </div>
              </div>

              {/* SVM Section */}
              <div className="algo-deep-dive">
                <div className="dive-header">
                  <span className="dive-pill svm-pill">Support Vector Machine (SVM)</span>
                  <span className="dive-type">Max-Margin Separator / Kernel Trick</span>
                </div>
                <p className="dive-text">
                  SVM searches for a hyperplane $w \cdot x + b = 0$ that maximizes the geometric distance (margin) to the nearest points of each class, known as <b>Support Vectors</b>. When classes are not linearly separable (such as concentric circles), the <b>RBF Kernel</b> $K(x, x') = \exp(-\gamma \|x - x'\|^2)$ implicitly maps inputs into an infinite-dimensional feature space where a linear boundary can separate them.
                </p>
                <div className="dive-insight">
                  <b>Key Insight for Lab Demonstrations:</b> Switch from <i>Linear</i> to <i>RBF</i> on the Concentric Circles preset. The Linear kernel will fail (~50% accuracy), while RBF creates a clean circular boundary separating the inner and outer rings.
                </div>
              </div>

              {/* Decision Tree Section */}
              <div className="algo-deep-dive">
                <div className="dive-header">
                  <span className="dive-pill dt-pill">Decision Tree Classifier</span>
                  <span className="dive-type">Recursive Binary Partitioning</span>
                </div>
                <p className="dive-text">
                  Decision Trees recursively divide feature space using orthogonal cuts aligned strictly with the feature axes ($X_1 \le \theta$ or $X_2 \le \theta$). At each node, the split that maximizes purity (minimizes <b>Gini Impurity</b> $1 - \sum p_i^2$ or <b>Entropy</b>) is selected.
                </p>
                <div className="dive-insight">
                  <b>Key Insight for Lab Demonstrations:</b> Notice the decision boundary is always a collection of 90° right-angle step lines. At Max Depth = 1, it forms a single line (Decision Stump). At high depths, it forms intricate staircases around individual points.
                </div>
              </div>
            </div>
          )}

          {activeTab === 'shortcuts' && (
            <div className="guide-shortcuts-grid">
              <div className="shortcut-card">
                <div className="shortcut-key">Click Canvas</div>
                <div className="shortcut-info">
                  <b>Add Point:</b> Places a point of the currently active class (Blue Class A or Orange Class B).
                </div>
              </div>

              <div className="shortcut-card">
                <div className="shortcut-key">Drag on Canvas</div>
                <div className="shortcut-info">
                  <b>Paint Points:</b> Rapidly sketch multiple samples smoothly with distance throttling.
                </div>
              </div>

              <div className="shortcut-card">
                <div className="shortcut-key">Ctrl + Z / ⌘ + Z</div>
                <div className="shortcut-info">
                  <b>Undo:</b> Reverts the last placed point or dataset operation.
                </div>
              </div>

              <div className="shortcut-card">
                <div className="shortcut-key">[</div>
                <div className="shortcut-info">
                  <b>Toggle Left Panel:</b> Collapse or expand the Classifier Configuration panel for maximum canvas width.
                </div>
              </div>

              <div className="shortcut-card">
                <div className="shortcut-key">]</div>
                <div className="shortcut-info">
                  <b>Toggle Right Panel:</b> Collapse or expand the Live Metrics dashboard.
                </div>
              </div>

              <div className="shortcut-card">
                <div className="shortcut-key">Auto-Train</div>
                <div className="shortcut-info">
                  <b>Continuous Re-fit:</b> When enabled, moving any slider or drawing points automatically updates the decision boundary in real time.
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="guide-modal-footer">
          <div className="footer-tip">
            💡 <b>Tip:</b> Try loading the <b>Two Moons</b> preset, select <b>SVM (RBF)</b>, and drag the <b>Gamma</b> slider from 0.1 to 4.0 to watch the boundary manifold contract.
          </div>
          <button className="btn btn-primary" onClick={onClose}>
            Got it, Start Experimenting
          </button>
        </div>
      </div>
    </div>
  );
}
