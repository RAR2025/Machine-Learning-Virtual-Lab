import category_encoders as ce

from backend.services.encoding.common import run_workflow


def run_loo_encoding(**kwargs):
    return run_workflow(
        "Leave-One-Out Encoding",
        lambda categorical_cols: ce.LeaveOneOutEncoder(cols=categorical_cols),
        **kwargs,
    )
