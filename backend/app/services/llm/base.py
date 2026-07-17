"""
Provider-agnostic LLM interface.

Every concrete provider (OpenAI, Groq, Gemini) implements this ABC.
Nothing outside this module ever imports openai/groq/google directly —
that's what makes swapping providers a one-file change.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Return a plain-text completion for a single-turn prompt."""
        raise NotImplementedError

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""
        raise NotImplementedError
