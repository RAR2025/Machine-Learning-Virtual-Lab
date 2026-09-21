import os
import re

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from backend.core import state
from backend.core.config import PROJECT_ROOT
from backend.services.modeling.registry import resolve_model


def _safe_filename(encoding_name, experiment_id=None):
    """Sanitise the encoding name so it is safe as a file name."""
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", encoding_name).strip("_")
    exp = re.sub(r"[^A-Za-z0-9_-]+", "_", str(experiment_id or "default")).strip("_")
    return f"confusion_matrix_{exp}_{safe or 'model'}.png"


def _unique_labels(y_test):
    try:
        return y_test.unique().tolist()
    except Exception:
        return sorted(set(list(y_test)))


def evaluate_model(model=None, X_train=None, X_test=None, y_train=None, y_test=None,
                   encoding_name="Model", experiment_id=None):
    if model is None:
        model = resolve_model("Classification", state.selected_model)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    classes = sorted(_unique_labels(y_test))

    if len(classes) < 2:
        raise ValueError(
            "Test split contains a single class; classification metrics "
            "need at least 2 classes."
        )

    if len(classes) > 2:
        average = "weighted"
        precision = precision_score(y_test, y_pred, average=average, zero_division=0)
        recall = recall_score(y_test, y_pred, average=average, zero_division=0)
        f1 = f1_score(y_test, y_pred, average=average, zero_division=0)
    else:
        pos_label = classes[-1]
        precision = precision_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        recall = recall_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        f1 = f1_score(y_test, y_pred, pos_label=pos_label, zero_division=0)

    accuracy = accuracy_score(y_test, y_pred)

    cm = confusion_matrix(y_test, y_pred, labels=classes)

    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix - {encoding_name}")
    plt.tight_layout()

    file_name = _safe_filename(encoding_name, experiment_id)
    plt.savefig(os.path.join(PROJECT_ROOT, file_name))
    plt.close()

    # TP/TN/FP/FN for binary classification.
    tp = tn = fp = fn = None
    if len(classes) == 2:
        yt, yp = np.asarray(y_test), np.asarray(y_pred)
        neg, pos = classes[0], classes[1]
        tn = int(((yt == neg) & (yp == neg)).sum())
        tp = int(((yt == pos) & (yp == pos)).sum())
        fp = int(((yt == neg) & (yp == pos)).sum())
        fn = int(((yt == pos) & (yp == neg)).sum())

    return {
        "Encoding": encoding_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ConfusionMatrix": cm.tolist(),
        "Classes": classes,
        "ConfusionImage": file_name,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
    }
