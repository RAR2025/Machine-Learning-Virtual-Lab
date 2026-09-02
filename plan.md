# Virtual ML Lab - Project Plan

## 1. Project Overview

The project is a **Virtual Machine Learning Laboratory** designed to allow students to perform ML experiments step by step while learning the theory behind each concept.

The system will not simply execute a complete ML pipeline automatically. Instead, the experiment will be divided into individual modules. After completing each module, the user will be able to view the relevant theory before proceeding to the next step.

The first experiment will focus on:

* Dataset analysis
* Classification / Regression detection
* Dataset cleaning
* ML algorithm selection
* Train/Test splitting
* Categorical encoding
* Model training
* Model evaluation
* Comparison of encoding techniques
* Theory for every major concept

---

# 2. Technology Stack

## Frontend

* React
* JavaScript
* HTML/CSS
* Chart/visualization library for metrics and confusion matrix

## Backend

* Python
* FastAPI

## Machine Learning

* Pandas
* NumPy
* Scikit-learn
* Category Encoders where required

## Dataset Source

Initially, only the **UCI Machine Learning Repository** will be supported through:

```python
from ucimlrepo import fetch_ucirepo
```

The user will provide Python code containing a UCI dataset ID.

Example:

```python
from ucimlrepo import fetch_ucirepo

# fetch dataset
bike_sharing = fetch_ucirepo(id=275)

# data (as pandas dataframes)
X = bike_sharing.data.features
y = bike_sharing.data.targets

# metadata
print(bike_sharing.metadata)

# variable information
print(bike_sharing.variables)
```

---

# 3. High-Level Architecture

```text
                         React Frontend
                              │
                              │ REST API
                              ↓
                         FastAPI Backend
                              │
                     Experiment Controller
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ↓                      ↓                      ↓
 Dataset Service       ML Experiment Services   Theory Content
       │                      │
       ↓                      ↓
  UCI Repository        ┌─────┴─────┐
                        │           │
                  Preprocessing   Modeling
                        │           │
                        └─────┬─────┘
                              ↓
                         Evaluation
                              │
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
                 Accuracy  Precision  Recall
                    │         │         │
                    └─────────┼─────────┘
                              ↓
                             F1
                              ↓
                     Confusion Matrix
                              │
                              ↓
                       React Frontend
```

---

# 4. Core Design Principle

The application must be **step-by-step**.

The user should not simply click one button and receive the final result.

The experiment should follow:

```text
Dataset Input
     ↓
1. Analyze Problem Type
     ↓
Theory
     ↓
2. Clean Dataset
     ↓
Theory
     ↓
3. Select ML Algorithm
     ↓
Theory
     ↓
4. Train/Test Split
     ↓
Theory
     ↓
5. Select Encoding Technique
     ↓
Theory
     ↓
6. Apply Encoding
     ↓
Theory
     ↓
7. Train Model
     ↓
Theory
     ↓
8. Evaluate Model
     ↓
Results
```

Each major step should have a corresponding theory section.

---

# 5. Module 1 - Problem Type Analyzer

## Purpose

Determine whether the selected dataset is primarily a:

* Classification problem
* Regression problem

The decision is based primarily on the target variable `y`.

## Input

```text
X
y
```

## Output

```text
Problem Type
Target Column
Target Datatype
Number of Unique Target Values
```

Example:

```json
{
    "problem_type": "Classification",
    "target": "income",
    "target_dtype": "object",
    "unique_values": 2
}
```

## Logic

### Categorical target

If the target is:

* Object
* Category
* Boolean

then it is treated as classification.

### Numeric target

If the target is numeric:

* Few unique values → likely classification
* Many unique values → likely regression

This is a heuristic rather than a mathematically guaranteed decision.

## Function

```python
detect_problem_type(y)
```

## Theory

The frontend should explain:

* What is a target variable?
* What is classification?
* What is regression?
* Difference between classification and regression
* Binary classification
* Multiclass classification
* Continuous target
* How target datatype helps identify the problem

---

# 6. Module 2 - Dataset Cleaning

## Purpose

Prepare the dataset before ML processing.

