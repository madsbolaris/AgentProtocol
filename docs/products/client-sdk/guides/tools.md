# Advanced Tool Patterns

Complex tool orchestration, chaining, and advanced patterns.

## Overview

Beyond basic tool usage, the Client SDK supports advanced patterns for complex workflows: tool chaining, conditional execution, parallel tool calls, and sophisticated error handling. This guide covers patterns for building production-grade tool integrations.

---

## Tool Chaining

Execute tools in sequence where each tool's output feeds into the next:

```python
from microsoft.agents.protocol import ToolCollection

tools = ToolCollection()

@tools.register("search_products")
async def search_products(query: str) -> list[dict]:
    """Search for products matching a query."""
    return [
        {"id": "p1", "name": "Laptop", "price": 999},
        {"id": "p2", "name": "Mouse", "price": 29}
    ]

@tools.register("get_inventory")
async def get_inventory(product_id: str) -> dict:
    """Get current inventory for a product."""
    return {"product_id": product_id, "stock": 42, "warehouse": "WH-01"}

@tools.register("reserve_item")
async def reserve_item(product_id: str, quantity: int) -> dict:
    """Reserve items from inventory."""
    return {"reservation_id": "r123", "expires_at": "2025-01-20T12:00:00Z"}

# Agent automatically chains: search → get_inventory → reserve_item
response = await client.complete_chat(
    "Find laptops, check inventory, and reserve 2 units",
    tools=tools
)
```

**The agent orchestrates the sequence:**

1. Calls `search_products("laptops")`
2. Receives results, selects product
3. Calls `get_inventory("p1")`
4. Verifies stock availability
5. Calls `reserve_item("p1", 2)`
6. Returns final confirmation to user

---

## Conditional Tool Execution

Tools can return data that guides the agent's next decision:

```python
@tools.register("check_user_permissions")
def check_user_permissions(user_id: str, action: str) -> dict:
    """Check if user has permission for an action."""
    permissions = get_user_permissions(user_id)
    has_permission = action in permissions

    return {
        "user_id": user_id,
        "action": action,
        "allowed": has_permission,
        "reason": "User has admin role" if has_permission else "Insufficient permissions"
    }

@tools.register("delete_resource")
def delete_resource(resource_id: str) -> str:
    """Delete a resource (requires admin)."""
    # This is only called if check_user_permissions returned allowed=True
    delete_from_database(resource_id)
    return f"Resource {resource_id} deleted successfully"

# Agent checks permissions first, only deletes if allowed
response = await client.complete_chat(
    "Delete resource res_123 for user usr_456",
    tools=tools
)
```

---

## Parallel Tool Calls

Some agents can call multiple tools in parallel for better performance:

```python
@tools.register("get_weather")
async def get_weather(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/v1/{city}")
        return response.json()

@tools.register("get_traffic")
async def get_traffic(city: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.traffic.com/v1/{city}")
        return response.json()

@tools.register("get_events")
async def get_events(city: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.events.com/v1/{city}")
        return response.json()

# Agent may call all three tools in parallel
response = await client.complete_chat(
    "I'm visiting San Francisco tomorrow. Give me weather, traffic, and event recommendations.",
    tools=tools
)
```

**Benefits:**

- Faster response times (3 parallel calls vs 3 sequential)
- Better resource utilization
- Improved user experience

---

## Tool Result Transformations

Transform tool results before returning to the agent:

```python
@tools.register("query_database")
async def query_database(sql: str) -> str:
    """Execute SQL query and return results."""
    async with database.connect() as conn:
        rows = await conn.fetch(sql)

    # Transform rows to human-readable format
    if not rows:
        return "No results found"

    # Format as markdown table
    headers = list(rows[0].keys())
    result = "| " + " | ".join(headers) + " |\n"
    result += "|" + "|".join(["---"] * len(headers)) + "|\n"

    for row in rows[:10]:  # Limit to 10 rows
        result += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"

    if len(rows) > 10:
        result += f"\n_(Showing 10 of {len(rows)} results)_"

    return result
```

---

## Tool Context and State

Pass context between tool calls using a shared state object:

