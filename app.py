import streamlit as st
import tempfile
from pdf_extractor import extract_text_from_pdf
from rfp_parser import extract_sections
from guide_generator_v2 import generate_guide
import traceback

st.set_page_config(page_title="📘 실전 제안서 작성 가이드", layout="wide")
st.title("💡 제안요청서 기반 실전형 작성 가이드")

uploaded_rfp = st.file_uploader("📎 제안요청서 PDF 업로드", type="pdf")

if uploaded_rfp:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_rfp.read())
            tmp_path = tmp_file.name

        st.info("🔍 제안요청서 분석 중입니다...")
        rfp_text = extract_text_from_pdf(tmp_path)
        sections = extract_sections(rfp_text)

        if not sections:
            st.warning("⚠️ 항목을 추출할 수 없습니다. PDF를 다시 확인해 주세요.")
        else:
            st.success(f"✅ 총 {len(sections)}개 항목 분석 완료")

            for section in sections:
                with st.expander(f"📘 {section['number']} {section['title']}"):
                    st.markdown("### 📄 원문 내용")
                    st.markdown(f"<div style='background-color:#f9f9f9;padding:10px;border-radius:5px;'>{section['body'][:1500]}...</div>", unsafe_allow_html=True)

                    guide = generate_guide(section)

                    st.markdown("### ✍️ 작성 가이드")
                    st.markdown(f"<pre style='background-color:#eef; padding:15px; border-radius:10px'>{guide}</pre>", unsafe_allow_html=True)

    except Exception as e:
        st.error("🚨 오류 발생")
        st.code(traceback.format_exc())
else:
    st.info("👆 먼저 PDF 파일을 업로드해 주세요.")
