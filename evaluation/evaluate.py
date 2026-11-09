"""Compare the old and improved scorers on fixed synthetic data.

Reference labels are transparent synthetic wellness proxies, not clinical outcomes.
Records 1-30 are tuning-only; records 31-100 are final evaluation-only.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from health_scoring import score_record

DATA = Path(__file__).parent / "data" / "synthetic_health_records.json"


def baseline_score(r):
    score = 100
    if r["sleep"] < 7:
        score -= min(25, int((7 - r["sleep"]) * 8))
    elif r["sleep"] > 9:
        score -= 5
    if r["exercise"] < 0.5:
        score -= 15
    elif r["exercise"] >= 1:
        score += 3
    if r["stress"] >= 7:
        score -= 25
    elif r["stress"] >= 4:
        score -= 10
    if r["water"] < 1.5:
        score -= 12
    elif r["water"] >= 2:
        score += 2
    return max(0, min(100, score))


def label(score):
    return "good" if score >= 80 else "caution" if score >= 60 else "attention"


def metrics(rows, predictions):
    truth = [r["reference_score"] for r in rows]
    mae = sum(abs(a - b) for a, b in zip(predictions, truth)) / len(rows)
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(predictions, truth)) / len(rows))
    accuracy = sum(label(p) == r["reference_label"] for p, r in zip(predictions, rows)) / len(rows)
    return {"n": len(rows), "MAE": round(mae, 3), "RMSE": round(rmse, 3), "label_accuracy": round(accuracy, 3)}


rows = json.loads(DATA.read_text(encoding="utf-8"))
tuning, final = rows[:30], rows[30:]
result = {
    "dataset": "synthetic_health_records.json",
    "tuning_records": len(tuning),
    "final_records": len(final),
    "interpretation": "synthetic proxy benchmark, not clinical validation",
    "baseline_final": metrics(final, [baseline_score(r) for r in final]),
    "improved_final": metrics(final, [score_record(r)[0] for r in final]),
}
print(json.dumps(result, indent=2))
