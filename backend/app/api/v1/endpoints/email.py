from fastapi import APIRouter

from app.schemas.agents import EmailRequest, EmailResponse
from app.services.agents.email_agent import draft_email

router = APIRouter()


@router.post("/email", response_model=EmailResponse)
async def create_email(request: EmailRequest) -> EmailResponse:
    draft = await draft_email(request.email_type, request.context, request.incoming_email)
    return EmailResponse(draft=draft)
