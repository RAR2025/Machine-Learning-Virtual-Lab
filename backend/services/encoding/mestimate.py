"""Optional legacy encoder (kept for backward compat, hidden from primary UI)."""
import category_encoders as ce

from backend.services.encoding.common import run_workflow


def run_m_estimate_encoding(**kwargs):
    return run_workflow(
        "M-Estimate Encoding",
        lambda categorical_cols: ce.MEstimateEncoder(cols=categorical_cols),
        **kwargs,
    )
