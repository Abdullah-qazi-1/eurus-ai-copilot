from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag.retriever import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await answer_question(request.question)
    return ChatResponse(answer=result.answer, sources=result.sources, instant=result.instant)
