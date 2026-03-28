"""
Calculator engine with safe expression evaluation.
Supports +, -, *, /, **, %, and parentheses.
"""

from __future__ import annotations

import ast
import operator
from typing import Callable

from utils import format_number


_BINARY_OPERATORS: dict[type, Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type, Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorEngine:
    """Evaluate math expressions safely using Python's AST."""

    def evaluate(self, expression: str) -> tuple[bool, str]:
        # Strip whitespace and validate presence of an expression.
        cleaned = expression.strip()
        if not cleaned:
            return False, "Please enter an expression."

        try:
            value = _safe_eval(cleaned)
        except ZeroDivisionError:
            return False, "Division by zero is not allowed."
        except Exception:
            return False, "Invalid expression."

        return True, format_number(value)


def _safe_eval(expression: str) -> float:
    # Parse into AST and evaluate only supported nodes.
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        # Guard against bools (they are subclasses of int).
        if isinstance(node.value, bool):
            raise ValueError("Unsupported constant.")
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Unsupported constant.")

    if isinstance(node, ast.Num):  # For compatibility with older AST nodes.
        return float(node.n)

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        operator_fn = _BINARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError("Unsupported operator.")
        return operator_fn(left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        operator_fn = _UNARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise ValueError("Unsupported unary operator.")
        return operator_fn(operand)

    raise ValueError("Unsupported expression.")
