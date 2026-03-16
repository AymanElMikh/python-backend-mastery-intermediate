# HTTP Status Codes & Response Customization in FastAPI

## 🎯 Interview Question
What HTTP status codes should a REST API use for common operations, and how do you set them in FastAPI?

## 💡 Short Answer (30 seconds)
FastAPI defaults to 200 for all responses. You override it in the decorator: `@app.post("/users", status_code=201)`. The most important codes: 200 OK (success read/update), 201 Created (POST that creates something), 204 No Content (DELETE with no body), 400 Bad Request (invalid input), 401 Unauthorized (missing auth), 403 Forbidden (auth present but insufficient), 404 Not Found, 422 Unprocessable Entity (validation failure — FastAPI's default for Pydantic errors).

## 🔬 Explanation
HTTP status codes communicate the result's meaning to clients, proxies, and monitoring systems. An API that returns 200 for everything — including errors — makes debugging a nightmare.

The `response_model` parameter tells FastAPI which Pydantic model to serialize the return value through. This is how you:
1. Filter sensitive fields (only fields in the response model are included)
2. Auto-generate accurate API docs
3. Validate that your response has the right shape

You can also return a `Response` object directly when you need full control — for example, returning a 204 with no body, or setting custom headers.

## 💻 Code Example
```python
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: CreateUserRequest):
    user = service.register(body.email)
    return user  # FastAPI serializes through UserResponse

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    service.delete(user_id)
    return None  # 204 = no content, no response body

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, body: UpdateUserRequest):
    user = service.update(user_id, body)
    return user  # 200 by default

# Override status code dynamically
@app.post("/items")
def create_or_update(body: ItemRequest, response: Response):
    item, created = service.upsert(body)
    response.status_code = 201 if created else 200
    return item
```

## ⚠️ Common Mistakes
1. **Returning 200 for created resources.** Use 201. It tells clients something new was created and is the correct semantic — some clients behave differently for 200 vs 201.
2. **Returning a body with 204.** HTTP 204 means "no content" — the response body must be empty. FastAPI enforces this. Use 200 if you need to return something.
3. **Confusing 401 and 403.** 401 means "you didn't tell me who you are" (missing/invalid token). 403 means "I know who you are, but you don't have permission." Using them wrong confuses clients and monitoring.

## ✅ Quick Reference — Most Common Status Codes

| Code | When to use |
|------|-------------|
| 200  | Successful GET, PUT, PATCH |
| 201  | Successful POST that created something |
| 204  | Successful DELETE (no response body) |
| 400  | Bad request — client error in input format |
| 401  | Not authenticated (missing or invalid token) |
| 403  | Authenticated but not authorized |
| 404  | Resource not found |
| 409  | Conflict (duplicate, version mismatch) |
| 422  | Validation error (FastAPI/Pydantic default) |
| 500  | Unexpected server error |

## 🔗 Related Concepts
- [fastapi/046_http_exception](../046_http_exception) — raising HTTP errors with specific status codes
- [fastapi/043_pydantic_models](../043_pydantic_models) — `response_model` filters the output
- [api_design](../../api_design) — REST conventions for when to use which codes

## 🚀 Next Step
In `python-backend-mastery`: **Custom response classes** — `FileResponse`, `StreamingResponse`, `HTMLResponse`, and building a response factory that normalizes your API's envelope format (`{"data": ..., "meta": ...}`).
