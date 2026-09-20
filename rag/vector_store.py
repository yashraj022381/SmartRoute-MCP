import os
import hashlib
import uuid

import chromadb

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_data")

_client = None
_collection = None

MAX_DISTANCE = 0.5

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="research_notes",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection

def _topic_id(topic: str) -> str:
    return hashlib.sha256(topic.strip().lower().encode()).hexdigest()

def add_research(topic: str, notes: str):
    
    collection = get_collection()
    #collection.add(
    collection.upsert(
        documents=[notes],
        metadatas=[{"topic": topic}],
        #ids=[str(uuid.uuid4())],
        ids=[_topic_id(topic)],
    )

def debug_closest_match(topic: str) -> dict:
    """
    Diagnostic helper: shows the closest match and its RAW distance,
    regardless of whether it passes any threshold. Use this to see the
    actual numbers your real embedding model produces, so we calibrate
    max_distance based on evidence rather than a guess.
    """
    collection = get_collection()

    if collection.count() == 0:
        return {"count": 0, "closest_topic": None, "distance": None}

    result = collection.query(query_texts=[topic], n_results=1)

    if not result["documents"] or not result["documents"][0]:
        return {"count": collection.count(), "closest_topic": None, "distance": None}

    return {
        "count": collection.count(),
        "closest_topic": result["metadatas"][0][0]["topic"],
        "distance": round(result["distances"][0][0], 4),
    }


def find_similar_research(topic: str, max_distance: float = MAX_DISTANCE) -> dict:
    collection = get_collection()

    if collection.count() == 0:
        return None

    result = collection.query(query_texts=[topic], n_results=1)

    if not result["documents"] or not result["documents"][0]:
        return None

    distance = result["distances"][0][0]

    if distance <= max_distance:
        return {
            "notes": result["documents"][0][0],
            "matched_topic": result["metadatas"][0][0]["topic"],
            "distance": round(distance, 4),
        }

    return None
