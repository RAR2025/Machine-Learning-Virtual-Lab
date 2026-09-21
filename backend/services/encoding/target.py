import category_encoders as ce

from backend.services.encoding.common import run_workflow


def run_target_encoding(**kwargs):
    return run_workflow(
        "Target Encoding",
        lambda categorical_cols: ce.TargetEncoder(cols=categorical_cols),
        **kwargs,
    )
