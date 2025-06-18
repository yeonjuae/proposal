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

# 추가 기능 1: 항목별 작성 가이드 및 예시 표시
def get_writing_guide(title):
    # 키워드 기반 예시 텍스트 추천
    if "기능" in title:
        return "이 항목에는 시스템 구성도, 흐름도, 주요 기능을 도표로 설명하는 것이 좋습니다.\n예시: '본 시스템은 실시간 교통정보 수집, 분석, 시각화를 포함한 3대 기능을 중심으로 구성됩니다.'"
    elif "전략" in title or "방향" in title:
        return "이 항목에는 사업의 추진 전략, 단계별 로드맵, 기대 효과를 포함하세요.\n예시: '단계별 전략은 인프라 고도화 → 데이터 통합 → 지능형 서비스로 이어집니다.'"
    elif "효과" in title or "기대" in title:
        return "정량적 기대성과(예: 처리시간 단축 %, 예산 절감액)와 정성적 효과(정책 반영, 대시민 서비스 향상)를 서술하면 좋습니다."
    else:
        return "작성 시 항목의 요구사항에 따라 도식, 표, 사례 등을 활용해 구체적으로 작성하는 것이 좋습니다."

# 기존 비교 루프 내에서 작성 가이드 및 예시를 추가로 출력
# → 기존 app.py 코드 중 for idx, (section_title, section_body) in enumerate(rfp_sections.items(), start=1): 아래에 삽입 필요

                with st.expander("✍ 작성 가이드 및 예시", expanded=False):
                    st.markdown(get_writing_guide(section_title))
