# -*- coding: utf-8 -*-
"""
Command parser that converts natural language requests into expressions.
"""

from __future__ import annotations

import re

from utils import normalize_text


_ALLOWED_EXPRESSION_RE = re.compile(r"^[0-9+\-*/%().\s]+$")
_HAS_DIGIT_RE = re.compile(r"\d")


class CommandParser:
    """Parse math commands and task commands from user input."""

    def __init__(self) -> None:
        self._prefixes = (
            "calculate",
            "what is",
            "what's",
            "whats",
            "compute",
            "solve",
            "посчитай",
            "вычисли",
            "сколько будет",
            "сколько",
        )

    def parse_command(self, text: str) -> tuple[str, str]:
        """
        Return a tuple of (command_type, payload).
        command_type: "math", "task", or "unknown".
        """
        # Normalize and strip punctuation that commonly ends a question.
        cleaned = normalize_text(text).rstrip(" ?")
        if not cleaned:
            return "unknown", ""

        task_text = self._parse_task(cleaned)
        if task_text:
            return "task", task_text

        is_math, expression = self._parse_math(cleaned)
        if is_math:
            return "math", expression

        return "unknown", ""

    def _parse_task(self, cleaned: str) -> str:
        # Handle task commands such as "task buy milk" or "add task: buy milk".
        task_match = re.match(
            r"^(add task|task|todo|remember|задача|добавь задачу|напомни|дело)\s*[:\-]?\s+(.+)$",
            cleaned,
        )
        if task_match:
            return task_match.group(2).strip()
        return ""

    def _parse_math(self, cleaned: str) -> tuple[bool, str]:
        # The input is already normalized; parse known math phrasing.
        cleaned = self._strip_prefixes(cleaned)

        # Handle imperative phrasing like "разделить 10 на 2".
        ru_divide = re.match(r"^(разделить|делить)\s+(.+?)\s+на\s+(.+)$", cleaned)
        if ru_divide:
            left = ru_divide.group(2).strip()
            right = ru_divide.group(3).strip()
            if left and right:
                return True, f"({left}) / ({right})"

        ru_multiply = re.match(r"^(умножить)\s+(.+?)\s+на\s+(.+)$", cleaned)
        if ru_multiply:
            left = ru_multiply.group(2).strip()
            right = ru_multiply.group(3).strip()
            if left and right:
                return True, f"({left}) * ({right})"

        en_divide = re.match(r"^(divide|divided)\s+(.+?)\s+by\s+(.+)$", cleaned)
        if en_divide:
            left = en_divide.group(2).strip()
            right = en_divide.group(3).strip()
            if left and right:
                return True, f"({left}) / ({right})"

        en_multiply = re.match(r"^(multiply|multiplied)\s+(.+?)\s+by\s+(.+)$", cleaned)
        if en_multiply:
            left = en_multiply.group(2).strip()
            right = en_multiply.group(3).strip()
            if left and right:
                return True, f"({left}) * ({right})"

        translated = _translate_natural_math(cleaned)

        # Handle "square root of 16" and similar commands.
        sqrt_match = re.match(r"^(square root of|square root|sqrt)\s+(.+)$", translated)
        if sqrt_match:
            expression = sqrt_match.group(2).strip()
            if expression:
                return True, f"({expression}) ** 0.5"

        # Handle "корень из 16" style commands.
        ru_sqrt_match = re.match(r"^(корень из|квадратный корень из)\s+(.+)$", translated)
        if ru_sqrt_match:
            expression = ru_sqrt_match.group(2).strip()
            if expression:
                return True, f"({expression}) ** 0.5"

        # Handle "power 2 8" or "power 2 to 8".
        power_match = re.match(r"^(power|pow)\s+(.+?)\s+(?:to\s+)?(.+)$", translated)
        if power_match:
            base = power_match.group(2).strip()
            exponent = power_match.group(3).strip()
            if base and exponent:
                return True, f"({base}) ** ({exponent})"

        # Handle "степень 2 8" or "в степень 2 8".
        ru_power_match = re.match(r"^(степень|в степень)\s+(.+?)\s+(.+)$", translated)
        if ru_power_match:
            base = ru_power_match.group(2).strip()
            exponent = ru_power_match.group(3).strip()
            if base and exponent:
                return True, f"({base}) ** ({exponent})"

        # Treat translated expression as valid if it only contains math characters.
        if _looks_like_expression(translated):
            return True, translated

        return False, ""

    def _strip_prefixes(self, cleaned: str) -> str:
        for prefix in self._prefixes:
            if cleaned.startswith(prefix + " "):
                return cleaned[len(prefix) :].strip()
        return cleaned


def _looks_like_expression(text: str) -> bool:
    return bool(_HAS_DIGIT_RE.search(text)) and bool(_ALLOWED_EXPRESSION_RE.match(text))


def _translate_natural_math(text: str) -> str:
    # Replace comma decimals with dot (e.g. 3,14 -> 3.14).
    text = re.sub(r"(\d),(\d)", r"\1.\2", text)

    replacements = [
        (r"\bmultiplied by\b", "*"),
        (r"\bmultiply by\b", "*"),
        (r"\btimes\b", "*"),
        (r"\bdivide by\b", "/"),
        (r"\bdivided by\b", "/"),
        (r"\bplus\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bto the power of\b", "**"),
        (r"\bpower of\b", "**"),
        (r"\bумножить на\b", "*"),
        (r"\bумножить\b", "*"),
        (r"\bразделить на\b", "/"),
        (r"\bделить на\b", "/"),
        (r"\bразделить\b", "/"),
        (r"\bделить\b", "/"),
        (r"\bплюс\b", "+"),
        (r"\bминус\b", "-"),
        (r"\bв степени\b", "**"),
        (r"\bв степень\b", "**"),
        (r"\bпо модулю\b", "%"),
        (r"\bmod\b", "%"),
        (r"\bостаток от деления\b", "%"),
    ]

    for pattern, token in replacements:
        text = re.sub(pattern, f" {token} ", text)

    # Replace "x" or "х" between numbers with multiplication.
    text = re.sub(r"(?<=\d)\s*[xх]\s*(?=\d)", " * ", text)

    # Replace "на" between numbers as multiplication (after division phrases).
    text = re.sub(r"(?<=\d)\s+на\s+(?=\d)", " * ", text)

    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text
