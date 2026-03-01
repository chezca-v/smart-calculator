# =============================================================
# FILE: paradigms/procedural.py
# PARADIGM: Procedural Programming
#
# Procedural programming solves problems through a sequence of
# step-by-step instructions (procedures/functions). Each function
# does one specific job — add, subtract, evaluate — and is called
# in order. There are no objects or classes; just plain functions
# and direct if/elif logic.
#
# How it works here:
#   1. Simple helper functions (add, subtract, etc.) handle
#      two-operand operations directly with if/elif chains.
#   2. calculate() parses any full expression using Python's AST
#      and walks the tree node by node with _eval_node().
# =============================================================

import ast, operator as _op

# ── Simple two-operand helpers ────────────────────────────────
# These are classic procedural functions: one task each,
# called directly by name, no state, no classes.

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    # Guard clause: check for zero before dividing
    if b == 0:
        return None, "Division by zero is not allowed."
    return a / b, None

def modulus(a, b):
    if b == 0:
        return None, "Modulus by zero is not allowed."
    return a % b, None


# ── Operator whitelist ────────────────────────────────────────
# Maps AST node types to their corresponding operator functions.
# This is the procedural way: an explicit lookup table (dict)
# instead of dynamic dispatch.
_ops = {
    ast.Add:      _op.add,
    ast.Sub:      _op.sub,
    ast.Mult:     _op.mul,
    ast.Div:      _op.truediv,
    ast.Mod:      _op.mod,
    ast.Pow:      _op.pow,
    ast.USub:     _op.neg,       # unary minus, e.g. -5
    ast.UAdd:     lambda x: x,   # unary plus, e.g. +5
}


def _eval_node(node):
    """Recursively evaluate a single AST node.

    This is a procedural recursive function — it checks the node
    type with if/elif (step-by-step) and calls itself for sub-nodes.
    """
    if isinstance(node, ast.Constant):
        # A plain number literal like 5 or 3.14
        return node.value
    if isinstance(node, ast.Num):
        # Legacy AST node for older Python versions
        return node.n
    if isinstance(node, ast.BinOp):
        # Binary operation: left OP right  (e.g. 3 + 4)
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported operator: {op_type}")
        left  = _eval_node(node.left)   # recurse left
        right = _eval_node(node.right)  # recurse right
        return _ops[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        # Unary operation: OP value  (e.g. -5)
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _ops[op_type](_eval_node(node.operand))
    raise ValueError(f"Invalid expression component: {node!r}")


def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression using procedural step-by-step logic.

    Steps:
      1. Strip and replace '^' with '**' (Python exponent syntax)
      2. Parse string into an AST (Abstract Syntax Tree)
      3. Walk the tree node by node using _eval_node()
      4. Return the final numeric result

    The UI sends tokens like "3 + 4" or "10 * 2"; the '^' symbol
    is replaced so expressions like "2^8" work correctly.
    """
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        return _eval_node(tree.body)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}") from e