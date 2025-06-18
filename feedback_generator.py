import re

def extract_sections(text):
    # 항목 번호와 제목 추출 (예: 3.1 주요 기능 설명)
    pattern = r'(\d{1,2}(?:\.\d+)+)\s+([가-힣A-Za-z ]{2,})'
    matches = list(re.finditer(pattern, text))

    sections = []
    for i, match in enumerate(matches):
        section_number = match.group(1).strip()
        section_title = match.group(2).strip()
        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        section_body = text[start:end].strip()
        sections.append({
            "number": section_number,
            "title": section_title,
            "body": section_body
        })

    return sections
