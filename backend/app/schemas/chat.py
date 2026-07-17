from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    instant: bool = False


class IngestUrlRequest(BaseModel):
    url: str


class IngestResponse(BaseModel):
    source: str
    chunks_indexed: int
