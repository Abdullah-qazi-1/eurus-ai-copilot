from dataclasses import dataclass

from app.services.llm.factory import get_llm_provider
from app.services.rag.quick_answers import find_quick_answer
from app.services.vectorstore.chroma_store import get_vector_store

SYSTEM_PROMPT = (
    "You are the Eurus AI Knowledge Assistant. Answer strictly using the provided "
    "context. If the context doesn't contain the answer, say you don't have that "
    "information — never invent facts. Keep answers concise and professional."
)


@dataclass
class RagAnswer:
    answer: str
    sources: list[str]
    instant: bool = False  # True if this skipped embedding search + LLM (served from cache)


async def answer_question(question: str, top_k: int = 5) -> RagAnswer:
    quick = find_quick_answer(question)
    if quick:
        return RagAnswer(answer=quick.answer, sources=quick.sources, instant=True)

    llm = get_llm_provider()
    store = get_vector_store()

    [query_embedding] = await llm.embed([question])
    hits = store.query(query_embedding, top_k=top_k)

    if not hits:
        return RagAnswer(
            answer="I don't have any indexed knowledge yet — please ingest some sources first.",
            sources=[],
        )

    context = "\n\n---\n\n".join(f"[Source: {h['source']}]\n{h['text']}" for h in hits)
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    answer_text = await llm.complete(SYSTEM_PROMPT, user_prompt)
    sources = sorted({h["source"] for h in hits})

    return RagAnswer(answer=answer_text, sources=sources)
