"""
Quick-answer cache.

For common, predictable questions, skip the embedding search + LLM call
entirely and return a pre-written answer instantly. This is both faster
(no network round-trip to Groq/embedding model) and free (no API call).

HOW TO ADD MORE:
Add an entry to QUICK_ANSWERS with a few phrasings of the same question
(the more variants, the better the match) and a verified answer + sources.
Only put facts here you've actually confirmed against the ingested pages —
don't guess, since these skip the "grounded in retrieved context" safety
net that the normal RAG path has.
"""
from dataclasses import dataclass
from difflib import SequenceMatcher

MATCH_THRESHOLD = 0.72  # 0-1, higher = stricter matching


@dataclass
class QuickAnswer:
    answer: str
    sources: list[str]


QUICK_ANSWERS: list[dict] = [
    {
        "questions": [
            "what ai and cloud services does eurus offer",
            "what services does eurus offer",
            "what does eurus do",
            "what services do you provide",
            "tell me about eurus services",
        ],
        "answer": (
            "Eurus Technologies offers:\n\n"
            "AI Services: Agentic AI, Generative AI, Machine Learning solutions\n\n"
            "Cloud Services: Cloud consulting, migration, infrastructure optimization, "
            "application development, hybrid architectures, disaster recovery, and "
            "management across AWS, Azure, and Google Cloud\n\n"
            "They also offer DevOps services to automate and optimize software "
            "development and deployment."
        ),
        "sources": [
            "https://eurustechnologies.com/",
            "https://eurustechnologies.com/services/",
            "https://eurustechnologies.com/services/artificial-intelligence-services/",
            "https://eurustechnologies.com/services/cloud-solutions/",
        ],
    },
]


def find_quick_answer(question: str) -> QuickAnswer | None:
    """Return a cached answer if the question closely matches a known FAQ, else None."""
    normalized = question.strip().lower()

    best_score = 0.0
    best_entry = None

    for entry in QUICK_ANSWERS:
        for known_question in entry["questions"]:
            score = SequenceMatcher(None, normalized, known_question).ratio()
            if score > best_score:
                best_score = score
                best_entry = entry

    if best_entry and best_score >= MATCH_THRESHOLD:
        return QuickAnswer(answer=best_entry["answer"], sources=best_entry["sources"])

    return None
