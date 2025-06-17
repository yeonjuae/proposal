
import streamlit as st
from pdf_extractor import extract_text_from_pdf
from comparator import compare_documents
from feedback_generator import generate_feedback

st.set_page_config(page_title="제안서 피드백 생성기", layout="centered")

st.title("📄 제안서 피드백 자동 생성기")
st.markdown("제안요청서와 제안서를 업로드하면 자동으로 차이점을 분석하고 피드백을 생성합니다.")

# PDF 업로드
req_file = st.file_uploader("📤 제안요청서 PDF 업로드", type=["pdf"], key="req")
prop_file = st.file_uploader("📤 제안서 PDF 업로드", type=["pdf"], key="prop")

# 버튼 클릭 시 분석 실행
if st.button("🧠 자동 피드백 생성"):
    if not req_file or not prop_file:
        st.warning("두 PDF 파일을 모두 업로드해주세요.")
    else:
        with st.spinner("PDF에서 텍스트 추출 중..."):
            request_text = extract_text_from_pdf(req_file)
            proposal_text = extract_text_from_pdf(prop_file)

        with st.spinner("문서 비교 중..."):
            comparison = compare_documents(request_text, proposal_text)

        with st.expander("🔍 비교 결과 요약 보기"):
            if comparison["missing"]:
                st.subheader("❌ 누락된 항목")
                for item in comparison["missing"]:
                    st.write(f"- {item}")
            if comparison["unmatched"]:
                st.subheader("⚠️ 내용이 다른 항목")
                for req, prop in comparison["unmatched"]:
                    st.write(f"- 요청: {req}")
                    st.write(f"  제안: {prop}")

        with st.spinner("🤖 피드백 문장 생성 중..."):
            api_key = st.secrets["groq_api_key"]
            result = generate_feedback(api_key, comparison)

        st.success("완료되었습니다!")
        st.markdown("### ✍️ 생성된 피드백 문장:")
        st.write(result)
