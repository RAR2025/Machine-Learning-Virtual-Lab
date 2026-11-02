import React from 'react';
import './ConclusionPage.css';

export default function ConclusionPage() {
  return (
    <main className="conclusion-page">
      <section className="conclusion-card">
        <span className="conclusion-eyebrow">EXPERIMENT SUMMARY</span>
        <h1>Conclusion</h1>
        <p>
          This virtual laboratory successfully demonstrates that classification
          algorithms utilize fundamentally distinct mathematical approaches to
          partition feature space. Through real-time interactive visualization,
          the lab confirms that K-Nearest Neighbors relies on local data
          proximity, Support Vector Machines maximize class margins using
          versatile kernels, and Decision Trees build boundaries strictly through
          axis-aligned feature splits.
        </p>
        <p>
          Furthermore, by dynamically tweaking hyperparameters such as{' '}
          <strong>K</strong>, <strong>C</strong>, <strong>γ</strong>, and tree
          depth, the experiment practically illustrates the Bias-Variance
          tradeoff—showing exactly how models transition from rigid underfitting
          (high bias) to complex, noise-capturing overfitting (high variance)
          based on user-defined constraints.
        </p>
      </section>
    </main>
  );
}
