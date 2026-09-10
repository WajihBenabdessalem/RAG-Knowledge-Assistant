"""Recherche par similarité dans le store vectoriel Chroma."""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_assistant.config import Settings


def retrieve(vector_store: Chroma, query: str, settings: Settings) -> list[Document]:
    """Retourne les top-k documents les plus pertinents pour une requête donnée."""
    return vector_store.similarity_search(query, k=settings.top_k)
