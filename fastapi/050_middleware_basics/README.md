# Middleware Basics in FastAPI

## 🎯 Interview Question
What is middleware in FastAPI and what would you use it for?

## 💡 Short Answer (30 seconds)
Middleware is code that runs for every request before it reaches your route handler, and for every response before it leaves your server. It wraps the entire request-response cycle. Common uses: request logging, timing every request, adding security headers, CORS handling, and compressing responses. FastAPI supports middleware via `@app.middleware("http")` or by adding Starlette middleware classes with `app.add_middleware()`.

## 🔬 Explanation
Think of middleware as an onion: each layer wraps the next. A request arrives, passes through every middleware layer inward, hits the route handler, then the response passes back outward through every middleware layer.

```
Request → [Logging MW] → [Auth MW] → [Route Handler]
                                           ↓
Response ← [Logging MW] ← [Auth MW] ← [Route Handler]
```

Each middleware can:
- Inspect/modify the request before it reaches your route
- Inspect/modify the response before it goes back to the client
- Short-circuit (return early without calling the route) — e.g., block unauthenticated requests

The key difference vs `Depends()`: middleware runs for **every request to the entire app**. `Depends()` runs only for specific routes. Use middleware for cross-cutting concerns; use `Depends()` for route-specific logic.

## 💻 Code Example
```python
import time
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.middleware("http")
async def add_timing_header(request: Request, call_next) -> Response:
    start = time.time()
    response = await call_next(request)  # run the route
    duration_ms = (time.time() - start) * 1000
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    print(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"← {response.status_code}")
    return response

# Or add built-in Starlette middleware:
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myfrontend.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ⚠️ Common Mistakes
1. **Using middleware for per-route logic.** If you need auth for only some routes, use `Depends()` or a router-level dependency. Middleware can't easily skip specific routes without inspecting the path.
2. **Forgetting `await call_next(request)`.** If you don't call `call_next`, the request never reaches your route and the client gets no response.
3. **Heavy processing in middleware.** Middleware runs for every request. An expensive operation (DB query, external API call) in middleware multiplies across your entire API's performance. Keep middleware lightweight.

## ✅ Middleware vs Depends() — Quick Guide

| Concern | Use |
|---------|-----|
| Runs for every request | Middleware |
| Runs for specific routes | `Depends()` |
| Add response headers | Middleware |
| Auth for all routes | Middleware or router-level Depends |
| Auth for one route | `Depends()` |
| Request logging/timing | Middleware |
| Service injection | `Depends()` |

## 🔗 Related Concepts
- [fastapi/044_depends_di](../044_depends_di) — per-route dependency injection
- [fastapi/047_routers_tags](../047_routers_tags) — router-level dependencies (between middleware and per-route)
- [design_patterns/024_decorator_pattern](../../design_patterns/024_decorator_pattern) — middleware IS the Decorator pattern applied to HTTP

## 🚀 Next Step
In `python-backend-mastery`: **Custom ASGI middleware** — writing middleware at the ASGI level for full control over streaming, WebSocket upgrades, and low-level protocol handling.
