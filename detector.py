import pandas as pd
import re
from pandas.api.types import is_numeric_dtype, is_object_dtype


def detect_problem_type(y):

    # If y is a DataFrame with one column
    if isinstance(y, pd.DataFrame):

        if y.shape[1] != 1:
            raise ValueError(
                "This application currently supports only one target column."
            )

        y = y.iloc[:, 0]

    # Remove missing values
    y_clean = y.dropna()

    if len(y_clean) == 0:
        return {
            "problem_type": "Unknown",
            "reason": "Target contains no valid values."
        }

    # Target information
    unique_values = y_clean.nunique()
    total_values = len(y_clean)
    unique_ratio = unique_values / total_values

    # Categorical / text / boolean target
    if (
        is_object_dtype(y_clean)
        or isinstance(y_clean.dtype, pd.CategoricalDtype)
        or pd.api.types.is_bool_dtype(y_clean)
    ):
        return {
            "problem_type": "Classification",
            "reason": "Target is categorical/text/boolean.",
            "unique_values": unique_values,
            "target_dtype": str(y_clean.dtype)
        }

    # Numeric target
    if is_numeric_dtype(y_clean):

        # Few unique values -> likely classification
        if unique_values <= 20 or unique_ratio < 0.05:
            return {
                "problem_type": "Classification",
                "reason": "Numeric target has relatively few unique values.",
                "unique_values": unique_values,
                "target_dtype": str(y_clean.dtype)
            }

        # Many unique values -> likely regression
        return {
            "problem_type": "Regression",
            "reason": "Numeric target contains many unique values.",
            "unique_values": unique_values,
            "target_dtype": str(y_clean.dtype)
        }

    return {
        "problem_type": "Unknown",
        "reason": f"Unsupported target datatype: {y_clean.dtype}"
    }


def extract_dataset_id(code):

    """
    Extract UCI dataset ID from code such as:

    bike_sharing = fetch_ucirepo(id=275)
    """

    pattern = r"fetch_ucirepo\s*\(\s*id\s*=\s*(\d+)\s*\)"

    match = re.search(pattern, code)

    if match:
        return int(match.group(1))

    return None


def analyze_code(code):

    # Check whether user entered anything
    if not code or not code.strip():
        return "Please enter UCI dataset code."

    # Extract dataset ID
    dataset_id = extract_dataset_id(code)

    if dataset_id is None:
        return (
            "Could not find a valid UCI dataset ID.\n\n"
            "Expected format:\n"
            "fetch_ucirepo(id=275)"
        )

    try:

        # Import here so the application only fetches the dataset
        from ucimlrepo import fetch_ucirepo

        # Fetch dataset
        dataset = fetch_ucirepo(id=dataset_id)

        # Get X and y
        X = dataset.data.features
        y = dataset.data.targets

        # Detect problem type
        result = detect_problem_type(y)

        # Target name
        target_name = y.columns[0] if isinstance(y, pd.DataFrame) else "Unknown"

        output = f"""
Dataset ID: {dataset_id}

Target Column: {target_name}

Target Data Type: {result.get("target_dtype", str(y.dtypes))}

Unique Target Values: {result.get("unique_values", y.nunique())}

Detected Problem Type:
{result["problem_type"]}

Reason:
{result["reason"]}
"""

        return output

    except Exception as e:

        return f"""
Error while fetching or analyzing dataset.

Dataset ID: {dataset_id}

Error:
{str(e)}
"""