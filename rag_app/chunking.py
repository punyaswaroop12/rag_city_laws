from dataclasses import dataclass
from typing import Iterable, List

import tiktoken


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_id: int
    page_number: int


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    encoding_name: str = "cl100k_base",
    page_number: int = 0,
) -> List[TextChunk]:
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    chunk_id = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text_value = encoding.decode(chunk_tokens).strip()
        if chunk_text_value:
            chunks.append(
                TextChunk(text=chunk_text_value, chunk_id=chunk_id, page_number=page_number)
            )
            chunk_id += 1
        start = end - overlap if end - overlap > 0 else end

    return chunks


def chunk_pages(
    pages: Iterable[str], chunk_size: int = 500, overlap: int = 100
) -> List[TextChunk]:
    chunks: List[TextChunk] = []
    for page_number, page_text in enumerate(pages, start=1):
        chunks.extend(
            chunk_text(
                page_text,
                chunk_size=chunk_size,
                overlap=overlap,
                page_number=page_number,
            )
        )
    return chunks
