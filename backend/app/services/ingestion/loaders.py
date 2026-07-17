"""
Loaders pull raw text from public sources only.

Rule: never load anything behind a login wall, paywall, or robots.txt
disallow. This module is the boundary that keeps the whole project
scraping only what's legitimately public.
"""
import httpx
from bs4 import BeautifulSoup

from app.core.logging import get_logger

logger = get_logger(__name__)


async def load_webpage(url: str) -> str:
    """Fetch a public URL and return its visible text, stripped of nav/script noise."""
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "EurusCopilotBot/1.0"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    logger.info(f"Loaded {len(lines)} non-empty lines from {url}")
    return "\n".join(lines)


def load_pdf(file_path: str) -> str:
    """Extract text from a local PDF file (e.g. a downloaded public brochure)."""
    import pymupdf  # PyMuPDF

    doc = pymupdf.open(file_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    logger.info(f"Loaded {len(pages)} pages from {file_path}")
    return "\n".join(pages)
