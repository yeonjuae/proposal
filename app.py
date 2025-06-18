import streamlit as st
import tempfile
from pdf_extractor import extract_text_from_pdf
from comparator import get_best_matching_section
from feedback_generator import generate_feedback
from rfp_parser import extract_sections_from_text
import traceback
import os

st.set_page_config(page_title="AI 기반 제안서 피드백 시스템", layout="wide")
st.title("📄 제안요청서 vs 제안서 비교 분석")

uploaded_rfp = st.file_uploader("📎 제안요청서 PDF 업로드", type="pdf")
uploaded_proposal = st.file_uploader("📄 제안서 PDF 업로드", type="pdf")

# 작성 가이드 예시 제공 함수
def get_writing_guide(title):
    if "기능" in title:
        return "이 항목에는 시스템 구성도, 흐름도, 주요 기능을 도표로 설명하는 것이 좋습니다.\n예시: '본 시스템은 실시간 교통정보 수집, 분석, 시각화를 포함한 3대 기능을 중심으로 구성됩니다.'"
    elif "전략" in title or "방향" in title:
        return "이 항목에는 사업의 추진 전략, 단계별 로드맵, 기대 효과를 포함하세요.\n예시: '단계별 전략은 인프라 고도화 → 데이터 통합 → 지능형 서비스로 이어집니다.'"
    elif "효과" in title or "기대" in title:
        return "정량적 기대성과(예: 처리시간 단축 %, 예산 절감액)와 정성적 효과(정책 반영, 대시민 서비스 향상)를 서술하면 좋습니다."
    else:
        return "작성 시 항목의 요구사항에 따라 도식, 표, 사례 등을 활용해 구체적으로 작성하는 것이 좋습니다."

if uploaded_rfp and uploaded_proposal:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_rfp:
            tmp_rfp.write(uploaded_rfp.read())
            rfp_path = tmp_rfp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_proposal:
            tmp_proposal.write(uploaded_proposal.read())
            proposal_path = tmp_proposal.name

        rfp_text = extract_text_from_pdf(rfp_path)
        proposal_text = extract_text_from_pdf(proposal_path)

        proposal_title = os.path.basename(uploaded_proposal.name).replace(".pdf", "")
        st.markdown(f"### 📌 제안서 제목 추정: `{proposal_title}`")

        rfp_sections = extract_sections_from_text(rfp_text)
        if not rfp_sections:
            st.warning("❗ 제안요청서 항목을 추출할 수 없습니다.")
            st.stop()

        st.success(f"✅ {len(rfp_sections)}개 항목 인식 완료")

        for idx, (section_title, section_body) in enumerate(rfp_sections.items(), start=1):
            with st.expander(f"{idx}. {section_title}"):
                st.markdown("#### 📄 제안요청서 항목 내용")
                st.write(section_body[:1500] + "..." if len(section_body) > 1500 else section_body)

                try:
                    matched_text, similarity = get_best_matching_section(proposal_text, section_body)
                    st.markdown("#### 🔍 제안서 중 유사한 내용")
                    st.info(f"📊 유사도: `{similarity:.2%}`")
                    st.write(matched_text[:1500] + "..." if len(matched_text) > 1500 else matched_text)

                    feedback = generate_feedback(section_body, matched_text)
                    st.markdown("#### 🧠 AI 피드백")
                    st.markdown(feedback)

                    with st.expander("✍ 작성 가이드 및 예시", expanded=False):
                        st.markdown(get_writing_guide(section_title))

                except Exception:
                    st.error("❌ 항목 비교 또는 피드백 생성 중 오류")
                    st.code(traceback.format_exc())

    except Exception:
        st.error("🚨 처리 중 오류 발생")
        st.code(traceback.format_exc())
else:
    st.info("👆 제안요청서와 제안서를 모두 업로드해 주세요.")
