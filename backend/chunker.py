from dataclasses import dataclass
from pdf_parser import PageContent


@dataclass
class Chunk:
    source_file: str
    page_number: int
    text: str
    chunk_index: int


def _has_table(text: str) -> bool:
    return any(line.strip().startswith("|") for line in text.splitlines())


def _split_prose_and_tables(text: str) -> list[str]:
    """Split page text into alternating prose and table sections.

    Tables get their own section so they embed without prose noise.
    """
    lines = text.splitlines()
    sections: list[str] = []
    current: list[str] = []
    in_table = False

    for line in lines:
        is_table_line = line.strip().startswith("|")
        if is_table_line != in_table:
            section = "\n".join(current).strip()
            if section:
                sections.append(section)
            current = [line]
            in_table = is_table_line
        else:
            current.append(line)

    section = "\n".join(current).strip()
    if section:
        sections.append(section)
    return sections


def chunk_page(page: PageContent, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    sections = _split_prose_and_tables(page.text)
    chunks: list[Chunk] = []
    idx = 0

    for section in sections:
        if _has_table(section):
            # Each table is its own dedicated chunk — keeps rows intact and
            # gives the table a focused embedding vector without prose noise.
            chunks.append(Chunk(
                source_file=page.source_file,
                page_number=page.page_number,
                text=section,
                chunk_index=idx,
            ))
            idx += 1
        else:
            words = section.split()
            if not words:
                continue
            if len(words) <= chunk_size:
                chunks.append(Chunk(
                    source_file=page.source_file,
                    page_number=page.page_number,
                    text=section,
                    chunk_index=idx,
                ))
                idx += 1
            else:
                start = 0
                while start < len(words):
                    end = min(start + chunk_size, len(words))
                    chunks.append(Chunk(
                        source_file=page.source_file,
                        page_number=page.page_number,
                        text=" ".join(words[start:end]),
                        chunk_index=idx,
                    ))
                    idx += 1
                    if end == len(words):
                        break
                    start = end - overlap

    return chunks
