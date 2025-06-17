import streamlit as st
import time
import logging
from typing import List, Dict
from datetime import datetime
from groq import Groq

# ================================================================
# 🛠️ Groq 기반 피드백 생성기 (Streamlit secrets.toml 버전)
# ================================================================

# 🔐 secrets.toml에서 API 키 불러오기
GROQ_API_KEY = st.secrets["groq_api_key"]

# 🤖 Groq API 클라이언트 초기화
client = Groq(api_key=GROQ_API_KEY)

# 📋 메시지 포맷 생성 함수
def build_messages(prompt: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "당신은 대한민국 공공기관의 제안서 심사위원입니다. "
                "제안요청서(RFP) 항목별로 제안서가 얼마나 충실히 작성되었는지 평가하십시오. "
                "‘포함됨’, ‘부분 포함’, ‘누락됨’ 상태에 따라 명확하고 전문적인 피드백을 작성해 주세요. "
                "말투는 공손하지만 분석적이어야 하며, 항목별로 간결하게 정리해 주세요."
            )
        },
        {
            "role": "user",
            "content": clean_prompt(prompt)
        }
    ]

# 🧼 프롬프트 클린징
def clean_prompt(prompt: str) -> str:
    cleaned = prompt.replace("\n\n", "\n").strip()
    return cleaned

# 🔍 항목별 피드백 요약 유틸
def summarize_sections(prompt: str) -> List[str]:
    lines = prompt.strip().split("\n")
    summaries = []
    for line in lines:
        if "→" in line:
            try:
                key, value = line.split("→")
                summaries.append(f"[요약] {key.strip()}: {value.strip()}")
            except ValueError:
                summaries.append(f"[형식 오류] {line}")
    return summaries

# 📦 유효성 검사 함수
def validate_prompt(prompt: str) -> bool:
    if not prompt or not isinstance(prompt, str):
        return False
    if "→" not in prompt:
        return False
    return True

# 📁 로깅 설정
LOG_PATH = "feedback_log.txt"
def log_event(message: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {message}\n")

# 🤖 피드백 생성 함수
def generate_feedback(prompt: str, debug: bool = False) -> str:
    if not validate_prompt(prompt):
        return "❌ 유효하지 않은 프롬프트 형식입니다. 항목별 ‘→ 포함 상태’ 형식을 따르세요."

    try:
        messages = build_messages(prompt)
        start_time = time.time()

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # 또는 llama3-70b-8192
            messages=messages,
            temperature=0.65,
            max_tokens=2000,
            top_p=1,
            stop=None
        )

        elapsed = round(time.time() - start_time, 2)
        content = response.choices[0].message.content.strip()

        log_event(f"피드백 생성 성공 (소요 시간: {elapsed}s)")

        if debug:
            return f"=== [디버그 모드] ===\n{content}\n\n⏱ 처리 시간: {elapsed}s"
        return content

    except Exception as e:
        log_event(f"⚠️ 피드백 생성 실패: {e}")
        return f"❌ 피드백 생성 중 오류가 발생했습니다: {e}"
