# AI Debate — Streamlit

ChatGPT, Claude, Gemini가 독립 답변과 익명 상호 비평을 거쳐 하나의 최종안을 만드는 Streamlit 웹앱입니다.

## 기능

- 2~3개 AI 참여자 선택
- 독립 답변 → 익명 상호 비평 → 최종 종합
- 단계별 진행 표시
- 세션 내 결과와 기록
- 데스크탑 앱과 같은 밝은 작업 화면, 네이비 산 일러스트 사이드바
- 결과 TXT 다운로드

## 보안 및 비용

- API 키는 현재 Streamlit 세션 메모리에만 유지됩니다.
- 키를 소스, GitHub, 기록 파일에 저장하지 않습니다.
- 기본 3인 토론은 최대 7회의 유료 제공사 API 호출을 사용합니다.
- 실제 과금과 데이터 처리 정책은 각 API 제공사 계정에 적용됩니다.

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

- Repository: `mackievboy/ai-debate-streamlit`
- Branch: `main`
- Main file path: `app.py`
- Python: `3.13`
- Secrets: 비워 둠
