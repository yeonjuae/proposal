import streamlit as st
from pdf_extractor import extract_text_from_pdf
from groq import Groq

st.set_page_config(page_title="제안서 도우미", layout="wide")

tabs = st.tabs(["📄 제안서 비교", "💬 Groq 챗봇"])

# 📄 제안서 비교 탭
with tabs[0]:
    st.header("📄 제안서 PDF 업로드")
    col1, col2 = st.columns(2)
    rfp_file = col1.file_uploader("제안요청서 PDF", type="pdf", key="rfp")
    proposal_file = col2.file_uploader("제안서 PDF", type="pdf", key="proposal")

    if rfp_file and proposal_file:
        rfp_text = extract_text_from_pdf(rfp_file)
        proposal_text = extract_text_from_pdf(proposal_file)
        st.subheader("✅ 텍스트 일부 미리보기")
        st.code(rfp_text[:500], language='markdown')
        st.code(proposal_text[:500], language='markdown')
    else:
        st.info("양쪽 PDF를 업로드하면 미리보기가 시작됩니다.")

# 💬 Groq 챗봇 탭
with tabs[1]:
    st.header("💬 제안서 챗봇 (Groq)")
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "당신은 공공사업 제안서를 작성하는 전문가입니다."}
        ]

    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("제안서 항목이나 질문을 입력하세요.")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Groq가 응답 중..."):
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=st.session_state.messages,
                    temperature=0.4,
                )
                reply = response.choices[0].message.content.strip()
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
