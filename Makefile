.PHONY: install ingest ask run test lint

install:
	pip install -r requirements-dev.txt

ingest:
	PYTHONPATH=src python -m rag_assistant.cli ingest

ask:
	PYTHONPATH=src python -m rag_assistant.cli ask "$(Q)"

run:
	PYTHONPATH=src uvicorn rag_assistant.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=src pytest --cov=src --cov-report=term-missing

lint:
	ruff check src tests
