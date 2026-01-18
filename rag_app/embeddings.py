from typing import List

from openai import AzureOpenAI


def embed_texts(client: AzureOpenAI, deployment: str, texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        model=deployment,
        input=texts,
    )
    return [item.embedding for item in response.data]
