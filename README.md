# RAG Knowledge Assistant

Assistant de questions-réponses basé sur une base documentaire interne, construit avec
une architecture RAG (Retrieval-Augmented Generation) : les réponses sont générées
**uniquement** à partir de documents indexés, avec citation systématique des sources.

Projet réalisé par [Wajih Benabdessalem](https://www.linkedin.com/in/wajihabdessalem)
dans le cadre d'une transition de Senior Software Engineer (iOS) vers l'AI Engineering.

## Pourquoi ce projet

Démontrer, sur un cas d'usage concret (assistant RH / documentation interne), une
maîtrise des briques essentielles d'un système RAG en production : ingestion et
découpage de documents, embeddings, base vectorielle, orchestration LLM, API,
tests automatisés et conteneurisation — avec les mêmes standards de qualité qu'un
projet mobile/backend en production (architecture modulaire, CI, tests, typage).

## Architecture

```
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│  Documents   │ --> │   Chunking    │ --> │  Embeddings   │
│ (.md/.txt/   │     │ (LangChain    │     │ (OpenAI /     │
│    .pdf)     │     │  splitter)    │     │  HuggingFace) │
└──────────────┘     └───────────────┘     └───────┬───────┘
                                                     │
                                                     v
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│   Réponse    │ <-- │  LLM + prompt │ <-- │ Chroma Vector │
│ + sources    │     │  RAG (LCEL)   │     │     Store     │
└──────────────┘     └───────────────┘     └───────────────┘
```

Le pipeline est exposé de deux façons : une **API REST (FastAPI)** et une **CLI**
(Typer), toutes deux au-dessus du même cœur métier (`rag_assistant`), pour éviter
toute duplication de logique.

## Stack technique

- **Langage** : Python 3.11+
- **Orchestration LLM** : LangChain (LCEL)
- **LLM** : OpenAI (`gpt-4o-mini` par défaut) ou Anthropic (Claude), au choix via config
- **Embeddings** : OpenAI `text-embedding-3-small`, ou modèle local (fallback)
- **Base vectorielle** : Chroma (persistée sur disque)
- **API** : FastAPI + Uvicorn
- **CLI** : Typer + Rich
- **Tests** : Pytest, avec mocks des appels LLM (aucune clé API requise pour la CI)
- **Qualité** : Ruff (lint), Mypy, GitHub Actions (CI)
- **Déploiement** : Docker / docker-compose

## Structure du projet

```
rag-knowledge-assistant/
├── src/rag_assistant/
│   ├── config.py              # Configuration (pydantic-settings)
│   ├── cli.py                 # CLI (ingest / ask)
│   ├── ingestion/
│   │   ├── loader.py          # Chargement des documents (.md/.txt/.pdf)
│   │   ├── chunker.py         # Découpage en chunks
│   │   ├── embeddings.py      # Fabrique d'embeddings
│   │   └── vector_store.py    # Store vectoriel Chroma
│   ├── retrieval/
│   │   └── retriever.py       # Recherche par similarité
│   ├── generation/
│   │   ├── llm.py             # Fabrique de modèle de chat
│   │   ├── prompt.py          # Prompt RAG
│   │   └── chain.py           # Pipeline RAG complet
│   └── api/
│       ├── main.py            # Endpoints FastAPI
│       └── schemas.py         # Schémas Pydantic
├── tests/                     # Tests unitaires et d'intégration (API mockée)
├── data/sample_docs/          # Corpus de démonstration (RH + technique)
├── docker/                    # Dockerfile + docker-compose
└── .github/workflows/ci.yml   # Lint + tests automatisés
```

## Installation

```bash
git clone https://github.com/<votre-user>/rag-knowledge-assistant.git
cd rag-knowledge-assistant

python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate

make install                   # ou : pip install -r requirements-dev.txt

cp .env.example .env
# Renseigner OPENAI_API_KEY (ou ANTHROPIC_API_KEY + LLM_PROVIDER=anthropic) dans .env
```

## Utilisation

### 1. Indexer les documents

Un corpus de démonstration est fourni dans `data/sample_docs/` (politique de congés,
guide d'onboarding, documentation d'architecture d'une entreprise fictive).

```bash
make ingest
# ou : PYTHONPATH=src python -m rag_assistant.cli ingest
```

### 2. Interroger l'assistant (CLI)

```bash
make ask Q="Combien de jours de congés payés par an ?"
```

### 3. Lancer l'API

```bash
make run
# Documentation interactive : http://localhost:8000/docs
```

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la politique de télétravail ?"}'
```

Réponse attendue (exemple) :

```json
{
  "answer": "Le télétravail est autorisé jusqu'à 3 jours par semaine... [source: politique_conges.md]",
  "sources": ["politique_conges.md"]
}
```

### 4. Avec Docker

```bash
cd docker
docker compose up --build
```

## Tests

```bash
make test
```

Les appels LLM/embeddings sont mockés dans les tests d'API : la suite s'exécute
sans clé API réelle et sans appel réseau, ce qui la rend adaptée à une CI classique.

## Choix de conception

- **Providers interchangeables** : `LLM_PROVIDER=openai|anthropic` dans `.env`, sans
  toucher au code métier — les fabriques (`get_chat_model`, `get_embeddings`) isolent
  cette dépendance.
- **Anti-hallucination** : le prompt système impose de répondre "je ne sais pas"
  si l'information n'est pas dans le contexte récupéré, et d'annoter chaque réponse
  avec ses sources.
- **Initialisation paresseuse (lazy)** : le pipeline RAG ne se connecte aux services
  externes (embeddings, LLM) qu'au premier appel réel, pour permettre de démarrer
  l'API et de la tester sans dépendance externe disponible.
- **Séparation ingestion / retrieval / generation** : chaque étape est un module
  indépendant et testable isolément, à l'image d'une architecture Clean/modulaire.

## Roadmap

- [ ] Streaming des réponses (SSE) côté API
- [ ] Ré-écriture de requête (query rewriting) pour améliorer la recherche
- [ ] Ré-ordonnancement des résultats (reranking) avant génération
- [ ] Évaluation automatisée (RAGAS) sur un jeu de questions/réponses de référence
- [ ] Authentification API (clé ou JWT) pour un déploiement multi-utilisateurs

## Licence

MIT — voir [LICENSE](LICENSE).
