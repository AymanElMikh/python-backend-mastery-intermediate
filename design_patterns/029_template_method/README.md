# Template Method Pattern

## 🎯 Interview Question
What is the Template Method pattern and where would you use it in backend code?

## 💡 Short Answer (30 seconds)
The Template Method defines a skeleton of an algorithm in a base class, with some steps left for subclasses to implement. The base class controls the order and overall flow; subclasses only customize specific steps. It's useful when you have a fixed process (like "parse → validate → save → notify") but the implementation of individual steps varies by use case.

## 🔬 Explanation
Classic backend example: data import pipelines. Every import follows the same flow: read the file, parse it, validate rows, save to DB, generate a report. But the parsing step differs for CSV vs Excel vs JSON.

With Template Method:
- The base class `DataImporter` defines `import_data()` which calls `read()`, `parse()`, `validate()`, `save()`, `report()` in order
- `CSVImporter` and `ExcelImporter` override only `parse()`
- The "framework" (base class) controls the sequence; subclasses fill in the blanks

This is how many web frameworks work internally — the framework calls `on_get()`, `on_post()` etc. in a defined sequence; you override what you need.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class DataImporter(ABC):
    def import_data(self, source: str) -> dict:
        """Template method — defines the fixed algorithm."""
        raw = self.read(source)
        rows = self.parse(raw)
        valid_rows = self.validate(rows)
        count = self.save(valid_rows)
        return self.report(count)

    def read(self, source: str) -> str:
        return open(source).read()  # Same for all formats

    @abstractmethod
    def parse(self, raw: str) -> list[dict]:
        """Each subclass implements its own parsing."""
        pass

    def validate(self, rows: list[dict]) -> list[dict]:
        return [r for r in rows if r]  # Default: skip empty rows

    def save(self, rows: list[dict]) -> int:
        print(f"Saving {len(rows)} rows to DB")
        return len(rows)

    def report(self, count: int) -> dict:
        return {"imported": count, "status": "ok"}

class CSVImporter(DataImporter):
    def parse(self, raw: str) -> list[dict]:
        lines = raw.strip().split("\n")
        headers = lines[0].split(",")
        return [dict(zip(headers, line.split(","))) for line in lines[1:]]
```

## ⚠️ Common Mistakes
1. **Overriding the template method itself.** The whole point of `import_data()` (the template) is that subclasses don't touch it. Override only the hook methods.
2. **Making too many steps abstract.** If everything is abstract, you have an interface, not a template. The base class should provide real default implementations for common steps.
3. **Confusing with Strategy.** Template Method uses inheritance (subclasses override steps). Strategy uses composition (inject a different object). Prefer Strategy if you want runtime swapping; use Template Method when the variations are naturally expressed as subclasses.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You have a fixed algorithm with one or two customizable steps
- Multiple classes share the same structure but differ in specific parts
- You want to prevent subclasses from changing the overall flow

**Don't use when:**
- You need to swap algorithms at runtime — use Strategy instead
- The variations are too numerous — subclass per variation gets unwieldy
- The "template" is so small that a simple function with a callback is cleaner

## 🔗 Related Concepts
- [oop/012_inheritance_super](../../oop/012_inheritance_super) — Template Method relies on inheritance
- [oop/014_abstract_base_classes](../../oop/014_abstract_base_classes) — abstract methods define the hook steps
- [design_patterns/023_strategy_pattern](../023_strategy_pattern) — Strategy is the composition-based alternative

## 🚀 Next Step
In `python-backend-mastery`: **Hook methods and extension points** — how Django class-based views use Template Method (`get_queryset()`, `get_serializer_class()`) to let you customize behavior at specific lifecycle points.
