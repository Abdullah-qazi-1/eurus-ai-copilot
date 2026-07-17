from fastapi import APIRouter

from app.api.v1.endpoints import chat, email, health, ingest, meeting, proposal

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router, tags=["ingestion"])
api_router.include_router(chat.router, tags=["rag"])
api_router.include_router(proposal.router, tags=["agents"])
api_router.include_router(email.router, tags=["agents"])
api_router.include_router(meeting.router, tags=["agents"])
