from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI

from rag_app.config import AppConfig


def create_search_index_client(config: AppConfig) -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=config.search_endpoint,
        credential=AzureKeyCredential(config.search_admin_key),
    )


def create_search_client(config: AppConfig, use_admin: bool = False) -> SearchClient:
    key = config.search_admin_key if use_admin else config.search_query_key
    return SearchClient(
        endpoint=config.search_endpoint,
        index_name=config.search_index_name,
        credential=AzureKeyCredential(key),
    )


def create_openai_client(config: AppConfig) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=config.openai_api_key,
        api_version=config.openai_api_version,
        azure_endpoint=config.openai_endpoint,
    )
