"""
Demo: Template Method Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod


# ── Section 1: Template method — the fixed algorithm skeleton ─────────────────

class ReportGenerator(ABC):
    """
    Base class defines the report generation algorithm.
    Subclasses customize specific steps.
    The overall flow is fixed in generate_report().
    """

    def generate_report(self, data: list[dict]) -> str:
        """
        THE TEMPLATE METHOD — subclasses must NOT override this.
        It calls the hook methods in a fixed order.
        """
        print(f"  [{self.__class__.__name__}] Starting report generation...")
        filtered = self.filter_data(data)
        sorted_data = self.sort_data(filtered)
        formatted = self.format_rows(sorted_data)
        header = self.make_header()
        footer = self.make_footer(len(sorted_data))
        return header + "\n" + formatted + "\n" + footer

    # ── Hook methods ── subclasses override these ──────────────────────────

    def filter_data(self, data: list[dict]) -> list[dict]:
        """Default: no filtering."""
        return data

    @abstractmethod
    def format_rows(self, data: list[dict]) -> str:
        """Subclasses must implement: how rows are formatted."""
        pass

    def sort_data(self, data: list[dict]) -> list[dict]:
        """Default: sort by name if present, else unsorted."""
        return sorted(data, key=lambda row: row.get("name", ""))

    def make_header(self) -> str:
        """Default header — subclasses can override."""
        return "--- REPORT ---"

    def make_footer(self, row_count: int) -> str:
        """Default footer."""
        return f"--- END ({row_count} records) ---"


# ── Section 2: Concrete implementations ──────────────────────────────────────

class CSVReportGenerator(ReportGenerator):
    """Generates CSV output."""

    def format_rows(self, data: list[dict]) -> str:
        if not data:
            return ""
        headers = ",".join(data[0].keys())
        rows = [",".join(str(v) for v in row.values()) for row in data]
        return headers + "\n" + "\n".join(rows)

    def make_header(self) -> str:
        return "# CSV Export"

    def make_footer(self, row_count: int) -> str:
        return f"# Total rows: {row_count}"


class HTMLReportGenerator(ReportGenerator):
    """Generates HTML table output."""

    def filter_data(self, data: list[dict]) -> list[dict]:
        """Override: filter out inactive users."""
        return [row for row in data if row.get("active", True)]

    def format_rows(self, data: list[dict]) -> str:
        if not data:
            return "<p>No data</p>"
        headers = "".join(f"<th>{k}</th>" for k in data[0].keys())
        rows = ""
        for row in data:
            cells = "".join(f"<td>{v}</td>" for v in row.values())
            rows += f"<tr>{cells}</tr>\n"
        return f"<table>\n<tr>{headers}</tr>\n{rows}</table>"

    def make_header(self) -> str:
        return "<html><body>"

    def make_footer(self, row_count: int) -> str:
        return f"<p>{row_count} records</p></body></html>"


class SummaryReportGenerator(ReportGenerator):
    """Only shows count and totals — no individual rows."""

    def format_rows(self, data: list[dict]) -> str:
        total = sum(row.get("amount", 0) for row in data)
        return f"  Records: {len(data)}\n  Total amount: ${total:.2f}"

    def make_header(self) -> str:
        return "=== SUMMARY ==="

    def make_footer(self, row_count: int) -> str:
        return "==============="


# ── Section 3: Comparing Template Method vs Strategy ─────────────────────────

# Template Method uses INHERITANCE — subclasses are wired at definition time
# Strategy uses COMPOSITION — the algorithm is injected at runtime

# Template Method is the right choice when:
# - Variations are naturally expressed as "types" (CSV report, HTML report)
# - The overall algorithm should be enforced (can't skip steps)

# Strategy is better when:
# - You want to swap the algorithm at runtime based on config or user input
# - You want to avoid subclassing


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Template Method Pattern")
    print("=" * 55)

    data = [
        {"name": "Charlie", "email": "charlie@x.com", "amount": 150.00, "active": True},
        {"name": "Alice", "email": "alice@x.com", "amount": 300.00, "active": True},
        {"name": "Bob", "email": "bob@x.com", "amount": 75.00, "active": False},
        {"name": "Diana", "email": "diana@x.com", "amount": 225.00, "active": True},
    ]

    print("\n--- CSV Report (no filtering, sorted by name) ---")
    csv_gen = CSVReportGenerator()
    print(csv_gen.generate_report(data))

    print("\n--- HTML Report (filters out inactive users) ---")
    html_gen = HTMLReportGenerator()
    print(html_gen.generate_report(data))

    print("\n--- Summary Report ---")
    summary_gen = SummaryReportGenerator()
    print(summary_gen.generate_report(data))

    print("\n--- All generators use the SAME algorithm flow ---")
    print("  generate_report() always calls:")
    print("  1. filter_data()")
    print("  2. sort_data()")
    print("  3. format_rows()")
    print("  4. make_header() + formatted + make_footer()")
    print("  Subclasses only customize individual steps, not the flow.")

    print("\n--- Common mistake: overriding the template method itself ---")
    print("  DON'T: override generate_report() in a subclass")
    print("  DO:    override filter_data(), format_rows(), make_header(), make_footer()")
    print("  The template method is the 'framework' — let it stay in control.")
