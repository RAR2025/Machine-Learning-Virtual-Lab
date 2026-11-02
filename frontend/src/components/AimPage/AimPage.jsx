import React from 'react';
import './AimPage.css';

export default function AimPage() {
  return (
    <main className="aim-page">
      <section className="aim-card">
        <span className="aim-eyebrow">VIRTUAL LAB OBJECTIVE</span>
        <h1>Aim</h1>
        <p>
          To design and implement a single-screen real-time Machine Learning Virtual Laboratory for rendering 2D decision boundaries of KNN, SVM, and Decision Tree algorithms on custom and preset datasets (Two Moons, Concentric Circles, XOR), enabling hands-on exploration of hyperparameter tuning and the Bias-Variance tradeoff.
        </p>
      </section>
    </main>
  );
}
