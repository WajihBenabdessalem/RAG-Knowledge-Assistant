"""Template de prompt pour la génération augmentée par le contexte récupéré."""

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """Tu es un assistant qui répond aux questions UNIQUEMENT à partir du \
contexte fourni ci-dessous.

Règles strictes :
- Si la réponse ne se trouve pas dans le contexte, dis clairement que tu ne sais pas \
et ne l'invente pas.
- Cite systématiquement les sources utilisées, au format [source: nom_du_fichier].
- Réponds de façon concise, factuelle et en français.
"""

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "Contexte :\n{context}\n\nQuestion : {question}"),
    ]
)
