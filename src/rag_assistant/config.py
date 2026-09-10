"""Configuration centralisée de l'application, chargée depuis les variables d'environnement."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de l'application, surchargeables via un fichier .env ou des variables d'env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    llm_provider: Literal["openai", "anthropic"] = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    # Stockage & données
    chroma_persist_dir: Path = Field(default=Path("data/chroma"), alias="CHROMA_PERSIST_DIR")
    docs_dir: Path = Field(default=Path("data/sample_docs"), alias="DOCS_DIR")

    # Découpage
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=4, alias="TOP_K")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance mise en cache des settings (évite de reparser l'env à chaque appel)."""
    return Settings()
