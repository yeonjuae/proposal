
import streamlit as st
from comparator import compare_documents_v2
from pdf_extractor import (
    extract_text_from_pdf,
    extract_text_by_page,
    summarize_pdf_statistics,
    get_file_info
)
from feedback_generator import generate_feedback

# 📄 앱 구성
st.set_page_config(page_title="제안서 자동 피드백 시스템", layout="wide")
st.title("📑 제안요청서 기반 제안서 피드백 자동 생성기")
st.markdown("제안요청서(RFP)와 제안서를 업로드하면 자동으로 비교, 분석, 피드백을 생성합니다.")

# 📁 파일 업로드
col1, col2 = st.columns(2)
with col1:
    rfp_file = st.file_uploader("📥 제안요청서 PDF 업로드", type="pdf", key="rfp")
with col2:
    proposal_file = st.file_uploader("📥 제안서 PDF 업로드", type="pdf", key="proposal")

if rfp_file and proposal_file:

    # 📋 파일 정보 출력
    st.subheader("🧾 업로드된 파일 정보")
    col1, col2 = st.columns(2)
    col1.json(get_file_info(rfp_file))
    col2.json(get_file_info(proposal_file))

    # 🧠 텍스트 추출
    with st.spinner("📖 문서 텍스트 분석 중..."):
        rfp_file.seek(0)
        rfp_text = extract_text_from_pdf(rfp_file)

        proposal_file.seek(0)
        proposal_text = extract_text_from_pdf(proposal_file)

    # 📊 문서 통계 분석
    with st.spinner("📊 문서 통계 계산 중..."):
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

    # 🔍 항목 포함 여부 비교
    st.subheader("🔍 항목 포함 여부 비교")
    comparison_result = compare_documents_v2(rfp_text, proposal_text)

    for item in comparison_result:
        st.markdown(f"### 📌 {item['항목']}")
        st.write(f"- 포함 여부: `{item['포함여부']}`")
        st.write(f"- 키워드 수: `{item['키워드수']}`")
        st.write(f"- 매칭률: `{item['매칭률'] * 100}%`")

    # 🤖 피드백 생성
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
