import re
from typing import Tuple, List

# Keywords and regex patterns strictly prohibited by college integrity policies
DISALLOWED_PATTERNS = [
    r"\bassignment\b",
    r"\bassignments\b",
    r"\bhomework\b",
    r"\bexam\b",
    r"\bexams\b",
    r"\bquiz\b",
    r"\bquizzes\b",
    r"\bproxy\b",
    r"\bproxy\s+attendance\b",
    r"\bwrite\s+my\s+paper\b",
    r"\bwrite\s+my\s+essay\b",
    r"\bthesis\s+writing\b",
    r"\bdissertation\s+writing\b",
    r"\blab\s+record\s+copy\b",
    r"\btest\s+paper\b",
    r"\bcheat\s+sheet\b",
    r"\bdo\s+my\s+exam\b",
    r"\bsolve\s+my\s+exam\b",
]

COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in DISALLOWED_PATTERNS]


def scan_for_academic_dishonesty(text: str) -> Tuple[bool, List[str]]:
    """
    Scans a gig's title and description for academic dishonesty keywords.
    Returns:
        (is_flagged, matched_keywords)
    """
    if not text:
        return False, []
    
    matches: List[str] = []
    for pattern in COMPILED_PATTERNS:
        found = pattern.findall(text)
        if found:
            matches.extend(found)
            
    unique_matches = list(set(m.lower().strip() for m in matches))
    return (len(unique_matches) > 0, unique_matches)
