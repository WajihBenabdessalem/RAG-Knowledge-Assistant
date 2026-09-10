from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.documents import Document

from rag_assistant.api.main import app
from rag_assistant.generation.chain import RAGAnswer

client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm_provider"] == "openai"


def test_query_endpoint_returns_answer_and_sources():
    fake_answer = RAGAnswer(answer="Réponse simulée.", sources=["politique_conges.md"])

    with patch("rag_assistant.api.main._pipeline.ask", return_value=fake_answer):
        response = client.post("/query", json={"question": "Combien de jours de congés ?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Réponse simulée."
    assert body["sources"] == ["politique_conges.md"]


def test_query_endpoint_rejects_too_short_question():
    response = client.post("/query", json={"question": "hi"})
    assert response.status_code == 422


def test_ingest_endpoint_indexes_documents(monkeypatch):
    fake_docs = [Document(page_content="contenu", metadata={"source": "a.md"})]

    monkeypatch.setattr("rag_assistant.api.main.load_documents", lambda path: fake_docs)
    monkeypatch.setattr(
        "rag_assistant.api.main.split_documents", lambda docs, size, overlap: fake_docs
    )
    monkeypatch.setattr("rag_assistant.api.main.get_vector_store", lambda settings: object())
    monkeypatch.setattr(
        "rag_assistant.api.main.add_documents", lambda vector_store, chunks: len(chunks)
    )

    response = client.post("/ingest")

    assert response.status_code == 200
    body = response.json()
    assert body == {"documents_indexed": 1, "chunks_indexed": 1}


def test_ingest_endpoint_returns_400_when_no_documents(monkeypatch):
    def raise_value_error(path):
        raise ValueError("Aucun document trouvé")

    monkeypatch.setattr("rag_assistant.api.main.load_documents", raise_value_error)

    response = client.post("/ingest")

    assert response.status_code == 400
