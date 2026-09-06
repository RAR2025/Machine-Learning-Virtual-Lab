import category_encoders as ce

from backend.encodingcommon import run_workflow


def run_target_encoding():
    return run_workflow(
        "Target Encoding",
        lambda categorical_cols: ce.TargetEncoder(cols=categorical_cols),
    )