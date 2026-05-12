import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from embedder import embed

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
TEST_COLLECTION = "test_hr_retriever"

pytestmark = pytest.mark.skipif(
    not os.getenv("QDRANT_URL"),
    reason="QDRANT_URL not set — skipping integration tests",
)


@pytest.fixture(autouse=True)
def setup_test_collection():
    client = QdrantClient(url=QDRANT_URL)
    if client.collection_exists(TEST_COLLECTION):
        client.delete_collection(TEST_COLLECTION)
    client.create_collection(
        collection_name=TEST_COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    text = "Employees accrue vacation at 3.077 hours biweekly for years 0-5 of continuous service."
    vectors = embed([text])
    client.upsert(
        collection_name=TEST_COLLECTION,
        points=[PointStruct(
            id=0,
            vector=vectors[0],
            payload={"text": text, "source_file": "handbook.pdf", "page_number": 9},
        )],
    )
    yield
    client.delete_collection(TEST_COLLECTION)


def test_english_query_finds_relevant_chunk(monkeypatch):
    import retriever
    monkeypatch.setattr(retriever, "COLLECTION_NAME", TEST_COLLECTION)
    monkeypatch.setattr(retriever, "QDRANT_URL", QDRANT_URL)
    from retriever import retrieve
    results = retrieve("How much vacation do I earn?", top_k=1)
    assert len(results) == 1
    assert results[0]["page_number"] == 9
    assert results[0]["source_file"] == "handbook.pdf"


def test_spanish_query_finds_english_content(monkeypatch):
    import retriever
    monkeypatch.setattr(retriever, "COLLECTION_NAME", TEST_COLLECTION)
    monkeypatch.setattr(retriever, "QDRANT_URL", QDRANT_URL)
    from retriever import retrieve
    results = retrieve("¿Cuántos días de vacaciones tengo?", top_k=1)
    assert len(results) == 1
    assert results[0]["page_number"] == 9