## Input

```text
X
y
```

## Operations

Initially:

1. Check missing values
2. Handle missing values
3. Check duplicate records
4. Remove duplicates where appropriate
5. Check datatype information
6. Separate numerical and categorical features

## Possible Functions

```python
check_missing_values(X)
handle_missing_values(X)
check_duplicates(X)
remove_duplicates(X)
identify_feature_types(X)
clean_dataset(X, y)
```

## Output

```text
Clean X
Clean y
Cleaning Report
```

Example:

```text
Rows Before Cleaning: 48842
Missing Values: 6465
Duplicates: 24
Rows After Cleaning: 48818
```

## Theory

Explain:

* What is data cleaning?
* Why data cleaning is required
* Missing values
* Duplicate data
* Invalid data
* Numerical features
* Categorical features
* Why poor-quality data affects ML models

---

# 7. Module 3 - ML Algorithm Selection

## Purpose

Allow the user to select an ML algorithm.

The system should display algorithms appropriate for the detected problem type.

## Initial Algorithms

### Classification

Initially:

```text
Random Forest Classifier
Logistic Regression
```

### Regression

Initially:

```text
Linear Regression
Random Forest Regressor
```

Important:

**Logistic Regression is a classification algorithm.**

It should not be presented as a regression model merely because its name contains "Regression".

## Function

```python
get_available_algorithms(problem_type)
```

and:

```python
get_model(problem_type, algorithm)
```

## Example UI

```text
Problem Type: Classification

Select Algorithm:

○ Random Forest Classifier
○ Logistic Regression
```

## Theory

For every algorithm, provide:

* What is the algorithm?
* How does it work?
* Advantages
* Disadvantages
* When should it be used?
* Important parameters
* Simple example

---

# 8. Module 4 - Train/Test Split

## Purpose

Divide the dataset into training and testing portions.

## Input

```text
X
y
```

## Output

```text
X_train
X_test
y_train
y_test
```

## Function

```python
split_data(X, y, test_size=0.2, random_state=42)
```

Internally:

```python
train_test_split(
    X,
    y,
    test_size=test_size,
    random_state=random_state
)
```

## User Controls

The frontend may eventually allow:

```text
Test Size:
[ 20% ]

Random State:
[ 42 ]
```

## Theory

Explain:

* Training data
* Testing data
* Why data is split
* Training vs testing
* Overfitting
* Generalization
* Test size
* Random state
* Data leakage

---

# 9. Module 5 - Model Service

## Purpose

Handle model creation and training.

The model service should not know anything about the frontend.

## Input

```text
Selected Algorithm
X_train
y_train
```

## Output

```text
Trained Model
```

## Functions

```python
create_model(problem_type, algorithm)
train_model(model, X_train, y_train)
```

Example:

```python
model = create_model(
    problem_type="Classification",
    algorithm="Random Forest"
)

model = train_model(
    model,
    X_train,
    y_train
)
```

---

# 10. Module 6 - Evaluation Service

## Purpose

Evaluate the trained model.

For classification experiments, the initial metrics will be:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix

## Input

```text
Trained Model
X_test
y_test
```

## Process

```text
Model
  ↓
Prediction
  ↓
Compare y_test with predictions
  ↓
Calculate metrics
```

## Output

Example:

```json
{
    "accuracy": 0.89,
    "precision": 0.87,
    "recall": 0.86,
    "f1": 0.86,
    "confusion_matrix": [
        [7000, 500],
        [700, 1500]
    ]
}
```

## Function

```python
evaluate_classification(
    model,
    X_test,
    y_test
)
```

## Metrics

### Accuracy

Measures the proportion of correctly classified samples.

### Precision

Measures how many predicted positive samples were actually positive.

### Recall

Measures how many actual positive samples were correctly identified.

### F1 Score

Harmonic mean of precision and recall.

### Confusion Matrix

Shows:

```text
                 Predicted
               Negative Positive

Actual Negative    TN       FP

Actual Positive    FN       TP
```

## Theory

Each metric should have:

* Definition
* Formula
* Meaning
* Example
* When it is useful
* Limitations

