import re
from collections import Counter

def extract_keywords(text):
    noun_candidates = re.findall(r'[가-힣]{2,}', text)
    common_terms = ['기능', '흐름도', '구성도', '제시', '연계', '분석', '시스템', '모듈', '지표', '성과', '전략']
    freq = Counter(noun_candidates)
    keywords = [word for word in freq if word in common_terms]
    return keywords[:5]

def extract_actions(text):
    actions = re.findall(r'([가-힣]{2,})(하[라시오])', text)
    return list(set([f"{a[0]}{a[1]}" for a in actions]))

def recommend_visuals(keywords):
    visuals = []
    if any(k in ['흐름도', '연계', '프로세스'] for k in keywords):
        visuals.append("📊 시스템 흐름도")
    if any(k in ['구성도', '모듈', '아키텍처'] for k in keywords):
        visuals.append("🧩 시스템 구성도")
    if any(k in ['지표', '성과', '분석'] for k in keywords):
        visuals.append("📈 정량 분석표 또는 KPI 테이블")
    return visuals or ["💬 시각자료 필요 없음"]

def generate_sample_sentence(keywords, actions):
    base = "이 항목에서는 "
    if keywords:
        base += f"'{keywords[0]}'를 중심으로 "
    if actions:
        base += f"{actions[0]}는 것이 요구됩니다. "
    base += "관련 자료를 표나 도식으로 함께 제시하면 설득력을 높일 수 있습니다."
    return base

def generate_tips():
    return [
        "- 개조식 요약, 도식 자료 활용, 사례 기반 설명이 효과적입니다.",
        "- 항목 요구사항을 다시 한 번 강조하면서 마무리하세요.",
        "- 시각자료는 반드시 캡션과 설명 포함하여 넣으세요."
    ]

def generate_guide(section):
    keywords = extract_keywords(section["body"])
    actions = extract_actions(section["body"])
    visuals = recommend_visuals(keywords)
    sample = generate_sample_sentence(keywords, actions)
    tips = generate_tips()

    guide = f"📌 항목: {section['number']} {section['title']}\n"
    guide += "📑 포함 키워드: " + (', '.join(keywords) if keywords else "추출 불가") + "\n"
    guide += "🛠 요구 동작: " + (', '.join(actions) if actions else "없음") + "\n"
    guide += "🖼 시각자료 제안: " + ', '.join(visuals) + "\n"
    guide += "\n💬 예시 문장:\n" + sample + "\n"
    guide += "\n✍️ 작성 팁:\n" + '\n'.join(tips) + "\n"
    return guide
