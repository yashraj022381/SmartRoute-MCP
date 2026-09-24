from router.calibration import get_current_threshold

COMPLEX_KEYWORDS = [
    "analyze", "analyse", "compare", "comparison", "explain in detail",
    "write code", "write a function", "debug", "architecture", "design a",
    "strategy", "pros and cons", "step by step", "step-by-step",
    "summarize the following", "essay", "research", "evaluate",
    "optimize", "algorithm", "prove", "derive", "why does", "trade-off",
    "tradeoff", "multi-step", "reasoning", "detailed", "comprehensive",
    "in-depth", "critical analysis", "implications", "challenges",
    "advantages and disadvantages", "case study", "real-world",
]

SIMPLE_KEYWORDS = [
    "hi", "hello", "what is", "what's", "define", "when was", "who is",
    "capital of", "translate", "spell", "how do you say",
]

def classify_complexity(query: str) -> dict:
    text = query.lower().strip()
    reasons = []
    score = 0.0

    # --- Clue 1: Length ---
    word_count = len(text.split())
    if word_count > 50:
        score += 0.40
        reasons.append(f"Very long question ({word_count} words)")
    elif word_count > 25:
        score += 0.25
        reasons.append(f"Long question ({word_count} words)")
    elif word_count > 12:
        score += 0.12
        reasons.append(f"Medium-length question ({word_count} words)")
    else:
        reasons.append(f"Short question ({word_count} words)")

    # --- Clue 2: Complex keywords ---
    found_complex = [kw for kw in COMPLEX_KEYWORDS if kw in text]
    if found_complex:
        bonus = min(0.18 * len(found_complex), 0.55)
        score += bonus
        reasons.append(f"Contains complex-task keywords: {found_complex}")

    # --- Clue 3: Simple keywords (only if no complex ones) ---
    found_simple = [kw for kw in SIMPLE_KEYWORDS if kw in text]
    if found_simple and not found_complex:
        score -= 0.30
        reasons.append(f"Contains simple-lookup keywords: {found_simple}")

    # --- Clue 4: Multiple questions ---
    question_marks = text.count("?")
    if question_marks > 1:
        score += 0.20
        reasons.append(f"Multiple questions ({question_marks} '?' marks)")

    # --- Clue 5: Code signals ---
    code_signals = ["```", "def ", "function", "class ", "import ", "code:"]
    if any(sig in text for sig in code_signals):
        score += 0.25
        reasons.append("Looks like it involves code")

    # --- Clue 6: Request for depth / structure ---
    depth_signals = ["detailed", "comprehensive", "in depth", "in-depth", 
                     "step by step", "pros and cons", "advantages", "challenges"]
    if any(sig in text for sig in depth_signals):
        score += 0.15
        reasons.append("Asks for depth or structured analysis")

    # Clamp
    score = round(max(0.0, min(1.0, score)), 2)

    threshold = get_current_threshold()  # usually 0.4
    tier = "strong" if score >= threshold else "weak"

    return {
        "score": score,
        "tier": tier,
        "threshold": threshold,
        "reasons": reasons,
    }
