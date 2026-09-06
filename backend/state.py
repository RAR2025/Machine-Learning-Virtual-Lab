import pandas as pd

X_data = None
y_data = None
dataset_id = None
problem_type = None
appropriate_models = []
selected_model = None


def reset():
    global X_data, y_data, dataset_id, problem_type, appropriate_models, selected_model

    X_data = None
    y_data = None
    dataset_id = None
    problem_type = None
    appropriate_models = []
    selected_model = None


def y_series():
    if y_data is None:
        return None

    if isinstance(y_data, pd.DataFrame):
        return y_data.iloc[:, 0]

    return y_data