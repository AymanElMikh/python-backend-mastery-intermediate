# Celery Intro — Distributed Task Queues

## 🎯 Interview Question
What is Celery and what problem does it solve? When would you use Celery in a Python backend?

## 💡 Short Answer (30 seconds)
Celery is a distributed task queue for Python. Instead of doing slow work synchronously in your API (like sending thousands of emails or processing a large file), you enqueue a "task" — a Python function — and a separate Celery worker process picks it up and runs it asynchronously. Your API returns immediately, the worker does the heavy lifting in the background. A message broker (usually Redis or RabbitMQ) holds the task queue between the API and the workers.

## 🔬 Explanation
The architecture:

```
[FastAPI / Flask]
    │  .delay()  (enqueue task)
    ▼
[Redis/RabbitMQ broker]  ← task queue
    │  picks up task
    ▼
[Celery Worker(s)]
    │  runs the function
    ▼
[Result backend (optional)]
```

**Why Celery instead of FastAPI's `BackgroundTasks`?**

| | BackgroundTasks | Celery |
|---|---|---|
| Separate process | ❌ Same as API | ✅ Separate worker |
| Survives API restart | ❌ Lost | ✅ Task stays in queue |
| Retry on failure | ❌ No | ✅ Built-in |
| Scheduled tasks | ❌ No | ✅ Celery Beat |
| Scale independently | ❌ No | ✅ Add more workers |
| Monitor tasks | ❌ No | ✅ Flower dashboard |

Use Celery for: long-running jobs, retry-required work, scheduled jobs, and anything that must survive a server restart.

## 💻 Code Example
```python
# celery_app.py
from celery import Celery

app = Celery(
    "myapp",
    broker="redis://localhost:6379/0",  # task queue
    backend="redis://localhost:6379/1",  # result storage
)

# tasks.py
from celery_app import app

@app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: int, email: str) -> str:
    try:
        # Call email service
        email_client.send(to=email, subject="Welcome!")
        return f"Email sent to {email}"
    except Exception as exc:
        # Retry in 60 seconds if it fails
        raise self.retry(exc=exc, countdown=60)

# In your FastAPI route:
@router.post("/users", status_code=201)
def create_user(body: CreateUserRequest):
    user = user_service.register(body.email)
    send_welcome_email.delay(user.id, user.email)  # enqueue
    return {"id": user.id}  # returns immediately
```

## ⚠️ Common Mistakes
1. **Passing ORM model instances as task arguments.** Celery serializes arguments to JSON. SQLAlchemy objects can't be serialized. Pass IDs (integers) and look up the object inside the task.
2. **Not configuring retries.** Without `max_retries` and `countdown`, a failed task is just lost. Always configure retries for tasks that call external APIs.
3. **Doing too much in one task.** A task that sends an email AND updates the DB AND calls three external APIs is hard to retry correctly (if email sent but DB update failed, you'd resend the email on retry). Keep tasks focused.

## ✅ When to Use Celery
**Use Celery for:**
- Emails, SMS, push notifications
- Image/video/file processing
- Scheduled reports or data exports
- Third-party API calls that might fail and need retries
- Any job that could take more than 1–2 seconds

**Don't use Celery for:**
- Simple fire-and-forget logging (BackgroundTasks is fine)
- In-request computation that the response depends on (must be synchronous)
- Single-worker scenarios with no need for retry (BackgroundTasks is simpler)

## 🔗 Related Concepts
- [performance/057_celery_task_basics](../057_celery_task_basics) — writing and calling tasks
- [performance/058_celery_periodic_tasks](../058_celery_periodic_tasks) — scheduled tasks with Celery Beat
- [fastapi/049_background_tasks](../../fastapi/049_background_tasks) — the simpler alternative

## 🚀 Next Step
In `python-backend-mastery`: **Celery canvas** — chains (`task_a | task_b`), groups (run in parallel), chords (parallel + callback), and building complex workflows for data pipelines.
