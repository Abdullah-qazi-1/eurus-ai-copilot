from functools import lru_cache

import chromadb

from app.core.config import get_settings
from app.services.ingestion.chunker import Chunk

settings = get_settings()


class ChromaStore:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(settings.chroma_collection_name)

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.collection.add(
            ids=[f"{c.source}-{c.chunk_index}" for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[{"source": c.source, "chunk_index": c.chunk_index} for c in chunks],
        )

    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        result = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        hits = []
        for doc, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            hits.append({"text": doc, "source": meta["source"], "score": 1 - dist})
        return hits


@lru_cache
def get_vector_store() -> ChromaStore:
    return ChromaStore()
