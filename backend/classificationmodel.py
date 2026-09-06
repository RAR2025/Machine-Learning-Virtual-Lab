import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from backend import state
from backend.models import resolve_model


def evaluate_model(model=None, X_train=None, X_test=None, y_train=None, y_test=None, encoding_name="Model"):

    if model is None:
        model = resolve_model("Classification", state.selected_model)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    classes = sorted(y_test.unique())

    if len(classes) > 2:
        average = "weighted"
        precision = precision_score(y_test, y_pred, average=average)
        recall = recall_score(y_test, y_pred, average=average)
        f1 = f1_score(y_test, y_pred, average=average)
    else:
        average = "binary"
        pos_label = classes[-1]
        precision = precision_score(y_test, y_pred, pos_label=pos_label)
        recall = recall_score(y_test, y_pred, pos_label=pos_label)
        f1 = f1_score(y_test, y_pred, pos_label=pos_label)

    accuracy = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 60)
    print(f"{encoding_name}")
    print("=" * 60)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")

    cm = confusion_matrix(y_test, y_pred)

    print("Confusion Matrix:")
    print(cm)

    plt.figure(figsize=(5, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
    )

    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix - {encoding_name}")
    plt.tight_layout()
    plt.savefig(f"confusion_matrix_{encoding_name}.png")
    plt.close()

    return {
        "Encoding": encoding_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ConfusionMatrix": cm.tolist(),
        "Classes": classes,
    }