import ast, operator as _op
from typing import Callable, Dict, List

_listeners: Dict[str, List[Callable]] = {}

def on(event: str, callback: Callable):
    _listeners.setdefault(event, []).append(callback)

def emit(event: str, data=None):
    for cb in _listeners.get(event, []):
        cb(data)

# AST evaluator same as other paradigms
_ops = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
    ast.USub: _op.neg,
    ast.UAdd: lambda x: x,
}

def _eval_node(node):
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
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        result = float(_eval_node(tree.body))
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

    emit('result', {'expression': expression, 'result': result})
    return result
