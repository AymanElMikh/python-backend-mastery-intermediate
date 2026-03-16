"""
Demo: Builder Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from dataclasses import dataclass
from typing import Optional


# ── Section 1: The problem — constructor with too many args ───────────────────

@dataclass
class EmailBad:
    to: str
    subject: str
    body: str
    cc: Optional[list] = None
    bcc: Optional[list] = None
    reply_to: Optional[str] = None
    html_body: Optional[str] = None
    attachments: Optional[list] = None
    priority: str = "normal"
    track_opens: bool = False

# Using this is noisy and error-prone:
# email = EmailBad("user@x.com", "Hi", "Body", None, None, None, "<b>Body</b>", None, "high", True)
# Which None is which? Hard to tell without counting args.


# ── Section 2: Builder pattern ────────────────────────────────────────────────

@dataclass
class Email:
    to: str
    subject: str
    body: str
    cc: list
    bcc: list
    reply_to: Optional[str]
    html_body: Optional[str]
    attachments: list
    priority: str
    track_opens: bool


class EmailBuilder:
    """
    Builds Email objects step by step.
    Each method returns self for chaining.
    """
    def __init__(self, to: str, subject: str):
        # Required fields go in __init__
        self._to = to
        self._subject = subject
        # Optional fields get sensible defaults
        self._body = ""
        self._cc: list = []
        self._bcc: list = []
        self._reply_to: Optional[str] = None
        self._html_body: Optional[str] = None
        self._attachments: list = []
        self._priority = "normal"
        self._track_opens = False

    def body(self, text: str) -> "EmailBuilder":
        self._body = text
        return self  # MUST return self for chaining

    def html(self, html: str) -> "EmailBuilder":
        self._html_body = html
        return self

    def cc(self, *addresses: str) -> "EmailBuilder":
        self._cc.extend(addresses)
        return self

    def bcc(self, *addresses: str) -> "EmailBuilder":
        self._bcc.extend(addresses)
        return self

    def reply_to(self, address: str) -> "EmailBuilder":
        self._reply_to = address
        return self

    def attach(self, filename: str) -> "EmailBuilder":
        self._attachments.append(filename)
        return self

    def priority(self, level: str) -> "EmailBuilder":
        if level not in ("low", "normal", "high"):
            raise ValueError(f"Invalid priority: '{level}'. Use low/normal/high.")
        self._priority = level
        return self

    def track_opens(self) -> "EmailBuilder":
        self._track_opens = True
        return self

    def build(self) -> Email:
        """Validate and construct the final Email object."""
        if not self._body and not self._html_body:
            raise ValueError("Email must have at least a text body or HTML body.")
        return Email(
            to=self._to,
            subject=self._subject,
            body=self._body,
            cc=self._cc,
            bcc=self._bcc,
            reply_to=self._reply_to,
            html_body=self._html_body,
            attachments=self._attachments,
            priority=self._priority,
            track_opens=self._track_opens,
        )


# ── Section 3: Real-world scenario — query builder ────────────────────────────

class SQLQueryBuilder:
    """
    Simplified query builder — like a mini SQLAlchemy.
    Shows how builder chaining produces readable database queries.
    """
    def __init__(self, table: str):
        self._table = table
        self._conditions: list[str] = []
        self._order: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: int = 0
        self._columns: list[str] = ["*"]

    def select(self, *columns: str) -> "SQLQueryBuilder":
        self._columns = list(columns)
        return self

    def where(self, condition: str) -> "SQLQueryBuilder":
        self._conditions.append(condition)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "SQLQueryBuilder":
        self._order = f"{column} {direction}"
        return self

    def limit(self, n: int) -> "SQLQueryBuilder":
        self._limit = n
        return self

    def offset(self, n: int) -> "SQLQueryBuilder":
        self._offset = n
        return self

    def build(self) -> str:
        """Return the SQL string."""
        cols = ", ".join(self._columns)
        sql = f"SELECT {cols} FROM {self._table}"
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        if self._order:
            sql += f" ORDER BY {self._order}"
        if self._limit:
            sql += f" LIMIT {self._limit}"
        if self._offset:
            sql += f" OFFSET {self._offset}"
        return sql


# ── Section 4: Common mistake — forgetting to return self ─────────────────────

class BrokenBuilder:
    def __init__(self, value: str):
        self._value = value

    def with_prefix(self, prefix: str):
        self._value = f"{prefix}_{self._value}"
        # BAD: forgot `return self` — chaining returns None

    def build(self) -> str:
        return self._value


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Builder Pattern")
    print("=" * 55)

    print("\n--- Simple email (just required + body) ---")
    email1 = (EmailBuilder("alice@example.com", "Hello!")
              .body("Hi Alice, just checking in.")
              .build())
    print(f"  To: {email1.to}")
    print(f"  Subject: {email1.subject}")
    print(f"  Body: {email1.body}")
    print(f"  Priority: {email1.priority}")

    print("\n--- Full-featured email ---")
    email2 = (EmailBuilder("bob@example.com", "Q4 Report")
              .body("Please find the Q4 report attached.")
              .html("<b>Please find</b> the Q4 report attached.")
              .cc("manager@example.com", "cfo@example.com")
              .bcc("archive@example.com")
              .reply_to("reports@example.com")
              .attach("q4_report.pdf")
              .attach("q4_appendix.pdf")
              .priority("high")
              .track_opens()
              .build())
    print(f"  To: {email2.to} | CC: {email2.cc}")
    print(f"  Attachments: {email2.attachments}")
    print(f"  Priority: {email2.priority} | Track opens: {email2.track_opens}")

    print("\n--- Builder validates on .build() ---")
    try:
        EmailBuilder("x@x.com", "No body").build()
    except ValueError as e:
        print(f"  ValueError: {e}")

    try:
        EmailBuilder("x@x.com", "Bad priority").body("hi").priority("urgent").build()
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n--- SQL Query Builder ---")
    queries = [
        (SQLQueryBuilder("users")
         .where("is_active = true")
         .order_by("created_at", "DESC")
         .limit(10)
         .build()),

        (SQLQueryBuilder("orders")
         .select("id", "user_id", "total")
         .where("status = 'pending'")
         .where("total > 100")
         .order_by("created_at")
         .limit(25)
         .offset(50)
         .build()),
    ]
    for q in queries:
        print(f"  {q}")

    print("\n--- Common mistake: forgot return self ---")
    broken = BrokenBuilder("myvalue")
    result = broken.with_prefix("test")
    print(f"  with_prefix returned: {result}  ← None! Chaining breaks.")
    # broken.with_prefix("test").build()  # Would raise: AttributeError: 'NoneType' has no attribute 'build'
    print("  Fix: always `return self` in builder methods")
