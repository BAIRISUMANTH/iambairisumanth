"""Code generation prompt helpers."""

from __future__ import annotations


def build_code_prompt(request: str, language: str) -> str:
    """Build prompt that asks model to return production quality code."""
    return (
        "You are a senior software engineer. Generate clean, well-commented code. "
        "Also include a short explanation and usage notes.\n\n"
        f"Target language: {language}\n"
        f"Request: {request}\n\n"
        "Return response in markdown with fenced code blocks."
    )
