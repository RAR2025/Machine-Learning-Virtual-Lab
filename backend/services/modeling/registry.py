from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier

CLASSIFIERS = {
    "logistic_regression": lambda: LogisticRegression(
        max_iter=1000, class_weight="balanced"
    ),
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=200, random_state=42, n_jobs=-1, class_weight="balanced"
    ),
    "decision_tree": lambda: DecisionTreeClassifier(
        random_state=42, class_weight="balanced"
    ),
    # Legacy display names -> same factories (backward compat with old state).
    "LogisticRegression": lambda: LogisticRegression(
        max_iter=1000, class_weight="balanced"
    ),
}

REGRESSORS = {
    "linear_regression": lambda: LinearRegression(),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=200, random_state=42, n_jobs=-1
    ),
    # Legacy display name.
    "LinearRegression": lambda: LinearRegression(),
}

MODEL_INFO = {
    "logistic_regression": {
        "key": "logistic_regression",
        "name": "Logistic Regression",
        "problem": "Classification",
        "description": "Linear classifier that maps a weighted sum of features through the sigmoid (or softmax) into class probabilities.",
        "intuition": "Learns weights w,b so that p(y=1|x)=sigmoid(w.x+b). Threshold at 0.5. Training maximises likelihood via gradient descent.",
        "advantages": [
            "Fast, interpretable coefficients show feature influence.",
            "Probabilistic outputs enable ROC-AUC and threshold tuning.",
            "Well suited for demonstrating encoding effects (linear boundary).",
        ],
        "limitations": [
            "Linear boundary only; struggles with strong non-linearity.",
            "Sensitive to unscaled features and severe multicollinearity.",
        ],
        "use_cases": "Binary classification baseline, encoding-effect demonstrations.",
        "default": True,
    },
    "random_forest": {
        "key": "random_forest",
        "name": "Random Forest",
        "problem": "Classification/Regression",
        "description": "Ensemble of decision trees trained on bootstrap samples with random feature subsets; votes (or averages) predictions.",
        "intuition": "Each tree overfits differently; averaging reduces variance while keeping non-linear capacity.",
        "advantages": [
            "Handles non-linearity and mixed feature types robustly.",
            "Resistant to overfitting relative to single trees.",
        ],
        "limitations": ["Less interpretable than linear models.", "Slower to train on large data."],
        "use_cases": "Strong general-purpose baseline when linearity is insufficient.",
        "default": False,
    },
    "decision_tree": {
        "key": "decision_tree",
        "name": "Decision Tree Classifier",
        "problem": "Classification",
        "description": "Recursively splits features by impurity (gini/entropy) to form an interpretable tree.",
        "intuition": "Axis-aligned partitions; each leaf predicts the majority class of its region.",
        "advantages": ["Highly interpretable.", "No scaling needed."],
        "limitations": ["Prone to overfitting without pruning.", "Unstable to small data changes."],
        "use_cases": "Teaching splits/impurity and Visual rule extraction.",
        "default": False,
    },
    "linear_regression": {
        "key": "linear_regression",
        "name": "Linear Regression",
        "problem": "Regression",
        "description": "Models y as a linear combination of features fitted by Ordinary Least Squares.",
        "intuition": "Closed-form w=(X'X)^-1 X'y minimising squared error.",
        "advantages": ["Extremely fast and interpretable.", "Great baseline."],
        "limitations": ["Linear assumption; sensitive to outliers."],
        "use_cases": "Regression baseline and encoding-effect demonstrations.",
        "default": True,
    },
}

_CANONICAL = {
    "logisticregression": "logistic_regression",
    "logistic_regression": "logistic_regression",
    "randomforestclassifier": "random_forest",
    "random_forest_classifier": "random_forest",
    "randomforest": "random_forest",
    "random_forest": "random_forest",
    "decisiontree": "decision_tree",
    "decision_tree": "decision_tree",
    "decisiontreeclassifier": "decision_tree",
    "linearregression": "linear_regression",
    "linear_regression": "linear_regression",
    "randomforestregressor": "random_forest",
}


def canonical_key(name: str | None, problem_type: str) -> str:
    if not name:
        return "logistic_regression" if problem_type == "Classification" else "linear_regression"
    n = str(name).strip().lower().replace(" ", "_").replace("-", "_")
    if n in CLASSIFIERS or n in REGRESSORS:
        # disambiguate shared "random_forest" by problem type
        if n == "random_forest":
            return "random_forest"
        return n
    return _CANONICAL.get(n, n)


# Experiment scope: exactly one model per problem type.
ALLOWED_MODELS = {
    "Classification": ("logistic_regression",),
    "Regression": ("linear_regression",),
}


def resolve_model(problem_type, model_name=None):
    key = canonical_key(model_name, problem_type)
    if problem_type == "Classification":
        registry = CLASSIFIERS
        default = "logistic_regression"
    elif problem_type == "Regression":
        registry = REGRESSORS
        default = "linear_regression"
    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")
    name = key or default
    if name not in ALLOWED_MODELS[problem_type]:
        raise ValueError(
            f"Model '{model_name}' is not supported in this experiment. "
            f"Use '{default}' for {problem_type}."
        )
    # allow legacy "LogisticRegression"/"LinearRegression" passthrough
    if name not in registry and model_name in registry:
        return registry[model_name]()
    return registry[name]()


def get_model_names(problem_type):
    # Keep legacy display names for old callers.
    if problem_type == "Classification":
        return ["LogisticRegression"]
    if problem_type == "Regression":
        return ["LinearRegression"]
    return []


def get_available_models(problem_type):
    """Single supported model per problem type for the Model Selection UI."""
    keys = list(ALLOWED_MODELS.get(problem_type, ()))
    out = []
    for k in keys:
        info = dict(MODEL_INFO.get(k, {}))
        info.setdefault("key", k)
        out.append(info)
    return out
