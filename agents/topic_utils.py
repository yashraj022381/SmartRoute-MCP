import re
 
 
def is_pure_arithmetic(topic: str) -> bool:
    """
    Detects a bare calculation like 'what is 2 + 2?' or '15 * 7' - a
    question that deserves a direct short answer, not a web search or a
    multi-paragraph article.
    """
    stripped = re.sub(r"\b(what'?s?|is|calculate|compute)\b", "", topic, flags=re.IGNORECASE)
    stripped = stripped.strip(" ?.!")
    if not stripped:
        return False
    return bool(re.fullmatch(r"[\d\s+\-*/xX.()]+", stripped)) and any(c.isdigit() for c in stripped)
