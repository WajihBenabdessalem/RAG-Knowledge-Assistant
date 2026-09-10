"""Fabrique d'embeddings, découplée du provider pour faciliter les tests et le changement de LLM."""

from rag_assistant.config import Settings


def get_embeddings(settings: Settings):
    """Retourne le client d'embeddings correspondant au provider configuré."""
    if settings.llm_provider == "anthropic":
        # Anthropic ne fournit pas d'API d'embeddings : on utilise un modèle local par défaut.
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
