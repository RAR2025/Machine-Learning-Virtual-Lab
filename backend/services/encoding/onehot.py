from sklearn.preprocessing import OneHotEncoder

from backend.services.encoding.common import run_workflow


def run_one_hot_encoding(**kwargs):
    return run_workflow(
        "One-Hot Encoding",
        lambda categorical_cols: OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,
        ),
        **kwargs,
    )
