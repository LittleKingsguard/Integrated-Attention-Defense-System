import os
from langchain_ollama import OllamaEmbeddings

def get_embeddings():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("EMBEDDING_MODEL", "embeddinggemma")
    
    return OllamaEmbeddings(
        base_url=base_url,
        model=model_name
    )
