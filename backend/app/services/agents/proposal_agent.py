from app.services.llm.factory import get_llm_provider
from app.services.rag.retriever import answer_question

SYSTEM_PROMPT = (
    "You are a proposal writer for a software/AI services company. Given the client's "
    "requirement and relevant company context, write a structured proposal with these "
    "sections: Project Overview, Objectives, Proposed Solution, Technology Stack, "
    "Timeline, Deliverables, Future Scope. Be specific and professional."
)


async def generate_proposal(client_name: str, requirement: str) -> str:
    # Step 1: pull relevant company context (services, past capabilities) via RAG
    context = await answer_question(
        f"What services and technical capabilities are relevant to: {requirement}"
    )

    # Step 2: draft the proposal using that grounded context
    llm = get_llm_provider()
    user_prompt = (
        f"Client: {client_name}\n"
        f"Requirement: {requirement}\n\n"
        f"Relevant company context:\n{context.answer}\n\n"
        f"Write the full proposal now."
    )
    return await llm.complete(SYSTEM_PROMPT, user_prompt, temperature=0.4)
