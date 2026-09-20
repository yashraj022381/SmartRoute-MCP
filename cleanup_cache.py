"""
cleanup_cache.py

One-time cleanup: removes the stale duplicate "why the ocean is salty"
entries left over from earlier testing/manual seeding. Safe to run - only
deletes documents whose topic metadata exactly matches that string.

Run from the project root: `python cleanup_cache.py`
"""

from rag.vector_store import get_collection

STALE_TOPIC = "why the ocean is salty"

if __name__ == "__main__":
    collection = get_collection()
    before = collection.count()

    matches = collection.get(where={"topic": STALE_TOPIC})
    ids_to_delete = matches["ids"]

    if not ids_to_delete:
        print(f"No entries found with topic={STALE_TOPIC!r}. Nothing to do.")
    else:
        collection.delete(ids=ids_to_delete)
        after = collection.count()
        print(f"Deleted {len(ids_to_delete)} stale entries.")
        print(f"Collection size: {before} -> {after}")
