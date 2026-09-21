"""Genuine trainable embedding-based categorical encoding (PyTorch).

NOT ordinal encoding: each categorical value maps to an index -> nn.Embedding
-> dense vector, concatenated with scaled numericals, trained end-to-end.
Vocabulary is learned from TRAIN ONLY; test unknowns map to <UNK>=0.
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.preprocessing import LabelEncoder, StandardScaler

from backend.core import experiments as exps
from backend.core import state
from backend.core.config import PROJECT_ROOT
from backend.services.splitting import make_split


def _safe_filename(encoding_name, experiment_id=None):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", encoding_name).strip("_")
    exp = re.sub(r"[^A-Za-z0-9_-]+", "_", str(experiment_id or "default")).strip("_")
    return f"confusion_matrix_{exp}_{safe or 'model'}.png"


def run_embedding_encoding(experiment_id=None, model=None, test_size=None,
                           random_state=None, split=None, embedding_dim=8,
                           epochs=20, batch_size=256):
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    # ---- resolve data ----
    exp = exps.get_experiment(experiment_id) if experiment_id else None
    if exp is not None and exps.is_loaded(exp):
        X, y_s = exp["X_data"], exps.y_series(exp)
        problem_type = exp.get("problem_type")
        eid = exp.get("experiment_id")
        ts = float(test_size) if test_size is not None else float(exp.get("test_size", 0.2))
        rs = int(random_state) if random_state is not None else int(exp.get("random_state", 42))
    else:
        X, y_s = state.X_data, state.y_series()
        problem_type = state.problem_type
        eid = experiment_id or "default"
        ts = float(test_size) if test_size is not None else 0.2
        rs = int(random_state) if random_state is not None else 42

    if X is None or y_s is None or len(X) == 0:
        raise ValueError("No dataset loaded. Please POST /api/analyze first.")
    if problem_type is None:
        from backend.services.detection import detect_problem_type
        problem_type = detect_problem_type(y_s)["problem_type"]
    if problem_type != "Classification":
        raise ValueError("Embedding encoder in this lab currently supports classification datasets (Adult).")

    y_arr = np.asarray(y_s)
    if len(np.unique(y_arr[pd.notna(y_arr)])) < 2:
        raise ValueError("Target has a single class. Classification needs at least 2 classes.")

    cat_cols = X.select_dtypes(include=["object", "category", "bool", "string"]).columns.tolist()
    num_cols = X.select_dtypes(include=["number"]).columns.tolist()
    notes = []
    if not cat_cols:
        notes.append("Embedding Encoding: dataset has no categorical columns; embeddings skipped, MLP trained on numericals only.")

    # ---- same split ----
    if split is not None and split.get("train_idx") and split.get("test_idx"):
        train_idx = np.asarray(split["train_idx"], dtype=int)
        test_idx = np.asarray(split["test_idx"], dtype=int)
        n = len(X)
        train_idx = train_idx[(train_idx >= 0) & (train_idx < n)]
        test_idx = test_idx[(test_idx >= 0) & (test_idx < n)]
        split_info = {
            "train_samples": int(len(train_idx)), "test_samples": int(len(test_idx)),
            "test_size": float(split.get("test_size", ts)),
            "random_state": int(split.get("random_state", rs)),
            "stratified": bool(split.get("stratified", False)),
        }
    else:
        rec = make_split(y_s, test_size=ts, random_state=rs, problem_type=problem_type, notes=notes)
        train_idx, test_idx = np.asarray(rec["train_idx"]), np.asarray(rec["test_idx"])
        split_info = {"train_samples": rec["train_samples"], "test_samples": rec["test_samples"],
                      "test_size": rec["test_size"], "random_state": rec["random_state"],
                      "stratified": rec["stratified"]}
        split = rec

    # ---- vocab from TRAIN ONLY ----
    torch.manual_seed(rs); np.random.seed(rs)
    vocabs = {}
    for c in cat_cols:
        vals = X.iloc[train_idx][c].astype(str).fillna("__MISSING__")
        uniq = pd.unique(vals)
        vocabs[c] = {str(v): i + 1 for i, v in enumerate(uniq)}  # 0 = UNK

    def encode_frame(frame: pd.DataFrame):
        cats = []
        for c in cat_cols:
            v = frame[c].astype(str).fillna("__MISSING__").map(lambda x: vocabs[c].get(str(x), 0))
            cats.append(v.to_numpy(dtype=np.int64))
        if cats:
            return np.stack(cats, axis=1)
        return np.zeros((len(frame), 0), dtype=np.int64)

    # numerical scaler fit on train
    scaler = StandardScaler()
    if num_cols:
        scaler.fit(X.iloc[train_idx][num_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=float))

    def num_frame(frame):
        if not num_cols:
            return np.zeros((len(frame), 0), dtype=np.float32)
        arr = frame[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=float)
        return scaler.transform(arr).astype(np.float32)

    # target encoder fit on train
    le = LabelEncoder()
    y_train_raw = pd.Series(np.asarray(y_s)).iloc[train_idx].astype(str)
    y_test_raw = pd.Series(np.asarray(y_s)).iloc[test_idx].astype(str)
    le.fit(y_train_raw)
    classes = le.classes_.tolist()
    # map unseen test labels -> most frequent train class (avoid crash; note it)
    y_test_mapped = y_test_raw.map(lambda x: x if x in set(classes) else classes[0])
    y_train = le.transform(y_train_raw).astype(np.int64)
    y_test = le.transform(y_test_mapped).astype(np.int64)
    n_classes = len(classes)

    Xtr_cat, Xte_cat = encode_frame(X.iloc[train_idx]), encode_frame(X.iloc[test_idx])
    Xtr_num, Xte_num = num_frame(X.iloc[train_idx]), num_frame(X.iloc[test_idx])

    # validation split from train (15%)
    n_tr = len(train_idx)
    perm = np.random.RandomState(rs).permutation(n_tr)
    n_val = max(1, int(0.15 * n_tr))
    va_idx, tr_idx = perm[:n_val], perm[n_val:]

    def to_tensors(cat, num, y):
        return (torch.tensor(cat, dtype=torch.long),
                torch.tensor(num, dtype=torch.float32),
                torch.tensor(y, dtype=torch.long))

    tr_cat, tr_num, tr_y = to_tensors(Xtr_cat[tr_idx], Xtr_num[tr_idx], y_train[tr_idx])
    va_cat, va_num, va_y = to_tensors(Xtr_cat[va_idx], Xtr_num[va_idx], y_train[va_idx])
    te_cat, te_num, te_y = to_tensors(Xte_cat, Xte_num, y_test)

    # ---- model ----
    emb_dim = int(max(2, min(int(embedding_dim), 32)))
    vocab_sizes = [len(vocabs[c]) + 1 for c in cat_cols]

    class EmbMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.embs = nn.ModuleList([nn.Embedding(vs, emb_dim) for vs in vocab_sizes])
            in_dim = emb_dim * len(vocab_sizes) + len(num_cols)
            self.net = nn.Sequential(
                nn.Linear(max(in_dim, 1), 64), nn.ReLU(), nn.Dropout(0.2),
                nn.Linear(64, 1 if n_classes == 2 else n_classes),
            )

        def forward(self, cat, num):
            parts = [e(cat[:, i]) for i, e in enumerate(self.embs)] if self.embs else []
            if len(num_cols):
                parts.append(num)
            h = torch.cat(parts, dim=1) if parts else torch.zeros((cat.shape[0], 1))
            return self.net(h).squeeze(-1) if n_classes == 2 else self.net(h)

    net = EmbMLP()
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    crit = nn.BCEWithLogitsLoss() if n_classes == 2 else nn.CrossEntropyLoss()

    train_loader = DataLoader(TensorDataset(tr_cat, tr_num, tr_y), batch_size=min(int(batch_size), max(16, len(tr_idx))), shuffle=True)

    def run_epoch(loader, train: bool):
        net.train(train)
        tot_loss, correct, n = 0.0, 0, 0
        for bc, bn, by in loader:
            if train:
                opt.zero_grad()
            with torch.set_grad_enabled(train):
                out = net(bc, bn)
                if n_classes == 2:
                    loss = crit(out, by.float())
                    pred = (torch.sigmoid(out) >= 0.5).long()
                else:
                    loss = crit(out, by)
                    pred = out.argmax(dim=1)
                if train:
                    loss.backward(); opt.step()
            tot_loss += loss.item() * len(by)
            correct += int((pred == by).sum())
            n += len(by)
        return tot_loss / max(n, 1), correct / max(n, 1)

    val_loader = DataLoader(TensorDataset(va_cat, va_num, va_y), batch_size=1024)
    test_loader = DataLoader(TensorDataset(te_cat, te_num, te_y), batch_size=1024)

    best_val, patience, best_state = float("inf"), 4, None
    wait, epochs_run = 0, 0
    for ep in range(max(2, min(int(epochs), 100))):
        run_epoch(train_loader, True)
        vl, _ = run_epoch(val_loader, False)
        epochs_run = ep + 1
        if vl < best_val - 1e-4:
            best_val, wait = vl, 0
            best_state = {k: v.detach().cpu().clone() for k, v in net.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                notes.append(f"Early stopping at epoch {ep + 1} (val_loss={best_val:.4f}).")
                break
    if best_state is not None:
        net.load_state_dict(best_state)
    net.eval()

    # ---- evaluate on test ----
    all_pred = []
    with torch.no_grad():
        for bc, bn, by in test_loader:
            out = net(bc, bn)
            if n_classes == 2:
                all_pred.append(((torch.sigmoid(out) >= 0.5).long()).cpu())
            else:
                all_pred.append(out.argmax(dim=1).cpu())
    y_pred = torch.cat(all_pred).numpy()

    y_test_list = te_y.numpy()
    acc = float(accuracy_score(y_test_list, y_pred))
    if n_classes > 2:
        prec = float(precision_score(y_test_list, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test_list, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test_list, y_pred, average="weighted", zero_division=0))
    else:
        prec = float(precision_score(y_test_list, y_pred, zero_division=0))
        rec = float(recall_score(y_test_list, y_pred, zero_division=0))
        f1 = float(f1_score(y_test_list, y_pred, zero_division=0))

    cm = confusion_matrix(y_test_list, y_pred, labels=list(range(n_classes)))
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted"); plt.ylabel("Actual")
    plt.title("Confusion Matrix - Embedding Encoding")
    plt.tight_layout()
    file_name = _safe_filename("Embedding_Encoding", eid)
    plt.savefig(os.path.join(PROJECT_ROOT, file_name)); plt.close()

    tp = tn = fp = fn = None
    if n_classes == 2:
        tn = int(((y_test_list == 0) & (y_pred == 0)).sum())
        tp = int(((y_test_list == 1) & (y_pred == 1)).sum())
        fp = int(((y_test_list == 0) & (y_pred == 1)).sum())
        fn = int(((y_test_list == 1) & (y_pred == 0)).sum())

    total_emb_dim = emb_dim * len(cat_cols)

    # Encoded preview (df.head): MLP input vectors for the first train rows.
    encoded_preview = None
    try:
        with torch.no_grad():
            s_cat = torch.tensor(Xtr_cat[:5], dtype=torch.long)
            s_num = torch.tensor(Xtr_num[:5], dtype=torch.float32)
            parts = [net.embs[i](s_cat[:, i]) for i in range(len(net.embs))] if len(net.embs) else []
            if len(num_cols):
                parts.append(s_num)
            h = torch.cat(parts, dim=1).cpu().numpy() if parts else np.zeros((min(5, len(Xtr_cat)), 0))
        names = [f"{c}[{i}]" for c in cat_cols for i in range(emb_dim)] + [str(c) for c in num_cols]
        if len(names) != h.shape[1]:
            names = [f"f{i}" for i in range(h.shape[1])]
        total_cols = len(names)
        show = min(total_cols, 12)
        encoded_preview = {
            "columns": [str(c) for c in names[:show]],
            "rows": [[round(float(v), 4) for v in row[:show]] for row in h.tolist()],
            "total_columns": int(total_cols),
            "hidden_columns": int(total_cols - show),
            "total_rows": int(split_info["train_samples"]),
            "shown_rows": int(min(5, h.shape[0])),
        }
    except Exception:
        encoded_preview = None

    result = {
        "Encoding": "Embedding Encoding",
        "Accuracy": acc, "Precision": prec, "Recall": rec, "F1": f1,
        "ConfusionMatrix": cm.tolist(), "Classes": classes,
        "ConfusionImage": file_name,
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
    }
    return {
        "encoding_name": "Embedding Encoding",
        "encoding_key": "embedding",
        "problem_type": "Classification",
        "selected_model": "EmbeddingMLP",
        "model_key": "embedding_mlp",
        "categorical_cols_encoded": cat_cols,
        "numerical_cols": num_cols,
        "encoded_applied": bool(cat_cols),
        "notes": notes + [
            f"Trainable PyTorch embeddings (dim={emb_dim}) + MLP; vocab from train only, <UNK> for unseen test categories.",
            "Test data untouched until final evaluation; validation split taken from training data.",
        ],
        "train_test_split": split_info,
        "n_features_in": int(len(cat_cols) + len(num_cols)),
        "n_features_out": int(total_emb_dim + len(num_cols)),
        "encoded_preview": encoded_preview,
        "embedding": {
            "embedding_dim": emb_dim,
            "num_categorical": len(cat_cols),
            "total_embedding_dim": int(total_emb_dim),
            "epochs_run": epochs_run,
        },
        "result": result,
    }
