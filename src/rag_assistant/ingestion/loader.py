"""Chargement des documents source (txt, markdown, pdf) depuis un dossier."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {
    ".txt": TextLoader,
    ".md": TextLoader,
    ".pdf": PyPDFLoader,
}


def load_documents(docs_dir: Path) -> list[Document]:
    """Charge tous les documents supportés d'un dossier, avec leur chemin relatif en métadonnée."""
    docs_dir = Path(docs_dir)
    if not docs_dir.exists():
        raise FileNotFoundError(f"Dossier de documents introuvable : {docs_dir}")

    documents: list[Document] = []
    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file():
            continue

        loader_cls = SUPPORTED_EXTENSIONS.get(path.suffix.lower())
        if loader_cls is None:
            continue

        loader = loader_cls(str(path))
        loaded = loader.load()
        for doc in loaded:
            doc.metadata["source"] = str(path.relative_to(docs_dir))
        documents.extend(loaded)

    if not documents:
        raise ValueError(
            f"Aucun document supporté trouvé dans {docs_dir} "
            f"(extensions supportées : {', '.join(SUPPORTED_EXTENSIONS)})"
        )

    return documents
