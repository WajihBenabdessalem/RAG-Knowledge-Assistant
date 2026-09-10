"""CLI de l'assistant RAG : ingestion des documents et interrogation en ligne de commande."""

import typer
from rich.console import Console
from rich.table import Table

from rag_assistant.config import get_settings
from rag_assistant.generation.chain import RAGPipeline
from rag_assistant.ingestion.chunker import split_documents
from rag_assistant.ingestion.loader import load_documents
from rag_assistant.ingestion.vector_store import add_documents, get_vector_store

app = typer.Typer(help="RAG Knowledge Assistant — CLI d'ingestion et d'interrogation.")
console = Console()


@app.command()
def ingest() -> None:
    """Charge, découpe et indexe les documents du dossier configuré (DOCS_DIR)."""
    settings = get_settings()
    console.print(f"[bold]Chargement des documents depuis {settings.docs_dir}...[/bold]")
    documents = load_documents(settings.docs_dir)
    console.print(f"{len(documents)} document(s) chargé(s). Découpage en cours...")

    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    vector_store = get_vector_store(settings)
    indexed = add_documents(vector_store, chunks)

    console.print(f"[green]✔ {len(documents)} documents indexés en {indexed} chunks.[/green]")


@app.command()
def ask(question: str) -> None:
    """Pose une question à l'assistant et affiche la réponse ainsi que ses sources."""
    pipeline = RAGPipeline()
    result = pipeline.ask(question)

    console.print(f"\n[bold cyan]Réponse :[/bold cyan] {result.answer}\n")
    if result.sources:
        table = Table(title="Sources utilisées")
        table.add_column("Fichier")
        for source in result.sources:
            table.add_row(source)
        console.print(table)


if __name__ == "__main__":
    app()
