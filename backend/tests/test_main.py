import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_returns_answer_and_citations(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "How much vacation do I get?",
        "language": "en",
        "history": [],
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["citations"], list)


def test_chat_endpoint_citation_has_source_and_page(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "How much vacation do I get?",
        "language": "en",
        "history": [],
    })
    citation = response.json()["citations"][0]
    assert citation["source_file"] == "handbook.pdf"
    assert citation["page_number"] == 9


def test_chat_endpoint_accepts_spanish(mock_retrieve, mock_chat_fn):
    response = client.post("/chat", json={
        "message": "¿Cuántos días de vacaciones tengo?",
        "language": "es",
        "history": [],
    })
    assert response.status_code == 200
