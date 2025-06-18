import streamlit as st
from groq import Groq
import os

# GROQ API 키 불러오기
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

st.set_page_config(page_title="Groq 챗봇", layout="centered")
st.title("🤖 Groq 기반 제안서 챗봇")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 입력창
user_input = st.text_input("무엇이든 물어보세요:", key="input")

# 대화 표시
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**🙋‍♀️ 나:** {msg}")
    else:
        st.markdown(f"**🤖 Groq:** {msg}")

# 대화 로직
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.spinner("Groq가 답변 중..."):
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "당신은 공공 제안서를 잘 작성하는 전문가입니다."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.4
        )
        answer = response.choices[0].message.content.strip()
        st.session_state.chat_history.append(("assistant", answer))
        st.rerun()
