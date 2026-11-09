"""Create the fixed, privacy-free synthetic benchmark."""
import json
import random
from pathlib import Path

OUT = Path(__file__).parent / "data" / "synthetic_health_records.json"
rng = random.Random(20261109)
records = []
for i in range(100):
    record = {
        "id": f"synthetic-{i + 1:03d}",
        "sleep": round(rng.uniform(4.0, 11.0), 1),
        "exercise": round(rng.uniform(0.0, 2.5), 1),
        "stress": rng.randint(0, 10),
        "water": round(rng.uniform(0.5, 3.5), 1),
    }
    sleep = max(0.0, 100.0 - abs(record["sleep"] - 8.0) * 12.0)
    exercise = min(100.0, record["exercise"] / 1.5 * 100.0)
    stress = 100.0 - record["stress"] * 10.0
    water = min(100.0, record["water"] / 2.0 * 100.0)
    record["reference_score"] = round(0.35 * sleep + 0.20 * exercise + 0.30 * stress + 0.15 * water)
    record["reference_label"] = "good" if record["reference_score"] >= 80 else "caution" if record["reference_score"] >= 60 else "attention"
    records.append(record)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, indent=2), encoding="utf-8")
print(f"wrote {len(records)} records to {OUT}")
