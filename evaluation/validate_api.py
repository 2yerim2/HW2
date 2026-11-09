"""Smoke-test validation, error handling, and the two public API endpoints."""
from datetime import date, timedelta
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app

app.pipeline = None
client = TestClient(app.app)
payload = {"sleep": 7.5, "exercise": 1.0, "stress": 3, "water": 2.0}
target = date(2026, 11, 3)

assert client.get("/api/health").status_code == 200
assert client.put(f"/api/records/{target - timedelta(days=1)}", json=payload).status_code == 200
assert client.put(f"/api/records/{target}", json=payload).status_code == 200
insight = client.get(f"/api/insight/{target}")
assert insight.status_code == 200 and insight.json()["days"] == 2
assert client.put("/api/records/not-a-date", json=payload).status_code == 400
assert client.put(f"/api/records/{target}", json={**payload, "stress": 11}).status_code == 422
print("API validation passed: health, record PUT, 3-day insight, date and range errors")
