from pydantic import BaseModel


class ProposalRequest(BaseModel):
    client_name: str
    requirement: str


class ProposalResponse(BaseModel):
    proposal_text: str
    pdf_path: str


class EmailRequest(BaseModel):
    email_type: str  # reply | cold_outreach | follow_up | meeting_confirmation | ...
    context: str
    incoming_email: str | None = None


class EmailResponse(BaseModel):
    draft: str


class MeetingSummaryRequest(BaseModel):
    transcript: str


class MeetingSummaryResponse(BaseModel):
    summary: str
    transcript: str | None = None  # populated when summarizing from an uploaded recording
