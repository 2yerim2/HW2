"""Versioned, transparent wellness scoring heuristic.

This is not a clinical risk prediction model. It normalizes the four inputs
onto a continuous 0-100 scale to reduce threshold jumps in the old rules.
"""


def score_record(record: dict) -> tuple[int, list[str]]:
    sleep = float(record["sleep"])
    exercise = float(record["exercise"])
    stress = int(record["stress"])
    water = float(record["water"])
    sleep_component = max(0.0, 100.0 - abs(sleep - 8.0) * 12.0)
    exercise_component = min(100.0, exercise / 1.5 * 100.0)
    stress_component = max(0.0, 100.0 - stress * 10.0)
    water_component = min(100.0, water / 2.0 * 100.0)
    score = round(
        0.35 * sleep_component
        + 0.20 * exercise_component
        + 0.30 * stress_component
        + 0.15 * water_component
    )
    notes = []
    if sleep < 7:
        notes.append("Sleep is below the reference range.")
    elif sleep > 9:
        notes.append("Sleep is above the reference range.")
    if exercise < 0.5:
        notes.append("Consider adding light activity.")
    if stress >= 7:
        notes.append("Stress is high; consider rest or professional support.")
    if water < 1.5:
        notes.append("Water intake is below the reference target.")
    return max(0, min(100, score)), notes
