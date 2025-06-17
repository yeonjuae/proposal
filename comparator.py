
import difflib

def compare_documents(request_text, proposal_text):
    request_lines = [line.strip() for line in request_text.splitlines() if line.strip()]
    proposal_lines = [line.strip() for line in proposal_text.splitlines() if line.strip()]

    missing_items = []
    unmatched_items = []

    for req_line in request_lines:
        matches = difflib.get_close_matches(req_line, proposal_lines, n=1, cutoff=0.7)
        if not matches:
            missing_items.append(req_line)
        elif matches[0] not in proposal_lines:
            unmatched_items.append((req_line, matches[0]))

    return {
        "missing": missing_items,
        "unmatched": unmatched_items
    }
