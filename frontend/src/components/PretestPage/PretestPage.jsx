import React, { useState } from 'react';
import './PretestPage.css';

const QUESTIONS = [
  {
    question: 'What is the primary goal of a classification algorithm?',
    options: [
      'To predict a continuous numerical value.',
      'To group unlabelled data into clusters.',
      'To assign categorical labels to new data points based on training data.',
      'To reduce the dimensionality of the dataset.'
    ],
    answer: 2
  },
  {
    question: 'Which of the following best describes a linear decision boundary in a 2D feature space?',
    options: [
      'A straight line separating different classes.',
      'A curved line that wraps around data points.',
      'A series of rectangular, axis-aligned boxes.',
      'A set of concentric circles.'
    ],
    answer: 0
  },
  {
    question: 'In the context of machine learning, what does "overfitting" mean?',
    options: [
      'The model performs well on training data but poorly on unseen test data.',
      'The model performs poorly on both training and test data.',
      'The model has generalized perfectly and ignores noise.',
      'The model is too simple to capture the underlying patterns.'
    ],
    answer: 0
  },
  {
    question: 'Which of these algorithms is known as a "lazy learner" because it defers building a model until a prediction is needed?',
    options: [
      'Decision Tree',
      'K-Nearest Neighbors (KNN)',
      'Support Vector Machine (SVM)',
      'Logistic Regression'
    ],
    answer: 1
  },
  {
    question: 'What does the Bias-Variance tradeoff primarily help us find?',
    options: [
      'The fastest algorithm for training a dataset.',
      'The sweet spot between model underfitting and overfitting.',
      'The minimum number of features required for training.',
      'The maximum limit of data points a model can handle.'
    ],
    answer: 1
  }
];

export default function PretestPage() {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [checkedAnswers, setCheckedAnswers] = useState({});

  const selectAnswer = (questionIndex, optionIndex) => {
    setSelectedAnswers((previous) => ({
      ...previous,
      [questionIndex]: optionIndex
    }));
    setCheckedAnswers((previous) => {
      const next = { ...previous };
      delete next[questionIndex];
      return next;
    });
  };

  const checkAnswer = (questionIndex) => {
    setCheckedAnswers((previous) => ({
      ...previous,
      [questionIndex]: true
    }));
  };

  return (
    <main className="pretest-page">
      <header className="pretest-header">
        <span className="pretest-eyebrow">KNOWLEDGE CHECK</span>
        <h1>Pre-test</h1>
        <p>Select one option for each question, then check your answer.</p>
      </header>

      <div className="pretest-list">
        {QUESTIONS.map((item, questionIndex) => {
          const selected = selectedAnswers[questionIndex];
          const checked = checkedAnswers[questionIndex];
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
                      checked && optionIndex === item.answer ? 'correct-option' : ''
                    } ${checked && selected === optionIndex && !isCorrect ? 'wrong-option' : ''}`}
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
              <div className="pretest-action-row">
                <button
                  className="btn btn-primary pretest-check-button"
                  type="button"
                  disabled={selected === undefined}
                  onClick={() => checkAnswer(questionIndex)}
                >
                  Check Answer
                </button>
                {checked && (
                  <p className={`pretest-feedback ${isCorrect ? 'correct' : 'wrong'}`}>
                    {isCorrect
                      ? 'Correct answer!'
                      : `Incorrect. The correct answer is ${String.fromCharCode(97 + item.answer)}) ${item.options[item.answer]}`}
                  </p>
                )}
              </div>
            </section>
          );
        })}
      </div>
    </main>
  );
}
