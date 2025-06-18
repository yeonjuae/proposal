
import streamlit as st
import re
from comparator import compare_documents_v2
from pdf_extractor import (
    extract_text_from_pdf,
    extract_text_by_page,
    summarize_pdf_statistics,
    get_file_info
)
from feedback_generator import generate_feedback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 🔍 제안서 제목 추출
def extract_document_title(text: str) -> str:
    candidates = text.split("\n")
    candidates = [line.strip() for line in candidates if len(line.strip()) > 5 and len(line.strip()) < 60]
    for line in candidates:
        if any(keyword in line for keyword in ["제안서", "계획", "방안", "구축", "시스템"]):
            return line
    return candidates[0] if candidates else "제안 제목 미상"

# 📘 제안요청서에서 가장 유사한 문단만 추출
def get_best_matching_section(rfp_text: str, title: str) -> str:
    paragraphs = [p.strip() for p in rfp_text.split("\n\n") if len(p.strip()) > 30]
    if not paragraphs:
        return "[❗ 유효한 문단이 없습니다.]"

    vectorizer = TfidfVectorizer().fit(paragraphs + [title])
    para_vectors = vectorizer.transform(paragraphs)
    title_vector = vectorizer.transform([title])

    scores = cosine_similarity(title_vector, para_vectors)[0]
    top_idx = scores.argmax()
    top_score = scores[top_idx]

    if top_score < 0.1:
        return "[❗ 관련 항목을 찾을 수 없습니다.]"

    return paragraphs[top_idx]

# 📄 앱 구성
st.set_page_config(page_title="제안서 피드백 시스템 (고도화)", layout="wide")
st.title("🧠 제안서 제목 기반 항목 비교 시스템 (유사도 정밀 추출 버전)")

col1, col2 = st.columns(2)
with col1:
    rfp_file = st.file_uploader("📥 제안요청서 PDF 업로드", type="pdf", key="rfp")
with col2:
    proposal_file = st.file_uploader("📥 제안서 PDF 업로드", type="pdf", key="proposal")

if rfp_file and proposal_file:
    st.subheader("📄 문서 정보")
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

    st.subheader("📊 문서 통계")
    tab1, tab2 = st.tabs(["제안요청서", "제안서"])
    with tab1:
        st.json(summarize_pdf_statistics(rfp_page_data))
    with tab2:
        st.json(summarize_pdf_statistics(proposal_page_data))

    st.subheader("📝 제안서 제목 자동 추출")
    proposal_title = extract_document_title(proposal_text)
    st.write(f"📌 추출된 제안서 제목: **{proposal_title}**")

    st.subheader("🎯 유사도 기반 제안요청서 항목 자동 추출")
    matched_section = get_best_matching_section(rfp_text, proposal_title)
    st.code(matched_section)

    st.subheader("📐 항목 비교 결과")
    comparison_result = compare_documents_v2(matched_section, proposal_text)
    for item in comparison_result:
        st.markdown(f"### 🔹 {item['항목']}")
        st.write(f"- 포함 여부: `{item['포함여부']}`")
        st.write(f"- 키워드 수: `{item['키워드수']}`")
        st.write(f"- 매칭률: `{round(item['매칭률'] * 100, 1)}%`")

    if st.button("🧾 피드백 생성"):
        with st.spinner("피드백 작성 중..."):
            prompt_text = ""
            for item in comparison_result:
                prompt_text += f"[{item['항목']}] → {item['포함여부']}\n"
            feedback = generate_feedback(prompt_text)
        st.subheader("🧠 생성된 피드백")
        st.write(feedback)

else:
    st.info("양쪽 문서를 모두 업로드해 주세요.")
