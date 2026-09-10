"""Création et alimentation du store vectoriel Chroma (persisté sur disque)."""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_assistant.config import Settings
from rag_assistant.ingestion.embeddings import get_embeddings

COLLECTION_NAME = "knowledge_base"


def get_vector_store(settings: Settings) -> Chroma:
    """Retourne (ou crée) le store vectoriel Chroma persisté sur le disque configuré."""
    embeddings = get_embeddings(settings)
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_persist_dir),
    )


def add_documents(vector_store: Chroma, documents: list[Document]) -> int:
    """Indexe une liste de chunks dans le store vectoriel, avec des ids déterministes."""
    if not documents:
        return 0

    ids = [
        f"{doc.metadata.get('source', 'doc')}::{doc.metadata.get('chunk_id', i)}"
        for i, doc in enumerate(documents)
    ]
    vector_store.add_documents(documents, ids=ids)
    return len(documents)
