from app.services.llm.factory import get_llm_provider

SYSTEM_PROMPT = (
    "You draft professional business emails. Match the requested tone and email type. "
    "Keep it concise, clear, and free of filler. Sign off generically unless a name is given."
)


async def draft_email(email_type: str, context: str, incoming_email: str | None = None) -> str:
    """
    email_type: 'reply' | 'cold_outreach' | 'follow_up' | 'meeting_confirmation' | etc.
    context: what the email needs to convey (e.g. "confirm 6-week timeline")
    incoming_email: the email being replied to, if any
    """
    llm = get_llm_provider()
    parts = [f"Email type: {email_type}", f"Context: {context}"]
    if incoming_email:
        parts.append(f"Incoming email to reply to:\n{incoming_email}")

    return await llm.complete(SYSTEM_PROMPT, "\n\n".join(parts), temperature=0.5)
