from app.core.logging import get_logger
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.loaders import load_pdf, load_webpage
from app.services.llm.factory import get_llm_provider
from app.services.vectorstore.chroma_store import get_vector_store

logger = get_logger(__name__)


async def ingest_url(url: str) -> int:
    """Load a public webpage, chunk it, embed it, store it. Returns chunk count."""
    raw_text = await load_webpage(url)
    return await _process(raw_text, source=url)


async def ingest_pdf(file_path: str) -> int:
    raw_text = load_pdf(file_path)
    return await _process(raw_text, source=file_path)


async def _process(raw_text: str, source: str) -> int:
    chunks = chunk_text(raw_text, source=source)
    if not chunks:
        logger.warning(f"No chunks produced for {source}")
        return 0

    llm = get_llm_provider()
    embeddings = await llm.embed([c.text for c in chunks])

    store = get_vector_store()
    store.add_chunks(chunks, embeddings)

    logger.info(f"Ingested {len(chunks)} chunks from {source}")
    return len(chunks)