---

# 11. Module 7 - Encoding Selection

## Purpose

Allow the user to select the categorical encoding technique.

Initial encoding techniques:

1. One-Hot Encoding
2. Target Encoding
3. Leave-One-Out Encoding
4. Embedded Encoding

## UI

```text
Select Encoding Technique:

○ One-Hot Encoding
○ Target Encoding
○ Leave-One-Out Encoding
○ Embedded Encoding
```

The user should be able to run the experiment using one technique at a time.

Eventually, the UI can also provide:

```text
[Run All Techniques]
```

to compare their results.

## Theory

Each technique should have its own theory page/panel.

---

# 12. Module 8 - Encoding Functions

Each encoding technique should be implemented as a separate module.

Structure:

```text
encoders/
│
├── one_hot.py
├── target.py
├── leave_one_out.py
└── embedded.py
```

Each encoder should have a consistent interface.

Example:

```python
encode(
    X_train,
    X_test,
    y_train
)
```

Output:

```text
X_train_encoded
X_test_encoded
```

The exact implementation may differ between encoding techniques.

---

# 13. One-Hot Encoding

## Purpose

Convert categorical values into binary columns.

Example:

```text
Color

Red
Blue
Green
```

becomes:

```text
Color_Red
Color_Blue
Color_Green
```

## Theory

Explain:

* What is categorical data?
* Why categorical data needs encoding
* How One-Hot Encoding works
* Dummy variables
* Advantages
* Disadvantages
* Curse of dimensionality

---

# 14. Target Encoding

## Purpose

Replace categories with a statistic calculated from the target.

Example:

```text
City → average target value
```

Important:

Target encoding must be implemented carefully to avoid **target leakage**.

The encoder should be fitted using training data only.

## Theory

Explain:

* Target encoding
* Category-to-target relationship
* Mean encoding
* Target leakage
* Training vs testing behavior

---

# 15. Leave-One-Out Encoding

## Purpose

A variation of target encoding where the current observation is excluded when calculating its encoded value.

This helps reduce certain forms of target leakage compared with naive target encoding.

## Theory

Explain:

* Leave-One-Out concept
* Difference from target encoding
* Leakage
* Advantages
* Disadvantages

---

# 16. Embedded Encoding

## Purpose

Represent categories through learned representations during model training.

The exact implementation should be decided based on the selected model and experiment requirements.

If the experiment means neural-network-style embeddings, a separate implementation using an appropriate neural model may be required.

## Theory

Explain:

* What embeddings are
* Dense vector representation
* Learned representations
* Difference between one-hot and embeddings
* Advantages
* Disadvantages

---

# 17. Correct Experiment Order

The encoding experiment must avoid data leakage.

The recommended flow is:

```text
Raw Dataset
     ↓
Data Cleaning
     ↓
Train/Test Split
     ↓
Separate categorical/numerical features
     ↓
Fit Encoder ONLY on Training Data
     ↓
Transform X_train
     ↓
Transform X_test
     ↓
Train Model
     ↓
Predict X_test
     ↓
Calculate Metrics
```

Do NOT do:

```text
Raw Dataset
     ↓
Encode entire dataset
     ↓
Train/Test Split
```

for target-based encoders.

That can allow information from the test set to influence the training process.

---

# 18. Module 9 - Final Experiment Runner

The experiment runner coordinates the complete workflow.

## Function

```python
run_experiment(
    dataset,
    algorithm,
    encoding
)
```

## Workflow

```text
1. Load Dataset
        ↓
2. Analyze Target
        ↓
3. Detect Classification/Regression
        ↓
4. Clean Dataset
        ↓
5. Select Algorithm
        ↓
6. Train/Test Split
        ↓
7. Select Encoding
        ↓
8. Fit Encoder on Training Data
        ↓
9. Transform Train/Test Data
        ↓
10. Create Model
        ↓
11. Train Model
        ↓
12. Generate Predictions
        ↓
13. Calculate Metrics
        ↓
14. Return Results
```

---

# 19. Comparison of Encoding Techniques

The system should eventually allow the user to compare all encoding techniques.

