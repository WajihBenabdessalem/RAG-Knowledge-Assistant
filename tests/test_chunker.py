from langchain_core.documents import Document

from rag_assistant.ingestion.chunker import split_documents


def test_split_documents_produces_multiple_chunks_for_long_text():
    text = "Ceci est une phrase de test. " * 200
    doc = Document(page_content=text, metadata={"source": "test.txt"})

    chunks = split_documents([doc], chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(chunk.metadata["source"] == "test.txt" for chunk in chunks)
    assert [chunk.metadata["chunk_id"] for chunk in chunks] == list(range(len(chunks)))


def test_split_documents_short_text_returns_single_chunk():
    doc = Document(page_content="Texte court.", metadata={"source": "short.txt"})

    chunks = split_documents([doc], chunk_size=800, chunk_overlap=120)

    assert len(chunks) == 1
    assert chunks[0].page_content == "Texte court."


def test_split_documents_empty_list_returns_empty_list():
    assert split_documents([], chunk_size=100, chunk_overlap=10) == []
