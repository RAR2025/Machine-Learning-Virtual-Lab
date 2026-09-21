"""End-to-end backend test over real UCI datasets.

Runs the true HTTP route functions (no server needed):
    POST /api/analyze -> POST /api/clean -> POST /api/train(all)
for each dataset id, and writes a Markdown report.

Usage:
    python scripts/e2e_uci.py
    python scripts/e2e_uci.py --ids 53 275 2
    python scripts/e2e_uci.py --skip-train
    python scripts/e2e_uci.py --report scripts/e2e_report.md

Exit code: 0 if no FAIL, 1 otherwise (SKIP for fetch errors doesn't fail).
"""

import argparse
import glob
import os
import sys
import time
import traceback

# Run from repo root regardless of CWD.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
os.chdir(REPO_ROOT)

from backend.api import analyze as analyze_route  # noqa: E402
from backend.api import cleaning as clean_route  # noqa: E402
from backend.api import training as train_route  # noqa: E402
from backend.core import experiments as exps  # noqa: E402
from backend.core import state  # noqa: E402
from backend.schemas import DatasetRequest, TrainRequest  # noqa: E402

# Curated spread: small/large, classification/regression, clean/messy.
DEFAULT_IDS = [53, 109, 2, 45, 73, 27, 159, 275, 186, 17, 12, 46, 92]

# Backend validation errors that mean "dataset unusable for this lab by
# design" (handled properly) rather than a backend bug -> SKIP, not FAIL.
EXPECTED_UNUSABLE = (
    "single class",
    "removed all rows",
    "removed all feature columns",
    "empty after",
)


def _err_short(exc, limit=300):
    msg = str(exc).replace("\n", " ")
    return msg[:limit] + ("..." if len(msg) > limit else "")


def run_one(dataset_id, do_train=True):
    """Returns a result dict for one dataset id."""
    rec = {"id": dataset_id, "status": "FAIL", "stages": {}}
    t0 = time.time()
    try:
        state.reset()
        exps.reset_all()
        t = time.time()
        analysis = analyze_route.analyze_dataset(
            DatasetRequest(code=f"fetch_ucirepo(id={dataset_id})")
        )
        _eid = analysis.get("experiment_id")
        rec["stages"]["analyze"] = round(time.time() - t, 1)
        rec["problem"] = analysis.get("problem_type")
        rec["target"] = analysis.get("target_column")
        rec["raw_shape"] = [analysis.get("num_samples"), analysis.get("num_features")]
        rec["raw_uniques"] = analysis.get("unique_target_values")

        t = time.time()
        cleaned = clean_route.clean_dataset_route(DatasetRequest(code="", experiment_id=_eid))
        rec["stages"]["clean"] = round(time.time() - t, 1)
        rec["clean_shape"] = cleaned.get("X_shape_after")
        rec["report"] = {
            k: cleaned.get(k)
            for k in (
                "nan_rows_removed", "duplicate_rows_removed",
                "placeholder_cells_found", "sentinel_cells_found",
                "rows_dropped_target_missing", "imputed_cells",
                "columns_dropped", "numeric_coerced", "datetime_converted",
                "rare_grouped", "outliers_capped", "warnings",
                "target_encoded", "num_classes",
            )
        }

        if do_train:
            t = time.time()
            payload = train_route.train_model(TrainRequest(encoding="all", experiment_id=_eid))
            results = payload.get("results", payload) if isinstance(payload, dict) else payload
            rec["stages"]["train"] = round(time.time() - t, 1)
            enc = {}
            for item in results:
                name = item.get("encoding_name", "?")
                res = item.get("result")
                if res is None:
                    enc[name] = {"ok": False, "error": item.get("error", "?")[:200]}
                elif "Accuracy" in res:
                    enc[name] = {"ok": True, "acc": round(res["Accuracy"], 4),
                                 "f1": round(res["F1"], 4)}
                else:
                    enc[name] = {"ok": True, "r2": round(res["R2"], 4)}
            rec["encodings"] = enc
            failed = [k for k, v in enc.items() if not v["ok"]]
            rec["status"] = "PASS" if not failed else "PARTIAL"
            rec["failed_encodings"] = failed
        else:
            rec["status"] = "PASS"
    except Exception as e:  # noqa: BLE001 - harness must not die
        msg = _err_short(e)
        lowered = msg.lower()
        if any(s in lowered for s in EXPECTED_UNUSABLE):
            rec["status"] = "SKIP"
            rec["skip_reason"] = "unusable-for-lab"
        elif "fetch" in lowered or "url" in lowered or "404" in lowered:
            rec["status"] = "SKIP"
            rec["skip_reason"] = "fetch"
        rec["error"] = msg
        rec["trace"] = traceback.format_exc(limit=5)
    finally:
        try:
            state.reset()
            exps.reset_all()
        except Exception:
            pass
        rec["total_s"] = round(time.time() - t0, 1)
    return rec


