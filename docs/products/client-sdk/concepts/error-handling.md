# Error Handling

Handle failures gracefully with structured exceptions and retry strategies.

## Overview

The Client SDK provides structured error handling with specific exception types for different failure scenarios. This allows you to catch and handle errors appropriately, implement retry logic, and provide helpful feedback to users.

---

## Exception Hierarchy

All Client SDK exceptions inherit from `AgentProtocolException`:

```
AgentProtocolException (base)
├── AgentNotFoundException
├── AgentAuthenticationException
├── AgentAuthorizationException
├── AgentTimeoutException
├── AgentRateLimitException
├── AgentServerException
├── AgentNetworkException
├── AgentValidationException
└── AgentToolException
```

---

## Basic Error Handling

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        AgentProtocolClient,
        AgentProtocolException,
        AgentNotFoundException,
        AgentTimeoutException
    )

    client = AgentProtocolClient("http://localhost:5000")

    try:
        response = await client.complete_chat("Hello")
        print(response)
    except AgentNotFoundException as e:
        print(f"Agent '{e.agent_id}' not found")
    except AgentTimeoutException as e:
        print(f"Request timed out after {e.timeout} seconds")
    except AgentProtocolException as e:
        print(f"Error: {e.message}")
    ```

=== "TypeScript"

    ```typescript
    import {
        AgentProtocolClient,
        AgentProtocolException,
        AgentNotFoundException,
        AgentTimeoutException
    } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    try {
        const response = await client.completeChat("Hello");
        console.log(response);
    } catch (error) {
        if (error instanceof AgentNotFoundException) {
            console.log(`Agent '${error.agentId}' not found`);
        } else if (error instanceof AgentTimeoutException) {
            console.log(`Request timed out after ${error.timeout}ms`);
        } else if (error instanceof AgentProtocolException) {
            console.log(`Error: ${error.message}`);
        }
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    try
    {
        var response = await client.CompleteChatAsync("Hello");
        Console.WriteLine(response);
    }
    catch (AgentNotFoundException ex)
    {
        Console.WriteLine($"Agent '{ex.AgentId}' not found");
    }
    catch (AgentTimeoutException ex)
    {
        Console.WriteLine($"Request timed out after {ex.Timeout}");
    }
    catch (AgentProtocolException ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
    }
    ```

---

## Exception Types

### AgentNotFoundException

Thrown when the specified agent doesn't exist.

```python
try:
    response = await client.complete_chat(
        "Hello",
        agent_id="nonexistent-agent"
    )
except AgentNotFoundException as e:
    print(f"Agent '{e.agent_id}' not found")
    # Handle: Show error to user, fall back to default agent
```

**Properties:**

- `agent_id` - The agent ID that wasn't found
- `message` - Error description

### AgentAuthenticationException

Thrown when API key or authentication credentials are invalid.

```python
try:
    client = AgentProtocolClient(
        "http://localhost:5000",
        api_key="invalid-key"
    )
    response = await client.complete_chat("Hello")
except AgentAuthenticationException as e:
    print("Invalid API key")
    # Handle: Prompt user to re-enter credentials
```

**Properties:**

- `message` - Error description
- `status_code` - HTTP status (typically 401)

### AgentAuthorizationException

Thrown when authenticated but not authorized for the requested operation.

```python
try:
    response = await client.complete_chat("Hello", agent_id="premium-agent")
except AgentAuthorizationException as e:
    print("Not authorized to access this agent")
    # Handle: Show upgrade prompt, redirect to allowed agents
```

**Properties:**

- `message` - Error description
- `status_code` - HTTP status (typically 403)

### AgentTimeoutException

Thrown when a request exceeds the configured timeout.

```python
try:
    response = await client.complete_chat(
        "Write a very long essay",
        timeout=5.0  # 5 second timeout
    )
except AgentTimeoutException as e:
    print(f"Request timed out after {e.timeout} seconds")
    # Handle: Retry with longer timeout, show "still processing" message
```

**Properties:**

- `timeout` - The timeout duration that was exceeded
- `run_id` - The run that timed out (if available)

### AgentRateLimitException

Thrown when rate limits are exceeded.

```python
try:
    response = await client.complete_chat("Hello")
except AgentRateLimitException as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
    # Retry...
```

**Properties:**

- `retry_after` - Seconds to wait before retrying
- `limit` - The rate limit that was exceeded
- `remaining` - Requests remaining in this period

### AgentServerException

Thrown when the agent server encounters an internal error (5xx).

```python
try:
    response = await client.complete_chat("Hello")
except AgentServerException as e:
    print(f"Server error: {e.message}")
    # Handle: Retry with exponential backoff, log for monitoring
```

**Properties:**

- `message` - Error description
- `status_code` - HTTP status (5xx)

### AgentNetworkException

Thrown when network connectivity issues occur.

```python
try:
    response = await client.complete_chat("Hello")
except AgentNetworkException as e:
    print(f"Network error: {e.message}")
    # Handle: Retry, check connectivity, show offline mode
```

**Properties:**

- `message` - Error description
- `cause` - Underlying network error

### AgentValidationException

Thrown when request parameters are invalid.

```python
try:
    response = await client.complete_chat("")  # Empty message
except AgentValidationException as e:
    print(f"Validation error: {e.message}")
    print(f"Field: {e.field}")
    # Handle: Show validation error to user
```

**Properties:**

- `message` - Error description
- `field` - The invalid field name
- `validation_errors` - Detailed validation errors

### AgentToolException

Thrown when a tool execution fails.

```python
@tools.register("divide")
def divide(a: float, b: float) -> float:
    if b == 0:
        raise AgentToolException("Cannot divide by zero")
    return a / b

try:
    response = await client.complete_chat(
        "What's 10 divided by 0?",
        tools=tools
    )
except AgentToolException as e:
    print(f"Tool error: {e.message}")
    # Agent will see the error and respond appropriately
```

**Properties:**

- `message` - Error description
- `tool_name` - The tool that failed
- `tool_arguments` - Arguments passed to the tool

---

## Retry Strategies

### Manual Retry

```python
import asyncio

max_retries = 3
retry_delay = 1.0

for attempt in range(max_retries):
    try:
        response = await client.complete_chat("Hello")
        print(response)
        break
    except AgentServerException as e:
        if attempt < max_retries - 1:
            print(f"Retry {attempt + 1}/{max_retries} after {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        else:
            print("Max retries exceeded")
            raise
```

### Exponential Backoff

```python
async def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except (AgentServerException, AgentNetworkException) as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s, ...
                print(f"Retry {attempt + 1}/{max_retries} after {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise

# Usage
response = await retry_with_backoff(
    lambda: client.complete_chat("Hello")
)
```

### SDK Built-in Retry

```python
client = AgentProtocolClient(
    "http://localhost:5000",
    retry_config={
        "max_retries": 3,
        "retry_delay": 1.0,
        "exponential_backoff": True,
        "retry_on": [
            AgentServerException,
            AgentNetworkException,
            AgentTimeoutException
        ]
    }
)

# SDK automatically retries transient errors
response = await client.complete_chat("Hello")
```

---

## Timeout Configuration

### Request-Level Timeout

```python
# Timeout for a single request
response = await client.complete_chat(
    "Write a long essay",
    timeout=30.0  # 30 seconds
)
```

### Client-Level Timeout

```python
# Default timeout for all requests
client = AgentProtocolClient(
    "http://localhost:5000",
    timeout=10.0  # 10 seconds default
)

# Override for specific request
response = await client.complete_chat(
    "Quick question",
    timeout=5.0
)
```

### Streaming Timeout

```python
# Timeout for entire streaming operation
try:
    await client.stream_chat(
        "Write a story",
        on_text_chunk=lambda t: print(t, end=""),
        timeout=60.0  # 60 seconds total
    )
except AgentTimeoutException:
    print("\nStreaming timed out")
```

---

## Circuit Breaker Pattern

Prevent cascading failures by "opening the circuit" after repeated errors:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func()
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise

# Usage
breaker = CircuitBreaker()

try:
    response = await breaker.call(
        lambda: client.complete_chat("Hello")
    )
except Exception as e:
    print(f"Circuit breaker: {e}")
```

---

## Graceful Degradation

Provide fallback behavior when the primary agent fails:

```python
async def get_response_with_fallback(message: str):
    """Try primary agent, fall back to simple responses."""
    try:
        # Try primary AI agent
        return await client.complete_chat(message, agent_id="gpt-4")
    except AgentNotFoundException:
        # Fall back to smaller model
        try:
            return await client.complete_chat(message, agent_id="gpt-3.5")
        except AgentProtocolException:
            # Fall back to rule-based responses
            return get_rule_based_response(message)

def get_rule_based_response(message: str) -> str:
    """Simple rule-based fallback."""
    message_lower = message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I help you?"
    elif "bye" in message_lower:
        return "Goodbye!"
    else:
        return "I'm having trouble right now. Please try again later."
```

---

## Error Logging and Monitoring

### Structured Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    response = await client.complete_chat("Hello")
except AgentProtocolException as e:
    logger.error(
        "Agent request failed",
        extra={
            "error_type": type(e).__name__,
            "message": str(e),
            "agent_id": getattr(e, 'agent_id', None),
            "status_code": getattr(e, 'status_code', None)
        }
    )
    raise
```

### Error Tracking Integration

```python
import sentry_sdk

sentry_sdk.init(dsn="your-dsn-here")

try:
    response = await client.complete_chat("Hello")
except AgentProtocolException as e:
    sentry_sdk.capture_exception(e)
    sentry_sdk.set_context("agent", {
        "agent_id": getattr(e, 'agent_id', None),
        "request_id": getattr(e, 'request_id', None)
    })
    raise
```

---

## Best Practices

1. **Catch Specific Exceptions First**
   ```python
   try:
       response = await client.complete_chat("Hello")
   except AgentTimeoutException:
       # Handle timeout specifically
       pass
   except AgentRateLimitException:
       # Handle rate limit specifically
       pass
   except AgentProtocolException:
       # Handle all other errors
       pass
   ```

2. **Don't Swallow Errors**
   ```python
   # Bad
   try:
       response = await client.complete_chat("Hello")
   except Exception:
       pass  # Error is lost!

   # Good
   try:
       response = await client.complete_chat("Hello")
   except AgentProtocolException as e:
       logger.error(f"Agent error: {e}")
       raise  # Re-raise for caller to handle
   ```

3. **Provide User-Friendly Messages**
   ```python
   try:
       response = await client.complete_chat("Hello")
   except AgentTimeoutException:
       return "The agent is taking longer than expected. Please try again."
   except AgentRateLimitException:
       return "We're experiencing high demand. Please wait a moment and try again."
   except AgentProtocolException:
       return "Something went wrong. Our team has been notified."
   ```

4. **Implement Timeouts**
   ```python
   # Always set reasonable timeouts
   response = await client.complete_chat(
       message,
       timeout=30.0  # Don't let requests hang forever
   )
   ```

5. **Use Circuit Breakers in Production**
   ```python
   # Prevent cascading failures
   if circuit_breaker.is_open():
       return "Service temporarily unavailable"

   try:
       response = await circuit_breaker.call(
           lambda: client.complete_chat(message)
       )
   except Exception as e:
       # Circuit breaker tracks failures
       pass
   ```

---

## Next Steps

<div class="grid cards" markdown>

- **:material-eye: Monitoring**

    Track errors in production

    [:octicons-arrow-right-24: Monitoring Guide](../guides/monitoring.md)

- **:material-test-tube: Testing**

    Test error scenarios

    [:octicons-arrow-right-24: Testing Guide](../guides/testing.md)

- **:material-book-open: How-To: Handle Errors**

    Practical error handling patterns

    [:octicons-arrow-right-24: How-To Guide](../guides/handle-errors.md)

</div>
