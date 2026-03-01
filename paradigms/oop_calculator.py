# =============================================================
# FILE: paradigms/oop_calculator.py
# PARADIGM: Object-Oriented Programming (OOP)
#
# OOP solves problems by modelling them as objects — things that
# have both state (data) and behaviour (methods). Instead of
# calling plain functions, you create an instance of a class and
# call methods on it.
#
# How it works here:
#   - Calculator is a class. It has attributes (num1, num2) that
#     hold the operands, and methods (add, subtract, etc.) that
#     operate on those attributes.
#   - The UI creates ONE shared instance (_OOP = Calculator()) and
#     reuses it for every calculation — this is encapsulation.
#   - calculate() parses expressions via an AST evaluator that
#     lives as a method inside the class (_eval_node), keeping all
#     calculation logic encapsulated within the object.
# =============================================================

import ast, operator as _op


class Calculator:
    """A calculator object that encapsulates operands and operations.

    Attributes:
        num1 (float): The first operand.
        num2 (float): The second operand.
    """

    def __init__(self):
        # Object state: the two operands are stored on the instance.
        # Encapsulation means this data belongs to the object, not
        # to any global variable or outside function.
        self.num1 = 0.0
        self.num2 = 0.0

    # ── Operation methods ─────────────────────────────────────
    # Each method is a behaviour of the Calculator object.
    # They read from self.num1 and self.num2 (the object's state).

    def add(self):
        return self.num1 + self.num2

    def subtract(self):
        return self.num1 - self.num2

    def multiply(self):
        return self.num1 * self.num2

    def divide(self):
        if self.num2 == 0:
            raise ValueError("Division by zero is not allowed.")
        return self.num1 / self.num2

    def modulus(self):
        if self.num2 == 0:
            raise ValueError("Modulus by zero is not allowed.")
        return self.num1 % self.num2

    # ── AST operator map (class-level attribute) ──────────────
    # Defined at class level so it is shared across all instances
    # (class attribute, not instance attribute).
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

    def _eval_node(self, node):
        """Recursively evaluate an AST node.

        This is an instance method — it belongs to the object and
        accesses self._ops through the object reference.
        Using 'self' is the OOP way; compare to procedural where
        _eval_node is a plain module-level function.
        """
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):
            # Compatibility with older Python AST
            return node.n
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self._ops:
                raise ValueError(f"Unsupported operator: {op_type}")
            # Recurse using self — the method calls itself through the object
            left  = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self._ops[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self._ops:
                raise ValueError(f"Unsupported unary operator: {op_type}")
            return self._ops[op_type](self._eval_node(node.operand))
        raise ValueError(f"Invalid expression component: {node!r}")

    def calculate(self, expression: str) -> float:
        """Evaluate an arithmetic expression through this Calculator object.

        This is the public interface of the class. The caller does not
        need to know about _eval_node or _ops — that implementation
        detail is hidden inside the object (encapsulation).

        Args:
            expression: e.g. "3 + 4", "10 * 2 - 1", "2^8"
        Returns:
            float result
        """
        expr = expression.strip().replace('^', '**')
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body)
        except Exception:
            raise ValueError(f"Invalid expression: {expression}")