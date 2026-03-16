# Application Factory Pattern

## 🎯 Interview Question
What is the application factory pattern in Flask or FastAPI, and why is it better than creating the app at module level?

## 💡 Short Answer (30 seconds)
The application factory pattern means you create the app inside a function (e.g., `create_app(config)`) instead of at module level. This lets you create multiple app instances with different configurations — one for tests with a test database, one for production. Without a factory, you can't easily create a fresh app instance per test, and tests bleed into each other.

## 🔬 Explanation
Without a factory:
```python
# app.py
app = Flask(__name__)
app.config["DATABASE_URL"] = "postgresql://prod..."
db.init_app(app)
```

Every test that imports `app` gets the exact same configured instance. To use a test database, you either mutate `app.config` (fragile) or can't.

With a factory:
```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or ProductionConfig)
    db.init_app(app)
    app.register_blueprint(users_bp)
    return app
```

Tests call `create_app(TestConfig)` — they get a fresh, isolated app with a test database every time. Different tests can use different configs. The test setup is clean.

In FastAPI the same idea applies: a `create_app()` function that instantiates `FastAPI()`, registers routes, and sets up middleware — instead of a module-level `app = FastAPI()` that's configured once and shared.

## 💻 Code Example
```python
# Flask example
from flask import Flask
from .extensions import db
from .routers import users_bp, orders_bp

def create_app(config=None) -> Flask:
    app = Flask(__name__)

    # Load config (default to production if not specified)
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object("config.ProductionConfig")

    # Initialize extensions
    db.init_app(app)

    # Register blueprints / routes
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(orders_bp, url_prefix="/orders")

    return app

# In tests:
app = create_app(TestConfig)
client = app.test_client()
```

## ⚠️ Common Mistakes
1. **Importing `app` at module level in tests.** `from app import app` imports the module-level app with production config. Instead, create a fresh test app: `app = create_app(TestConfig)`.
2. **Doing too much in the factory.** The factory should wire things together (register blueprints, init extensions). It should NOT have business logic or seed data.
3. **Not passing config as a parameter.** A factory that reads config from a hardcoded environment variable internally misses the point — the config should be injectable.

## ✅ When to Use vs When NOT to Use
**Always use when:**
- Building any Flask app (this is the standard Flask pattern)
- You write automated tests (which you always should)
- You have multiple environments (dev, test, prod)

**Optional for FastAPI** — FastAPI apps are often simpler because DI handles per-request configuration. But a `create_app()` factory is still useful for registering routers and setting up middleware.

## 🔗 Related Concepts
- [clean_architecture/033_dependency_injection](../033_dependency_injection) — factory wires up DI
- [clean_architecture/036_settings_config](../036_settings_config) — config objects passed into the factory
- [unit_tests](../../unit_tests) — testing with a factory-created app
- [flask](../../flask) — blueprints and Flask-specific setup

## 🚀 Next Step
In `python-backend-mastery`: **Lifespan management in FastAPI** — the `@asynccontextmanager` lifespan pattern for startup/shutdown events (connecting to DB, warming caches, graceful shutdown).
