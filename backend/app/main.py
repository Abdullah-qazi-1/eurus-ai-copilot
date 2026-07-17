from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging

settings = get_settings()
setup_logging(settings.debug)
logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the frontend's actual origin before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def warm_up() -> None:
    """
    Load the embedding model and open the vector store once, at startup,
    instead of lazily on whatever request happens to hit them first. Without
    this, the first /chat or /proposal call after a restart pays the full
    model-load cost (which used to include slow HuggingFace network checks —
    see local_embedder.py) and can look like the server has hung.
    """
    import time

    from app.services.llm.factory import get_llm_provider
    from app.services.vectorstore.chroma_store import get_vector_store

    start = time.perf_counter()
    logger.info("Warming up embedding model and vector store...")
    get_vector_store()
    await get_llm_provider().embed(["warm-up"])
    logger.info(f"Warm-up complete in {time.perf_counter() - start:.1f}s")


@app.get("/")
async def root() -> dict:
    return {"message": f"{settings.app_name} is running", "docs": "/docs"}