Example result:

| Encoding      | Accuracy | Precision | Recall |   F1 |
| ------------- | -------: | --------: | -----: | ---: |
| One-Hot       |     0.89 |      0.87 |   0.86 | 0.86 |
| Target        |     0.90 |      0.88 |   0.87 | 0.87 |
| Leave-One-Out |     0.90 |      0.88 |   0.87 | 0.87 |
| Embedded      |     0.91 |      0.89 |   0.88 | 0.88 |

The system should not automatically claim that the highest accuracy is always the best technique.

The user should be able to understand all metrics.

---

# 20. Confusion Matrix UI

For classification experiments, display the confusion matrix visually.

Example:

```text
                 Predicted
                0        1

Actual 0      7000     500

Actual 1       700    1500
```

The frontend should convert the backend matrix into a visual heatmap.

The confusion matrix should be available separately for each encoding technique.

---

# 21. Theory System

Theory is a core part of the Virtual Lab.

Every experimental step should have an associated theory section.

Example:

```text
Step 1
Analyze Problem Type

[ Theory ]

What is Classification?
What is Regression?
How are they different?

[ Continue ]
```

Then:

```text
Step 2
Data Cleaning

[ Theory ]

What is Data Cleaning?
Why is it necessary?

[ Continue ]
```

The theory should not be mixed into the ML implementation.

Recommended backend structure:

```text
theory/
│
├── problem_type.md
├── data_cleaning.md
├── train_test_split.md
├── random_forest.md
├── logistic_regression.md
├── one_hot.md
├── target_encoding.md
├── leave_one_out.md
├── embedded_encoding.md
├── accuracy.md
├── precision.md
├── recall.md
├── f1_score.md
└── confusion_matrix.md
```

---

# 22. Frontend Structure

```text
frontend/
│
├── src/
│
├── pages/
│   ├── Home.jsx
│   └── Experiment1.jsx
│
├── components/
│   ├── ExperimentStepper.jsx
│   ├── DatasetInput.jsx
│   ├── DatasetSummary.jsx
│   ├── CleaningPanel.jsx
│   ├── AlgorithmSelector.jsx
│   ├── EncodingSelector.jsx
│   ├── TheoryPanel.jsx
│   ├── MetricCard.jsx
│   ├── ResultsTable.jsx
│   └── ConfusionMatrix.jsx
│
└── services/
    └── api.js
```

---

# 23. Frontend Experiment Flow

The experiment should look approximately like:

```text
┌─────────────────────────────────────────────┐
│              Experiment 1                   │
├─────────────────────────────────────────────┤
│                                             │
│  ① Dataset Analysis       ✓                 │
│                                             │
│  ② Data Cleaning          ✓                 │
│                                             │
│  ③ Algorithm Selection                      │
│                                             │
│  ④ Train/Test Split                         │
│                                             │
│  ⑤ Encoding Selection                       │
│                                             │
│  ⑥ Model Training                           │
│                                             │
│  ⑦ Evaluation                               │
│                                             │
│  ⑧ Results                                  │
│                                             │
└─────────────────────────────────────────────┘
```

Each completed step should become available for the next step.

---

# 24. Backend Project Structure

Recommended structure:

```text
backend/
│
├── main.py
│
├── api/
│   ├── dataset.py
│   ├── experiment.py
│   └── theory.py
│
├── services/
│   ├── dataset_service.py
│   ├── problem_analyzer.py
│   ├── data_cleaner.py
│   ├── algorithm_selector.py
│   ├── data_splitter.py
│   ├── model_service.py
│   ├── evaluation_service.py
│   ├── encoding_selector.py
│   └── experiment_runner.py
│
├── encoders/
│   ├── one_hot.py
│   ├── target.py
│   ├── leave_one_out.py
│   └── embedded.py
│
├── theory/
│   ├── problem_type.md
│   ├── data_cleaning.md
│   ├── train_test_split.md
│   ├── algorithms.md
│   ├── encodings.md
│   └── metrics.md
│
└── schemas/
    └── experiment.py
```

---

# 25. API Responsibilities

## Dataset API

Example:

