"""
Central application settings.

Every module reads config from here — never from os.environ directly.
This is what lets you swap providers (OpenAI <-> Groq) or change chunk
sizes without touching business logic.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "Eurus AI Employee Copilot"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True

    # --- LLM provider ---
    # "openai" | "groq" | "gemini"
    llm_provider: str = "groq"
    openai_api_key: str = ""
    groq_api_key: str = ""
    gemini_api_key: str = ""
    chat_model: str = "llama-3.3-70b-versatile"   # used when llm_provider == groq
    embedding_model: str = "text-embedding-3-small"  # used when embeddings need OpenAI

    # --- Vector store ---
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "eurus_knowledge_base"

    # --- Ingestion ---
    chunk_size: int = 800
    chunk_overlap: int = 120

    # --- PDF export ---
    pdf_output_dir: str = "./generated_pdfs"


@lru_cache
def get_settings() -> Settings:
    """Cached so we parse .env once, not on every request."""
    return Settings()
