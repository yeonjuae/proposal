import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq 대화 인터페이스", layout="wide")
st.title("💬 Groq와 대화하기")

# 키는 환경변수나 secrets.toml에 저장되었어야 함
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("Groq에게 물어보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Groq가 생각 중..."):
        try:
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "당신은 제안서, 공공문서, 사업계획서를 도와주는 전문 AI입니다."},
                    *st.session_state.messages
                ],
                temperature=0.6,
            )
            reply = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "content": reply})

            with st.chat_message("assistant"):
                st.markdown(reply)
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")