
import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from groq import Groq

# ================================================================
# 🛠️ Groq 기반 피드백 생성기 (고급 버전)
# - 제안요청서와 제안서를 비교하여 생성된 항목별 분석 결과를 기반으로
#   전문가처럼 피드백을 생성하는 Streamlit 보조 모듈
# - 이 버전은 로깅, 유닛 테스트, 포맷 정리 기능 포함
# ================================================================

# ------------------------------------------------------------
# 🔐 환경변수 설정 및 검사
# ------------------------------------------------------------
GROQ_API_KEY = os.environ.get("groq_api_key")

if not GROQ_API_KEY:
    raise EnvironmentError("❌ 환경 변수 'groq_api_key'가 설정되지 않았습니다. secrets.toml 또는 시스템 환경 설정을 확인하세요.")

# ------------------------------------------------------------
# 🤖 Groq API 클라이언트 초기화
# ------------------------------------------------------------
client = Groq(api_key=GROQ_API_KEY)

# ------------------------------------------------------------
# 📋 메시지 포맷 생성 함수
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# 🧼 프롬프트 클린징
# ------------------------------------------------------------
def clean_prompt(prompt: str) -> str:
    cleaned = prompt.replace("\n\n", "\n").strip()
    return cleaned

# ------------------------------------------------------------
# 🔍 항목별 피드백 요약 유틸
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# 📦 유효성 검사 함수
# ------------------------------------------------------------
def validate_prompt(prompt: str) -> bool:
    if not prompt or not isinstance(prompt, str):
        return False
    if "→" not in prompt:
        return False
    return True

# ------------------------------------------------------------
# 📁 로깅 설정
# ------------------------------------------------------------
LOG_PATH = "feedback_log.txt"

def log_event(message: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {message}\n")

# ------------------------------------------------------------
# 🤖 피드백 생성 함수 (핵심 함수)
# ------------------------------------------------------------
def generate_feedback(prompt: str, debug: bool = False) -> str:
    """
    Groq API를 사용하여 전문가 수준의 제안서 피드백을 생성합니다.

    Parameters:
        prompt (str): 항목별 포함 여부 목록 (ex. "[3.1 보안] → 포함됨")
        debug (bool): 디버그 모드 활성화 여부

    Returns:
        str: 전문가 피드백 문장
    """
    if not validate_prompt(prompt):
        return "❌ 유효하지 않은 프롬프트 형식입니다. 항목별 ‘→ 포함 상태’ 형식을 따르세요."

    try:
        messages = build_messages(prompt)
        start_time = time.time()

        # Groq API 호출
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            temperature=0.65,
            max_tokens=2000,
            top_p=1,
            stop=None
        )

        elapsed = round(time.time() - start_time, 2)
        content = response.choices[0].message.content.strip()

        # 로깅
        log_event(f"피드백 생성 성공 (소요 시간: {elapsed}s)")

        if debug:
            return f"=== [디버그 모드] ===\n{content}\n\n⏱ 처리 시간: {elapsed}s"
        return content

    except Exception as e:
        log_event(f"⚠️ 피드백 생성 실패: {e}")
        return f"❌ 피드백 생성 중 오류가 발생했습니다: {e}"

# ------------------------------------------------------------
# 🧪 테스트 케이스 모음
# ------------------------------------------------------------
def run_test_case():
    sample_prompt = (
        "[3.1 보안 기술 명시] → 부분 포함\n"
        "[3.2 주요 기능 설명] → 누락됨\n"
        "[3.3 데이터 수집 방법] → 포함됨\n"
        "[3.4 유지보수 방안] → 누락됨\n"
        "[3.5 이행 일정 제시] → 포함됨"
    )
    print("🧪 테스트용 샘플 프롬프트 입력:")
    print(sample_prompt)
    print("\n🎯 요약 항목:")
    for line in summarize_sections(sample_prompt):
        print(line)
    print("\n📝 생성된 피드백:")
    print(generate_feedback(sample_prompt, debug=True))


# ------------------------------------------------------------
# 🧾 포맷 안내 템플릿
# ------------------------------------------------------------
def get_format_guide() -> str:
    return (
        "📌 항목별 프롬프트 예시:\n"
        "[3.1 보안 기술 명시] → 포함됨\n"
        "[3.2 주요 기능 설명] → 누락됨\n"
        "[3.3 데이터 수집 방법] → 부분 포함\n"
        "\n위와 같이 '[항목명] → 상태' 형태로 작성해 주세요."
    )


# ------------------------------------------------------------
# ▶️ 모듈 단독 실행 시 테스트
# ------------------------------------------------------------
if __name__ == "__main__":
    print("✅ [피드백 생성기 유닛 테스트 시작]")
    print(get_format_guide())
    print("-" * 40)
    run_test_case()
    print("✅ [테스트 완료]")
