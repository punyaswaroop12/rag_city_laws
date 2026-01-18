from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    search_endpoint: str
    search_admin_key: str
    search_query_key: str
    search_index_name: str
    openai_endpoint: str
    openai_api_key: str
    openai_api_version: str
    openai_embedding_deployment: str
    openai_chat_deployment: str


    @staticmethod
    def from_env() -> "AppConfig":
        search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "").strip()
        search_admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY", "").strip()
        search_query_key = os.environ.get("AZURE_SEARCH_QUERY_KEY", "").strip()
        search_index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME", "").strip()
        openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
        openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
        openai_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01").strip()
        openai_embedding_deployment = os.environ.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""
        ).strip()
        openai_chat_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()

        missing = [
            name
            for name, value in {
                "AZURE_SEARCH_ENDPOINT": search_endpoint,
                "AZURE_SEARCH_ADMIN_KEY": search_admin_key,
                "AZURE_SEARCH_INDEX_NAME": search_index_name,
                "AZURE_OPENAI_ENDPOINT": openai_endpoint,
                "AZURE_OPENAI_API_KEY": openai_api_key,
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": openai_embedding_deployment,
                "AZURE_OPENAI_CHAT_DEPLOYMENT": openai_chat_deployment,
            }.items()
            if not value
        ]

        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        if not search_query_key:
            search_query_key = search_admin_key

        return AppConfig(
            search_endpoint=search_endpoint,
            search_admin_key=search_admin_key,
            search_query_key=search_query_key,
            search_index_name=search_index_name,
            openai_endpoint=openai_endpoint,
            openai_api_key=openai_api_key,
            openai_api_version=openai_api_version,
            openai_embedding_deployment=openai_embedding_deployment,
            openai_chat_deployment=openai_chat_deployment,
        )
