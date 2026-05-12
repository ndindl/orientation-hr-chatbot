import os
import pdfplumber
from dataclasses import dataclass
from typing import Generator


@dataclass
class PageContent:
    source_file: str
    page_number: int  # 1-indexed
    text: str


def parse_pdf(pdf_path: str) -> Generator[PageContent, None, None]:
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = _extract_page_text(page)
            if text.strip():
                yield PageContent(
                    source_file=os.path.basename(pdf_path),
                    page_number=i + 1,
                    text=text,
                )


def _extract_page_text(page) -> str:
    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]

    # Extract text from regions outside table bounding boxes
    filtered = page
    for bbox in table_bboxes:
        filtered = filtered.outside_bbox(bbox)
    non_table_text = (filtered.extract_text() or "").strip()

    # Render each table as Markdown so it survives embedding intact
    table_parts = []
    for table in tables:
        data = table.extract()
        if data:
            table_parts.append(_table_to_markdown(data))

    parts = []
    if non_table_text:
        parts.append(non_table_text)
    parts.extend(table_parts)
    return "\n\n".join(parts)


def _table_to_markdown(table: list[list]) -> str:
    normalized = [
        [str(cell or "").replace("\n", " ").strip() for cell in row]
        for row in table
    ]

    # Merge continuation rows: when row[0] is empty, the row is a wrapped
    # continuation of the previous row caused by merged cells in the PDF.
    merged: list[list[str]] = []
    for row in normalized:
        if not any(row):
            continue
        if merged and row[0] == "":
            prev = merged[-1]
            for j in range(min(len(row), len(prev))):
                if row[j]:
                    prev[j] = (prev[j] + " " + row[j]).strip()
        else:
            merged.append(list(row))

    if not merged:
        return ""

    # Compact each row to only its non-empty cells — collapses sparse
    # merged-cell columns into a clean readable table for embedding.
    lines = []
    for i, row in enumerate(merged):
        non_empty = [c for c in row if c]
        if not non_empty:
            continue
        lines.append("| " + " | ".join(non_empty) + " |")
        if i == 0:
            lines.append("| " + " | ".join(["---"] * len(non_empty)) + " |")
    return "\n".join(lines)
