from rag_app.config import AppConfig
from rag_app.indexing import ensure_index


def main() -> None:
    config = AppConfig.from_env()
    ensure_index(config)
    print(f"Index '{config.search_index_name}' created.")


if __name__ == "__main__":
    main()
