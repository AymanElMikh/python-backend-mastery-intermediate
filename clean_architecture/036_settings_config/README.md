# Settings & Configuration Management

## 🎯 Interview Question
How do you manage configuration (database URLs, API keys, feature flags) in a Python backend project? What's wrong with hardcoding config values?

## 💡 Short Answer (30 seconds)
Configuration belongs in environment variables, not in code. You read them at startup into a settings object using Pydantic's `BaseSettings` or a simple dataclass. Hardcoding config breaks the 12-factor app principle, leaks secrets into git history, and makes the same code impossible to deploy to different environments (dev, staging, prod) without code changes.

## 🔬 Explanation
The rule: **code is the same everywhere; config is what changes between environments.**

Dev uses `sqlite:///dev.db`; prod uses `postgresql://prod-server/mydb`. That's config. If you hardcode the SQLite URL, your code can't run in prod without editing the source file — and now prod credentials might end up in git.

Best practices:
1. **Environment variables** — set in `.env` locally, in your cloud platform in prod
2. **A single settings object** — one place to look up any config value
3. **Type validation** — Pydantic `BaseSettings` validates types at startup so you fail fast on missing config, not at 3am when a feature is first used

Never commit `.env` files to git. Always commit `.env.example` with fake values as documentation.

## 💻 Code Example
```python
# settings.py — using Pydantic BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    max_connections: int = 10
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

# Create once, import everywhere
settings = Settings()

# Usage:
# from settings import settings
# engine = create_engine(settings.database_url)
```

```bash
# .env (local dev — never commit)
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-only-secret
DEBUG=true

# .env.example (DO commit — documentation)
DATABASE_URL=postgresql://user:pass@host/dbname
SECRET_KEY=your-secret-key-here
DEBUG=false
```

## ⚠️ Common Mistakes
1. **Hardcoding secrets in source code.** `api_key = "sk_live_abc123"` in your code will end up in git history forever (even after you delete it). Rotate the key immediately if this happens.
2. **Reading `os.environ` everywhere.** Scattered `os.environ.get("DB_URL")` calls make it impossible to see all config in one place and don't validate types. Use a settings object.
3. **Committing `.env` to git.** Add `.env` to `.gitignore` immediately. Only `.env.example` (with fake values) should be committed.

## ✅ When to Use vs When NOT to Use
**Always use environment variables for:**
- Database connection strings
- API keys and secrets
- Feature flags
- Environment-specific URLs

**Hardcoding is OK for:**
- Default values that are the same everywhere (`pagination_limit = 20`)
- Non-sensitive constants that never change between environments

## 🔗 Related Concepts
- [clean_architecture/033_dependency_injection](../033_dependency_injection) — settings are injected into services that need them
- [devops_backend](../../devops_backend) — `.env` files in Docker and docker-compose
- [security](../../security) — environment variables are part of secrets management

## 🚀 Next Step
In `python-backend-mastery`: **Secrets management at scale** — HashiCorp Vault, AWS Secrets Manager, and Kubernetes secrets for rotating credentials without redeployment.
