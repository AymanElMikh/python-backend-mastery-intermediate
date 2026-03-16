# Background Tasks in FastAPI

## 🎯 Interview Question
What are FastAPI's `BackgroundTasks` and when would you use them instead of Celery?

## 💡 Short Answer (30 seconds)
FastAPI's `BackgroundTasks` lets you run a function after the HTTP response has been sent — the client gets the response immediately while the server continues processing. It's perfect for lightweight tasks like sending a confirmation email or logging an event. For heavier, distributed, or retry-capable work — like sending thousands of emails or processing video — use Celery with a broker like Redis.

## 🔬 Explanation
When a user registers, they shouldn't wait for the welcome email to be sent before getting a 201 response. You want to:
1. Validate and create the user
2. Send the HTTP response immediately
3. Send the welcome email in the background

FastAPI `BackgroundTasks` runs tasks in the same process, in the same thread pool, after the response is sent. This is synchronous but post-response.

**Key tradeoffs vs Celery:**

| | BackgroundTasks | Celery |
|---|---|---|
| Setup | Zero — built-in | Redis/RabbitMQ broker needed |
| Retries | ❌ No | ✅ Yes |
| Distributed | ❌ Same process | ✅ Separate workers |
| Suitable for | Quick side effects | Long, heavy, or mission-critical work |
| Process restart | Task lost | Task survives (in queue) |

## 💻 Code Example
```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_welcome_email(email: str) -> None:
    # Runs after response is returned — client doesn't wait
    print(f"Sending welcome email to {email}")
    time.sleep(2)  # simulate slow email sending

def log_signup_event(user_id: int, email: str) -> None:
    print(f"Analytics: new signup user_id={user_id} email={email}")

@app.post("/users", status_code=201)
def create_user(body: CreateUserRequest, background_tasks: BackgroundTasks):
    user = user_service.register(body.email)

    # These run AFTER the 201 response is sent
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(log_signup_event, user.id, user.email)

    return {"id": user.id, "email": user.email}
    # ← Response sent here; then background tasks run
```

## ⚠️ Common Mistakes
1. **Using BackgroundTasks for mission-critical work.** If the server restarts after sending the response but before the background task runs, the task is lost forever. For payment processing, order fulfillment, or anything that must not be lost — use Celery.
2. **Passing ORM session objects into background tasks.** The request's DB session is closed when the response is sent. Background tasks need their own session. Create a new `SessionLocal()` inside the task.
3. **Over-using background tasks for logic that should be synchronous.** If the outcome of the task affects what you return to the client (e.g., the user needs the email for OTP), it must run synchronously.

## ✅ When to Use BackgroundTasks vs Celery
**BackgroundTasks for:**
- Welcome/confirmation emails
- Event logging / analytics pings
- Cache invalidation
- Non-critical notifications

**Celery for:**
- Long-running jobs (image processing, PDF generation)
- Work that must survive server restarts
- Work that needs retries
- Distributing load across multiple workers

## 🔗 Related Concepts
- [performance](../../performance) — Celery for heavy async work
- [design_patterns/028_command_pattern](../../design_patterns/028_command_pattern) — background tasks are essentially queued commands
- [fastapi/044_depends_di](../044_depends_di) — BackgroundTasks is injected via Depends()

## 🚀 Next Step
In `python-backend-mastery`: **Celery with FastAPI** — connecting a Celery worker to a Redis broker, triggering tasks from FastAPI routes, monitoring with Flower, and handling task results asynchronously.
