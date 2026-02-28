import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

# ── Event-driven hooks ─────────────────────────────────────────
_listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}


def on(event: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    """Register event listener for events like:
    calculation_success, calculation_error, retry, history_updated.
    """
    _listeners.setdefault(event, []).append(callback)


def emit(event: str, payload: Optional[Dict[str, Any]] = None) -> None:
    for cb in _listeners.get(event, []):
        cb(payload or {})


# ── Advanced error handling ────────────────────────────────────
class CalculatorError(ValueError):
    def __init__(self, message: str, *, code: str = "CALC_ERROR", recoverable: bool = True):
        super().__init__(message)
        self.code = code
        self.recoverable = recoverable


# ── History tracking (OOP + procedural convenience) ───────────
@dataclass
class HistoryEntry:
    expression: str
    result: float
    timestamp: str
    input_type: str


_history: List[HistoryEntry] = []


def _record(expression: str, result: float, input_type: str) -> None:
    entry = HistoryEntry(
        expression=expression,
        result=result,
        timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        input_type=input_type,
    )
    _history.append(entry)
    emit("history_updated", {"entry": entry})


def get_history() -> List[Tuple[str, float]]:
    """Backwards-compatible history view for existing UI usage."""
    return [(item.expression, item.result) for item in _history]


def get_history_entries() -> List[HistoryEntry]:
    return list(_history)


def clear_history() -> None:
    _history.clear()


# ── Functional operation mapping ───────────────────────────────
_BINARY_OPS: Dict[str, Callable[[float, float], float]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "^": lambda a, b: a ** b,
}


def exponentiate(base: float, exp: float) -> float:
    result = _BINARY_OPS["^"](base, exp)
    _record(f"{base} ^ {exp}", result, "exponent")
    return result


def square_root(n: float) -> float:
    if n < 0:
        raise CalculatorError(
            "Cannot take square root of a negative number.",
            code="NEGATIVE_ROOT",
            recoverable=False,
        )
    result = math.sqrt(n)
    _record(f"√{n}", result, "sqrt")
    return result


def percentage(value: float, percent: float) -> float:
    result = (value * percent) / 100.0
    _record(f"{value} × {percent}%", result, "percentage")
    return result


# ── Input type detection (procedural parsing) ──────────────────
def detect_input_type(expression: str) -> str:
    expr = expression.strip()
    if not expr:
        return "empty"

    if expr.startswith("sqrt ") or expr.startswith("√"):
        return "sqrt"

    parts = expr.split()
    if len(parts) == 1:
        try:
            float(parts[0])
            return "number"
        except ValueError:
            return "unknown"

    if len(parts) == 3:
        if parts[1] == "%":
            return "percentage"
        if parts[1] in _BINARY_OPS:
            return "binary"

    return "unknown"


def _parse_number(token: str) -> float:
    try:
        return float(token)
    except ValueError as exc:
        raise CalculatorError(f"Non-numeric input detected: '{token}'", code="TYPE_ERROR") from exc


def _calculate_once(expression: str, *, previous_result: Optional[float] = None) -> float:
    input_type = detect_input_type(expression)
    expr = expression.strip()

    if input_type == "empty":
        raise CalculatorError("Expression is empty.", code="EMPTY_INPUT")

    if input_type == "number":
        result = _parse_number(expr)
        _record(expression, result, input_type)
        return result

    if input_type == "sqrt":
        token = expr[1:] if expr.startswith("√") else expr.split(maxsplit=1)[1]
        result = square_root(_parse_number(token.strip()))
        return result

    parts = expr.split()
    if len(parts) != 3:
        raise CalculatorError("Invalid format. Use 'num op num' (e.g. '2 + 3').", code="FORMAT_ERROR")

    left, op, right = parts

    # Continuous mode support: allow '_' to represent previous result.
    if left == "_":
        if previous_result is None:
            raise CalculatorError("No previous result available for '_' placeholder.", code="NO_CONTEXT")
        num1 = previous_result
    else:
        num1 = _parse_number(left)

    num2 = _parse_number(right)

    if op == "%":
        result = percentage(num1, num2)
        return result

    if op not in _BINARY_OPS:
        raise CalculatorError(f"Unsupported operator: {op}", code="UNSUPPORTED_OP")

    if op == "/" and num2 == 0:
        raise CalculatorError("Division by zero.", code="DIV_BY_ZERO")

    result = _BINARY_OPS[op](num1, num2)
    _record(expression, result, input_type)
    return result


# ── OOP continuous calculation mode ────────────────────────────
class ContinuousCalculator:
    def __init__(self):
        self.last_result: Optional[float] = None

    def calculate(self, expression: str) -> float:
        result = _calculate_once(expression, previous_result=self.last_result)
        self.last_result = result
        emit("calculation_success", {"expression": expression, "result": result})
        return result

    def continue_with(self, operator_symbol: str, value: float) -> float:
        if self.last_result is None:
            raise CalculatorError("No previous result to continue from.", code="NO_CONTEXT")
        expression = f"_ {operator_symbol} {value}"
        return self.calculate(expression)

    def reset(self) -> None:
        self.last_result = None


_SESSION = ContinuousCalculator()


# ── Retry system ───────────────────────────────────────────────
def calculate_with_retry(expression: str, retries: int = 1) -> float:
    """Retry once with lightweight normalization; emits retry/error events."""
    attempts = max(0, retries) + 1
    current = expression

    for attempt in range(1, attempts + 1):
        try:
            return _SESSION.calculate(current)
        except CalculatorError as err:
            emit(
                "retry",
                {
                    "attempt": attempt,
                    "max_attempts": attempts,
                    "expression": current,
                    "error": str(err),
                    "code": err.code,
                },
            )
            if attempt >= attempts:
                emit("calculation_error", {"expression": expression, "error": str(err), "code": err.code})
                raise

            # simple recoveries for common user typing in UI
            normalized = current.strip().replace("x", "*").replace("X", "*").replace("÷", "/")
            if normalized.lower().startswith("sqrt") and not normalized.lower().startswith("sqrt "):
                normalized = normalized[:4] + " " + normalized[4:]
            current = normalized


# ── Existing public API used by Kivy UI ────────────────────────
def calculate(expression: str) -> float:
    return calculate_with_retry(expression, retries=1)