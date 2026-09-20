"""
config.py

Shared constants for the revision loop. Living in one place means
reviewer.py and graph.py can never disagree about what the caps
actually are - previously each file had its own copy of similar logic,
which is exactly how counting bugs like the last one sneak in.
"""

MAX_FACTUAL_REVISIONS = 1    # factual problems get more attempts - getting facts
                              # right matters more than getting them fast
MAX_STYLISTIC_REVISIONS = 1  # style problems are cheaper to fix, 1 attempt is plenty
