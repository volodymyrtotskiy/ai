"""
Shared utility helpers.
"""

from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for simpler parsing."""
    cleaned = text.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def format_number(value: float) -> str:
    """Format numbers to avoid trailing .0 where possible."""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.10g}"
