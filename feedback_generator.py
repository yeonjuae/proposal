
import requests

def generate_feedback(api_key, analysis_result):
    # 차이점 요약
    summary = ""
    if analysis_result["missing"]:
        summary += "다음 항목들이 제안서에서 누락되었습니다:\n" + "\n".join(analysis_result["missing"]) + "\n"
    if analysis_result["unmatched"]:
        summary += "다음 항목들은 요청서와 제안서 간 내용이 다릅니다:\n"
        summary += "\n".join([f"- 요청: {r}\n  제안: {p}" for r, p in analysis_result["unmatched"]])

    # Groq 요청
    prompt = f"""다음은 제안요청서와 제안서 비교 결과입니다. 누락 또는 불일치한 항목에 대해 전문가처럼 자연스러운 피드백 문장을 생성해주세요:

{summary}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    try:
        return result['choices'][0]['message']['content']
    except Exception:
        return f"[오류] Groq 응답 실패: {result}"
