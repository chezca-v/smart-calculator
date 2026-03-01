# =============================================================
# FILE: extras/additional_features.py
# PURPOSE: Shared utilities used by the UI and all paradigms
#
# This module provides:
#   1. History tracker  — records every calculation done in the app
#   2. Extra math ops   — square_root, exponentiate, percentage
#   3. AST evaluator    — general-purpose expression calculator
#
# It is intentionally separate from the paradigm files so that
# history recording and helper math are available everywhere
# without tying them to any one programming paradigm.
# =============================================================

import math
from typing import List, Tuple
import ast, operator as _op


# ── History tracker ───────────────────────────────────────────
# A simple in-memory list of (expression, result) pairs.
# Cleared when the app closes (session-only).
_history: List[Tuple[str, float]] = []


def get_history() -> List[Tuple[str, float]]:
    """Return a copy of the full calculation history."""
    return list(_history)


def clear_history():
    """Wipe all history entries."""
    _history.clear()


def record(expression: str, result: float):
    """Append one entry to the history list.

    Called publicly from the UI after every = press, and
    internally by the extra math functions below.
    """
    _history.append((expression, result))


# Private alias so internal code uses the same function
_record = record


# ── Extra math operations ─────────────────────────────────────
# These wrap Python's math functions, record to history, and
# are called by the scientific tray buttons in the UI.

def exponentiate(base: float, exp: float) -> float:
    """Raise base to the power of exp and record to history."""
    result = base ** exp
    _record(f"{base} ^ {exp}", result)
    return result


def square_root(n: float) -> float:
    """Return the square root of n. Raises if n is negative."""
    if n < 0:
        raise ValueError("Cannot take square root of a negative number.")
    result = math.sqrt(n)
    _record(f"sqrt({n})", result)
    return result


def percentage(value: float, percent: float) -> float:
    """Return what percent% of value is, e.g. percentage(200, 15) = 30."""
    result = (value * percent) / 100.0
    _record(f"{value} x {percent}%", result)
    return result


# ── AST-based expression evaluator ───────────────────────────
# A safe general-purpose evaluator used by calculate() below.
# Uses Python's ast module to parse the expression into a tree,
# then walks the tree to compute the result — no eval() calls.

_ops = {
    ast.Add:  _op.add,
    ast.Sub:  _op.sub,
    ast.Mult: _op.mul,
    ast.Div:  _op.truediv,
    ast.Mod:  _op.mod,
    ast.Pow:  _op.pow,
    ast.USub: _op.neg,
    ast.UAdd: lambda x: x,
}


def _eval_node(node):
    """Recursively evaluate one node of a parsed AST."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported operator: {op_type}")
        return _ops[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _ops[op_type](_eval_node(node.operand))
    raise ValueError(f"Invalid expression component: {node!r}")


def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression with PEMDAS support.

    Handles:
      - Full operator precedence via AST parsing
      - Caret (^) as exponent operator
      - 'sqrt N' shorthand, e.g. 'sqrt 9' → 3.0

    This is used as a fallback/utility evaluator — each paradigm
    file has its own calculate() that demonstrates that paradigm.
    """
    parts = expression.strip().split()
    # Shortcut: "sqrt 9" → square_root(9)
    if len(parts) == 2 and parts[0].lower() == 'sqrt':
        return square_root(float(parts[1]))

    expr = expression.strip().replace('^', '**')
    try:
        tree   = ast.parse(expr, mode='eval')
        result = float(_eval_node(tree.body))
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

    _record(expression, result)
    return result