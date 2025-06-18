import re
import json
from typing import List, Dict, Tuple
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_keywords(text: str) -> List[str]:
    stopwords = set([
        "및", "등", "이", "그", "저", "를", "으로", "에", "의", "은", "는", "가", "하", "고", "도", "다",
        "수", "들", "것", "때", "있", "되", "없", "등", "각", "통해", "대한", "위한"
    ])
    words = re.findall(r'\b[\w가-힣]+\b', text.lower())
    return [word for word in words if word not in stopwords and len(word) > 1]

def keyword_match_score(section_text: str, proposal_text: str) -> float:
    section_keywords = extract_keywords(section_text)
    proposal_keywords = extract_keywords(proposal_text)
    if not section_keywords:
        return 0.0
    match_count = sum((Counter(proposal_keywords) & Counter(section_keywords)).values())
    return match_count / len(section_keywords)

def determine_status(score: float, thresholds=(0.75, 0.4)) -> str:
    if score >= thresholds[0]:
        return "포함됨"
    elif score >= thresholds[1]:
        return "부분 포함"
    else:
        return "누락됨"

def check_item(rfp_section: Tuple[str, str], proposal_text: str) -> Dict:
    title, content = rfp_section
    score = keyword_match_score(content, proposal_text)
    status = determine_status(score)
    return {
        "항목명": title,
        "매칭 점수": round(score, 2),
        "포함여부": status
    }

def compare_documents_v2(rfp_text: str, proposal_text: str) -> List[Dict]:
    sections = []
    lines = rfp_text.splitlines()
    current_title = ""
    current_body = []

    for line in lines:
        line = line.strip()
        if re.match(r'^([0-9]+\.|[Ⅰ-Ⅸ]+)[ \t\-]*', line):
            if current_title and current_body:
                sections.append((current_title, " ".join(current_body)))
                current_body = []
            current_title = line
        elif current_title:
            current_body.append(line)

    if current_title and current_body:
        sections.append((current_title, " ".join(current_body)))

    results = []
    for section in sections:
        result = check_item(section, proposal_text)
        results.append(result)

    return results

def save_log(results: List[Dict], log_path: str = "comparison_log.json"):
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def run_unit_test():
    rfp = '''
    1. 개요: 이 사업은 경주시의 스마트 교통체계 구축을 목적으로 한다.
    2. 주요 기능: 실시간 교통량 수집 및 분석, 교통정보 제공 시스템 구축
    3. 기대 효과: 교통 혼잡 완화 및 시민 만족도 제고
    '''
    proposal = '''
    본 사업은 교통정보 제공 시스템을 중심으로 실시간 데이터 수집 및 분석 체계를 구현하며,
    시민들의 교통편의성을 높이는 것을 목표로 한다.
    '''

    results = compare_documents_v2(rfp, proposal)
    print(json.dumps(results, ensure_ascii=False, indent=2))

# ✅ 추가 기능: TF-IDF 기반 유사 문단 매칭
def get_best_matching_section(document_text: str, target_text: str) -> Tuple[str, float]:
    sections = [s.strip() for s in document_text.split("\n\n") if len(s.strip()) > 30]

    if not sections:
        return "", 0.0

    tfidf = TfidfVectorizer().fit_transform([target_text] + sections)
    cosine_similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    best_index = cosine_similarities.argmax()
    return sections[best_index], float(cosine_similarities[best_index])
