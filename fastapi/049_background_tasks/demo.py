"""
Demo: Background Tasks in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

import time
from dataclasses import dataclass, field
from typing import Callable
from threading import Thread


# ── Minimal BackgroundTasks simulator ────────────────────────────────────────

class BackgroundTasks:
    """
    Simulates FastAPI's BackgroundTasks.
    In real FastAPI: inject as a parameter and FastAPI runs tasks after the response.
    """
    def __init__(self):
        self._tasks: list[tuple[Callable, tuple, dict]] = []

    def add_task(self, func: Callable, *args, **kwargs) -> None:
        self._tasks.append((func, args, kwargs))

    def run_all(self) -> None:
        """In FastAPI, this is called automatically after the response is sent."""
        for func, args, kwargs in self._tasks:
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"    [BG] Task {func.__name__} failed: {e}")


# ── Fake infrastructure ───────────────────────────────────────────────────────

USERS: dict[int, dict] = {}
EVENT_LOG: list[dict] = []
EMAILS_SENT: list[dict] = []
NEXT_USER_ID = 1


# ── Section 1: Background task functions ─────────────────────────────────────

def send_welcome_email(email: str, name: str) -> None:
    """
    Sends a welcome email. In production this calls SendGrid/Mailgun/etc.
    Runs AFTER the response is sent — client doesn't wait.
    """
    time.sleep(0.1)  # simulate network latency
    EMAILS_SENT.append({"type": "welcome", "to": email, "name": name})
    print(f"    [BG Email] Welcome email sent to {email}")


def log_signup_analytics(user_id: int, email: str) -> None:
    """Records signup in analytics system."""
    EVENT_LOG.append({"event": "user_signup", "user_id": user_id, "email": email})
    print(f"    [BG Analytics] Logged signup: user_id={user_id}")


def update_user_count_cache() -> None:
    """Invalidates/updates a cached user count."""
    print(f"    [BG Cache] User count cache updated: {len(USERS)} users")


def send_admin_notification(email: str) -> None:
    """Notifies the admin team of new signups."""
    print(f"    [BG Notify] Admin notified: new user {email}")


# ── Section 2: Route handler using BackgroundTasks ────────────────────────────

def create_user_route(email: str, name: str, background_tasks: BackgroundTasks) -> dict:
    """
    In real FastAPI:

        @app.post("/users", status_code=201)
        def create_user(body: CreateUserRequest, background_tasks: BackgroundTasks):
            user = service.register(body.email, body.name)
            background_tasks.add_task(send_welcome_email, user.email, user.name)
            background_tasks.add_task(log_signup_analytics, user.id, user.email)
            return UserResponse.from_domain(user)
            # ← 201 sent here; THEN background tasks run
    """
    global NEXT_USER_ID

    # --- Synchronous work (blocks until done, before response) ---
    user = {"id": NEXT_USER_ID, "email": email, "name": name}
    USERS[NEXT_USER_ID] = user
    NEXT_USER_ID += 1

    # --- Register background tasks (run AFTER response is returned) ---
    background_tasks.add_task(send_welcome_email, email, name)
    background_tasks.add_task(log_signup_analytics, user["id"], email)
    background_tasks.add_task(update_user_count_cache)

    # Response is returned NOW — client doesn't wait for emails/logging
    return {"id": user["id"], "email": email, "status": "created"}


# ── Section 3: BackgroundTasks vs Celery comparison ──────────────────────────

def simulate_request(email: str, name: str) -> dict:
    """Simulates the full FastAPI request lifecycle with background tasks."""
    tasks = BackgroundTasks()

    print(f"\n  [Request] POST /users  {{email: {email!r}}}")
    start = time.time()

    # 1. Route handler runs (synchronous)
    response = create_user_route(email, name, tasks)

    response_time = time.time() - start
    print(f"  [Response] 201 sent in {response_time*1000:.1f}ms: {response}")
    print(f"  [Server] Now running {len(tasks._tasks)} background tasks...")

    # 2. Background tasks run AFTER response
    tasks.run_all()

    total_time = time.time() - start
    print(f"  [Done] Total server time: {total_time*1000:.1f}ms (client only waited {response_time*1000:.1f}ms)")
    return response


# ── Section 4: The "lost task" problem ───────────────────────────────────────

def demonstrate_task_loss():
    """
    Shows why BackgroundTasks is NOT suitable for mission-critical work.
    If server crashes between response and task execution, task is lost.
    """
    print("\n  Scenario: send 201 response, then crash before background task runs")
    print("  With BackgroundTasks: task never ran — email never sent — no retry possible")
    print("  With Celery: task is in the Redis queue — worker picks it up when server restarts")


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: Background Tasks in FastAPI")
    print("=" * 55)

    print("\n--- Register users with background tasks ---")
    for name, email in [("Alice", "alice@x.com"), ("Bob", "bob@x.com"), ("Carol", "carol@x.com")]:
        simulate_request(email, name)

    print(f"\n--- State after all requests ---")
    print(f"  Users in DB:      {list(USERS.values())}")
    print(f"  Emails sent:      {EMAILS_SENT}")
    print(f"  Events logged:    {EVENT_LOG}")

    print("\n--- BackgroundTasks vs Celery decision guide ---")
    scenarios = [
        ("Welcome email after signup",         "BackgroundTasks", "lightweight, loss acceptable"),
        ("Payment confirmation email",          "Celery",         "must not be lost, needs retry"),
        ("Analytics event ping",               "BackgroundTasks", "lightweight, loss ok"),
        ("Generate a PDF report (5 seconds)",  "Celery",         "long running, blocks worker"),
        ("Cache invalidation",                 "BackgroundTasks", "fast, no retry needed"),
        ("Send 50,000 marketing emails",       "Celery",         "heavy, needs scaling"),
        ("Log a request for debugging",        "BackgroundTasks", "fire-and-forget, no retry"),
        ("Process uploaded video (minutes)",   "Celery",         "long, survives restarts"),
    ]
    print(f"\n  {'Scenario':45s} {'Tool':20s} {'Why'}")
    print("  " + "-" * 80)
    for scenario, tool, why in scenarios:
        print(f"  {scenario:45s} {tool:20s} {why}")

    demonstrate_task_loss()

    print("\n--- Common mistake: sharing DB session with background task ---")
    print("  BAD:")
    print("    @app.post('/users')")
    print("    def create_user(db: Session = Depends(get_db), background_tasks: BackgroundTasks):")
    print("        user = db.query(User).get(1)")
    print("        background_tasks.add_task(send_email, user, db)  ← db is CLOSED after response!")
    print()
    print("  GOOD:")
    print("    def send_email_task(user_id: int):")
    print("        db = SessionLocal()  ← create NEW session inside the task")
    print("        try:")
    print("            user = db.query(User).get(user_id)")
    print("            send_email(user.email)")
    print("        finally:")
    print("            db.close()")
