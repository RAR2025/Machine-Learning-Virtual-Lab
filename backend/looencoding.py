import category_encoders as ce

from backend.encodingcommon import run_workflow


def run_loo_encoding():
    return run_workflow(
        "Leave-One-Out Encoding",
        lambda categorical_cols: ce.LeaveOneOutEncoder(cols=categorical_cols),
    )