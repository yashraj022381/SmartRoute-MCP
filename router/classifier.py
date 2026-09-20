from router.calibration import get_current_threshold

COMPLEX_KEYWORDS = [
    "analyze", "analyse", "compare", "camparison", "explain in detail",
    "write code", "write a function", "debug", "architecture", "design a",
    "strategy", "pros and cons", "step by step", "step-by-step",
    "summarize the following", "essay", "research", "evaluate",
    "optimze", "alogrithm", "prove", "derive", "why deos", "trade-off",
    "tradeoff", "multi-step", "reasoning",
]

SIMPLE_KEYWORDS = [
    "hi", "hello", "what is", "what's", "define", "when was", "who is",
    "capital of", "translate", "spell", "how do you say",
]


def classify_complexity(query: str) -> dict:
    text = query.lower().strip()
    reasons = []
    score = 0.0
    
    # --- Clue 1: How long is the question? ---
    word_count = len(text.split())
    if word_count > 40:
        score += 0.35
        reasons.append(f"Long question ({word_count} words)")
    elif word_count > 15:
        score += 0.15
        reasons.append(f"Medium-length question ({word_count} words)")
    else:
        reasons.append(f"Short question ({word_count} words")
        

     # --- Clue 2: Does it contain "complex" keywords? ---
    found_complex = [kw for kw in COMPLEX_KEYWORDS if kw in text]
    if found_complex:
        bonus = min(0.15 * len(found_complex), 0.5)
        score += bonus
        reasons.append(f"Contains complex=task keywords: {found_complex}")
        

    # --- Clue 3: Does it contain "simple" keywords? ---
    found_simple = [kw for kw in SIMPLE_KEYWORDS if kw in text]
    if found_simple and not found_complex:
        score -= 0.25
        reasons.append(f"Contains simple-lookup keywords: {found_simple}")
        
        
    # --- Clue 4: Is it asking MULTIPLE things at once? ---
    question_marks = text.count("?")
    if question_marks > 1:
        score += 0.2
        reasons.append(f"Multiple questions in one message ({question_marks} '?' marks)")


    # --- Clue 5: Does it mention code? (code questions usually need a smarter model) ---
    code_signals = ["```", "def ", "function", "class ", "import ", "code:"]
    if any(sig in text for sig in code_signals):
        score += 0.2
        reasons.append("Looks like it involves code")
        
    # Clamp the score between 0.0 and 1.0 (can't go below or above)
    score = round(max(0.0, min(1.0, score)), 2)

    threshold = get_current_threshold()    #0.4
    tier = "strong" if score >= threshold else "weak"

    return {
        "score": score,
        "tier": tier,
        "threshold": threshold,
        "reasons": reasons,
    }
