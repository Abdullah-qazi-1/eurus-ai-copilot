"""
Local embeddings — runs on your own machine via sentence-transformers.
No API key, no per-call cost. Slightly lower quality than OpenAI's
embeddings but more than good enough for a demo knowledge base.

The model downloads once (~80MB) the first time it's used, then it's
cached locally.
"""
import os
from functools import lru_cache


@lru_cache
def _get_model():
    from sentence_transformers import SentenceTransformer

    # Once the model is cached locally, skip HuggingFace's "check for
    # updates" network calls (a handful of HEAD requests per file) — this
    # is what was adding a long delay on every server restart. If the
    # model isn't cached yet, fall back to a normal (online) load once.
    os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        os.environ.pop("HF_HUB_OFFLINE", None)
        return SentenceTransformer("all-MiniLM-L6-v2")


class LocalEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        model = _get_model()
        # encode() is sync/CPU-bound; fine for a demo's request volume
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return vectors.tolist()
