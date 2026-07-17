from fastapi import APIRouter

from app.schemas.agents import ProposalRequest, ProposalResponse
from app.services.agents.proposal_agent import generate_proposal
from app.services.pdf.exporter import export_text_to_pdf

router = APIRouter()


@router.post("/proposal", response_model=ProposalResponse)
async def create_proposal(request: ProposalRequest) -> ProposalResponse:
    proposal_text = await generate_proposal(request.client_name, request.requirement)
    pdf_path = export_text_to_pdf(f"Proposal for {request.client_name}", proposal_text)
    return ProposalResponse(proposal_text=proposal_text, pdf_path=pdf_path)
