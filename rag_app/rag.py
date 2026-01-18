from dataclasses import dataclass
from typing import List

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source_file: str
    page_number: int


def retrieve_chunks(
    search_client: SearchClient, query_vector: List[float], top_k: int = 5
) -> List[RetrievedChunk]:
    vector_query = VectorizedQuery(
        vector=query_vector, k_nearest_neighbors=top_k, fields="content_vector"
    )
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["content", "source_file", "page_number"],
    )

    chunks = []
    for result in results:
        chunks.append(
            RetrievedChunk(
                content=result["content"],
                source_file=result["source_file"],
                page_number=result["page_number"],
            )
        )
    return chunks


def build_context(chunks: List[RetrievedChunk]) -> str:
    context_blocks = []
    for chunk in chunks:
        context_blocks.append(
            f"Source: {chunk.source_file} (page {chunk.page_number})\n{chunk.content}"
        )
    return "\n\n".join(context_blocks)


def answer_question(
    client: AzureOpenAI,
    deployment: str,
    question: str,
    context: str,
) -> str:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant answering questions about zoning laws. "
                    "Use only the provided context. If the answer is not in the context, "
                    "say you do not have enough information. Include citations with the "
                    "source file and page number."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
        temperature=0.2,
        max_tokens=800,
    )
    return response.choices[0].message.content
