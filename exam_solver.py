"""Exam solving prompt helpers."""

from __future__ import annotations


def build_exam_prompt(question: str) -> str:
    """Create a chain-of-thought-lite style instruction for exam solutions."""
    return (
        "You are an AI tutor solving an exam question. "
        "Provide a clear step-by-step solution and final answer. "
        "Use headings and bullet points where helpful.\n\n"
        f"Question:\n{question}"
    )
