"""
diagnose_cache.py

Run this from the project root: `python diagnose_cache.py`

Prints, for each topic, the closest match currently in chroma_data and its
RAW cosine distance - regardless of any threshold. This tells us the real
numbers your embedding model produces, so we set MAX_DISTANCE based on
evidence instead of a guess.
"""

from rag.vector_store import get_collection, debug_closest_match

TOPICS = [
    "The basics of home composting",
    "The current state of commercial nuclear fusion",
    "How photosynthesis works",
    "The history of the Voyager 1 space probe",
]


if __name__ == "__main__":
    collection = get_collection()
    print(f"Total documents currently in chroma_data: {collection.count()}")

    # Dump every document + its topic metadata, so we can see exactly
    # what's already in there (this is almost certainly the smoking gun).
    if collection.count() > 0:
        everything = collection.get()
        print("\nCurrent contents of the cache:")
        for i, (doc_id, meta) in enumerate(zip(everything["ids"], everything["metadatas"])):
            print(f"  [{i}] topic={meta.get('topic')!r}  id={doc_id}")

    print("\nClosest match per test topic:")
    for topic in TOPICS:
        result = debug_closest_match(topic)
        print(f"  QUERY: {topic!r}")
        print(f"    -> closest_topic={result['closest_topic']!r}  distance={result['distance']}")
