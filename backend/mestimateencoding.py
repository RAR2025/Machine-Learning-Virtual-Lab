import category_encoders as ce

from backend.encodingcommon import run_workflow


def run_m_estimate_encoding():
    return run_workflow(
        "M-Estimate Encoding",
        lambda categorical_cols: ce.MEstimateEncoder(cols=categorical_cols),
    )