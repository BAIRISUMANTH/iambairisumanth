"""PDF ingestion and question-answer prompt helpers."""

from __future__ import annotations

from io import BytesIO

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text content from a PDF file."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def build_pdf_qa_prompt(pdf_text: str, question: str) -> str:
    """Build a robust prompt for answering questions from PDF content."""
    return (
        "You are an expert study assistant. Use the supplied PDF notes to answer clearly. "
        "If information is missing in notes, say so honestly.\n\n"
        f"PDF NOTES:\n{pdf_text[:12000]}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Provide a concise, student-friendly answer."
    )
