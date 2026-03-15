# Closures — Functions That Remember

## 🎯 Interview Question
"What is a closure in Python? Can you give a real-world example of where you'd use one?"

## 💡 Short Answer (30 seconds)
A closure is a function that remembers variables from the scope where it was defined — even after that outer function has finished running. You create one by defining a function inside another function and returning it. They're useful for building factory functions, simple caches, and are the foundation of how decorators work.

## 🔬 Explanation
In Python, functions are objects. When an inner function references a variable from its enclosing function, Python "closes over" that variable — it captures a reference to it and keeps it alive even after the outer function returns.

Think of it like this: the inner function carries a little backpack containing the variables it needs from the outer scope.

```
outer() defines x = 10
  inner() uses x
outer() returns inner
→ inner still "remembers" x = 10 via its closure
```

The actual variables are stored in `function.__closure__` — each cell holds a reference to a captured variable.

Real-world uses:
- **Decorator factories**: `@retry(max_attempts=3)` — `retry` is a closure factory
- **Configuration-baked functions**: create a `send_email` function pre-configured with SMTP settings
- **Simple counters/accumulators** without a class
- **Middleware/plugin patterns**: wrapping functions with environment-specific config

The key mental model: **closures are a lightweight alternative to single-method classes**. If you'd otherwise write a class just to hold one piece of state and call one method, a closure is often cleaner.

## 💻 Code Example
```python
def make_multiplier(factor):
    """Factory function — returns a closure."""
    def multiply(number):
        return number * factor  # 'factor' is captured from outer scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15

# Each closure has its own 'factor':
print(double.__closure__[0].cell_contents)  # 2
print(triple.__closure__[0].cell_contents)  # 3
```

## ⚠️ Common Mistakes

1. **The loop closure trap** — creating closures in a loop where all closures end up sharing the same variable (the loop variable's final value). Fix: use a default argument to capture the current value: `def make_fn(i=i):`.

2. **Mutating a closed-over variable without `nonlocal`** — in Python 3, if you try to reassign (not just read) a variable from the enclosing scope, you get `UnboundLocalError`. You need `nonlocal var_name` to tell Python you mean the outer variable.

3. **Using closures when a class would be clearer** — closures are great for simple cases, but once you have 3+ captured variables or multiple methods, a class becomes easier to read and test.

## ✅ When to Use vs When NOT to Use

**Use closures when:**
- You need a factory that produces customized functions (multipliers, formatters, validators)
- Writing decorators (they're always closures)
- You need lightweight state with a single operation — avoid the overhead of a class

**Avoid closures when:**
- State has more than 2–3 variables — use a class instead
- The behavior needs to be testable in isolation — closures can make testing harder
- You need to serialize or pickle the function — closures don't serialize well

## 🔗 Related Concepts
- [001_decorators_basics](../001_decorators_basics) — decorators are closures
- [010_functools_basics](../010_functools_basics) — `functools.partial` is a built-in closure alternative

## 🚀 Next Step
In `python-backend-mastery`: **Descriptors and `__get__`** — how Python's attribute lookup protocol works, which is the foundation of `property`, `classmethod`, and all ORM field definitions.
