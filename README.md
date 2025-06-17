
# 제안서 자동 피드백 생성기 (Proposal Feedback Generator)

Streamlit 기반의 웹 애플리케이션으로, 제안요청서(RFP)와 제안서(PPT 또는 PDF)를 비교하여 누락된 항목과 불일치한 내용을 자동으로 감지하고, Groq API를 통해 전문가처럼 자연스러운 피드백 문장을 생성합니다.

---

## 📌 주요 기능

- 📤 PDF 업로드 (제안요청서 / 제안서)
- 🔍 줄 단위 비교로 누락 및 불일치 항목 감지
- 🤖 Groq API를 이용한 피드백 문장 자동 생성
- 🧾 Streamlit UI 기반 사용자 인터페이스

---

## 🚀 실행 방법

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

`.streamlit/secrets.toml` 파일 또는 Streamlit Cloud > Settings > Secrets에 다음을 추가하세요:

```toml
groq_api_key = "gsk_여기에_발급받은_Groq_API_키"
```

### 3. 실행

```bash
streamlit run app.py
```

---

## 📁 파일 구조

```
├── app.py                   # Streamlit 앱 메인 실행 파일
├── pdf_extractor.py         # PDF 텍스트 추출
├── comparator.py            # 문서 비교 기능
├── feedback_generator.py    # Groq API 호출 및 피드백 생성
├── requirements.txt         # 의존성 목록
└── README.md                # 설명 문서 (바로 이 파일)
```

---

## 🧠 사용 기술

- Python 3.x
- Streamlit
- PyMuPDF
- difflib (내장 비교 알고리즘)
- Groq API (mixtral-8x7b-32768 모델)

---

## 📝 라이선스

본 프로젝트는 개인 또는 팀 프로젝트 데모 용도로 제공되며 상업적 목적 사용 시 라이선스를 반드시 확인하세요.
