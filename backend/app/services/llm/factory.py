from functools import lru_cache

from app.core.config import get_settings
from app.services.llm.base import LLMProvider

settings = get_settings()


@lru_cache
def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        from app.services.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if settings.llm_provider == "groq":
        from app.services.llm.groq_provider import GroqProvider
        return GroqProvider()

    raise ValueError(
        f"Unknown llm_provider '{settings.llm_provider}'. "
        f"Add a new provider class implementing LLMProvider and register it here."
    )
