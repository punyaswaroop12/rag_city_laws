import streamlit as st

from rag_app.clients import create_openai_client, create_search_client
from rag_app.config import AppConfig
from rag_app.embeddings import embed_texts
from rag_app.rag import answer_question, build_context, retrieve_chunks


st.set_page_config(page_title="City Laws RAG", layout="wide")


@st.cache_resource
def get_config() -> AppConfig:
    return AppConfig.from_env()


@st.cache_resource
def get_clients():
    config = get_config()
    return config, create_openai_client(config), create_search_client(config)


config, openai_client, search_client = get_clients()

st.title("City Laws RAG Assistant")

with st.sidebar:
    st.header("Retrieval Settings")
    top_k = st.slider("Top K", min_value=2, max_value=10, value=5)
    st.caption("Uses Azure AI Search vector retrieval.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

prompt = st.chat_input("Ask a question about your city zoning PDFs")

if prompt:
    question_embedding = embed_texts(
        openai_client,
        config.openai_embedding_deployment,
        [prompt],
    )[0]
    chunks = retrieve_chunks(search_client, question_embedding, top_k=top_k)
    context = build_context(chunks)
    answer = answer_question(
        openai_client,
        config.openai_chat_deployment,
        prompt,
        context,
    )

    st.session_state.chat_history.append(
        {"role": "user", "content": prompt}
    )
    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer, "chunks": chunks}
    )

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            with st.expander("Retrieved Sources"):
                for chunk in message.get("chunks", []):
                    st.markdown(
                        f"**{chunk.source_file}** (page {chunk.page_number})\n\n{chunk.content}"
                    )