```python
from typing import Any

class ToolContext:
    """Shared context for tools."""
    def __init__(self):
        self.user_id: str = None
        self.session_data: dict = {}
        self.transaction_id: str = None

# Create context
context = ToolContext()
context.user_id = "usr_123"

# Create tools with access to context
tools = ToolCollection()

@tools.register("start_transaction")
def start_transaction() -> str:
    """Start a new transaction."""
    context.transaction_id = f"txn_{uuid.uuid4()}"
    context.session_data["transaction_start"] = datetime.now()
    return f"Transaction {context.transaction_id} started"

@tools.register("add_item")
def add_item(product_id: str, quantity: int) -> str:
    """Add item to transaction."""
    if not context.transaction_id:
        return "Error: No active transaction. Start a transaction first."

    key = f"transaction_{context.transaction_id}_items"
    items = context.session_data.get(key, [])
    items.append({"product_id": product_id, "quantity": quantity})
    context.session_data[key] = items

    return f"Added {quantity}x {product_id} to transaction"

@tools.register("complete_transaction")
def complete_transaction() -> str:
    """Complete the current transaction."""
    if not context.transaction_id:
        return "Error: No active transaction"

    key = f"transaction_{context.transaction_id}_items"
    items = context.session_data.get(key, [])

    # Process transaction
    total = sum(get_price(item["product_id"]) * item["quantity"] for item in items)

    result = f"Transaction {context.transaction_id} completed. Total: ${total:.2f}"
    context.transaction_id = None  # Reset

    return result
```

---

## Tool Rate Limiting

Implement rate limiting for external API calls:

```python
from asyncio import Semaphore, sleep
from collections import defaultdict
import time

class RateLimiter:
    """Rate limiter for tool calls."""
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = defaultdict(list)
        self.semaphore = Semaphore(calls_per_minute)

    async def acquire(self, tool_name: str):
        """Wait if rate limit is exceeded."""
        now = time.time()

        # Remove calls older than 1 minute
        self.calls[tool_name] = [
            t for t in self.calls[tool_name]
            if now - t < 60
        ]

        # Wait if limit exceeded
        if len(self.calls[tool_name]) >= self.calls_per_minute:
            wait_time = 60 - (now - self.calls[tool_name][0])
            await sleep(wait_time)

        self.calls[tool_name].append(now)

# Usage
rate_limiter = RateLimiter(calls_per_minute=10)

@tools.register("call_external_api")
async def call_external_api(endpoint: str) -> dict:
    """Call external API with rate limiting."""
    await rate_limiter.acquire("call_external_api")

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint)
        return response.json()
```

---

## Tool Caching

Cache expensive tool results:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class ToolCache:
    """Simple time-based cache for tool results."""
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.cache = {}

    def get(self, key: str) -> Any:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = (value, datetime.now())

# Create cache
cache = ToolCache(ttl_seconds=300)  # 5 minute TTL

@tools.register("get_stock_price")
async def get_stock_price(symbol: str) -> float:
    """Get current stock price (cached for 5 minutes)."""
    cached = cache.get(f"stock_{symbol}")
    if cached is not None:
        return cached

    # Fetch from API
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.stocks.com/v1/price/{symbol}")
        price = response.json()["price"]

    cache.set(f"stock_{symbol}", price)
    return price
```

---

## Tool Error Recovery

Implement retry logic and fallbacks:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@tools.register("fetch_with_retry")
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_with_retry(url: str) -> dict:
    """Fetch data with automatic retry on failure."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

@tools.register("fetch_with_fallback")
async def fetch_with_fallback(symbol: str) -> dict:
    """Fetch data with fallback to secondary source."""
    try:
        # Try primary source
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.primary.com/v1/{symbol}")
            return response.json()
    except Exception as e:
        # Fall back to secondary source
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.secondary.com/v1/{symbol}")
                return response.json()
        except Exception:
            return {"error": "All sources failed", "symbol": symbol}
```

---

## Tool Validation

Validate tool inputs before execution:

```python
from pydantic import BaseModel, validator

class TransferRequest(BaseModel):
    """Validated transfer request."""
    from_account: str
    to_account: str
    amount: float

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 10000:
            raise ValueError('Amount exceeds daily limit')
        return v

    @validator('from_account', 'to_account')
    def account_must_be_valid(cls, v):
        if not v.startswith('acct_'):
            raise ValueError('Invalid account ID format')
        return v

@tools.register("transfer_money")
def transfer_money(from_account: str, to_account: str, amount: float) -> str:
    """Transfer money between accounts (validated)."""
    # Validate using Pydantic
    try:
        request = TransferRequest(
            from_account=from_account,
            to_account=to_account,
            amount=amount
        )
    except ValueError as e:
        return f"Validation error: {e}"

    # Process transfer
    return f"Transferred ${amount:.2f} from {from_account} to {to_account}"
```

