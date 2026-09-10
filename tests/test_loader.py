from pathlib import Path

import pytest

from rag_assistant.ingestion.loader import load_documents


def test_load_documents_reads_markdown_and_txt_files(tmp_path: Path):
    (tmp_path / "a.md").write_text("# Titre\nContenu A", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Contenu B", encoding="utf-8")
    (tmp_path / "ignored.json").write_text("{}", encoding="utf-8")

    documents = load_documents(tmp_path)

    sources = {doc.metadata["source"] for doc in documents}
    assert sources == {"a.md", "b.txt"}


def test_load_documents_raises_on_missing_directory(tmp_path: Path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        load_documents(missing)


def test_load_documents_raises_when_no_supported_files(tmp_path: Path):
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_documents(tmp_path)
