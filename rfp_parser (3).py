import re

def extract_sections_from_text(text):
    sections = {}
    current_section = None

    lines = text.split('\n')
    for line in lines:
        line = line.strip()

        # 항목 포맷: Ⅱ-4 시스템 기능 요구사항, 3. 주요 기능 설명 등 다양한 형식 대응
        match = re.match(r'^(\(?:(?:[ⅠⅡⅢⅣⅤ])|\d+)(?:[-.]\d+)*\)?[\.\)]?)[\s\t]*(.+)', line)
        if match:
            section_number = match.group(1).strip()
            section_title = match.group(2).strip()
            current_section = f"{section_number} {section_title}"
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    # 본문 내용을 다시 합치기
    for key in sections:
        sections[key] = '\n'.join(sections[key]).strip()

    return sections