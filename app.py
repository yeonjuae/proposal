import streamlit as st
from pdf_extractor_with_headings import extract_text_from_pdf, extract_headings_from_text
from groq_helper_direct_key import analyze_section_with_groq

st.set_page_config(page_title="제안요청서 항목 가이드", layout="wide")
st.title("📄 제안요청서 자동 항목 가이드 생성기")

uploaded = st.file_uploader("📥 제안요청서 PDF 업로드", type="pdf")

if uploaded:
    with st.spinner("PDF에서 텍스트 추출 중..."):
        text = extract_text_from_pdf(uploaded)
        headings = extract_headings_from_text(text)

    st.subheader("📚 자동 추출된 주요 항목")
    if not headings:
        st.warning("❌ 목차 스타일 항목을 찾을 수 없습니다.")
    else:
        for i, heading in enumerate(headings):
            with st.expander(f"{i+1}. {heading}", expanded=False):
                if st.button(f"✍️ 작성 예시 보기", key=f"btn_{i}"):
                    with st.spinner("Groq AI로 예시 생성 중..."):
                        try:
                            example = analyze_section_with_groq(heading, i)
                            st.markdown(f"✅ **작성 가이드 예시:**\n\n{example}")
                        except Exception as e:
                            st.error(f"❌ 예시 생성 실패: {e}")
else:
    st.info("👆 상단에서 제안요청서 PDF를 업로드하세요.")
