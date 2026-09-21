"""Train/test splitting with stratification for classification.

Splits are materialised as index arrays and stored on the experiment so all
encoders in a "run all" comparison share exactly the same rows.
"""
import numpy as np
from sklearn.model_selection import train_test_split


def make_split(y, test_size=0.2, random_state=42, problem_type="Classification", notes=None):
    notes = notes if notes is not None else []
    y_arr = np.asarray(y)
    stratify = None
    stratified = False
    if problem_type == "Classification":
        try:
            _, counts = np.unique(y_arr, return_counts=True)
            if len(counts) >= 2 and counts.min() >= 2:
                stratify = y_arr
                stratified = True
        except Exception:
            stratify = None
    n = len(y_arr)
    idx = np.arange(n)
    try:
        train_idx, test_idx = train_test_split(
            idx, test_size=test_size, random_state=random_state,
            stratify=stratify,
        )
    except ValueError as e:
        if stratify is not None:
            notes.append(
                "Stratified split was not possible (a class has too few "
                f"samples); fell back to unstratified split. ({e})"
            )
            train_idx, test_idx = train_test_split(
                idx, test_size=test_size, random_state=random_state
            )
        else:
            raise
        stratified = False
    else:
        if stratify is None and problem_type == "Classification":
            notes.append("Unstratified split used (stratification not possible).")
    return {
        "train_idx": [int(i) for i in train_idx],
        "test_idx": [int(i) for i in test_idx],
        "train_samples": int(len(train_idx)),
        "test_samples": int(len(test_idx)),
        "test_size": float(test_size),
        "random_state": int(random_state),
        "stratified": bool(stratified),
    }
