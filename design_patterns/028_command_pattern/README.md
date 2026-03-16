# Command Pattern

## 🎯 Interview Question
What is the Command pattern and what problem does it solve in backend systems?

## 💡 Short Answer (30 seconds)
The Command pattern wraps a request or action as an object. Instead of calling a function directly, you create a "command" object that describes the action, then execute it. This lets you queue commands, log them, retry them, or undo them — because the action is just data. In backend systems it's used for job queues, undo/redo in editors, and audit trails.

## 🔬 Explanation
Think of a task queue: instead of directly calling `send_email(user_id=5)`, you create a `SendEmailCommand(user_id=5)` object, put it in a queue, and a worker picks it up and executes it later. The command carries all the data needed to run — it's self-contained.

This also enables:
- **Undo/redo**: each command knows how to reverse itself
- **Audit logging**: you store the command objects to see what happened
- **Retries**: if a command fails, you re-run the same object
- **Deferred execution**: build up a list of commands and run them in one transaction

Celery tasks are basically the Command pattern — you define a task class (the command), send it to a queue (store the command), and a worker executes it.

## 💻 Code Example
```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    def undo(self) -> None:
        raise NotImplementedError("This command doesn't support undo")

class SendEmailCommand(Command):
    def __init__(self, to: str, subject: str, body: str):
        self.to = to
        self.subject = subject
        self.body = body

    def execute(self) -> None:
        print(f"Sending email to {self.to}: {self.subject}")

class CommandQueue:
    def __init__(self):
        self._queue: list[Command] = []

    def add(self, command: Command) -> None:
        self._queue.append(command)

    def run_all(self) -> None:
        while self._queue:
            cmd = self._queue.pop(0)
            cmd.execute()

queue = CommandQueue()
queue.add(SendEmailCommand("alice@x.com", "Welcome", "Hi Alice!"))
queue.run_all()
```

## ⚠️ Common Mistakes
1. **Making commands too large.** A command should do one thing. `ProcessOrderAndSendEmailAndUpdateInventoryCommand` is too big — split it into three commands.
2. **Storing mutable objects in commands.** Commands should be self-contained snapshots. If you store a reference to a live object that changes, your command won't replay correctly.
3. **Implementing undo for everything.** Not all commands need `undo`. A `DeleteUserCommand` with undo needs careful thought (what if dependent data changed?). Only implement undo where it's genuinely needed.

## ✅ When to Use vs When NOT to Use
**Use when:**
- You need to queue, defer, or retry actions (job queues, task workers)
- You need an audit trail of what happened and when
- You're building an undo/redo system (text editors, admin panels)
- You want to batch actions and run them atomically

**Don't use when:**
- The action is simple and fire-and-forget with no need for queuing or logging
- Adding the command wrapper just adds indirection without benefit
- A simple function call is all you need

## 🔗 Related Concepts
- [design_patterns/025_observer_pattern](../025_observer_pattern) — events trigger commands
- [design_patterns/023_strategy_pattern](../023_strategy_pattern) — strategy defines how; command defines what
- [performance](../../performance) — Celery uses command-like tasks for async job queues

## 🚀 Next Step
In `python-backend-mastery`: **CQRS (Command Query Responsibility Segregation)** — separating write operations (commands) from read operations (queries) at the architecture level, enabling separate scaling.
