from groq import Groq

# ⚠️ 여기에 직접 Groq 키를 입력하세요 (Streamlit에서는 secrets 사용 권장)
client = Groq(api_key="")

def analyze_section_with_groq(section_text, index):
    section_text = section_text.encode("utf-8", "ignore").decode("utf-8")  # ✅ 한글 인코딩 문제 해결
    prompt = f"""
    [제안요청 항목 {index+1}]
    {section_text}

    [작성 가이드]
    위 항목에 대해 제안서를 쓸 때 어떤 내용을 넣으면 좋을지 구체적인 예시 문장으로 알려줘.
    반드시 항목에 어울리는 내용으로만 작성하고, 중복되거나 추상적인 내용은 빼줘.
    """
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "당신은 공공사업 제안서를 전문적으로 작성하는 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