def to_markdown(records, elapsed):
    lines = [
        "# E2E UCI Report",
        "",
        f"Datasets: {len(records)} | "
        + ", ".join(
            f"{s}: {sum(1 for r in records if r['status'] == s)}"
            for s in ("PASS", "PARTIAL", "FAIL", "SKIP")
        )
        + f" | total {elapsed:.0f}s",
        "",
        "| id | status | problem | raw (rows×feat) | clean (rows×feat) | "
        "placeholders→NA | imputed | cols dropped | encodings | time |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in records:
        rep = r.get("report", {}) or {}
        enc = r.get("encodings")
        if enc is None:
            enc_str = "skipped"
        else:
            parts = []
            for k, v in enc.items():
                if v["ok"]:
                    metric = v.get("acc", v.get("r2"))
                    parts.append(f"{k} ✓{metric}")
                else:
                    parts.append(f"{k} ✗")
            enc_str = "<br>".join(parts)
        raw = r.get("raw_shape", ["?", "?"])
        clean = r.get("clean_shape", ["?", "?"])
        stages = r.get("stages", {})
        t = "+".join(f"{v}s" for v in stages.values()) or "-"
        lines.append(
            f"| {r['id']} | **{r['status']}** | {r.get('problem', '-')} | "
            f"{raw[0]}×{raw[1]} | {clean[0]}×{clean[1]} | "
            f"{rep.get('placeholder_cells_found', '-')} | "
            f"{rep.get('imputed_cells', '-')} | "
            f"{rep.get('columns_dropped', '-')} | {enc_str} | {t} |"
        )
    lines.append("")
    for r in records:
        if r["status"] in ("FAIL", "SKIP") or r.get("failed_encodings"):
            lines += [
                f"## id={r['id']} → {r['status']}",
                "",
                f"```\n{r.get('error', r.get('failed_encodings', ''))}\n```",
                "",
            ]
            if r.get("trace") and r["status"] == "FAIL":
                lines += [f"<details><summary>trace</summary>\n\n```\n{r['trace']}\n```\n</details>", ""]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", type=int, default=DEFAULT_IDS)
    ap.add_argument("--skip-train", action="store_true")
    ap.add_argument("--report", default="scripts/e2e_report.md")
    args = ap.parse_args()

    for f in glob.glob(os.path.join(REPO_ROOT, "confusion_matrix_*.png")):
        os.remove(f)

    print(f"Testing {len(args.ids)} UCI datasets: {args.ids}", flush=True)
    t0 = time.time()
    records = []
    for i, did in enumerate(args.ids, 1):
        print(f"\n[{i}/{len(args.ids)}] id={did} ...", flush=True)
        rec = run_one(did, do_train=not args.skip_train)
        records.append(rec)
        extra = ""
        if rec["status"] == "FAIL":
            extra = f" ERROR: {rec.get('error')}"
        elif rec.get("failed_encodings"):
            extra = f" failed enc: {rec['failed_encodings']}"
        print(f"  -> {rec['status']} ({rec.get('problem', '?')}) "
              f"raw={rec.get('raw_shape')} clean={rec.get('clean_shape')} "
              f"{rec.get('total_s')}s{extra}", flush=True)

    elapsed = time.time() - t0
    md = to_markdown(records, elapsed)
    with open(os.path.join(REPO_ROOT, args.report), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\nReport -> {args.report}")
    print(md.split("\n\n")[0].replace("# ", ""))

    n_fail = sum(1 for r in records if r["status"] == "FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
