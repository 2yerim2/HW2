# 개인 건강 위험 모니터링

FastAPI와 HTML/CSS/JavaScript로 만든 로컬 전용 건강 생활 지표 모니터입니다. 날짜별로 수면량, 운동 시간, 스트레스 정도, 물 섭취량을 기록하고 건강 상태 점수, 분석 결과, 최근 3일 인사이트를 확인할 수 있습니다.

## 요구 환경

- Windows PowerShell
- Python 3.14 이상 권장
- 가상환경 없이 설치된 전역 Python으로 실행 가능
- 일반 노트북 CPU에서 실행 가능

## 설치

PowerShell에서 `upload` 폴더로 이동한 뒤 실행합니다.

```powershell
cd C:\path\to\upload
py -m pip install -r requirements.txt
```

인터넷이 제한된 환경에서는 PyPI 패키지 설치가 실패할 수 있습니다. 이 경우 네트워크를 허용한 뒤 같은 명령을 다시 실행하세요.

## 모델 준비

앱은 `transformers`와 CPU용 `torch`를 사용하며, 첫 분석 시 다음 사전학습 모델을 준비하려고 시도합니다.

`distilbert-base-uncased-finetuned-sst-2-english`

모델은 Hugging Face에서 사용자 PC의 캐시에 다운로드되며 프로젝트 폴더에는 저장되지 않습니다. 대략 수백 MB의 디스크 공간이 필요할 수 있습니다. 모델 다운로드가 불가능하면 앱은 설명 가능한 규칙 기반 건강 분석으로 자동 전환되어 계속 실행됩니다.

모델을 미리 준비하려면 인터넷이 가능한 상태에서 앱을 한 번 실행하고 기록을 저장하세요. 모델 파일, Hugging Face 캐시, 인증정보는 GitHub에 올리지 마세요.

## 실행

```powershell
cd C:\path\to\upload
py -m uvicorn app:app --host 127.0.0.1 --port 8000
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다. 서버를 종료하려면 실행 중인 PowerShell 창에서 `Ctrl+C`를 누릅니다.

## 데이터와 주의사항

기록은 현재 실행 중인 서버 메모리에만 저장되며 앱을 종료하면 사라집니다. 이 앱의 점수와 분석은 생활 습관을 확인하기 위한 참고 정보이며 정확한 의학적 진단이 아닙니다. 증상이나 건강 우려가 있으면 의료 전문가와 상담하세요.

## 포함 파일

- `app.py`: FastAPI 서버와 분석 로직
- `static/`: 웹 화면, 스타일, 클라이언트 JavaScript
- `requirements.txt`: 실행 의존성
- `.gitignore`: 캐시, 로컬 설정, 로그, 모델 파일 제외 규칙
