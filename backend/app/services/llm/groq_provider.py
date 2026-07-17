from groq import AsyncGroq

from app.core.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.local_embedder import LocalEmbedder

settings = get_settings()


class GroqProvider(LLMProvider):
    """
    Groq gives fast, free-tier chat completions but has no embeddings API.
    So: generation -> Groq, embeddings -> a free local sentence-transformers
    model. Zero API cost, no second key needed.
    """

    def __init__(self) -> None:
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self._embedder = LocalEmbedder()  # only used for .embed()

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        response = await self.client.chat.completions.create(
            model=settings.chat_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._embedder.embed(texts)
