import os
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pdf_parser import parse_pdf
from chunker import chunk_page
from embedder import embed

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "hr_documents"
VECTOR_SIZE = 768
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./documents")


def main():
    client = QdrantClient(url=QDRANT_URL)

    # Wipe and rebuild on every run — this ensures stale content from
    # removed or replaced PDFs never survives a re-index
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION_NAME}'")

    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {DOCUMENTS_DIR}")
        return

    all_chunks = []
    for pdf_path in sorted(pdf_files):
        print(f"Parsing {pdf_path} ...")
        for page in parse_pdf(pdf_path):
            all_chunks.extend(chunk_page(page))

    print(f"Embedding {len(all_chunks)} chunks ...")
    vectors = embed([c.text for c in all_chunks])

    points = [
        PointStruct(
            id=i,
            vector=vectors[i],
            payload={
                "source_file": all_chunks[i].source_file,
                "page_number": all_chunks[i].page_number,
                "text": all_chunks[i].text,
            },
        )
        for i in range(len(all_chunks))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Indexed {len(points)} chunks into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
