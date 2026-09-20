"""
eval_questions.py

100 questions of varying difficulty, used by run_eval.py to test the
router at scale. Roughly split into easy/simple lookups and hard/complex
reasoning tasks - a real mix, like a school exam covering both easy warm
up questions and the hard essay questions at the end.
"""

EASY_QUESTIONS = [
    "What is the capital of Japan?",
    "Define gravity.",
    "What is 15 + 27?",
    "Who wrote Romeo and Juliet?",
    "What is the boiling point of water in Celsius?",
    "Translate 'hello' to Spanish.",
    "What year did World War 2 end?",
    "Define photosynthesis.",
    "What is the capital of Australia?",
    "Who painted the Mona Lisa?",
    "What's 100 divided by 4?",
    "What is the largest planet in our solar system?",
    "Define democracy.",
    "What is the chemical symbol for gold?",
    "Who is the current king of England?",
    "What's the freezing point of water in Fahrenheit?",
    "Define inflation.",
    "What is the capital of Canada?",
    "How many continents are there?",
    "What's 7 times 8?",
    "Define ecosystem.",
    "Who invented the telephone?",
    "What is the capital of Egypt?",
    "Define metabolism.",
    "What's the square root of 64?",
    "What is the tallest mountain in the world?",
    "Define renewable energy.",
    "Who wrote Pride and Prejudice?",
    "What is the capital of Brazil?",
    "What's 12 squared?",
    "Define supply and demand.",
    "What is the smallest country in the world?",
    "Who discovered penicillin?",
    "What's the capital of South Korea?",
    "Define natural selection.",
    "What is the speed of light?",
    "Who wrote 1984?",
    "What's 9 times 9?",
    "Define GDP.",
    "What is the longest river in the world?",
    "What's the capital of Italy?",
    "Define osmosis.",
    "Who was the first person on the moon?",
    "What's 45 minus 18?",
    "Define climate.",
    "What is the capital of Germany?",
    "Who wrote The Great Gatsby?",
    "What's the atomic number of oxygen?",
    "Define herbivore.",
    "What's 6 times 7?",
]

HARD_QUESTIONS = [
    "Compare and analyze the trade-offs between renewable and fossil fuel "
    "energy sources for a developing economy.",
    "Write a Python function that reverses a linked list, and explain step "
    "by step how it works.",
    "Design a strategy to optimize a supply chain for a mid-size e-commerce "
    "company, considering cost, speed, and sustainability trade-offs.",
    "Explain in detail the architecture trade-offs between microservices "
    "and monolithic systems, and design a migration plan.",
    "Analyze the pros and cons of universal basic income and evaluate its "
    "potential economic impact.",
    "Derive the quadratic formula and explain each step of the process.",
    "Compare the economic policies of Keynesianism and Austrian economics, "
    "and analyze which is better suited for a recession.",
    "Write a function to detect cycles in a graph and explain the "
    "algorithm's time complexity in detail.",
    "Evaluate the trade-offs between SQL and NoSQL databases for a "
    "high-traffic social media application, and design a schema strategy.",
    "Explain step by step how a neural network learns through "
    "backpropagation, including the math behind gradient descent.",
    "Compare and analyze the geopolitical strategy differences between the "
    "US and China's approaches to global trade.",
    "Design an algorithm to detect fraud in financial transactions, and "
    "explain the trade-offs between accuracy and speed.",
    "Write code to implement a binary search tree with insert, delete, and "
    "search operations, explaining the reasoning behind each method.",
    "Analyze the trade-offs between centralized and decentralized "
    "governance systems, using historical examples.",
    "Explain in detail the strategy behind optimizing a machine learning "
    "model for both accuracy and inference speed.",
    "Compare the architectural trade-offs of REST versus GraphQL APIs for "
    "a large-scale application, and design a migration strategy.",
    "Derive the formula for compound interest and explain how it applies "
    "to long-term investment strategy.",
    "Analyze and evaluate the pros and cons of remote work versus "
    "in-office work for software engineering teams.",
    "Write a step-by-step algorithm to sort a large dataset efficiently, "
    "and explain the trade-offs between different sorting algorithms.",
    "Design a strategy to reduce technical debt in a legacy codebase while "
    "maintaining feature velocity, analyzing the trade-offs involved.",
]

ALL_QUESTIONS = EASY_QUESTIONS + HARD_QUESTIONS  # 50 + 20 = 70

# Pad up to exactly 100 by cycling through variations, so we have a solid
# round number for the report (this also tests the classifier on
# near-duplicate phrasing, which is realistic - real users repeat
# themselves in slightly different words all the time).
EXTRA_EASY_TEMPLATES = [
    "What is {}?",
    "Define {}.",
    "Who discovered {}?",
]
EXTRA_TOPICS = [
    "the mitochondria", "the water cycle", "electricity", "gravity waves",
    "the internet", "vaccines", "plate tectonics", "the stock market",
    "black holes", "DNA",
]

for template in EXTRA_EASY_TEMPLATES:
    for topic in EXTRA_TOPICS:
        ALL_QUESTIONS.append(template.format(topic))
        if len(ALL_QUESTIONS) >= 100:
            break
    if len(ALL_QUESTIONS) >= 100:
        break

ALL_QUESTIONS = ALL_QUESTIONS[:100]
