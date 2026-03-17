# Cache Invalidation Strategies

## 🎯 Interview Question
What are the main cache invalidation strategies and how do you choose between them?

## 💡 Short Answer (30 seconds)
There are three main strategies: **TTL-based** (let the cache expire automatically after N seconds — simple, eventually consistent), **explicit invalidation** (delete the cache key immediately when the underlying data changes — more complex but more accurate), and **event-driven invalidation** (publish a "data changed" event and let cache subscribers react — decoupled but requires messaging infrastructure). Most production systems use TTL as the baseline and explicit invalidation for critical data.

## 🔬 Explanation
Phil Karlton's famous quote: "There are only two hard things in computer science: cache invalidation and naming things."

**Why it's hard**: the cache has a copy of data. When the original data changes, the cache copy is stale. You need a way to know when data changed and act on it.

**TTL-based invalidation:**
- Cache entry expires after N seconds automatically
- Staleness window = TTL duration (you'll show old data for up to N seconds)
- Zero additional logic required
- Right choice for: product catalog, user profiles, config data — anything where slight staleness is acceptable

**Explicit invalidation:**
- When you update the DB, immediately `DELETE` the cache key
- Zero staleness — cache is always empty after an update (next read re-fetches)
- Must not forget to invalidate everywhere the data changes (multiple code paths)
- Right choice for: user account details, permissions, anything security-sensitive

**Pattern invalidation** (`products:*`):
- Delete all keys matching a pattern when a category changes
- Redis supports `SCAN` + `DELETE` for this (not `KEYS *` in production — too slow)

## 💻 Code Example
```python
# Strategy 1: TTL only — simple, some staleness acceptable
def cache_product(product_id: int, ttl: int = 300):
    def get():
        cached = r.get(f"product:{product_id}")
        if cached: return json.loads(cached)
        product = db.get_product(product_id)
        r.set(f"product:{product_id}", json.dumps(product), ex=ttl)
        return product
    return get

# Strategy 2: Explicit invalidation on write
def update_product(product_id: int, data: dict):
    db.update_product(product_id, data)
    r.delete(f"product:{product_id}")        # immediate invalidation

# Strategy 3: Pattern invalidation (invalidate all products in a category)
def invalidate_category(category: str):
    # Scan for keys matching "products:category:*" then delete them
    # In real Redis: use SCAN with MATCH, not KEYS (KEYS blocks Redis)
    keys_to_delete = [k for k in r.scan_iter(f"products:category:{category}:*")]
    if keys_to_delete:
        r.delete(*keys_to_delete)
```

## ⚠️ Common Mistakes
1. **`KEYS *` in production.** `r.keys("products:*")` blocks Redis while it scans the entire keyspace. Use `SCAN` with a cursor for pattern-based deletion.
2. **Forgetting invalidation in all write paths.** If you update a user's email in 3 different API endpoints, all 3 must invalidate the cache. Missing one = stale data. Extract the invalidation logic to one place (the repository method).
3. **Setting TTL too long on frequently-changed data.** A 1-hour TTL on a user's "unread message count" means users see stale counts for up to an hour. Match TTL length to how often data actually changes.

## ✅ TTL Length Guidelines

| Data type | Suggested TTL |
|-----------|---------------|
| Static content (legal pages, FAQs) | 1 hour – 24 hours |
| Product catalog | 5–15 minutes |
| User profile (read by others) | 1–5 minutes |
| User's own account data | 30–60 seconds |
| Permission/role data | 1–5 minutes |
| Real-time counters (likes, views) | 10–30 seconds |
| Never cache | Account balance, inventory stock |

## 🔗 Related Concepts
- [performance/054_cache_aside_pattern](../054_cache_aside_pattern) — explicit delete on write
- [performance/053_redis_as_cache](../053_redis_as_cache) — Redis DELETE and TTL mechanics
- [design_patterns/025_observer_pattern](../../design_patterns/025_observer_pattern) — event-driven invalidation uses Observer

## 🚀 Next Step
In `python-backend-mastery`: **Distributed cache invalidation** — using Redis pub/sub to broadcast invalidation events to multiple app instances, and cache versioning ("cache busting") to safely deploy without stale data.
