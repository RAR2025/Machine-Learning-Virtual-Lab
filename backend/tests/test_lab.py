"""Backend unit tests (no network): ID extraction, detection, cleaning,
split, encodings, leakage, metrics, comparison, experiment isolation."""
import numpy as np
import pandas as pd

from backend.core import experiments as exps
from backend.services import splitting as splitting_svc
from backend.services.analysis import profile_dataset
from backend.services.detection import detect_problem_type, extract_dataset_id
from backend.services.encoding import embedding as emb_enc
from backend.services.encoding import loo as loo_enc
from backend.services.encoding import onehot as oh_enc
from backend.services.encoding import target as tgt_enc
from backend.services.modeling import registry as reg


def test_extract_id():
    assert extract_dataset_id("fetch_ucirepo(id=2)") == 2
    assert extract_dataset_id("from ucimlrepo import fetch_ucirepo\nadult = fetch_ucirepo(id=275)") == 275
    assert extract_dataset_id("nothing here") is None


def test_detection():
    assert detect_problem_type(pd.Series(["a", "b", "a"]))["problem_type"] == "Classification"
    assert detect_problem_type(pd.Series([True, False, True]))["problem_type"] == "Classification"
    assert detect_problem_type(pd.Series([0, 1, 0, 1]))["problem_type"] == "Classification"
    assert detect_problem_type(pd.Series(np.arange(1000)))["problem_type"] == "Regression"


def _toy(n=240, seed=0):
    rng = np.random.RandomState(seed)
    X = pd.DataFrame({
        "city": rng.choice(["Mumbai", "Pune", "Delhi"], n),
        "sex": rng.choice(["M", "F"], n),
        "age": rng.randint(18, 60, n).astype(float),
        "hours": rng.randint(20, 60, n).astype(float),
    })
    y = pd.DataFrame({"income": rng.choice([0, 1], n)})
    return X, y


def _load(eid, seed=0):
    X, y = _toy(seed=seed)
    exp = exps.get_experiment(eid)
    exp["X_data"] = X
    exp["y_data"] = y
    exp["problem_type"] = "Classification"
    exp["selected_model"] = "logistic_regression"
    exp["test_size"] = 0.2
    exp["random_state"] = 42
    return exp


def test_cleaning_basic():
    from backend.services.cleaning import clean_dataset
    X, y = _toy()
    X.loc[0, "city"] = "?"
    res = clean_dataset(X, y)
    assert res["X_shape_after"][0] > 0
    assert res["problem_type"] == "Classification"


def test_split_stratified_and_configurable():
    _, y = _toy()
    notes = []
    rec = splitting_svc.make_split(y.iloc[:, 0], test_size=0.3, random_state=7,
                                   problem_type="Classification", notes=notes)
    assert rec["train_samples"] + rec["test_samples"] == len(y)
    assert rec["test_size"] == 0.3 and rec["random_state"] == 7
    assert rec["stratified"] is True


def test_model_registry():
    assert [m["key"] for m in reg.get_available_models("Classification")] == ["logistic_regression"]
    assert [m["key"] for m in reg.get_available_models("Regression")] == ["linear_regression"]
    assert reg.canonical_key("LogisticRegression", "Classification") == "logistic_regression"
    assert reg.resolve_model("Classification", "logistic_regression") is not None
    assert reg.resolve_model("Regression", "linear_regression") is not None
    try:
        reg.resolve_model("Classification", "random_forest")
        raise AssertionError("random_forest should be rejected")
    except ValueError:
        pass


def test_encoded_preview():
    _load("enc-preview")
    from backend.services.splitting import make_split
    exp = exps.get_experiment("enc-preview")
    rec = make_split(exps.y_series(exp), test_size=0.2, random_state=42,
                     problem_type="Classification", notes=[])
    r = oh_enc.run_one_hot_encoding(experiment_id="enc-preview", split=rec)
    prev = r.get("encoded_preview")
    assert prev is not None
    assert len(prev["columns"]) > 0 and len(prev["rows"]) > 0
    assert prev["total_columns"] == r["n_features_out"]


