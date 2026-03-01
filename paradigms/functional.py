# =============================================================
# FILE: paradigms/functional.py
# PARADIGM: Functional Programming
#
# Functional programming treats computation as the evaluation of
# mathematical functions. Key principles:
#   - Pure functions: same input always gives same output, no
#     side effects (no modifying global state, no printing, etc.)
#   - First-class functions: functions are values that can be
#     stored in dicts, passed as arguments, and returned.
#   - No mutable state: operations don't change variables in place.
#
# How it works here:
#   - _OPERATIONS maps operator symbols to functions from Python's
#     `operator` module — functions treated as data (first-class).
#   - _ops maps AST node types to operator functions the same way.
#   - _eval_node is a pure function: given a node, it returns a
#     value without touching any external state.
#   - calculate() is also pure: no side effects, just input → output.
# =============================================================

import ast, operator as _op
from typing import Dict, Callable


# ── First-class functions stored as values ────────────────────
# In functional programming, functions are values just like numbers
# or strings. Here we store them in a dict — this is function
# composition via data structures rather than if/elif chains.

_OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    '+': _op.add,       # operator.add is a function object
    '-': _op.sub,
    '*': _op.mul,
    '/': _op.truediv,
    '%': _op.mod,
}

# ── AST operator map ──────────────────────────────────────────
# Same idea: AST node type → function. No if/elif needed;
# lookup replaces branching (more functional style).
_ops = {
    ast.Add:  _op.add,
    ast.Sub:  _op.sub,
    ast.Mult: _op.mul,
    ast.Div:  _op.truediv,
    ast.Mod:  _op.mod,
    ast.Pow:  _op.pow,
    ast.USub: _op.neg,
    ast.UAdd: lambda x: x,   # identity function — a common FP concept
}


def _eval_node(node):
    """Pure function: evaluates one AST node with no side effects.

    Pure means:
      - It does not modify any variable outside itself.
      - It does not print, write to a file, or change global state.
      - Given the same node, it always returns the same result.

    Recursion is preferred in functional programming over loops
    because each recursive call is a new scope with no shared state.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported operator: {op_type}")
        # Apply the operator function to the two evaluated sub-nodes.
        # _ops[op_type] is a function object retrieved from the dict —
        # this is function application, a core FP concept.
        return _ops[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _ops[op_type](_eval_node(node.operand))
    raise ValueError(f"Invalid expression component: {node!r}")


def calculate(expression: str) -> float:
    """Pure function: evaluate an arithmetic expression functionally.

    No side effects — does not record to history, modify globals,
    or change any state. Just maps input string → output number.

    The functional approach: transform the data (string → AST → value)
    through a pipeline of pure functions without mutation.
    """
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        # _eval_node is applied to the root of the AST tree —
        # this is function application over a data structure.
        return _eval_node(tree.body)
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")