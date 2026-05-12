import os
import pytest

# Must be set before chat.py is imported — the Anthropic SDK raises at
# client construction time if ANTHROPIC_API_KEY is absent.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-pytest")


@pytest.fixture
def mock_retrieve(monkeypatch):
    chunks = [
        {
            "text": "Employees accrue 3.077 hours vacation biweekly for years 0-5.",
            "source_file": "handbook.pdf",
            "page_number": 9,
            "score": 0.92,
        }
    ]
    monkeypatch.setattr("main.retrieve", lambda q, **kwargs: chunks)
    return chunks


@pytest.fixture
def mock_chat_fn(monkeypatch):
    monkeypatch.setattr(
        "main.chat_fn",
        lambda msg, chunks, lang, hist: "You earn vacation per the accrual table.",
    )
    return "You earn vacation per the accrual table."
