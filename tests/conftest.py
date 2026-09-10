"""Configuration partagée des tests : fournit des variables d'environnement factices
pour permettre l'import des modules de configuration sans clé API réelle."""

import os

os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")
os.environ.setdefault("LLM_PROVIDER", "openai")
