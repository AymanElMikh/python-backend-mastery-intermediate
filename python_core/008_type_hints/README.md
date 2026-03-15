# Type Hints — Annotations in Practice

## 🎯 Interview Question
"Why would you add type hints to Python code, and what are the most useful types to know for backend development?"

## 💡 Short Answer (30 seconds)
Type hints are annotations that tell developers (and tools like mypy, Pyright, and your IDE) what types a function expects and returns. They don't change runtime behavior — Python still runs untyped. But they catch bugs before runtime, make code self-documenting, and are required by Pydantic and FastAPI to work their magic. For backend work, knowing `Optional`, `Union`, `List`, `Dict`, `Tuple`, and `Callable` is essential.

## 🔬 Explanation
Type hints were added in Python 3.5 (PEP 484) and have evolved significantly. Here's what you need in real backend work:

**Basic types** — `str`, `int`, `float`, `bool`, `bytes`

**Collection types** (Python 3.9+ can use built-in, older needs `from typing import`):
```python
# Python 3.9+
def process(items: list[str]) -> dict[str, int]: ...

# Python 3.8 and older
from typing import List, Dict
def process(items: List[str]) -> Dict[str, int]: ...
```

**`Optional[X]`** = `X | None` — a value that might be None. Very common in function parameters with defaults.

**`Union[X, Y]`** = value can be X or Y. Python 3.10+ syntax: `X | Y`.

**`Callable[[ArgTypes], ReturnType]`** — for function arguments (decorators, callbacks).

**Why they matter in the real world:**
- FastAPI uses type hints to auto-generate request validation and OpenAPI docs
- Pydantic models are entirely type-hint-driven
- mypy/Pyright catches type mismatches before your code hits production
- IDEs use them for autocomplete and refactoring
- New team members understand APIs instantly without reading implementations

## 💻 Code Example
```python
from typing import Optional, Union
from datetime import datetime

def get_user(user_id: int) -> dict[str, str]:
    ...

def find_user(email: str) -> Optional[dict]:  # might return None
    ...

def parse_date(value: Union[str, datetime]) -> datetime:
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value

# Python 3.10+ shorthand (equivalent to Union):
def parse_date_modern(value: str | datetime) -> datetime:
    ...

# Return type annotations for functions with no return value
def log_event(message: str, level: str = "INFO") -> None:
    print(f"[{level}] {message}")
```

## ⚠️ Common Mistakes

1. **Using `Optional[str]` but not handling `None`** — annotating a return as `Optional[str]` and then calling `.upper()` on it without checking is `None`. The type hint is a promise — honor it.

2. **`list` vs `List` confusion** — in Python 3.9+, use `list[str]` directly. In Python 3.8, you need `from typing import List` and use `List[str]`. Mixing them up causes `TypeError` at runtime on older versions.

3. **Annotating everything immediately in legacy code** — adding type hints to existing untyped code all at once often introduces errors. Prefer gradual typing: annotate new code and critical functions first.

## ✅ When to Use vs When NOT to Use

**Use type hints when:**
- Writing any function that will be used by other developers (public APIs)
- Working with FastAPI, Pydantic, or any type-driven framework
- Building a codebase where you want mypy or Pyright in CI
- The parameter's type isn't obvious from the name

**Skip type hints on:**
- Short internal scripts or one-off utilities
- Very obvious cases where the type is self-evident from context (but even then, IDE users benefit)
- Highly dynamic code where the type genuinely varies (though consider `Any` from `typing`)

## 🔗 Related Concepts
- [005_args_kwargs](../005_args_kwargs) — annotating variadic args: `*args: int`, `**kwargs: str`
- [007_exception_handling](../007_exception_handling) — `-> None` vs `-> NoReturn` for functions that always raise

## 🚀 Next Step
In `python-backend-mastery`: **Protocols and structural subtyping** — using `typing.Protocol` to define interfaces without inheritance, and runtime checkable protocols; also `TypeVar` for generic functions.
