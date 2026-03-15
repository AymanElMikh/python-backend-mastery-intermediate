"""
Demo: Comprehensions — List, Dict, Set
Level: Intermediate (2–3 years experience)
Run:  python demo.py
"""

# ── Section 1: List comprehension ─────────────────────────────────────────────

users = [
    {"id": 1, "name": "Alice",  "age": 30, "active": True,  "score": 95, "role": "admin"},
    {"id": 2, "name": "Bob",    "age": 17, "active": True,  "score": 72, "role": "user"},
    {"id": 3, "name": "Carol",  "age": 25, "active": False, "score": 88, "role": "user"},
    {"id": 4, "name": "Dave",   "age": 35, "active": True,  "score": 61, "role": "user"},
    {"id": 5, "name": "Eve",    "age": 22, "active": True,  "score": 99, "role": "admin"},
]


# ── Section 2: Dict comprehension ─────────────────────────────────────────────

# Build a lookup: id → user (very common when you need repeated lookups)
users_by_id = {u["id"]: u for u in users}

# Build id → name mapping
id_to_name = {u["id"]: u["name"] for u in users}

# Invert a dict (only works when values are unique!)
name_to_id = {v: k for k, v in id_to_name.items()}

# Filter + transform dict (remove None values from an API response)
raw_api_response = {"name": "Alice", "email": None, "age": 30, "bio": None, "score": 95}
cleaned = {k: v for k, v in raw_api_response.items() if v is not None}


# ── Section 3: Set comprehension ──────────────────────────────────────────────

posts = [
    {"title": "Python tips", "tags": ["python", "beginner", "tips"]},
    {"title": "FastAPI guide", "tags": ["python", "fastapi", "web"]},
    {"title": "Docker basics", "tags": ["docker", "devops"]},
    {"title": "API design", "tags": ["web", "api", "rest"]},
]

# All unique tags across all posts
all_tags = {tag for post in posts for tag in post["tags"]}

# All roles in use (deduplicated automatically)
roles_in_use = {u["role"] for u in users}


# ── Section 4: Common patterns ────────────────────────────────────────────────

# Conditional expression (ternary) inside comprehension
def classify_users(users):
    return [
        {"name": u["name"], "tier": "high" if u["score"] >= 90 else "standard"}
        for u in users
        if u["active"]
    ]

# Flattening a nested list
def flatten(nested):
    return [item for sublist in nested for item in sublist]


# ── Section 5: Common mistakes ────────────────────────────────────────────────

def show_mistakes():
    # WRONG: using list comprehension for side effects
    # This is wasteful — builds a list you don't need
    results = [print(u["name"]) for u in users]  # don't do this

    # RIGHT: use a for loop for side effects
    for u in users:
        pass  # do_something(u)

    # WRONG: list comp when generator would do
    import sys
    n = 10_000
    list_total = sum([x * x for x in range(n)])   # builds list in memory
    gen_total  = sum(x * x for x in range(n))     # lazy — no list built

    list_size = sys.getsizeof([x * x for x in range(n)])
    gen_size  = sys.getsizeof(x * x for x in range(n))

    return list_total, gen_total, list_size, gen_size


if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: Comprehensions — List, Dict, Set")
    print("=" * 50)

    print("\n--- Section 1: List comprehensions ---")
    names = [u["name"] for u in users]
    print(f"  All names: {names}")

    active_names = [u["name"] for u in users if u["active"]]
    print(f"  Active users: {active_names}")

    adult_names = [u["name"] for u in users if u["age"] >= 18 and u["active"]]
    print(f"  Active adults: {adult_names}")

    upper_names = [u["name"].upper() for u in users]
    print(f"  Uppercased: {upper_names}")

    print("\n--- Section 2: Dict comprehensions ---")
    print(f"  users_by_id keys: {list(users_by_id.keys())}")
    print(f"  id_to_name: {id_to_name}")
    print(f"  name_to_id: {name_to_id}")
    print(f"  cleaned API response: {cleaned}")

    print("\n--- Section 3: Set comprehensions ---")
    print(f"  All unique tags: {sorted(all_tags)}")
    print(f"  Roles in use: {roles_in_use}")

    print("\n--- Section 4: Common patterns ---")
    classified = classify_users(users)
    for c in classified:
        print(f"  {c}")

    nested = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
    print(f"  Flattened {nested} → {flatten(nested)}")

    print("\n--- Section 5: List comp vs generator expression ---")
    list_total, gen_total, list_size, gen_size = show_mistakes()
    print(f"  Results equal: {list_total == gen_total}")
    print(f"  List comprehension size:     {list_size:,} bytes")
    print(f"  Generator expression size:   {gen_size} bytes")
    print(f"  → Use generator when passing to sum/max/any/all")

    print("\n--- Readability comparison ---")
    # READABLE comprehension
    high_scores = [u["name"] for u in users if u["score"] >= 90]
    print(f"  High scorers (comprehension): {high_scores}")

    # UNREADABLE nested — better as a for loop
    # (2 loops + condition — don't do this in practice)
    combo = [
        f"{post['title']}:{tag}"
        for post in posts
        for tag in post["tags"]
        if "python" in tag
    ]
    print(f"  Python-tagged posts (nested): {combo}")
    print("  ^ This works but is hard to read — a for loop is clearer for 2+ loops")
