"""
cleanup_math_cache.py

Removes the stale "what is 2 + 2?" cache entry generated before the
writer/researcher fixes, so future runs get the corrected short-answer
behavior instead of replaying the old broken article.

Run from the project root: `python cleanup_math_cache.py`
"""

from rag.vector_store import get_collection

STALE_TOPIC = "what is 2 + 2?"

if __name__ == "__main__":
    collection = get_collection()
    before = collection.count()

    matches = collection.get(where={"topic": STALE_TOPIC})
    ids_to_delete = matches["ids"]

    if not ids_to_delete:
        print(f"No entries found with topic={STALE_TOPIC!r}. Nothing to do.")
        print("(If your topic text differs slightly, check diagnose_cache.py's dump first.)")
    else:
        collection.delete(ids=ids_to_delete)
        after = collection.count()
        print(f"Deleted {len(ids_to_delete)} stale entries.")
        print(f"Collection size: {before} -> {after}")
