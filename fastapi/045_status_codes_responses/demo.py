"""
Demo: HTTP Status Codes & Response Customization in FastAPI
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: Status code reference ─────────────────────────────────────────

STATUS_CODES = {
    # 2xx Success
    200: ("OK",                    "GET, PUT, PATCH success"),
    201: ("Created",               "POST that creates a new resource"),
    204: ("No Content",            "DELETE success (no body)"),
    # 4xx Client errors
    400: ("Bad Request",           "Malformed request / missing required field"),
    401: ("Unauthorized",          "Not authenticated (no/invalid token)"),
    403: ("Forbidden",             "Authenticated but insufficient permission"),
    404: ("Not Found",             "Resource does not exist"),
    409: ("Conflict",              "Duplicate, version mismatch, state conflict"),
    422: ("Unprocessable Entity",  "FastAPI/Pydantic validation failure"),
    # 5xx Server errors
    500: ("Internal Server Error", "Unexpected bug — should never reach client"),
}

def explain(code: int) -> str:
    name, usage = STATUS_CODES.get(code, ("Unknown", ""))
    return f"  HTTP {code} {name}: {usage}"


# ── Section 2: Simulated FastAPI responses ────────────────────────────────────

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Response:
    status_code: int
    body: Any
    headers: dict

    def __repr__(self):
        body_str = str(self.body)[:60]
        return f"Response({self.status_code}, body={body_str})"


def make_response(status_code: int, body: Any = None, headers: dict = None) -> Response:
    return Response(status_code=status_code, body=body, headers=headers or {})


# ── Fake data store ───────────────────────────────────────────────────────────

USERS: dict[int, dict] = {
    1: {"id": 1, "email": "alice@x.com", "name": "Alice", "password_hash": "abc123"},
    2: {"id": 2, "email": "bob@x.com",   "name": "Bob",   "password_hash": "xyz789"},
}
NEXT_ID = 3


# ── Section 3: CRUD endpoints with correct status codes ──────────────────────

def get_user(user_id: int) -> Response:
    """GET /users/{id} → 200 or 404"""
    user = USERS.get(user_id)
    if user is None:
        return make_response(404, {"error": f"User #{user_id} not found"})
    # response_model filtering: exclude password_hash
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return make_response(200, safe)


def list_users() -> Response:
    """GET /users → 200 always"""
    safe_users = [{k: v for k, v in u.items() if k != "password_hash"} for u in USERS.values()]
    return make_response(200, safe_users)


def create_user(email: str, name: str) -> Response:
    """POST /users → 201 Created or 409 Conflict"""
    global NEXT_ID
    # Check for duplicate
    if any(u["email"] == email for u in USERS.values()):
        return make_response(409, {"error": f"Email '{email}' already registered"})
    user = {"id": NEXT_ID, "email": email, "name": name, "password_hash": "hashed"}
    USERS[NEXT_ID] = user
    NEXT_ID += 1
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return make_response(201, safe)  # 201, not 200!


def update_user(user_id: int, name: str) -> Response:
    """PUT /users/{id} → 200 or 404"""
    user = USERS.get(user_id)
    if user is None:
        return make_response(404, {"error": f"User #{user_id} not found"})
    user["name"] = name
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return make_response(200, safe)


def delete_user(user_id: int) -> Response:
    """DELETE /users/{id} → 204 No Content or 404"""
    if user_id not in USERS:
        return make_response(404, {"error": f"User #{user_id} not found"})
    del USERS[user_id]
    return make_response(204, None)   # 204 = NO body!


def create_or_update_user(user_id: int, name: str) -> Response:
    """PUT /users/{id}/upsert — dynamic 200 or 201 based on whether it existed"""
    existed = user_id in USERS
    if existed:
        USERS[user_id]["name"] = name
    else:
        USERS[user_id] = {"id": user_id, "email": f"user{user_id}@x.com", "name": name, "password_hash": ""}
    safe = {k: v for k, v in USERS[user_id].items() if k != "password_hash"}
    status = 200 if existed else 201
    return make_response(status, safe)


if __name__ == "__main__":
    print("=" * 55)
    print("DEMO: HTTP Status Codes & Response Customization")
    print("=" * 55)

    print("\n--- Status code reference ---")
    for code in [200, 201, 204, 400, 401, 403, 404, 409, 422, 500]:
        print(explain(code))

    print("\n--- GET /users (200 always) ---")
    resp = list_users()
    print(f"  → {resp.status_code}: {resp.body}")

    print("\n--- GET /users/1 (200) and /users/99 (404) ---")
    for uid in [1, 2, 99]:
        resp = get_user(uid)
        print(f"  GET /users/{uid} → {resp.status_code}: {resp.body}")

    print("\n--- POST /users → 201 Created ---")
    resp = create_user("carol@x.com", "Carol")
    print(f"  New user → {resp.status_code}: {resp.body}")
    print(f"  Note: password_hash NOT in response (filtered by response_model)")

    print("\n--- POST /users → 409 Conflict (duplicate) ---")
    resp = create_user("alice@x.com", "Alice2")
    print(f"  Duplicate → {resp.status_code}: {resp.body}")

    print("\n--- PUT /users/1 → 200 ---")
    resp = update_user(1, "Alice Updated")
    print(f"  Updated → {resp.status_code}: {resp.body}")

    print("\n--- DELETE /users/2 → 204 No Content ---")
    resp = delete_user(2)
    print(f"  Deleted → {resp.status_code}, body={resp.body!r}  ← no body for 204")

    resp = delete_user(2)  # already deleted
    print(f"  Delete again → {resp.status_code}: {resp.body}")

    print("\n--- Dynamic 200 vs 201 (upsert) ---")
    resp = create_or_update_user(99, "New User")
    print(f"  Upsert (create) → {resp.status_code}: {resp.body}")
    resp = create_or_update_user(99, "Updated User")
    print(f"  Upsert (update) → {resp.status_code}: {resp.body}")

    print("\n--- Common mistakes ---")
    print("  BAD:  POST /users → 200  (should be 201)")
    print("  BAD:  DELETE /users/1 → 200 with body  (should be 204, no body)")
    print("  BAD:  return 401 when user is logged in but lacks permission  (should be 403)")
    print("  BAD:  return 500 for validation errors  (should be 400 or 422)")