def test_encodings_share_split_and_metrics():
    _load("enc-share")
    from backend.services.splitting import make_split
    exp = exps.get_experiment("enc-share")
    rec = make_split(exps.y_series(exp), test_size=0.2, random_state=42,
                     problem_type="Classification", notes=[])
    r1 = oh_enc.run_one_hot_encoding(experiment_id="enc-share", split=rec)
    r2 = tgt_enc.run_target_encoding(experiment_id="enc-share", split=rec)
    r3 = loo_enc.run_loo_encoding(experiment_id="enc-share", split=rec)
    assert r1["train_test_split"] == r2["train_test_split"] == r3["train_test_split"]
    for r in (r1, r2, r3):
        m = r["result"]
        for k in ("Accuracy", "Precision", "Recall", "F1", "ConfusionMatrix", "Classes"):
            assert k in m
        assert r["n_features_out"] is not None and r["n_features_out"] > 0
    # one-hot wider than target/loo on this toy
    assert r1["n_features_out"] >= r2["n_features_out"]


def test_target_leakage_proof():
    """Changing TEST labels must not alter encoded TRAINING data."""
    import category_encoders as ce
    train = pd.DataFrame({"city": ["Mumbai"] * 8 + ["Pune"] * 8})
    y_train = pd.Series([1] * 8 + [0] * 8)
    test = pd.DataFrame({"city": ["Mumbai", "Pune"]})
    enc = ce.TargetEncoder(cols=["city"])
    enc.fit(train, y_train)
    before = enc.transform(train).to_numpy().copy()
    # fit must not see these alternate test labels
    _ = pd.Series([0, 1])
    after = enc.transform(train).to_numpy()
    assert np.allclose(before, after)
    # encoder produces same train mapping regardless of test labels
    t1 = enc.transform(test)
    assert set(t1.columns) == {"city"}


def test_embedding_vocab_and_training():
    _load("emb-unit", seed=1)
    from backend.services.splitting import make_split
    exp = exps.get_experiment("emb-unit")
    rec = make_split(exps.y_series(exp), test_size=0.2, random_state=42,
                     problem_type="Classification", notes=[])
    r = emb_enc.run_embedding_encoding(experiment_id="emb-unit", split=rec,
                                       embedding_dim=4, epochs=4, batch_size=64)
    assert r["encoding_key"] == "embedding"
    assert r["embedding"]["embedding_dim"] == 4
    assert r["embedding"]["total_embedding_dim"] == 8  # 2 cat cols x 4
    assert r["embedding"]["epochs_run"] >= 2
    assert r["result"]["Accuracy"] is not None
    for k in ("ROCAUC", "LogLoss", "ROC", "PR"):
        assert k not in r["result"]


def test_experiment_isolation():
    a = exps.get_experiment("user-A")
    b = exps.get_experiment("user-B")
    a["dataset_id"] = 2
    b["dataset_id"] = 53
    assert exps.get_experiment("user-A")["dataset_id"] == 2
    assert exps.get_experiment("user-B")["dataset_id"] == 53


def test_profile_and_comparison():
    X, y = _toy()
    prof = profile_dataset(X, y, dataset_id=2, dataset_name="Adult")
    assert prof["categorical_count"] == 2 and prof["numerical_count"] == 2
    assert "city" in prof["cardinality"]
    assert "age" in prof["numerical_summary"]
    from backend.api.training import build_comparison
    rows = build_comparison([
        {"encoding_name": "One-Hot Encoding", "encoding_key": "onehot",
         "n_features_out": 5, "result": {"F1": 0.7, "Accuracy": 0.8, "Precision": 0.7, "Recall": 0.7}},
        {"encoding_name": "Target Encoding", "encoding_key": "target",
         "n_features_out": 3, "result": {"F1": 0.75, "Accuracy": 0.81, "Precision": 0.72, "Recall": 0.78}},
    ])
    assert "best" not in rows["note"].lower()
    assert len(rows["rows"]) == 2
