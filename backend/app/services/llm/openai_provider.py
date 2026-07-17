from openai import AsyncOpenAI

from app.core.config import get_settings
from app.services.llm.base import LLMProvider

settings = get_settings()


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]