```text
POST /dataset/analyze
```

Input:

```json
{
    "code": "from ucimlrepo import fetch_ucirepo..."
}
```

Output:

```json
{
    "dataset_id": 275,
    "target": "cnt",
    "problem_type": "Regression"
}
```

---

## Cleaning API

```text
POST /experiment/clean
```

Returns:

```json
{
    "rows_before": 17379,
    "rows_after": 17379,
    "missing_values": 0,
    "duplicates": 0
}
```

---

## Algorithm API

```text
GET /algorithms/{problem_type}
```

Example:

```json
{
    "problem_type": "Classification",
    "algorithms": [
        "Random Forest Classifier",
        "Logistic Regression"
    ]
}
```

---

## Encoding API

```text
GET /encodings/{problem_type}
```

Returns:

```json
{
    "encodings": [
        "One-Hot",
        "Target",
        "Leave-One-Out",
        "Embedded"
    ]
}
```

---

## Experiment API

```text
POST /experiment/run
```

Example:

```json
{
    "algorithm": "Random Forest Classifier",
    "encoding": "One-Hot"
}
```

Returns:

```json
{
    "accuracy": 0.89,
    "precision": 0.87,
    "recall": 0.86,
    "f1": 0.86,
    "confusion_matrix": [
        [7000, 500],
        [700, 1500]
    ]
}
```

---

# 26. Experiment State

The backend should maintain a clear experiment state.

Conceptually:

```text
Experiment
│
├── dataset
├── X
├── y
├── problem_type
├── target
├── cleaning_status
├── selected_algorithm
├── X_train
├── X_test
├── y_train
├── y_test
├── selected_encoding
├── encoded_X_train
├── encoded_X_test
├── trained_model
└── evaluation_results
```

The frontend should display the state, while the backend owns the actual ML state and processing.

---

# 27. Important ML Rules

## Rule 1 - Do not leak test data

Target-based encoding must be fitted only using training data.

## Rule 2 - Keep the model constant during encoding comparison

When comparing encoding techniques:

```text
Same Dataset
Same Cleaning
Same Train/Test Split
Same Model
Different Encoding
```

This makes the comparison meaningful.

## Rule 3 - Use the same random state

For fair comparisons:

```python
random_state=42
```

should initially be kept constant.

## Rule 4 - Do not judge using accuracy alone

The application should display:

* Accuracy
* Precision
* Recall
* F1
* Confusion Matrix

---

# 28. Current Prototype

A Gradio prototype has already been created for the first functionality.

Current prototype:

```text
User enters UCI Python code
        ↓
Extract UCI dataset ID
        ↓
fetch_ucirepo()
        ↓
Extract X and y
        ↓
Analyze target
        ↓
Classification / Regression
```

This prototype should be retained as a proof of concept.

The ML logic should then be moved into reusable backend services.

---

# 29. Development Strategy

Development should happen incrementally.

## Phase 0 - Prototype

Completed functionality:

```text
UCI Code Input
     ↓
Dataset ID Extraction
     ↓
Dataset Fetching
     ↓
Target Detection
     ↓
Classification / Regression
```

Current technology:

```text
Python + Gradio
```

---

# 30. Phase 1 - Backend Foundation

Build:

```text
FastAPI
    ↓
Dataset Service
    ↓
Problem Analyzer
```

Move the existing problem detection logic into the backend.

Test the API independently.

---

# 31. Phase 2 - Cleaning

Implement:

```text
Missing Value Detection
Missing Value Handling
Duplicate Detection
Duplicate Handling
Feature Type Detection
```

Add theory content.

---

# 32. Phase 3 - Algorithm Selection

Implement:

```text
Classification
    ├── Random Forest Classifier
    └── Logistic Regression

Regression
    ├── Linear Regression
    └── Random Forest Regressor
```

Allow user selection.

---

# 33. Phase 4 - Train/Test Split

Implement:

```text
train_test_split()
```

with configurable:

```text
test_size
random_state
```

---

# 34. Phase 5 - Encoding

Implement independently:

```text
One-Hot
Target
Leave-One-Out
Embedded
```

