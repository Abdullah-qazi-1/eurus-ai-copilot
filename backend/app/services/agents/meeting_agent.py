from app.services.llm.factory import get_llm_provider

SYSTEM_PROMPT = (
    "You summarize meeting transcripts. Output must have two clear sections: "
    "'Summary' (key points, decisions, budget/timeline if mentioned) and "
    "'Action Items' (owner -> task -> deadline, one per line). "
    "If a detail isn't in the transcript, omit it rather than guessing."
)


async def summarize_meeting(transcript: str) -> str:
    llm = get_llm_provider()
    return await llm.complete(SYSTEM_PROMPT, f"Transcript:\n{transcript}", temperature=0.2)
