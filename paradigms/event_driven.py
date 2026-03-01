# =============================================================
# FILE: paradigms/event_driven.py
# PARADIGM: Event-Driven Programming
#
# Event-driven programming structures code around events and
# responses to those events. Instead of calling a function
# directly, you:
#   1. Register a listener (callback) for a named event using on()
#   2. Fire/emit that event using emit() when something happens
#   3. All registered listeners are automatically called with the data
#
# This decouples the producer (code that does the work) from the
# consumer (code that reacts to the result). The calculator does
# not need to know who is listening — it just emits 'result'.
#
# How it works here:
#   - _listeners is the event registry: a dict mapping event names
#     to lists of callback functions.
#   - on(event, callback) registers a listener.
#   - emit(event, data) notifies all listeners for that event.
#   - calculate() evaluates the expression, then emits a 'result'
#     event with the expression and result as payload data.
#     Any part of the app can listen for 'result' without
#     calculate() needing to know about it.
# =============================================================

import ast, operator as _op
from typing import Callable, Dict, List


# ── Event registry ────────────────────────────────────────────
# This dict is the core of the event system.
# Keys are event names (strings), values are lists of callbacks.
# Example after registration:
#   _listeners = {'result': [fn1, fn2], 'error': [fn3]}
_listeners: Dict[str, List[Callable]] = {}


def on(event: str, callback: Callable):
    """Register a listener (callback) for a named event.

    Any function can subscribe to any event. Multiple listeners
    can be registered for the same event — all will be called.

    Args:
        event:    Name of the event to listen for, e.g. 'result'
        callback: Function to call when the event is emitted.
                  Receives the event data as its argument.

    Example:
        def log_result(data):
            print(data['result'])
        on('result', log_result)
    """
    _listeners.setdefault(event, []).append(callback)


def emit(event: str, data=None):
    """Fire an event, calling all registered listeners with data.

    The emitter does not know or care who is listening. This is
    the key advantage of event-driven design: loose coupling.

    Args:
        event: Name of the event to fire, e.g. 'result'
        data:  Payload passed to every listener (can be any type)

    Example:
        emit('result', {'expression': '3+4', 'result': 7})
        # → calls every function registered with on('result', ...)
    """
    for cb in _listeners.get(event, []):
        cb(data)


# ── AST operator map ──────────────────────────────────────────
# Same safe operator whitelist used across all paradigms.
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
    """Recursively evaluate an AST node to a numeric value."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        # Legacy support for older Python AST
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
    """Evaluate an expression and emit a 'result' event with the outcome.

    This is the event-driven difference: after computing the result,
    instead of just returning it silently, we EMIT an event.
    Any listener registered with on('result', ...) will be notified
    automatically — the calculator doesn't need to call them directly.

    Flow:
      expression string
          → AST parse
          → _eval_node() walks the tree
          → result computed
          → emit('result', {...})  ← event fired here
          → return result

    Args:
        expression: Arithmetic string, e.g. "3 + 4", "2^8"
    Returns:
        float result
    """
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        # Evaluate the AST — same as other paradigms up to this point
        result = _eval_node(tree.body)
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

    # ── Event emission ─────────────────────────────────────────
    # This is what makes it event-driven. We broadcast the result
    # as an event payload. Any registered listener receives it.
    # In a larger app, this could update a history panel, a log
    # file, a network socket — all without calculate() knowing.
    emit('result', {'expression': expression, 'result': result})

    return result