import os
from qdrant_client import QdrantClient
from embedder import embed_query

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "hr_documents"


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    client = QdrantClient(url=QDRANT_URL)
    vector = embed_query(query)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "text": r.payload["text"],
            "source_file": r.payload["source_file"],
            "page_number": r.payload["page_number"],
            "score": r.score,
        }
        for r in results
    ]
