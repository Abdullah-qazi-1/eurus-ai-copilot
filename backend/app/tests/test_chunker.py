from app.services.ingestion.chunker import chunk_text


def test_chunk_text_produces_chunks():
    text = "a" * 2000
    chunks = chunk_text(text, source="test-source")

    assert len(chunks) > 1
    assert all(c.source == "test-source" for c in chunks)
    assert chunks[0].chunk_index == 0


def test_chunk_text_empty_input():
    assert chunk_text("", source="empty") == []
