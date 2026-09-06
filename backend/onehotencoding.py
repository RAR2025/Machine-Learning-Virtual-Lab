from sklearn.preprocessing import OneHotEncoder

from backend.encodingcommon import run_workflow


def run_one_hot_encoding():
    return run_workflow(
        "One-Hot Encoding",
        lambda categorical_cols: OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,
        ),
    )