import math
from typing import List, Tuple
import ast, operator as _op

# ── History tracker ──────────────────────────────────────────
_history: List[Tuple[str, float]] = []

def get_history() -> List[Tuple[str, float]]:
    return list(_history)

def clear_history():
    _history.clear()

def record(expression: str, result: float):
    """Public record — called from UI too so ALL ops are tracked."""
    _history.append((expression, result))

# keep private alias for internal use
_record = record

# ── Extra math operations ─────────────────────────────────────
def exponentiate(base: float, exp: float) -> float:
    result = base ** exp
    _record(f"{base} ^ {exp}", result)
    return result

def square_root(n: float) -> float:
    if n < 0:
        raise ValueError("Cannot take square root of a negative number.")
    result = math.sqrt(n)
    _record(f"sqrt({n})", result)
    return result

def percentage(value: float, percent: float) -> float:
    result = (value * percent) / 100.0
    _record(f"{value} x {percent}%", result)
    return result


# existing imports and history code remain unchanged above

def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression with PEMDAS and extra features.

    Supports caret (^) for exponent and normal operators.  The expression
    is expected to have tokens separated by spaces coming from the UI,
    but the AST parser handles normal precedence regardless of spacing.
    """
    # shortcut for sqrt notation
    parts = expression.strip().split()
    if len(parts) == 2 and parts[0].lower() == 'sqrt':
        return square_root(float(parts[1]))

    # generic evaluation using AST
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        result = float(_eval_node(tree.body))
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

    _record(expression, result)
    return result