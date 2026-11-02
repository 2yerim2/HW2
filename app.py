from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from transformers import pipeline
except Exception:
    pipeline = None

BASE_DIR = Path(__file__).parent
app = FastAPI(title="개인 건강 위험 모니터링", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
records: Dict[str, dict] = {}
records_lock = Lock()
sentiment_model = None
model_status = "미사용(규칙 기반 건강 분석)"


class HealthRecord(BaseModel):
    sleep: float = Field(..., ge=0, le=24, description="수면 시간(시간)")
    exercise: float = Field(..., ge=0, le=24, description="운동 시간(시간)")
    stress: int = Field(..., ge=0, le=10, description="스트레스 0~10")
    water: float = Field(..., ge=0, le=20, description="물 섭취량(리터)")


def score_record(r: dict) -> tuple[int, list[str]]:
    score = 100
    notes = []
    if r["sleep"] < 7:
        score -= min(25, int((7 - r["sleep"]) * 8))
        notes.append("수면이 권장 범위보다 부족합니다.")
    elif r["sleep"] > 9:
        score -= 5
        notes.append("수면 시간이 다소 깁니다.")
    if r["exercise"] < 0.5:
        score -= 15
        notes.append("가벼운 운동을 조금 더 시도해 보세요.")
    elif r["exercise"] >= 1:
        score += 3
    if r["stress"] >= 7:
        score -= 25
        notes.append("스트레스가 높습니다. 휴식이나 도움을 고려하세요.")
    elif r["stress"] >= 4:
        score -= 10
    if r["water"] < 1.5:
        score -= 12
        notes.append("수분 섭취가 부족할 수 있습니다.")
    elif r["water"] >= 2:
        score += 2
    return max(0, min(100, score)), notes


def health_label(score: int) -> str:
    return "양호" if score >= 80 else "주의" if score >= 60 else "관찰 필요"


def ai_analysis(r: dict, score: int, notes: list[str]) -> str:
    global sentiment_model, model_status
    summary = f"sleep {r['sleep']} hours, exercise {r['exercise']} hours, stress {r['stress']} out of 10, water {r['water']} liters"
    # The pretrained CPU sentiment model is an additional signal, not a diagnosis.
    if sentiment_model is None and pipeline is not None:
        try:
            sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
            model_status = "distilbert-base-uncased-finetuned-sst-2-english (CPU)"
        except Exception:
            model_status = "모델 다운로드 불가 - 설명 가능한 규칙 기반 분석으로 전환"
    signal = ""
    if sentiment_model:
        try:
            result = sentiment_model(summary, truncation=True)[0]
            signal = f" 사전학습 모델 신호: {result['label']} ({result['score']:.0%})."
        except Exception:
            pass
    if not notes:
        return "수면, 활동, 스트레스, 수분 지표가 전반적으로 균형적입니다." + signal
    return " ".join(notes[:3]) + signal


def analyze(day: str, r: dict) -> dict:
    score, notes = score_record(r)
    return {"date": day, "metrics": r, "score": score, "label": health_label(score), "analysis": ai_analysis(r, score, notes), "medical_disclaimer": "이 결과는 의학적 진단이 아니며, 증상이 있으면 의료 전문가와 상담하세요."}


def insight_for(days: list[dict]) -> str:
    if not days:
        return "최근 3일 기록을 입력하면 생활 패턴 기반 인사이트가 표시됩니다."
    avg = sum(x["score"] for x in days) / len(days)
    stress = sum(x["metrics"]["stress"] for x in days) / len(days)
    if stress >= 7:
        return "최근 3일은 스트레스가 높아 짧은 휴식과 수면 회복을 우선해 보세요."
    if avg >= 80:
        return "최근 3일 건강 점수가 안정적입니다. 현재 루틴을 꾸준히 유지해 보세요."
    return "최근 3일 점수에 개선 여지가 있습니다. 수면과 수분 섭취부터 작은 목표를 세워 보세요."


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True, "model": model_status}


@app.get("/api/records/{day}")
def get_record(day: str):
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(400, "날짜 형식은 YYYY-MM-DD여야 합니다.")
    with records_lock:
        return records.get(day)


@app.put("/api/records/{day}")
def put_record(day: str, record: HealthRecord):
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(400, "날짜 형식은 YYYY-MM-DD여야 합니다.")
    result = analyze(day, record.model_dump())
    with records_lock:
        records[day] = result
    return result


@app.get("/api/insight/{day}")
def insight(day: str):
    try:
        target = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(400, "날짜 형식은 YYYY-MM-DD여야 합니다.")
    with records_lock:
        recent = [records[d] for d in sorted(records) if target - timedelta(days=2) <= date.fromisoformat(d) <= target]
    return {"insight": insight_for(recent), "days": len(recent)}
