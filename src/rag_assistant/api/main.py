"""Point d'entrée FastAPI : santé, ingestion et interrogation de la base de connaissances."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from rag_assistant.api.schemas import (
    HealthResponse,
    IngestResponse,
    QueryRequest,
    QueryResponse,
)
from rag_assistant.config import get_settings
from rag_assistant.generation.chain import RAGPipeline
from rag_assistant.ingestion.chunker import split_documents
from rag_assistant.ingestion.loader import load_documents
from rag_assistant.ingestion.vector_store import add_documents, get_vector_store

app = FastAPI(
    title="RAG Knowledge Assistant",
    description="Assistant de questions-réponses basé sur une base documentaire interne (RAG).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Le pipeline est instancié une seule fois au démarrage. Ses dépendances lourdes
# (embeddings, LLM, store vectoriel) ne sont créées qu'au premier appel réel (lazy).
_pipeline = RAGPipeline()


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Vérifie que le service répond et indique le provider LLM configuré."""
    settings = get_settings()
    return HealthResponse(status="ok", llm_provider=settings.llm_provider)


@app.post("/ingest", response_model=IngestResponse, tags=["ingestion"])
def ingest() -> IngestResponse:
    """Charge, découpe et indexe les documents du dossier configuré (DOCS_DIR)."""
    settings = get_settings()
    try:
        documents = load_documents(settings.docs_dir)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    vector_store = get_vector_store(settings)
    indexed = add_documents(vector_store, chunks)
    return IngestResponse(documents_indexed=len(documents), chunks_indexed=indexed)


@app.post("/query", response_model=QueryResponse, tags=["query"])
def query(payload: QueryRequest) -> QueryResponse:
    """Répond à une question en s'appuyant sur les documents précédemment indexés."""
    try:
        result = _pipeline.ask(payload.question)
    except Exception as exc:  # noqa: BLE001 — on renvoie une 500 explicite au client
        detail = f"Erreur lors de la génération : {exc}"
        raise HTTPException(status_code=500, detail=detail) from exc
    return QueryResponse(answer=result.answer, sources=result.sources)
