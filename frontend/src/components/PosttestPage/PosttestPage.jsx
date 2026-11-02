import React, { useState } from 'react';
import '../PretestPage/PretestPage.css';

const QUESTIONS = [
  {
    question: 'In the KNN algorithm, what happens to the decision boundary when you decrease the value of K to 1?',
    options: [
      'The boundary becomes a perfectly straight line.',
      'The boundary becomes highly jagged and wraps tightly around individual data points.',
      'The boundary becomes smoother and completely ignores outliers.',
      'The algorithm fails to draw any boundary.'
    ],
    answer: 1
  },
  {
    question: 'When using a Support Vector Machine (SVM) on a non-linearly separable dataset like "Concentric Circles", which kernel is required to successfully separate the classes?',
    options: [
      'Linear Kernel',
      'Manhattan Kernel',
      'RBF (Radial Basis Function) Kernel',
      'Orthogonal Kernel'
    ],
    answer: 2
  },
  {
    question: 'Why do the decision boundaries of a standard Decision Tree always look like a series of rectangles or staircases in a 2D plot?',
    options: [
      'Because it calculates the Euclidean distance between points.',
      'Because it aims to maximize the margin between support vectors.',
      'Because it randomly partitions the feature space into grids.',
      'Because it makes orthogonal splits (perpendicular to the feature axes) one variable at a time.'
    ],
    answer: 3
  },
  {
    question: 'What is the effect of setting a very high regularization parameter (C) in a Support Vector Machine?',
    options: [
      'It creates a soft margin, allowing many misclassifications for a smoother boundary.',
      'It heavily penalizes misclassifications, forcing a hard margin that bends to capture every point.',
      'It transforms the dataset into a lower dimension.',
      'It automatically changes the kernel from RBF to Linear.'
    ],
    answer: 1
  },
  {
    question: 'If you increase the tree depth limit in a Decision Tree to its absolute maximum, how does this affect the Bias-Variance tradeoff?',
    options: [
      'Increases bias, decreases variance (Underfitting).',
      'Decreases bias, increases variance (Overfitting).',
      'Decreases both bias and variance.',
      'Increases both bias and variance.'
    ],
    answer: 1
  }
];

export default function PosttestPage() {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [isChecked, setIsChecked] = useState(false);

  const selectAnswer = (questionIndex, optionIndex) => {
    setSelectedAnswers((previous) => ({
      ...previous,
      [questionIndex]: optionIndex
    }));
    setIsChecked(false);
  };

  return (
    <main className="pretest-page">
      <header className="pretest-header">
        <span className="pretest-eyebrow">KNOWLEDGE CHECK</span>
        <h1>Post-test</h1>
        <p>Review what you learned by selecting one option for each question.</p>
      </header>

      <div className="pretest-list">
        {QUESTIONS.map((item, questionIndex) => {
          const selected = selectedAnswers[questionIndex];
          const isCorrect = selected === item.answer;

          return (
            <section className="pretest-question" key={item.question}>
              <h2>
                <span>Q{questionIndex + 1}</span>
                {item.question}
              </h2>
              <div className="pretest-options">
                {item.options.map((option, optionIndex) => (
                  <label
                    className={`pretest-option ${selected === optionIndex ? 'selected' : ''} ${
                      isChecked && optionIndex === item.answer ? 'correct-option' : ''
                    } ${isChecked && selected === optionIndex && !isCorrect ? 'wrong-option' : ''}`}
                    key={option}
                  >
                    <input
                      type="checkbox"
                      checked={selected === optionIndex}
                      onChange={() => selectAnswer(questionIndex, optionIndex)}
                    />
                    <span className="option-marker">{String.fromCharCode(97 + optionIndex)})</span>
                    <span>{option}</span>
                  </label>
                ))}
              </div>
              {isChecked && (
                <div className="pretest-action-row">
                  <p className={`pretest-feedback ${isCorrect ? 'correct' : 'wrong'}`}>
                    {isCorrect
                      ? 'Correct answer!'
                      : `Incorrect. The correct answer is ${String.fromCharCode(97 + item.answer)}) ${item.options[item.answer]}`}
                  </p>
                </div>
              )}
            </section>
          );
        })}
      </div>
      <button
        className="btn btn-primary pretest-submit-button"
        type="button"
        disabled={Object.keys(selectedAnswers).length !== QUESTIONS.length}
        onClick={() => setIsChecked(true)}
      >
        Check Answers
      </button>
    </main>
  );
}
