import React from 'react';
import './ProcedurePage.css';

const STEPS = [
  {
    number: '01',
    title: 'Choose an algorithm',
    text: 'Use the left panel in the Simulation tab to select KNN, SVM, or Decision Tree. The available controls update for the selected algorithm.'
  },
  {
    number: '02',
    title: 'Load or create a dataset',
    text: 'Choose a starter preset such as Two Moons, Concentric Circles, Linearly Separable, or XOR. You can also draw Class A and Class B points directly on the canvas.'
  },
  {
    number: '03',
    title: 'Adjust hyperparameters',
    text: 'Change K for KNN, the kernel, C, or gamma for SVM, and tree depth for Decision Trees. Observe how each setting changes model complexity.'
  },
  {
    number: '04',
    title: 'Fit the model',
    text: 'Keep Auto-Train enabled for live updates, or click Fit Model after making changes. Clear removes the current points so you can begin a new experiment.'
  },
  {
    number: '05',
    title: 'Interpret the decision boundary',
    text: 'Observe which regions are assigned to each class. Compare smooth, jagged, curved, or axis-aligned boundaries and relate them to the selected algorithm.'
  },
  {
    number: '06',
    title: 'Compare performance',
    text: 'Use the metrics and confusion matrix on the right to compare accuracy, precision, recall, F1-score, and the bias-variance behavior of different settings.'
  }
];

export default function ProcedurePage() {
  return (
    <main className="procedure-page">
      <header className="procedure-header">
        <span className="procedure-eyebrow">EXPERIMENT WORKFLOW</span>
        <h1>Procedure</h1>
        <p>Follow these steps to conduct an interactive classification decision-boundary experiment.</p>
      </header>

      <section className="procedure-card">
        {STEPS.map((step) => (
          <article className="procedure-step" key={step.number}>
            <span className="procedure-step-number">{step.number}</span>
            <div>
              <h2>{step.title}</h2>
              <p>{step.text}</p>
            </div>
          </article>
        ))}
      </section>

      <aside className="procedure-note">
        <strong>Suggested investigation:</strong> Compare KNN with K = 1 and a larger K on Two Moons, then compare Linear and RBF SVM on Concentric Circles. Finally, increase Decision Tree depth and observe the transition from underfitting to overfitting.
      </aside>
    </main>
  );
}
