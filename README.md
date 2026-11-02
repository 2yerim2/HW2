# 개인 건강 위험 모니터링

## 실행 (PowerShell, 가상환경 없음)

```powershell
cd C:\Users\Snowf\Downloads\HW2
py -m pip install -r requirements.txt
py -m uvicorn app:app --host 127.0.0.1 --port 8000
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다. 첫 분석 시 Hugging Face의 `distilbert-base-uncased-finetuned-sst-2-english`를 CPU용으로 준비할 수 있으며, 다운로드가 불가능하면 설명 가능한 규칙 기반 분석으로 자동 전환됩니다. 기록은 서버 메모리에만 보관됩니다.

이 앱의 점수와 분석은 건강 습관을 살펴보기 위한 참고 정보이며 의학적 진단이 아닙니다.
