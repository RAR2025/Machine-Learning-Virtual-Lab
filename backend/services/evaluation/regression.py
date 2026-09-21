import numpy as np

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from backend.core import state
from backend.services.modeling.registry import resolve_model


def evaluate_model(model=None, X_train=None, X_test=None, y_train=None, y_test=None, encoding_name="Model"):

    if model is None:
        model = resolve_model("Regression", state.selected_model)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    rmse = float(np.sqrt(mse))
    mae = mean_absolute_error(y_test, y_pred)
    try:
        r2 = r2_score(y_test, y_pred)
    except Exception:
        r2 = float("nan")

    print("\n" + "=" * 60)
    print(f"{encoding_name}")
    print("=" * 60)

    print(f"R2 Score  : {r2:.4f}")
    print(f"MSE       : {mse:.4f}")
    print(f"RMSE      : {rmse:.4f}")
    print(f"MAE       : {mae:.4f}")

    return {
        "Encoding": encoding_name,
        "R2": r2,
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
    }
