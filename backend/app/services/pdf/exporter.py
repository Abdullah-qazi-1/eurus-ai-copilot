import os
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.core.config import get_settings

settings = get_settings()


def export_text_to_pdf(title: str, body: str) -> str:
    """Writes a simple PDF with a title and body paragraphs, returns the file path."""
    os.makedirs(settings.pdf_output_dir, exist_ok=True)
    file_path = os.path.join(settings.pdf_output_dir, f"{uuid.uuid4().hex}.pdf")

    doc = SimpleDocTemplate(
        file_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    for paragraph in body.split("\n\n"):
        clean = paragraph.strip().replace("\n", "<br/>")
        if clean:
            story.append(Paragraph(clean, styles["BodyText"]))
            story.append(Spacer(1, 10))

    doc.build(story)
    return file_path
