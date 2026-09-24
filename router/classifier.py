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
    "future", "impact", "solutions", "discussion", "arguments"
]

SIMPLE_KEYWORDS = [
    "hi", "hello", "what is", "what's", "define", "when was", "who is",
    "capital of", "translate", "spell", "how do you say", "yes", "no"
]


def classify_complexity(query: str) -> dict:
    text = query.lower().strip()
    reasons = []
    score = 0.0

    # --- 1. Length (stronger signal) ---
    word_count = len(text.split())
    if word_count > 45:
        score += 0.45
        reasons.append(f"Very long question ({word_count} words)")
    elif word_count > 22:
        score += 0.28
        reasons.append(f"Long question ({word_count} words)")
    elif word_count > 10:
        score += 0.12
        reasons.append(f"Medium-length question ({word_count} words)")
    else:
        reasons.append(f"Short question ({word_count} words)")

    # --- 2. Complex keywords (stronger bonus) ---
    found_complex = [kw for kw in COMPLEX_KEYWORDS if kw in text]
    if found_complex:
        bonus = min(0.22 * len(found_complex), 0.60)
        score += bonus
        reasons.append(f"Contains complex-task keywords: {found_complex}")

    # --- 3. Simple keywords (only if no complex ones) ---
    found_simple = [kw for kw in SIMPLE_KEYWORDS if kw in text]
    if found_simple and not found_complex:
        score -= 0.35
        reasons.append(f"Contains simple-lookup keywords: {found_simple}")

    # --- 4. Multiple questions ---
    question_marks = text.count("?")
    if question_marks > 1:
        score += 0.22
        reasons.append(f"Multiple questions ({question_marks} '?' marks)")

    # --- 5. Code signals ---
    code_signals = ["```", "def ", "function", "class ", "import ", "code:"]
    if any(sig in text for sig in code_signals):
        score += 0.28
        reasons.append("Looks like it involves code")

    # --- 6. Depth / Analysis signals ---
    depth_signals = [
        "detailed", "comprehensive", "in depth", "in-depth",
        "step by step", "pros and cons", "advantages", "challenges",
        "compare", "comparison", "analyze", "evaluate", "research"
    ]
    if any(sig in text for sig in depth_signals):
        score += 0.18
        reasons.append("Asks for depth or structured analysis")

    # Clamp score
    score = round(max(0.0, min(1.0, score)), 2)

    # Slightly lower threshold for better balance
    threshold = get_current_threshold()
    if threshold > 0.35:
        threshold = 0.35   # force a more reasonable default

    tier = "strong" if score >= threshold else "weak"

    return {
        "score": score,
        "tier": tier,
        "threshold": threshold,
        "reasons": reasons,
    }
