from dataclasses import dataclass

from app.core.config import get_settings

settings = get_settings()


@dataclass
class Chunk:
    text: str
    source: str
    chunk_index: int


def chunk_text(text: str, source: str) -> list[Chunk]:
    """
    Simple sliding-window chunker: chunk_size chars, chunk_overlap chars
    of overlap between consecutive chunks so we don't cut a sentence's
    meaning in half at the boundary.
    """
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks: list[Chunk] = []

    start = 0
    index = 0
    while start < len(text):
        end = start + size
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, source=source, chunk_index=index))
            index += 1
        start += size - overlap

    return chunks
