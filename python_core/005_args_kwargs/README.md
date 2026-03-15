# *args and **kwargs — Flexible Function Signatures

## 🎯 Interview Question
"What are `*args` and `**kwargs` in Python? When would you use them in a real project?"

## 💡 Short Answer (30 seconds)
`*args` collects any extra positional arguments into a tuple, and `**kwargs` collects any extra keyword arguments into a dict. You use them when writing functions that need to accept a variable number of arguments — like a decorator that wraps any function, a base class method that passes arguments to a parent, or a utility function that forwards options to another library.

## 🔬 Explanation
The `*` and `**` operators have two related uses:

**In function definitions** (collecting):
- `*args` → collects extra positional args into a tuple
- `**kwargs` → collects extra keyword args into a dict

**In function calls** (unpacking):
- `*my_list` → unpacks a list/tuple as positional args
- `**my_dict` → unpacks a dict as keyword args

You see this in real backend code constantly:
- **Decorators**: `def wrapper(*args, **kwargs)` — must accept any arguments to wrap any function
- **`super().__init__(**kwargs)`** — forwarding keyword args up the inheritance chain
- **Logging functions**: `log("msg", extra={"user_id": 42})` — optional extra context
- **ORM/query builders**: `Model.filter(**conditions)` — dynamic filter conditions

The naming `args` and `kwargs` is just convention — you could write `*stuff` or `**options`. The `*` and `**` are what matter.

## 💻 Code Example
```python
# *args: accepts any number of positional arguments
def total(*numbers):
    return sum(numbers)

total(1, 2, 3)        # 6
total(10, 20)         # 30
total()               # 0

# **kwargs: accepts any number of keyword arguments
def create_user(**fields):
    return {key: value for key, value in fields.items()}

create_user(name="Alice", email="alice@example.com", role="admin")

# Combining: fixed, *args, keyword-only, **kwargs
def send_notification(message, *recipients, priority="normal", **metadata):
    print(f"Sending '{message}' to {recipients}")
    print(f"Priority: {priority}, Metadata: {metadata}")

send_notification("Server down", "alice", "bob", priority="high", source="monitor")
```

## ⚠️ Common Mistakes

1. **Wrong parameter order** — Python enforces a strict order: `(regular, *args, keyword_only, **kwargs)`. Putting `**kwargs` before `*args` or a regular argument after `**kwargs` is a `SyntaxError`.

2. **Modifying `args` or `kwargs` thinking it affects the caller** — `args` is a copy of the positional arguments as a tuple (immutable). `kwargs` is a new dict. Mutating `kwargs` inside a function doesn't affect the caller's variables.

3. **Using `*args` when a named parameter is clearer** — if you always pass exactly 2 arguments, name them. `*args` signals "variable number" to readers; using it for a fixed count is misleading.

## ✅ When to Use vs When NOT to Use

**Use `*args` when:**
- The function genuinely accepts a variable number of items (like `print()`, `max()`, `sum()`)
- Writing decorators that must pass through any arguments
- Calling a function with a dynamically built list of arguments

**Use `**kwargs` when:**
- Forwarding options to another function without listing every option
- Building functions with optional metadata or config (like logging context)
- `super().__init__()` in cooperative multiple inheritance

**Avoid when:**
- A fixed, named parameter list is clearer — explicit is better than implicit
- You're hiding required arguments inside `**kwargs` — makes the API hard to discover

## 🔗 Related Concepts
- [001_decorators_basics](../001_decorators_basics) — decorators use `*args, **kwargs` to wrap any function
- [004_closures](../004_closures) — the wrapper in a closure uses `*args, **kwargs`

## 🚀 Next Step
In `python-backend-mastery`: **Positional-only parameters** (`/` in signatures) and **keyword-only parameters** (`*` separator) — Python 3.8+ fine-grained API design for library authors, and how Pydantic and FastAPI exploit `**kwargs` internally.
