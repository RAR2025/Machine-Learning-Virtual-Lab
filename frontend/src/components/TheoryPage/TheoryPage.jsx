import React from 'react';
import './TheoryPage.css';

function BoundaryDiagram() {
  return (
    <svg className="theory-diagram" viewBox="0 0 360 180" role="img" aria-label="Feature space divided by a decision boundary">
      <rect width="360" height="180" rx="8" fill="#F8FAFC" />
      <path d="M178 8 C145 45 215 58 176 91 C139 122 210 137 177 172" fill="none" stroke="#0F172A" strokeWidth="3" />
      <text x="72" y="24" fill="#2563EB" fontSize="12" fontWeight="700">Class A</text>
      <text x="260" y="24" fill="#EA580C" fontSize="12" fontWeight="700">Class B</text>
      {[['#2563EB', 82, 56], ['#2563EB', 112, 93], ['#2563EB', 75, 135], ['#EA580C', 270, 57], ['#EA580C', 235, 101], ['#EA580C', 282, 139]].map(([fill, cx, cy], index) => (
        <circle key={index} cx={cx} cy={cy} r="6" fill={fill} />
      ))}
      <text x="186" y="88" fill="#0F172A" fontSize="11">boundary</text>
    </svg>
  );
}

function KnnDiagram() {
  return (
    <svg className="theory-diagram" viewBox="0 0 360 180" role="img" aria-label="K nearest neighbors voting around a query point">
      <rect width="360" height="180" rx="8" fill="#F0F9FF" />
      <circle cx="180" cy="90" r="52" fill="none" stroke="#0284C7" strokeDasharray="5 4" strokeWidth="2" />
      {[['#2563EB', 145, 58], ['#2563EB', 154, 119], ['#2563EB', 218, 74], ['#EA580C', 222, 121], ['#2563EB', 188, 43]].map(([fill, cx, cy], index) => (
        <circle key={index} cx={cx} cy={cy} r="7" fill={fill} />
      ))}
      <circle cx="180" cy="90" r="9" fill="#FFFFFF" stroke="#0F172A" strokeWidth="3" />
      <path d="M176 90h8M180 86v8" stroke="#0F172A" strokeWidth="2" />
      <text x="14" y="24" fill="#0284C7" fontSize="12" fontWeight="700">K nearest points vote</text>
      <text x="190" y="160" fill="#0F172A" fontSize="11">query point</text>
    </svg>
  );
}

function SvmDiagram() {
  return (
    <svg className="theory-diagram" viewBox="0 0 360 180" role="img" aria-label="SVM maximum margin separating hyperplane">
      <rect width="360" height="180" rx="8" fill="#F5F3FF" />
      <path d="M72 156 L282 24" stroke="#7C3AED" strokeWidth="3" />
      <path d="M49 156 L259 24M95 156 L305 24" stroke="#A78BFA" strokeWidth="2" strokeDasharray="6 5" />
      {[['#2563EB', 91, 126], ['#2563EB', 125, 102], ['#2563EB', 155, 91], ['#EA580C', 202, 74], ['#EA580C', 237, 54], ['#EA580C', 270, 35]].map(([fill, cx, cy], index) => (
        <circle key={index} cx={cx} cy={cy} r="6" fill={fill} />
      ))}
      <text x="143" y="164" fill="#7C3AED" fontSize="11">maximum margin</text>
    </svg>
  );
}

function TreeDiagram() {
  return (
    <svg className="theory-diagram" viewBox="0 0 360 180" role="img" aria-label="Decision tree axis-aligned rectangular regions">
      <rect width="360" height="180" rx="8" fill="#FFF7ED" />
      <path d="M180 12V168M25 92H335M95 92V168M270 92V168" stroke="#EA580C" strokeWidth="3" />
      <rect x="25" y="15" width="155" height="77" fill="#DBEAFE" opacity="0.8" />
      <rect x="180" y="15" width="155" height="77" fill="#FFEDD5" opacity="0.8" />
      <rect x="25" y="92" width="70" height="76" fill="#FFEDD5" opacity="0.8" />
      <rect x="95" y="92" width="85" height="76" fill="#DBEAFE" opacity="0.8" />
      <rect x="180" y="92" width="90" height="76" fill="#DBEAFE" opacity="0.8" />
      <rect x="270" y="92" width="65" height="76" fill="#FFEDD5" opacity="0.8" />
      <text x="135" y="30" fill="#9A3412" fontSize="11">orthogonal cuts</text>
    </svg>
  );
}

