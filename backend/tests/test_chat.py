import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock
from chat import build_system_prompt, chat

SAMPLE_CHUNKS = [
    {
        "text": "Vacation accrual is 3.077 hours biweekly for years 0-5.",
        "source_file": "handbook.pdf",
        "page_number": 9,
        "score": 0.92,
    }
]


def test_system_prompt_specifies_english():
    assert "English" in build_system_prompt(SAMPLE_CHUNKS, "en")


def test_system_prompt_specifies_spanish():
    assert "Spanish" in build_system_prompt(SAMPLE_CHUNKS, "es")


def test_system_prompt_includes_hr_contact():
    prompt = build_system_prompt(SAMPLE_CHUNKS, "en")
    assert "hr@abcwidgets.fake" in prompt
    assert "555" in prompt


def test_system_prompt_includes_chunk_text():
    assert "3.077 hours biweekly" in build_system_prompt(SAMPLE_CHUNKS, "en")


def test_system_prompt_includes_source_citation():
    prompt = build_system_prompt(SAMPLE_CHUNKS, "en")
    assert "handbook.pdf" in prompt
    assert "p.9" in prompt


def test_system_prompt_with_no_chunks_still_has_contact():
    assert "hr@abcwidgets.fake" in build_system_prompt([], "en")


def test_chat_returns_model_text(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="You earn 3.077 hours biweekly.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    result = chat("How much vacation do I earn?", SAMPLE_CHUNKS, "en", [])
    assert result == "You earn 3.077 hours biweekly."


def test_chat_passes_full_history_to_api(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Answer.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"},
    ]
    chat("Follow-up question", SAMPLE_CHUNKS, "en", history)

    messages = mock_client.messages.create.call_args[1]["messages"]
    assert len(messages) == 3  # 2 history + 1 current
    assert messages[-1]["content"] == "Follow-up question"


def test_chat_uses_correct_model(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Answer.")]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_resp
    monkeypatch.setattr("chat.client", mock_client)

    chat("Question", SAMPLE_CHUNKS, "en", [])
    assert mock_client.messages.create.call_args[1]["model"] == "claude-sonnet-4-6"
