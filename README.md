# Smart Calculator — Multi-Paradigm Kivy App
![Calculator](https://png.pngtree.com/png-vector/20231116/ourmid/pngtree-watercolor-cute-calculator-png-image_10449965.png)

## Project Structure

```
SmartCalculator/
├── ui/
│   └── main.py                  # Kivy UI entry point
├── paradigms/
│   ├── procedural.py            # Procedural paradigm
│   ├── oop_calculator.py        # OOP paradigm (Calculator class)
│   ├── functional.py            # Functional paradigm
│   └── event_driven.py          # Event-driven paradigm
├── extras/
│   └── additional_features.py  # Extended math + history
└── README.md
```

## How to Run

```bash
pip install kivy
python ui/main.py
```

## How to Build APK (Buildozer)

```bash
pip install buildozer
buildozer init
# Edit buildozer.spec: set source.dir = . and source.include_exts = py,kv
buildozer android debug
```

## Features

- **4 Paradigms**: Switch via Spinner — Procedural, OOP, Functional, Event-Driven
- **Extended Mode**: Supports `^` (exponentiation), `√` (square root), `%` (percentage)
- **Dark / Light Theme**: Toggle with ☀/🌙 button
- **Expression display**: Shows expression above result, like a real calculator
- **Error handling**: Displays errors inline, no crashes
- **History**: Tracked in `additional_features` module (call `get_history()`)

## Paradigm Signatures

All paradigms expose:
```python
def calculate(expression: str) -> float
# expression format: "num op num"  e.g. "12 * 5000"
```

OOP additionally usable as:
```python
calc = Calculator()
calc.calculate("10 + 5")  # -> 15.0
```

