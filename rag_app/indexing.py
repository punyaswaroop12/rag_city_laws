from typing import List

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from rag_app.clients import create_search_index_client
from rag_app.config import AppConfig


VECTOR_DIMENSIONS = 1536


def build_index(config: AppConfig) -> SearchIndex:
    fields: List[SearchField] = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="content-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="content-hnsw")],
        profiles=[
            VectorSearchProfile(
                name="content-profile",
                algorithm_configuration_name="content-hnsw",
            )
        ],
    )

    return SearchIndex(
        name=config.search_index_name,
        fields=fields,
        vector_search=vector_search,
    )


def ensure_index(config: AppConfig) -> None:
    client = create_search_index_client(config)
    index = build_index(config)
    existing = client.get_index_names()
    if config.search_index_name in existing:
        client.delete_index(config.search_index_name)
    client.create_index(index)