Each encoder must be independently testable.

---

# 35. Phase 6 - Model Training and Evaluation

Implement:

```text
Model Creation
     ↓
Model Training
     ↓
Prediction
     ↓
Accuracy
     ↓
Precision
     ↓
Recall
     ↓
F1
     ↓
Confusion Matrix
```

---

# 36. Phase 7 - Experiment Runner

Combine all modules into:

```text
run_experiment()
```

The experiment runner should orchestrate existing services rather than contain the implementation of every operation itself.

---

# 37. Phase 8 - React Frontend

Build:

```text
Home
   ↓
Experiment 1
   ↓
Dataset Input
   ↓
Problem Analysis
   ↓
Cleaning
   ↓
Algorithm
   ↓
Train/Test Split
   ↓
Encoding
   ↓
Training
   ↓
Evaluation
   ↓
Results
```

---

# 38. Phase 9 - Theory Integration

Attach theory to each step.

The user should be able to understand the concept before executing the operation.

The theory system should include:

```text
Problem Type
Data Cleaning
Train/Test Split
Classification
Regression
Random Forest
Logistic Regression
Linear Regression
One-Hot Encoding
Target Encoding
Leave-One-Out Encoding
Embedded Encoding
Accuracy
Precision
Recall
F1
Confusion Matrix
Data Leakage
```

---

# 39. Final User Experience

The final application should feel like a **Virtual ML Laboratory**, not an AutoML black box.

The user should:

```text
1. Enter dataset
        ↓
2. Understand problem type
        ↓
3. Learn cleaning
        ↓
4. Clean dataset
        ↓
5. Learn algorithms
        ↓
6. Select algorithm
        ↓
7. Learn train/test split
        ↓
8. Split dataset
        ↓
9. Learn encoding
        ↓
10. Select encoding
        ↓
11. Apply encoding
        ↓
12. Train model
        ↓
13. Learn evaluation metrics
        ↓
14. Evaluate
        ↓
15. View metrics
        ↓
16. View confusion matrix
        ↓
17. Compare encoding techniques
```

---

# 40. Final Architecture

```text
                           VIRTUAL ML LAB
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
             FRONTEND                          BACKEND
              React                            FastAPI
                 │                                 │
                 │                          ┌──────┴──────┐
                 │                          │             │
                 │                       Theory      Experiment
                 │                          │             │
                 │                          │       ┌─────┴─────┐
                 │                          │       │           │
                 │                          │    Dataset       ML
                 │                          │       │           │
                 │                          │       ↓           ↓
                 │                          │   Analyzer    Preprocessing
                 │                          │                   │
                 │                          │          ┌────────┴────────┐
                 │                          │          │                 │
                 │                          │       Cleaning          Encoding
                 │                          │                            │
                 │                          │                            ↓
                 │                          │                       Train/Test
                 │                          │                            │
                 │                          │                            ↓
                 │                          │                         Model
                 │                          │                            │
                 │                          │                            ↓
                 │                          │                       Evaluation
                 │                          │                            │
                 │                          │                ┌───────────┼──────────┐
                 │                          │                ↓           ↓          ↓
                 │                          │            Accuracy    Precision    Recall
                 │                          │                │           │          │
                 │                          │                └───────────┼──────────┘
                 │                          │                            ↓
                 │                          │                           F1
                 │                          │                            ↓
                 │                          │                   Confusion Matrix
                 │                          │
                 └──────────────────────────┴─────────────────────────────
```

# 41. Core Principle

The project should prioritize **educational transparency over automation**.

The system should show the student:

```text
WHAT
↓
WHY
↓
HOW
↓
EXECUTE
↓
RESULT
```

for every major ML operation.

The goal is not simply:

```text
Dataset → Accuracy
```

The goal is:

```text
Dataset
   ↓
Understand the problem
   ↓
Understand the preprocessing
   ↓
Understand the algorithm
   ↓
Understand the encoding
   ↓
Understand the evaluation
   ↓
Perform the experiment
   ↓
Interpret the results
```

This structure should allow additional ML experiments to be added later without rewriting the core architecture.