---

## Tool Observability

Add logging and metrics to tools:

```python
import logging
from time import time

logger = logging.getLogger(__name__)

def monitored_tool(func):
    """Decorator to add monitoring to tools."""
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time()

        logger.info(f"Tool {tool_name} called with args={args}, kwargs={kwargs}")

        try:
            result = await func(*args, **kwargs)
            duration = time() - start_time

            logger.info(f"Tool {tool_name} completed in {duration:.2f}s")
            # Send metric to monitoring system
            metrics.record("tool_duration", duration, tags={"tool": tool_name})

            return result
        except Exception as e:
            duration = time() - start_time

            logger.error(f"Tool {tool_name} failed after {duration:.2f}s: {e}")
            metrics.record("tool_error", 1, tags={"tool": tool_name})

            raise

    return wrapper

# Usage
@tools.register("database_query")
@monitored_tool
async def database_query(sql: str) -> list[dict]:
    """Execute database query with monitoring."""
    async with database.connect() as conn:
        return await conn.fetch(sql)
```

---

## Tool Security

Implement security controls for sensitive operations:

```python
import hmac
import hashlib

class SecureTool:
    """Wrapper for tools requiring authentication."""
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def verify_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

# Usage
secure = SecureTool(secret_key=os.getenv("TOOL_SECRET_KEY"))

@tools.register("delete_account")
def delete_account(account_id: str, signature: str) -> str:
    """Delete account (requires signature)."""
    if not secure.verify_signature(account_id, signature):
        return "Error: Invalid signature"

    # Perform deletion
    delete_from_database(account_id)
    return f"Account {account_id} deleted"

# Generate signature
signature = hmac.new(
    os.getenv("TOOL_SECRET_KEY").encode(),
    "acct_123".encode(),
    hashlib.sha256
).hexdigest()
```

---

## Tool Composition

Compose complex tools from simpler ones:

```python
@tools.register("get_user")
async def get_user(user_id: str) -> dict:
    """Get user details."""
    return await db.fetch_user(user_id)

@tools.register("get_orders")
async def get_orders(user_id: str) -> list[dict]:
    """Get user's orders."""
    return await db.fetch_orders(user_id)

@tools.register("get_user_profile")
async def get_user_profile(user_id: str) -> dict:
    """Get complete user profile (composite)."""
    # Compose from multiple tools
    user = await get_user(user_id)
    orders = await get_orders(user_id)

    return {
        "user": user,
        "orders": orders,
        "total_spent": sum(o["amount"] for o in orders),
        "order_count": len(orders)
    }
```

---

## Best Practices

1. **Keep Tools Focused**
   - One tool = one responsibility
   - Compose complex operations from simple tools

2. **Validate Inputs**
   - Use type hints and validation libraries
   - Return clear error messages for invalid inputs

3. **Handle Errors Gracefully**
   - Implement retry logic for transient failures
   - Provide fallback options when possible

4. **Add Observability**
   - Log tool calls and results
   - Track metrics (duration, error rate)
   - Monitor rate limits and quotas

5. **Secure Sensitive Operations**
   - Require authentication/authorization
   - Validate permissions before execution
   - Audit sensitive tool calls

6. **Optimize Performance**
   - Cache expensive operations
   - Use parallel execution when possible
   - Implement rate limiting for external APIs

7. **Document Thoroughly**
   - Clear descriptions help agents make better decisions
   - Include examples in docstrings
   - Document prerequisites and side effects

---

## Next Steps

<div class="grid cards" markdown>

- **:material-brain: Tools Concept**

    Understand tool fundamentals

    [:octicons-arrow-right-24: Tools Concept](../concepts/tools.md)

- **:material-test-tube: Testing Tools**

    Test tool implementations

    [:octicons-arrow-right-24: Testing Guide](testing.md)

- **:material-book-open: Tool Tutorial**

    Build a tool-enabled assistant

    [:octicons-arrow-right-24: Tutorial](../guides/tutorials/tools-tutorial.md)

</div>
