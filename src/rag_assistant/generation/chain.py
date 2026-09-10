"""Assemblage du pipeline RAG complet : récupération + génération, via LangChain (LCEL)."""

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from rag_assistant.config import Settings, get_settings
from rag_assistant.generation.llm import get_chat_model
from rag_assistant.generation.prompt import RAG_PROMPT
from rag_assistant.ingestion.vector_store import get_vector_store
from rag_assistant.retrieval.retriever import retrieve


@dataclass
class RAGAnswer:
    """Résultat d'une requête RAG : réponse générée et sources utilisées."""

    answer: str
    sources: list[str]


def format_context(docs: list[Document]) -> str:
    """Assemble les documents récupérés en un contexte textuel unique pour le prompt."""
    parts = [
        f"[source: {doc.metadata.get('source', 'inconnue')}]\n{doc.page_content}" for doc in docs
    ]
    return "\n\n---\n\n".join(parts)


class RAGPipeline:
    """Pipeline RAG de bout en bout : recherche vectorielle puis génération contextualisée.

    Le store vectoriel et le modèle de chat sont initialisés paresseusement (lazy),
    ce qui permet d'importer/instancier cette classe sans clé API valide (utile en tests
    et pour le démarrage de l'API avant tout appel réel).
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._vector_store = None
        self._chat_model = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = get_vector_store(self.settings)
        return self._vector_store

    @property
    def chat_model(self):
        if self._chat_model is None:
            self._chat_model = get_chat_model(self.settings)
        return self._chat_model

    def ask(self, question: str) -> RAGAnswer:
        """Répond à une question en s'appuyant uniquement sur les documents indexés."""
        docs = retrieve(self.vector_store, question, self.settings)
        if not docs:
            no_info = "Je n'ai trouvé aucune information pertinente dans la base de connaissances."
            return RAGAnswer(answer=no_info, sources=[])

        context = format_context(docs)
        chain = RAG_PROMPT | self.chat_model | StrOutputParser()
        answer = chain.invoke({"context": context, "question": question})
        sources = sorted({doc.metadata.get("source", "inconnue") for doc in docs})
        return RAGAnswer(answer=answer, sources=sources)
