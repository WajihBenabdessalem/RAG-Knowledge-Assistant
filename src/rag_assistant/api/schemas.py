"""Schémas Pydantic des requêtes/réponses de l'API."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        examples=["Combien de jours de congés payés par an ?"],
    )


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


class IngestResponse(BaseModel):
    documents_indexed: int
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
