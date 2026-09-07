import re

PATTERNS = [
    # european union directives
    r"\b(eu|european union)\s+(directive|regulation|decision)\b",

    # eur regulations
    r"\b(eu|european union)\s+(regulation|directive|decision)\s+(\d{4}/\d{1,4})\b",

    # french articles
    r"\b(article|art\.)\s+(\d{1,4})\b",

    # RED II / RED III
    r"\b(red\s+(ii|iii))\b",

    # generic eu references
    r"\b(eu|european union)\b",
]


def extract_legal_references(text: str) -> list[str]:
    """
    Extracts legal references from the given text using regex patterns.

    Args:
        text (str): The text from which to extract legal references.

    Returns:
        list: A list of extracted legal references.
    """
    legal_references = []
    for pattern in PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for match in matches:
            # If the match is a tuple (from groups), join it into a single string
            if isinstance(match, tuple):
                legal_references.append(" ".join(match))
            else:
                legal_references.append(match)
    return sorted(legal_references)