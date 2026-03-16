"""
Demo: Command Pattern
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Section 1: Command interface ──────────────────────────────────────────────

class Command(ABC):
    """Every command must be executable. Undo is optional."""
    @abstractmethod
    def execute(self) -> str:
        """Run the command. Returns a result description."""
        pass

    def undo(self) -> str:
        """Reverse the command. Not all commands support this."""
        raise NotImplementedError(f"{self.__class__.__name__} does not support undo.")


# ── Section 2: Concrete commands ─────────────────────────────────────────────

@dataclass
class SendEmailCommand(Command):
    to: str
    subject: str
    body: str

    def execute(self) -> str:
        # In real code: call an email API here
        return f"Email sent to {self.to!r} — subject: {self.subject!r}"

    def undo(self) -> str:
        # Emails can't really be unsent, but you could log a recall attempt
        return f"(Cannot undo sent email to {self.to!r})"


@dataclass
class UpdateUserRoleCommand(Command):
    user_id: int
    new_role: str
    _previous_role: Optional[str] = field(default=None, init=False, repr=False)

    # Simulated DB state (in real app this would hit the DB)
    _user_db: dict = field(default_factory=lambda: {1: "user", 2: "user", 3: "admin"}, init=False, repr=False)

    def execute(self) -> str:
        self._previous_role = self._user_db.get(self.user_id, "unknown")
        self._user_db[self.user_id] = self.new_role
        return f"User #{self.user_id} role changed: {self._previous_role!r} → {self.new_role!r}"

    def undo(self) -> str:
        if self._previous_role is None:
            return "Cannot undo — command was never executed."
        self._user_db[self.user_id] = self._previous_role
        restored = self._previous_role
        self._previous_role = None
        return f"Undone: User #{self.user_id} role restored to {restored!r}"


@dataclass
class CreateReportCommand(Command):
    report_type: str
    date_range: str

    def execute(self) -> str:
        # Simulates generating a report file
        filename = f"{self.report_type}_{self.date_range.replace(' ', '_')}.csv"
        return f"Report generated: {filename}"


# ── Section 3: Command queue (job queue simulation) ───────────────────────────

class CommandQueue:
    """
    Stores commands and executes them in order.
    Think of Celery tasks — commands queued and run by workers.
    """
    def __init__(self):
        self._pending: list[Command] = []
        self._history: list[tuple[Command, str]] = []  # (command, result)

    def add(self, command: Command) -> None:
        self._pending.append(command)
        print(f"  [Queue] Queued: {command.__class__.__name__}")

    def run_all(self) -> list[str]:
        results = []
        while self._pending:
            cmd = self._pending.pop(0)
            try:
                result = cmd.execute()
                self._history.append((cmd, result))
                print(f"  [Run]   {result}")
                results.append(result)
            except Exception as e:
                print(f"  [FAIL]  {cmd.__class__.__name__} failed: {e}")
        return results

    def undo_last(self) -> Optional[str]:
        if not self._history:
            print("  [Undo]  Nothing to undo.")
            return None
        cmd, _ = self._history.pop()
        try:
            result = cmd.undo()
            print(f"  [Undo]  {result}")
            return result
        except NotImplementedError as e:
            print(f"  [Undo]  {e}")
            return None

    def print_history(self) -> None:
        print(f"  Command history ({len(self._history)} entries):")
        for i, (cmd, result) in enumerate(self._history, 1):
            print(f"    {i}. {cmd.__class__.__name__}: {result}")


# ── Section 4: Audit log decorator for commands ───────────────────────────────

class AuditedCommand(Command):
    """
    Wraps any command to log execution time and result.
    Combines Decorator pattern + Command pattern.
    """
    def __init__(self, command: Command):
        self._command = command

    def execute(self) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = self._command.execute()
        print(f"  [AUDIT] {timestamp} | {self._command.__class__.__name__} | {result}")
        return result

    def undo(self) -> str:
        return self._command.undo()


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Command Pattern")
    print("=" * 55)

    print("\n--- Basic command execution ---")
    email_cmd = SendEmailCommand(
        to="alice@example.com",
        subject="Your account is ready",
        body="Welcome to the platform!"
    )
    result = email_cmd.execute()
    print(f"  Result: {result}")

    print("\n--- Command queue (async job simulation) ---")
    queue = CommandQueue()
    queue.add(SendEmailCommand("bob@example.com", "Invoice", "See attached"))
    queue.add(UpdateUserRoleCommand(user_id=1, new_role="admin"))
    queue.add(CreateReportCommand("sales", "2026-Q1"))
    queue.add(SendEmailCommand("cfo@example.com", "Q1 Report", "Generated"))

    print()
    queue.run_all()

    print("\n--- History ---")
    queue.print_history()

    print("\n--- Undo last command ---")
    queue.undo_last()  # CreateReportCommand (no undo)

    print("\n--- UpdateUserRoleCommand supports undo ---")
    role_cmd = UpdateUserRoleCommand(user_id=2, new_role="moderator")
    print(f"  Execute: {role_cmd.execute()}")
    print(f"  Undo:    {role_cmd.undo()}")

    print("\n--- Audited command (Decorator + Command) ---")
    audited = AuditedCommand(CreateReportCommand("revenue", "2026-01"))
    audited.execute()
    audited = AuditedCommand(SendEmailCommand("cto@example.com", "Alert", "Disk 90%"))
    audited.execute()
