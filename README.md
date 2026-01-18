# rag_city_laws
RAG on real estate zoning regulations for every city in united states.

## Overview
This repo contains a production-ready Streamlit RAG application that uses Azure AI Search for vector retrieval and Azure OpenAI for embeddings + chat completions. You can drop your PDFs into `data/pdfs`, create the search index, ingest documents, and run the app.

## Architecture
- **Azure AI Search** stores chunked PDF text and embeddings for vector search.
- **Azure OpenAI** generates embeddings and answers with citations.
- **Streamlit** provides the chat UI.

## Step-by-step setup
### 1) Provision Azure resources
Use your Terraform repo to create:
- Azure AI Search service
- Azure OpenAI resource with chat + embedding deployments

### 2) Clone this repo and install dependencies
```bash
cd /workspace/rag_city_laws
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure environment variables
Copy the template and fill in the values from your Azure resources:
```bash
cp .env.example .env
```

Required variables:
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_ADMIN_KEY`
- `AZURE_SEARCH_INDEX_NAME`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`

### 4) Add your PDFs
Place your two PDFs in:
```
data/pdfs
```

### 5) Create the Azure AI Search index
Run from the repo root so imports resolve:
```bash
python -m scripts.create_search_index
```

### 6) Ingest the PDFs (chunk, embed, upload)
```bash
python -m scripts.ingest_pdfs
```

For faster ingestion, increase batch size and workers (subject to your Azure OpenAI rate limits):
```bash
python -m scripts.ingest_pdfs --batch-size 128 --workers 8
```

### 7) Run the Streamlit app
```bash
streamlit run streamlit_app.py
```

## Troubleshooting
### `ModuleNotFoundError: No module named 'azure'`
Install dependencies inside your virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'rag_app'`
Make sure you run the commands from the repo root using module execution:
```bash
python -m scripts.create_search_index
python -m scripts.ingest_pdfs
```

## Production notes
- Use a **query key** in production for the app (set `AZURE_SEARCH_QUERY_KEY`).
- The ingestion script uses the **admin key** for indexing.
- Run ingestion from a CI/CD pipeline when PDFs change.
- Add monitoring and logging around `scripts/ingest_pdfs.py` for scale.
