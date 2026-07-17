from fastapi import APIRouter, HTTPException

from app.schemas.chat import IngestResponse, IngestUrlRequest
from app.services.ingestion.pipeline import ingest_url

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestUrlRequest) -> IngestResponse:
    try:
        chunk_count = await ingest_url(request.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to ingest {request.url}: {exc}") from exc

    return IngestResponse(source=request.url, chunks_indexed=chunk_count)
