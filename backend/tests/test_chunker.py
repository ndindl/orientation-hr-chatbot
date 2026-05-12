import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pdf_parser import PageContent
from chunker import chunk_page, _has_table


def _make_page(text, page_number=1, source="test.pdf"):
    return PageContent(source_file=source, page_number=page_number, text=text)


def test_short_text_returns_single_chunk():
    chunks = chunk_page(_make_page("Short vacation policy text."))
    assert len(chunks) == 1
    assert chunks[0].text == "Short vacation policy text."


def test_chunk_carries_source_metadata():
    chunks = chunk_page(_make_page("Some text.", page_number=5, source="handbook.pdf"))
    assert chunks[0].source_file == "handbook.pdf"
    assert chunks[0].page_number == 5


def test_long_text_splits_into_multiple_chunks():
    page = _make_page(" ".join(["word"] * 600))
    chunks = chunk_page(page, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_overlap_connects_adjacent_chunks():
    words = [str(i) for i in range(600)]
    chunks = chunk_page(_make_page(" ".join(words)), chunk_size=500, overlap=50)
    last_word_of_chunk0 = chunks[0].text.split()[-1]
    assert last_word_of_chunk0 in chunks[1].text.split()


def test_table_gets_own_chunk_separate_from_prose():
    # Tables are split into their own dedicated chunk so they embed without
    # prose noise — prose and table should be in separate chunks.
    table_text = (
        "Policy overview.\n\n"
        "| Years of Service | Hours Biweekly | Max Days |\n"
        "| --- | --- | --- |\n"
        "| 0-5 | 3.077 | 10 |\n"
        "| 6-10 | 4.62 | 15 |"
    )
    chunks = chunk_page(_make_page(table_text))
    assert len(chunks) == 2
    table_chunk = next(c for c in chunks if _has_table(c.text))
    assert "| 0-5 |" in table_chunk.text
    assert "| 6-10 |" in table_chunk.text


def test_has_table_detects_pipe_lines():
    assert _has_table("| a | b |\n| --- | --- |") is True
    assert _has_table("Regular text without pipes.") is False


def test_all_chunks_have_incrementing_index():
    page = _make_page(" ".join(["word"] * 600))
    chunks = chunk_page(page, chunk_size=500, overlap=50)
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i
