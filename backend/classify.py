import pandas as pd
from sklearn.preprocessing import LabelEncoder


def encode_target(y):
    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError(
                "This application currently supports only one target column."
            )
        col = y.columns[0]
    else:
        col = "target"
        y = pd.DataFrame({col: y})

    le = LabelEncoder()
    encoded_values = le.fit_transform(y[col])

    y_encoded = pd.DataFrame({"target_encoded": encoded_values}, index=y.index)

    class_mapping = {
        str(label): int(code)
        for label, code in zip(le.classes_, le.transform(le.classes_))
    }

    return {
        "y_encoded": y_encoded,
        "encoded_column": "target_encoded",
        "class_mapping": class_mapping,
        "num_classes": int(len(le.classes_)),
        "unique_target_values": int(le.classes_.size),
    }