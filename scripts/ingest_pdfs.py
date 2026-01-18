import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

from rag_app.chunking import chunk_pages
from rag_app.clients import create_openai_client, create_search_client
from rag_app.config import AppConfig
from rag_app.embeddings import embed_texts
from rag_app.pdf_loader import load_pdf_pages


def build_document_id(source_file: str, page_number: int, chunk_id: int) -> str:
    raw_id = f"{source_file}-{page_number}-{chunk_id}"
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()


def load_documents(pdf_dir: Path) -> List[Dict]:
    documents: List[Dict] = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        pages = load_pdf_pages(pdf_path)
        chunks = chunk_pages(pages)
        for chunk in chunks:
            documents.append(
                {
                    "id": build_document_id(pdf_path.name, chunk.page_number, chunk.chunk_id),
                    "content": chunk.text,
                    "source_file": pdf_path.name,
                    "page_number": chunk.page_number,
                    "chunk_id": chunk.chunk_id,
                }
            )
    return documents


def chunk_batches(documents: List[Dict], batch_size: int) -> List[List[Dict]]:
    return [documents[start : start + batch_size] for start in range(0, len(documents), batch_size)]


def embed_batch(config: AppConfig, batch: List[Dict]) -> List[Dict]:
    openai_client = create_openai_client(config)
    embeddings = embed_texts(
        openai_client,
        config.openai_embedding_deployment,
        [doc["content"] for doc in batch],
    )
    for doc, embedding in zip(batch, embeddings):
        doc["content_vector"] = embedding
    return batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into Azure AI Search.")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    config = AppConfig.from_env()
    pdf_dir = Path("data/pdfs")
    if not pdf_dir.exists():
        raise FileNotFoundError("data/pdfs directory does not exist")

    documents = load_documents(pdf_dir)
    if not documents:
        raise ValueError("No PDF documents found in data/pdfs")

    search_client = create_search_client(config, use_admin=True)

    batches = chunk_batches(documents, args.batch_size)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for index, batch in enumerate(executor.map(lambda b: embed_batch(config, b), batches), start=1):
            search_client.upload_documents(documents=batch)
            uploaded = min(index * args.batch_size, len(documents))
            print(f"Uploaded {uploaded} / {len(documents)}")

    print("Ingestion complete.")


if __name__ == "__main__":
    main()
