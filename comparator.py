
import re
import json
from typing import List, Dict
from datetime import datetime

# ====================================================
# 📊 comparator.py (확장형)
# - 제안요청서 항목별 포함 여부 판단 모듈
# - 포함됨 / 부분 포함 / 누락됨 판단 + 키워드 매칭률 계산 + 로깅 포함
# ====================================================

# ----------------------------------------------------
# 🔧 설정: 불용어
# ----------------------------------------------------
DEFAULT_STOPWORDS = {"및", "등", "관련", "사항", "기술", "설명", "필요", "제시", "내용", "수립", "요구"}

# ----------------------------------------------------
# 🧼 텍스트 전처리
# ----------------------------------------------------
def normalize(text: str) -> str:
    return text.lower().strip().replace("“", "").replace("”", "").replace("‘", "").replace("’", "")

# ----------------------------------------------------
# 🔍 핵심 키워드 추출 함수
# ----------------------------------------------------
def extract_keywords(text: str, stopwords: set = DEFAULT_STOPWORDS) -> List[str]:
    text = normalize(text)
    words = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text)
    return [word for word in words if word not in stopwords]

# ----------------------------------------------------
# 📐 키워드 매칭률 계산 함수
# ----------------------------------------------------
def keyword_match_score(keywords: List[str], proposal_text: str) -> float:
    if not keywords:
        return 0.0
    matches = sum(1 for word in keywords if word in proposal_text.lower())
    return round(matches / len(keywords), 2)

# ----------------------------------------------------
# 📊 항목 상태 판단
# ----------------------------------------------------
def determine_status(score: float, threshold_full: float = 0.9, threshold_partial: float = 0.4) -> str:
    if score >= threshold_full:
        return "포함됨"
    elif score >= threshold_partial:
        return "부분 포함"
    else:
        return "누락됨"

# ----------------------------------------------------
# 🧠 항목별 비교 실행
# ----------------------------------------------------
def check_item(request_item: str, proposal_text: str) -> Dict:
    keywords = extract_keywords(request_item)
    score = keyword_match_score(keywords, proposal_text)
    status = determine_status(score)
    return {
        "항목": request_item.strip(),
        "키워드수": len(keywords),
        "매칭률": score,
        "포함여부": status
    }

# ----------------------------------------------------
# 📋 전체 비교 실행
# ----------------------------------------------------
def compare_documents_v2(request_text: str, proposal_text: str) -> List[Dict]:
    request_lines = [line.strip() for line in request_text.split("\n") if line.strip()]
    proposal_text = normalize(proposal_text)
    result = []

    for line in request_lines:
        result.append(check_item(line, proposal_text))

    return result

# ----------------------------------------------------
# 📝 JSON 로그 저장
# ----------------------------------------------------
def save_log(results: List[Dict], filename: str = "compare_log.json"):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_name = f"{filename.replace('.json', '')}_{now}.json"
    with open(full_name, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# ----------------------------------------------------
# 🧪 유닛 테스트 실행
# ----------------------------------------------------
def run_unit_test():
    print("🧪 단위 테스트 시작")
    rfp_text = """3.1 보안 기술 명시
3.2 데이터 수집 방법
3.3 유지보수 방안
3.4 이행 일정
3.5 성과 측정 기준"""
    proposal_text = """
    이 문서에는 보안 방안을 간략히 언급하였으며, 이행 일정과 성과 측정 지표가 포함되어 있습니다.
    데이터 수집은 내부 표준을 따르며 유지보수 내용은 별첨 문서에 있습니다.
    """
    results = compare_documents_v2(rfp_text, proposal_text)
    for r in results:
        print(f"[{r['항목']}] → {r['포함여부']} | 매칭률: {r['매칭률'] * 100}%")

    save_log(results)
    print("✅ 단위 테스트 및 로그 저장 완료")

# ----------------------------------------------------
# ▶️ 직접 실행
# ----------------------------------------------------
if __name__ == "__main__":
    run_unit_test()
