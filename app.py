
import os
import re
import streamlit as st
import fitz  # PyMuPDF

# ==============================
# 🔧 Helper 함수들 직접 포함
# ==============================

def get_proposal_title_from_filename(filename):
    return filename.replace(".pdf", "").strip()

# 항목 추출 (정밀도 개선)
def extract_sections_from_text(text):
    lines = text.splitlines()
    sections = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 조건: 숫자+괄호/점, 장 제목, 한글 포함, 길이 5자 이상
        if re.match(r"^(제?\d+장|\d+[\.\)]\s*|[ⅠⅡⅢ])", line) and len(line) >= 5 and re.search(r"[가-힣]", line):
            sections.add(line)
    return list(sections)

# 예시 추천 (부분 매칭 허용)
def get_examples_for_section(section_title):
    section_title = section_title.lower()
    mapping = {
        "기능": [
            "본 시스템은 실시간 교통 데이터를 수집 및 분석하여, 도심 내 혼잡 구간을 사전 예측합니다.",
            "주요 기능으로는 교통량 예측, 사고 감지, 통합 관제 기능이 포함됩니다."
        ],
        "추진": [
            "3단계 추진 전략으로 초기 분석 → 시스템 설계 → 현장 적용의 구조로 수행됩니다.",
            "추진일정은 약 6개월 간격으로 세부단계를 설정하고, PM 주관 하에 분기별 점검이 이뤄집니다."
        ],
        "효과": [
            "교통 체증 완화와 함께, 시민의 이동 편의성이 증대됩니다.",
            "사업을 통해 연간 약 5억 원의 비용 절감 효과가 기대됩니다."
        ],
        "사업관리": [
            "사업관리는 주관기관과 협력업체 간의 정기 회의 및 성과 점검으로 운영됩니다.",
            "리스크 관리를 위한 백업 계획과 이슈 대응 프로세스를 반드시 포함해야 합니다."
        ]
    }
    for key, value in mapping.items():
        if key in section_title:
            return value
    return ["해당 항목에 대한 예시가 준비되지 않았습니다."]

# 시각화 구성
def visualize_feedback(section, status, examples):
    color_map = {
        "포함됨": "✅",
        "부분 포함": "⚠️",
        "누락됨": "❌"
    }
    st.markdown(f"**검출 상태:** {color_map.get(status, '❓')} `{status}`")
    st.markdown("**✒️ 작성 예시:**")
    for ex in examples:
        st.markdown(f"- {ex}")

# ==============================
# 📄 PDF 텍스트 추출 함수
# ==============================

def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# ==============================
# 🎯 Streamlit 메인 앱
# ==============================

st.set_page_config(page_title="AI 제안서 작성 도우미", layout="wide")
st.title("📑 제안요청서 기반 AI 피드백 도우미")

uploaded_rfp = st.file_uploader("📌 제안요청서(PDF)를 업로드하세요", type=["pdf"])

if uploaded_rfp:
    rfp_text = extract_text_from_pdf(uploaded_rfp)
    rfp_title = get_proposal_title_from_filename(uploaded_rfp.name)
    st.subheader(f"📝 제안요청서 제목: {rfp_title}")

    st.markdown("---")
    st.markdown("## 📂 자동 추출된 주요 항목")
    rfp_sections = extract_sections_from_text(rfp_text)

    if not rfp_sections:
        st.warning("❌ 항목을 찾을 수 없습니다.")
    else:
        for section in rfp_sections:
            with st.expander(f"🔹 {section}"):
                status = "부분 포함" if len(section) >= 8 else "누락됨"
                examples = get_examples_for_section(section)
                visualize_feedback(section, status, examples)
