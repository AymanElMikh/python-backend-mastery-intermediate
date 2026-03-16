"""
Demo: Decorator Pattern (Design Pattern)
Level: Intermediate (2–3 years experience)
Run:  python demo.py

Note: This is the DESIGN PATTERN (OOP wrapping), not Python's @decorator syntax.
Both share the concept of "wrapping to add behavior" but are different things.
"""

from abc import ABC, abstractmethod


# ── Section 1: The interface and base implementation ──────────────────────────

class DataExporter(ABC):
    """The common interface. Every layer (real or decorator) must implement this."""
    @abstractmethod
    def export(self, data: list) -> str:
        pass


class CSVExporter(DataExporter):
    """The real implementation — just converts data to CSV."""
    def export(self, data: list) -> str:
        return ",".join(str(item) for item in data)


# ── Section 2: Decorator wrappers ─────────────────────────────────────────────

class LoggingDecorator(DataExporter):
    """
    Adds logging before and after the real export.
    Doesn't know or care what the wrapped exporter does.
    """
    def __init__(self, wrapped: DataExporter):
        self._wrapped = wrapped

    def export(self, data: list) -> str:
        print(f"  [LOG] Starting export of {len(data)} items")
        result = self._wrapped.export(data)  # Always delegate!
        print(f"  [LOG] Export complete. Output: '{result[:30]}...' ({len(result)} chars)")
        return result


class CompressionDecorator(DataExporter):
    """
    Simulates compression — adds a tag to indicate the output was compressed.
    In real code: zlib.compress(result.encode())
    """
    def __init__(self, wrapped: DataExporter):
        self._wrapped = wrapped

    def export(self, data: list) -> str:
        result = self._wrapped.export(data)
        compressed = f"[COMPRESSED:{len(result)}bytes]{result}"
        print(f"  [ZIP] Compressed {len(result)} → {len(compressed)} bytes (demo)")
        return compressed


class CachingDecorator(DataExporter):
    """
    Caches export results. If the same data is exported again, skip the work.
    """
    def __init__(self, wrapped: DataExporter):
        self._wrapped = wrapped
        self._cache: dict = {}

    def export(self, data: list) -> str:
        key = tuple(data)  # Lists aren't hashable, convert to tuple for dict key
        if key in self._cache:
            print(f"  [CACHE] Hit! Returning cached result")
            return self._cache[key]
        print(f"  [CACHE] Miss. Computing...")
        result = self._wrapped.export(data)
        self._cache[key] = result
        return result


# ── Section 3: Stacking decorators ────────────────────────────────────────────

def build_exporter(logging: bool = True, caching: bool = True, compression: bool = False) -> DataExporter:
    """
    Factory that builds an exporter with the requested behaviors stacked.
    The base is always CSVExporter; decorators are layered on top.
    """
    exporter: DataExporter = CSVExporter()
    if logging:
        exporter = LoggingDecorator(exporter)
    if compression:
        exporter = CompressionDecorator(exporter)
    if caching:
        exporter = CachingDecorator(exporter)
    return exporter


# ── Section 4: Common mistake — inheritance explosion ────────────────────────

# Without Decorator pattern, you'd end up with subclasses like:
# class LoggedCSVExporter(CSVExporter): ...
# class CachedCSVExporter(CSVExporter): ...
# class LoggedCachedCSVExporter(CSVExporter): ...
# class LoggedCachedCompressedCSVExporter(CSVExporter): ...
# With 4 boolean options that's 2^4 = 16 subclasses. Decorator avoids this entirely.


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Decorator Design Pattern")
    print("=" * 55)

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    print("\n--- Base exporter (no decorators) ---")
    base = CSVExporter()
    print(f"  Result: {base.export(data)}")

    print("\n--- Logging decorator only ---")
    logged = LoggingDecorator(CSVExporter())
    logged.export([10, 20, 30])

    print("\n--- Stacked: Caching → Logging → CSV ---")
    # Order: cache checks first, then logs, then exports
    stacked = CachingDecorator(LoggingDecorator(CSVExporter()))
    print("  First call (cache miss):")
    result1 = stacked.export(data)
    print(f"  Got: {result1[:30]}...")
    print("  Second call (cache hit):")
    result2 = stacked.export(data)
    print(f"  Got: {result2[:30]}...")
    print(f"  Same result: {result1 == result2}")

    print("\n--- Full stack: Caching → Logging → Compression → CSV ---")
    full = CachingDecorator(LoggingDecorator(CompressionDecorator(CSVExporter())))
    full.export([100, 200, 300])

    print("\n--- Factory builds different stacks ---")
    print("  Minimal (no logging, no cache):")
    minimal = build_exporter(logging=False, caching=False)
    print(f"  {minimal.export([1, 2, 3])}")

    print("\n  Full-featured:")
    full_featured = build_exporter(logging=True, caching=True, compression=True)
    full_featured.export([1, 2, 3])

    print("\n--- Key insight: all exporters share the same interface ---")
    exporters = [
        ("plain", CSVExporter()),
        ("logged", LoggingDecorator(CSVExporter())),
        ("cached+logged", CachingDecorator(LoggingDecorator(CSVExporter()))),
    ]
    for name, exp in exporters:
        print(f"\n  [{name}] export([7, 8, 9]):")
        exp.export([7, 8, 9])
