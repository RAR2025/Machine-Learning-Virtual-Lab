from sklearn.linear_model import LogisticRegression, LinearRegression

CLASSIFIERS = {
    "LogisticRegression": lambda: LogisticRegression(max_iter=1000),
}

REGRESSORS = {
    "LinearRegression": lambda: LinearRegression(),
}


def resolve_model(problem_type, model_name=None):
    if problem_type == "Classification":
        registry = CLASSIFIERS
        default = "LogisticRegression"
    elif problem_type == "Regression":
        registry = REGRESSORS
        default = "LinearRegression"
    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")

    name = model_name or default

    if name not in registry:
        raise ValueError(
            f"Model '{name}' is not a valid appropriate model for {problem_type}."
        )

    return registry[name]()


def get_model_names(problem_type):
    if problem_type == "Classification":
        return list(CLASSIFIERS)
    if problem_type == "Regression":
        return list(REGRESSORS)
    return []