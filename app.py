
import streamlit as st
from comparator import compare_documents_v2
from pdf_extractor import (
    extract_text_from_pdf,
    extract_text_by_page,
    summarize_pdf_statistics,
    get_file_info
)
from feedback_generator import generate_feedback
import re

# 📌 목차 기반 키워드 자동 추출
def extract_keywords_from_rfp(rfp_text: str) -> list:
    # 숫자형 목차 패턴 예: 1. 기술 제안 / 3.2 시스템 개요
    pattern = r"\n?\s*(?:[0-9]{1,2}(?:\.[0-9]{1,2})*)[\)\.\-]?[\s·]*([가-힣A-Za-z ]{2,30})"
    matches = re.findall(pattern, rfp_text)
    cleaned = set()
    for match in matches:
        for word in re.split(r"[ /,·]", match.strip()):
            if 2 <= len(word) <= 12:
                cleaned.add(word)
    return list(cleaned)

def filter_rfp_by_keywords(rfp_text: str, keywords: list) -> str:
    lines = [line.strip() for line in rfp_text.split("\n") if line.strip()]
    filtered = [line for line in lines if any(k in line for k in keywords)]
    return "\n".join(filtered)

# 📄 앱 구성
st.set_page_config(page_title="제안서 자동 피드백 시스템", layout="wide")
st.title("📑 제안요청서 기반 제안서 피드백 자동 생성기")
st.markdown("제안요청서의 목차를 분석하여 관련 키워드를 자동 추출하고 해당 항목만 비교합니다.")

col1, col2 = st.columns(2)
with col1:
    rfp_file = st.file_uploader("📥 제안요청서 PDF 업로드", type="pdf", key="rfp")
with col2:
    proposal_file = st.file_uploader("📥 제안서 PDF 업로드", type="pdf", key="proposal")

if rfp_file and proposal_file:

    st.subheader("🧾 업로드된 파일 정보")
    col1, col2 = st.columns(2)
    col1.json(get_file_info(rfp_file))
    col2.json(get_file_info(proposal_file))

    with st.spinner("📖 텍스트 추출 중..."):
        rfp_file.seek(0)
        rfp_text = extract_text_from_pdf(rfp_file)

        proposal_file.seek(0)
        proposal_text = extract_text_from_pdf(proposal_file)

        rfp_file.seek(0)
        rfp_page_data = extract_text_by_page(rfp_file.read())

        proposal_file.seek(0)
        proposal_page_data = extract_text_by_page(proposal_file.read())

    st.subheader("📊 문서 통계 분석")
    tab1, tab2 = st.tabs(["제안요청서", "제안서"])
    with tab1:
        st.json(summarize_pdf_statistics(rfp_page_data))
    with tab2:
        st.json(summarize_pdf_statistics(proposal_page_data))

    # 🧠 목차 키워드 추출
    keywords = extract_keywords_from_rfp(rfp_text)
    st.subheader("📘 목차 기반 자동 키워드")
    st.write(keywords if keywords else "❗ 자동 추출된 키워드가 없습니다. 제안요청서를 확인해주세요.")

    filtered_rfp_text = filter_rfp_by_keywords(rfp_text, keywords) if keywords else rfp_text
    st.subheader("📃 자동 선별된 항목")
    st.code(filtered_rfp_text if filtered_rfp_text.strip() else "[⚠️ 키워드에 해당하는 항목이 없습니다.]")

    # 🔍 항목 비교
    comparison_result = compare_documents_v2(filtered_rfp_text, proposal_text)

    for item in comparison_result:
        st.markdown(f"### 📌 {item['항목']}")
        st.write(f"- 포함 여부: `{item['포함여부']}`")
        st.write(f"- 키워드 수: `{item['키워드수']}`")
        st.write(f"- 매칭률: `{item['매칭률'] * 100}%`")

    # 🤖 피드백
    if st.button("🤖 항목 기반 피드백 생성"):
        with st.spinner("AI가 피드백을 작성 중입니다..."):
            prompt_text = ""
            for item in comparison_result:
                prompt_text += f"[{item['항목']}] → {item['포함여부']}\n"
            feedback = generate_feedback(prompt_text)
        st.subheader("📝 생성된 피드백")
        st.write(feedback)

else:
    st.info("좌측의 제안요청서와 제안서를 모두 업로드해 주세요.")
