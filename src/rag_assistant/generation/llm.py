"""Fabrique de modèle de chat, découplée du provider (OpenAI / Anthropic)."""

from rag_assistant.config import Settings


def get_chat_model(settings: Settings):
    """Retourne le client LLM correspondant au provider configuré, en mode déterministe."""
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model, api_key=settings.anthropic_api_key, temperature=0
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=settings.llm_model, api_key=settings.openai_api_key, temperature=0)
