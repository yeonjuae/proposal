
import fitz  # PyMuPDF
import os
import datetime
from typing import Optional, List, Dict

# ================================================================
# 📄 PDF 텍스트 추출기 (확장형 500줄 수준)
# - 기능: 텍스트 추출 + 통계 + 구조 정보 수집 + 에러 로깅
# ================================================================


# ------------------------------------------------------------
# 📘 페이지별 텍스트 추출 함수
# ------------------------------------------------------------
def extract_text_by_page(file_bytes: bytes) -> List[Dict]:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_data = []

        for i, page in enumerate(doc):
            text = page.get_text("text")
            images = page.get_images(full=True)
            chars = len(text)
            has_image = bool(images)
            entry = {
                "page_number": i + 1,
                "character_count": chars,
                "has_image": has_image,
                "text": text.strip() if text else "[빈 페이지]"
            }
            page_data.append(entry)

        return page_data

    except Exception as e:
        return [{"page_number": 0, "error": str(e), "text": "[오류 발생]"}]


# ------------------------------------------------------------
# 📄 전체 PDF 통합 텍스트 추출
# ------------------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    """
    Streamlit 업로드 객체 또는 바이너리에서 전체 텍스트 추출
    """
    try:
        file_bytes = uploaded_file.read()
        pages = extract_text_by_page(file_bytes)
        full_text = "\n".join([p["text"] for p in pages if "text" in p])
        return full_text

    except Exception as e:
        return f"[PDF 텍스트 추출 실패]: {e}"


# ------------------------------------------------------------
# 📦 PDF 통계 요약
# ------------------------------------------------------------
def summarize_pdf_statistics(page_data: List[Dict]) -> Dict:
    total_pages = len(page_data)
    total_characters = sum(p.get("character_count", 0) for p in page_data)
    pages_with_images = sum(1 for p in page_data if p.get("has_image"))
    blank_pages = sum(1 for p in page_data if not p.get("text") or p["text"] in ("[빈 페이지]", ""))

    return {
        "총 페이지 수": total_pages,
        "총 문자 수": total_characters,
        "이미지 포함 페이지 수": pages_with_images,
        "빈 페이지 수": blank_pages,
        "텍스트 평균 길이": round(total_characters / total_pages, 2) if total_pages > 0 else 0
    }


# ------------------------------------------------------------
# 🧪 로컬 경로에서 PDF 텍스트 추출
# ------------------------------------------------------------
def extract_text_from_local_pdf(path: str) -> str:
    if not os.path.exists(path):
        return "[파일 없음]"
    with open(path, "rb") as f:
        return extract_text_from_pdf(f)


# ------------------------------------------------------------
# 🧪 전체 메타정보 및 구조 분석 출력
# ------------------------------------------------------------
def analyze_pdf_structure(uploaded_file) -> Dict:
    file_bytes = uploaded_file.read()
    page_data = extract_text_by_page(file_bytes)
    stats = summarize_pdf_statistics(page_data)
    return {
        "통계": stats,
        "페이지별 정보": page_data
    }


# ------------------------------------------------------------
# 🧾 파일 정보 출력 (Streamlit 업로드 파일 기준)
# ------------------------------------------------------------
def get_file_info(uploaded_file) -> Dict:
    try:
        return {
            "파일명": uploaded_file.name,
            "파일크기(Byte)": uploaded_file.size,
            "업로드시간": datetime.datetime.now().isoformat()
        }
    except Exception:
        return {"파일 정보": "불러올 수 없음"}


# ------------------------------------------------------------
# ▶️ 유닛 테스트 코드 (직접 실행 시)
# ------------------------------------------------------------
if __name__ == "__main__":
    test_file = "sample.pdf"

    if not os.path.exists(test_file):
        print("❌ sample.pdf 파일이 현재 디렉토리에 없습니다.")
    else:
        with open(test_file, "rb") as f:
            file_bytes = f.read()

        print("✅ 페이지별 텍스트 추출")
        page_data = extract_text_by_page(file_bytes)
        for p in page_data:
            print(f"- 페이지 {p['page_number']} | 문자수: {p['character_count']} | 이미지 포함: {p['has_image']}")

        print("\n📊 PDF 통계")
        stats = summarize_pdf_statistics(page_data)
        for k, v in stats.items():
            print(f"{k}: {v}")

        print("\n🧾 전체 텍스트 미리보기:")
        print("\n".join([p["text"][:100] for p in page_data if "text" in p]))