export default function TheoryPage() {
  return (
    <main className="theory-page">
      <header className="theory-page-header">
        <span className="theory-eyebrow">MACHINE LEARNING CONCEPTS</span>
        <h1>Decision Boundaries and Classification</h1>
        <p>Understand how KNN, SVM, and Decision Trees divide feature space before experimenting in the Simulation.</p>
      </header>

      <section className="theory-section">
        <div className="theory-section-copy">
          <span className="theory-section-number">01</span>
          <div>
            <h2>Decision Boundaries and Feature Space</h2>
            <p>In supervised classification, an algorithm learns a mapping from feature coordinates in an n-dimensional space to class labels. A decision boundary is the geometric manifestation of this mapping: a hypersurface that partitions feature space into distinct regions.</p>
            <ul>
              <li><strong>Linear separability:</strong> Classes can be separated by one straight line in 2D or a flat hyperplane in higher dimensions.</li>
              <li><strong>Non-linear boundaries:</strong> Datasets such as Two Moons and Concentric Circles require curved or complex boundaries.</li>
            </ul>
          </div>
        </div>
        <BoundaryDiagram />
      </section>

      <section className="theory-section">
        <div className="theory-section-copy">
          <span className="theory-section-number">02</span>
          <div>
            <h2>K-Nearest Neighbors (KNN)</h2>
            <p>KNN is a non-parametric, instance-based learner. It stores the training data and defers computation until prediction time, when it measures distances to the stored points and uses a majority vote.</p>
            <ul>
              <li><strong>Geometric behavior:</strong> KNN implicitly creates Voronoi tessellations.</li>
              <li><strong>Distance metrics:</strong> Euclidean distance creates circular or spherical regions, while Manhattan distance creates diamond-like regions.</li>
              <li><strong>Distance weighting:</strong> Weighted votes give closer neighbors more influence and can create tighter boundaries.</li>
              <li><strong>The role of K:</strong> Small K, such as K = 1, creates irregular high-variance boundaries. Large K produces smoother boundaries but may miss fine patterns.</li>
            </ul>
          </div>
        </div>
        <KnnDiagram />
      </section>

      <section className="theory-section">
        <div className="theory-section-copy">
          <span className="theory-section-number">03</span>
          <div>
            <h2>Support Vector Machine (SVM)</h2>
            <p>SVM finds a separating hyperplane that maximizes the margin between classes. The nearest points to that boundary are the support vectors.</p>
            <ul>
              <li><strong>Kernel trick:</strong> Kernels map inputs into a higher-dimensional space where a linear separator can represent a curved boundary in the original space.</li>
              <li><strong>Linear:</strong> Straight boundaries for linearly separable data.</li>
              <li><strong>Polynomial:</strong> Polynomial-shaped curves.</li>
              <li><strong>RBF:</strong> Localized, circular, or island-like boundaries for complex data.</li>
              <li><strong>Regularization C:</strong> Low C allows errors and gives a smoother boundary; high C penalizes errors and can create a tighter fit.</li>
              <li><strong>Gamma:</strong> Low gamma gives each point a broad reach; high gamma gives a close reach and can create isolated islands.</li>
            </ul>
          </div>
        </div>
        <SvmDiagram />
      </section>

      <section className="theory-section">
        <div className="theory-section-copy">
          <span className="theory-section-number">04</span>
          <div>
            <h2>Decision Trees</h2>
            <p>Decision Trees partition feature space using a sequence of hierarchical binary questions, such as whether a coordinate is greater than a threshold. A greedy top-down process selects each split.</p>
            <ul>
              <li><strong>Splitting criteria:</strong> Gini impurity measures incorrect-classification probability, while entropy measures disorder and information gain.</li>
              <li><strong>Geometric behavior:</strong> Feature-by-feature splits are orthogonal, so boundaries form rectangular, step-like regions and approximate diagonals as staircases.</li>
              <li><strong>Tree depth:</strong> Shallow trees can underfit with large blocks; deep trees can overfit by creating tiny regions around individual points.</li>
            </ul>
          </div>
        </div>
        <TreeDiagram />
      </section>

      <section className="theory-section bias-variance-section">
        <div className="theory-section-copy">
          <span className="theory-section-number">05</span>
          <div>
            <h2>The Bias-Variance Tradeoff</h2>
            <p>Total model error can be viewed as <strong>Error = Bias<sup>2</sup> + Variance + Irreducible Error</strong>.</p>
            <ul>
              <li><strong>Bias (underfitting):</strong> A model that is too simple ignores important structure, such as a Linear SVM on Concentric Circles.</li>
              <li><strong>Variance (overfitting):</strong> A model that is too complex follows noise, such as KNN with K = 1 or an unrestricted Decision Tree.</li>
              <li><strong>Finding the sweet spot:</strong> Tune K, C, gamma, or tree depth until the boundary captures the underlying pattern without following random noise.</li>
            </ul>
          </div>
        </div>
        <div className="tradeoff-diagram" role="img" aria-label="Bias variance tradeoff curve">
          <svg className="theory-diagram" viewBox="0 0 360 180">
            <rect width="360" height="180" rx="8" fill="#F8FAFC" />
            <path d="M40 145H330M45 150V20" stroke="#64748B" strokeWidth="2" />
            <path d="M52 38 C115 52 188 85 310 137" fill="none" stroke="#2563EB" strokeWidth="3" />
            <path d="M52 135 C125 105 205 70 310 43" fill="none" stroke="#EA580C" strokeWidth="3" />
            <path d="M52 120 C120 95 190 82 245 91 C280 97 300 110 310 122" fill="none" stroke="#16A34A" strokeWidth="3" />
            <text x="245" y="142" fill="#64748B" fontSize="11">model complexity</text>
            <text x="53" y="31" fill="#2563EB" fontSize="11">bias</text>
            <text x="53" y="165" fill="#EA580C" fontSize="11">variance</text>
            <text x="178" y="78" fill="#16A34A" fontSize="11">total error</text>
          </svg>
        </div>
      </section>
    </main>
  );
}
