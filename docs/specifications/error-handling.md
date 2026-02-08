# Error Handling Specification

**Version**: 1.0

## Overview

This specification defines error codes, error response formats, recovery strategies, and retry behavior for the Agent Runtime API.

**Error Handling Principles:**
- **Consistent Format**: All errors use same structure
- **Machine-Readable Codes**: Structured error codes for programmatic handling
- **Actionable Messages**: Clear guidance on how to resolve errors
- **Retry Guidance**: Explicit retry vs. no-retry classification

## Error Response Format

### Structure

**TypeSpec**: Based on `ErrorContent` and `RunError` models

```typescript
{
  error: {
    code: string;               // Machine-readable error code
    message: string;            // Human-readable message
    field?: string;             // Field that caused error (validation)
    details?: Record<unknown>;  // Additional context
  }
}
```

### HTTP Status Codes

| Status | Usage | Examples |
|--------|-------|----------|
| 400 Bad Request | Client error (invalid input) | `INVALID_INPUT`, `VALIDATION_FAILED` |
| 401 Unauthorized | Authentication required | `AUTH_REQUIRED`, `INVALID_TOKEN` |
| 403 Forbidden | Permission denied | `PERMISSION_DENIED`, `INSUFFICIENT_SCOPES` |
| 404 Not Found | Resource doesn't exist | `RESOURCE_NOT_FOUND`, `THREAD_NOT_FOUND` |
| 409 Conflict | State conflict | `INVALID_STATE`, `ALREADY_EXISTS` |
| 422 Unprocessable Entity | Business logic error | `MAX_TURNS_EXCEEDED`, `TOOL_EXECUTION_FAILED` |
| 429 Too Many Requests | Rate limit exceeded | `RATE_LIMIT_EXCEEDED` |
| 500 Internal Server Error | Server error | `INTERNAL_ERROR`, `PROVIDER_ERROR` |
| 503 Service Unavailable | Temporary unavailable | `SERVICE_UNAVAILABLE`, `PROVIDER_UNAVAILABLE` |

### Examples

**Validation Error (400):**
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Field 'input' must be non-empty array",
    "field": "input",
    "details": {
      "provided": [],
      "expected": "non-empty array"
    }
  }
}
```

**Authentication Error (401):**
```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Missing required OAuth2 scopes",
    "details": {
      "missing_scopes": {
        "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user"
      },
      "authorize_url": "https://login.microsoftonline.com/authorize?..."
    }
  }
}
```

**Rate Limit Error (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "retry_after": 60,
      "limit": 100,
      "used": 100,
      "reset_at": "2026-02-05T10:31:00Z"
    }
  }
}
```

## Error Categories

### Client Errors (4xx)

**Characteristics:**
- Caused by invalid client request
- Should NOT retry without fixing request
- Client must change request to succeed

**Examples:**
- Invalid input format
- Missing required fields
- Resource not found
- Permission denied

### Server Errors (5xx)

**Characteristics:**
- Caused by server or provider issues
- MAY retry (with exponential backoff)
- Issue is transient or server-side

**Examples:**
- Internal server error
- Provider API failure
- Service unavailable
- Timeout

## Error Code Catalog

### Validation Errors (400)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `INVALID_INPUT` | Input validation failed | No | Fix input data |
| `REQUIRED_FIELD_MISSING` | Required field not provided | No | Provide missing field |
| `INVALID_FIELD_TYPE` | Field type incorrect | No | Fix field type |
| `INVALID_ENUM_VALUE` | Enum value not recognized | No | Use valid enum value |
| `INVALID_FORMAT` | Format validation failed | No | Fix format (URI, date, etc.) |
| `SCHEMA_VALIDATION_FAILED` | JSON Schema validation failed | No | Match schema requirements |
| `TEXT_TOO_LONG` | Text exceeds max length | No | Reduce text length |
| `IMAGE_TOO_LARGE` | Image exceeds size limit | No | Reduce image size |
| `TOO_MANY_CONTENTS` | Too many content items | No | Reduce content count |

### Authentication Errors (401/403)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `AUTH_REQUIRED` | Authentication required | No | Provide authentication |
| `INVALID_TOKEN` | Token invalid or expired | No | Refresh/renew token |
| `TOKEN_EXPIRED` | Access token expired | Yes | Refresh token automatically |
| `PERMISSION_DENIED` | Missing required permissions | No | Request additional scopes |
| `INSUFFICIENT_SCOPES` | Missing OAuth2 scopes | No | Request consent for scopes |
| `CONSENT_DENIED` | User denied consent | No | Explain and request again |
| `INVALID_CONNECTION` | Connection config invalid | No | Fix connection configuration |

### Resource Errors (404)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `RESOURCE_NOT_FOUND` | Resource doesn't exist | No | Check resource ID |
| `THREAD_NOT_FOUND` | Thread doesn't exist | No | Create thread first |
| `RUN_NOT_FOUND` | Run doesn't exist | No | Check run ID |
| `MESSAGE_NOT_FOUND` | Message doesn't exist | No | Check message ID |
| `AGENT_NOT_FOUND` | Agent doesn't exist | No | Check agent ID |
| `TOOL_NOT_FOUND` | Tool not found | No | Register tool or fix name |

### State Errors (409/422)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `INVALID_STATE` | Operation not valid in current state | No | Check resource state |
| `ALREADY_EXISTS` | Resource already exists | No | Use existing resource |
| `THREAD_ARCHIVED` | Thread is archived | No | Reactivate thread |
| `RUN_ALREADY_COMPLETED` | Run already completed | No | Create new run |
| `INVALID_TRANSITION` | State transition not allowed | No | Check state machine |

### Execution Errors (422)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `MAX_TURNS_EXCEEDED` | Run hit max turns limit | No | Increase limit or simplify task |
| `CONTEXT_LENGTH_EXCEEDED` | Token limit exceeded | No | Reduce context or split request |
| `TOOL_EXECUTION_FAILED` | Tool execution error | Sometimes | Check tool or retry |
| `TOOL_TIMEOUT` | Tool execution timeout | Yes | Increase timeout or optimize tool |
| `TOOL_ARGUMENT_INVALID` | Tool arguments don't match schema | No | Fix arguments |
| `INCOMPLETE_TOOL_RESULTS` | Missing tool results | No | Provide all tool results |

### Rate Limit Errors (429)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded | Yes | Wait and retry with backoff |
| `QUOTA_EXCEEDED` | Quota/budget exceeded | No | Increase quota or wait for reset |
| `CONCURRENT_REQUESTS_EXCEEDED` | Too many concurrent requests | Yes | Reduce concurrency and retry |

### Provider Errors (500/503)

| Code | Message | Retry | Fix |
|------|---------|-------|-----|
| `INTERNAL_ERROR` | Internal server error | Yes | Retry with exponential backoff |
| `PROVIDER_ERROR` | LLM provider error | Yes | Retry or switch provider |
| `PROVIDER_UNAVAILABLE` | Provider service unavailable | Yes | Wait and retry |
| `SERVICE_UNAVAILABLE` | Runtime service unavailable | Yes | Wait and retry |
| `TIMEOUT` | Request timeout | Yes | Retry or increase timeout |

## Timeout Values

**Standard Timeouts:**

| Operation Type | Default | Maximum | Configurable | Applies To |
|----------------|---------|---------|--------------|------------|
| WebSocket hook evaluation | 5s | 30s | Yes | Per-event hook evaluation |
| WebSocket handshake | 5s | - | No | Initial connection setup |
| HTTP request | 2s | 10s | Yes | HTTP hook/condition requests |
| Remote condition (WebSocket) | 5s | 30s | Yes | Per-evaluation condition check |
| Remote condition (HTTP) | 2s | 10s | Yes | Per-request condition check |

**Source**: Hooks Design (lines 1101-1103), agent-auto-response.md (lines 223-224, 436-437)

**Timeout Behavior:**
- **Hooks (blocking)**: Apply fallback behavior based on event type (see Fallback Strategies)
- **Conditions**: Return `false` (fail-closed) - condition evaluation failed

**Example Configuration:**
```json
{
  "hookConfig": {
    "websocketTimeout": 5000,
    "websocketTimeoutMax": 30000,
    "httpTimeout": 2000,
    "httpTimeoutMax": 10000
  }
}
```

## WebSocket Close Codes

**Standard Close Codes:**

| Code | Meaning | Behavior | Retry Strategy |
|------|---------|----------|----------------|
| 1000 | Normal closure | Accept close, no reconnection needed | None - clean shutdown |
| 1001 | Going away | Attempt reconnection or HTTP fallback | Reconnect with backoff |
| 1003 | Unsupported data | No reconnection, log protocol error | None - protocol error |
| 1008 | Policy violation | No reconnection, log violation | None - policy error |
| 1011 | Server error | Attempt reconnection with backoff | Retry 3x with backoff |

**Source**: Hooks Design (lines 1110-1114), agent-auto-response.md (lines 473-477)

**Close Code Usage:**

**Normal Closure (1000):**
```typescript
// Hook endpoint closes after run completes
websocket.close(1000, "Run completed successfully");
```

**Going Away (1001):**
```typescript
// Server restarting, client should reconnect
websocket.close(1001, "Server maintenance - please reconnect");
// Client: attempts reconnection or falls back to HTTP
```

**Unsupported Data (1003):**
```typescript
// Invalid JSON received
if (!isValidJSON(message)) {
  websocket.close(1003, "Invalid JSON format");
}
```

**Policy Violation (1008):**
```typescript
// Hook sent multiple approval actions (not allowed)
if (hasMultipleApprovals(response)) {
  websocket.close(1008, "Multiple approval actions not allowed");
}
```

**Server Error (1011):**
```typescript
// Internal server error during hook processing
websocket.close(1011, "Internal server error");
// Client: attempts reconnection with exponential backoff
```

## Recovery Strategies

### Automatic Retry (Client)

**Retryable Errors:**
- `RATE_LIMIT_EXCEEDED` - Retry after delay
- `TOKEN_EXPIRED` - Refresh token, retry
- `PROVIDER_ERROR` - Retry with backoff
- `SERVICE_UNAVAILABLE` - Retry with backoff
- `TIMEOUT` - Retry (maybe increase timeout)
- `TOOL_TIMEOUT` - Retry with longer timeout

**Retry Pattern:**

> **Retry Strategy**: Exponential backoff with 100ms, 200ms, 400ms delays (max 3 retries)
>
> **Source**: Hooks Design, agent-auto-response.md
> - Applies to: Remote hooks, remote conditions, provider errors, rate limits
> - Jitter: Applied to prevent thundering herd

```python
import time
import random
from typing import Optional

def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 0.1,  # 100ms base
    max_delay: float = 0.4     # 400ms max
):
    """Retry with exponential backoff (100ms, 200ms, 400ms)"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if not is_retryable(e):
                raise

            if attempt == max_retries - 1:
                raise

            # Calculate delay: 100ms, 200ms, 400ms
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            jittered_delay = delay * (0.5 + 0.5 * random.random())

            print(f"Retry {attempt + 1}/{max_retries} after {jittered_delay*1000:.0f}ms")
            time.sleep(jittered_delay)

def is_retryable(error) -> bool:
    """Check if error is retryable"""
    retryable_codes = [
        "RATE_LIMIT_EXCEEDED",
        "TOKEN_EXPIRED",
        "PROVIDER_ERROR",
        "SERVICE_UNAVAILABLE",
        "TIMEOUT",
        "TOOL_TIMEOUT"
    ]
    return error.code in retryable_codes
```

**Usage:**
```python
response = retry_with_exponential_backoff(
    lambda: client.create_run(request),
    max_retries=3
)
```

### Rate Limit Handling

**Pattern:**

```python
def handle_rate_limit(error):
    """Handle rate limit error with retry-after"""
    if error.code == "RATE_LIMIT_EXCEEDED":
        retry_after = error.details.get("retry_after", 60)
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return "retry"
    return "fail"
```

**Respect Headers:**
```python
response = requests.post(url, json=data)
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    time.sleep(retry_after)
    # Retry request
```

### Token Refresh

**Pattern:**

```python
def execute_with_token_refresh(client, request):
    """Execute request with automatic token refresh"""
    try:
        return client.create_run(request)
    except APIError as e:
        if e.code == "TOKEN_EXPIRED":
            # Refresh token
            new_token = refresh_access_token(client.refresh_token)
            client.set_access_token(new_token)
            # Retry with new token
            return client.create_run(request)
        raise
```

### Fallback Strategies

#### Condition Evaluation Fallback (Fail-Closed)

**Behavior**: When remote condition evaluation fails (timeout, network error, 5xx), return `false` (condition not met).

**Rationale**: Fail-closed ensures that agents only participate when conditions are explicitly met. This is safer for authorization and filtering scenarios.

**Source**: Hooks Design (line 239), agent-auto-response.md (lines 227, 436-438, 443-444)

**Example:**
```python
def evaluate_condition(condition, context):
    """Evaluate condition with fail-closed fallback"""
    try:
        result = remote_condition_check(condition, context)
        return result  # True or False
    except (TimeoutError, NetworkError, ServerError) as e:
        logging.warning(f"Condition evaluation failed: {e}")
        return False  # Fail-closed: condition not met
```

**Applies To:**
- Remote conditions (hooks)
- Remote conditions (agent auto-response)
- Expression evaluation timeouts

#### Hook Fallback (Event-Type-Based)

**Behavior**: Fallback behavior depends on event type (early vs late):

**Early Events (Fail-Closed - BLOCK):**
- `run.started` - Run is starting, block if unsure
- `content.created` - New content, block if unsure
- **Fallback**: BLOCK - don't proceed without approval

**Late Events (Fail-Open - ALLOW):**
- `content.updated` - Mid-stream content update
- `message.completed` - Message finished
- `content.completed` - Content finished
- **Fallback**: ALLOW - don't interrupt streaming

**Source**: Hooks Design (lines 710, 1116-1130)

**Rationale**:
- **Early events**: Blocking at start prevents unauthorized runs
- **Late events**: Allowing during streaming prevents UX disruption

**Example:**
```python
def apply_hook_fallback(event_type: str) -> str:
    """Apply fallback behavior based on event type"""

    # Early events: fail-closed (BLOCK)
    early_events = ["run.started", "content.created"]
    if event_type in early_events:
        logging.warning(f"Hook timeout for {event_type}, applying BLOCK fallback")
        return "block"

    # Late events: fail-open (ALLOW)
    late_events = ["content.updated", "message.completed", "content.completed"]
    if event_type in late_events:
        logging.warning(f"Hook timeout for {event_type}, applying ALLOW fallback")
        return "allow"
```

#### HTTP Fallback (WebSocket Failure)

**Behavior**: When WebSocket connection fails, attempt HTTP request before applying timeout fallback.

**Source**: Hooks Design (lines 606-608, 1153-1155)

**Flow:**
1. Attempt WebSocket connection
2. If WebSocket fails (handshake timeout, connection refused):
   - Try HTTP POST to hook endpoint
   - If HTTP succeeds: use response
   - If HTTP fails: apply timeout fallback

**Example:**
```python
def invoke_hook_with_fallback(hook, event):
    """Invoke hook with WebSocket → HTTP fallback"""

    # Try WebSocket first
    try:
        return invoke_hook_websocket(hook, event)
    except WebSocketError as e:
        logging.warning(f"WebSocket failed: {e}, trying HTTP fallback")

        # Try HTTP fallback
        try:
            return invoke_hook_http(hook, event)
        except HTTPError as e:
            logging.error(f"HTTP fallback failed: {e}, applying timeout fallback")

            # Apply event-type-based fallback
            return apply_hook_fallback(event.type)
```

### Provider Fallback

```python
PROVIDERS = ["openai", "anthropic", "azure"]

def create_run_with_fallback(request):
    """Try providers in order until one succeeds"""
    for provider in PROVIDERS:
        try:
            client = get_client(provider)
            return client.create_run(request)
        except ProviderError as e:
            print(f"{provider} failed: {e}")
            continue
    raise AllProvidersFailed()
```

**Degraded Mode:**

```python
def create_run_with_degradation(request):
    """Try full request, fall back to simpler version"""
    try:
        return create_run(request)
    except ContextLengthExceeded:
        # Fall back to simpler request
        request.input = truncate_context(request.input)
        return create_run(request)
```

## Error Handling Patterns

### Try-Catch Pattern

**Python:**
```python
try:
    response = client.create_run(request)
except ValidationError as e:
    # Don't retry validation errors
    print(f"Invalid request: {e.message}")
    print(f"Field: {e.field}")
    return None
except AuthError as e:
    # Handle authentication errors
    if e.code == "TOKEN_EXPIRED":
        refresh_token()
        return create_run(request)  # Retry
    else:
        print(f"Auth error: {e.message}")
        return None
except RateLimitError as e:
    # Wait and retry
    time.sleep(e.retry_after)
    return create_run(request)
except ProviderError as e:
    # Retry with backoff
    return retry_with_backoff(lambda: create_run(request))
except Exception as e:
    # Unknown error
    print(f"Unexpected error: {e}")
    return None
```

### Error Context Propagation

**Good - Preserve Context:**
```python
try:
    result = execute_tool(tool_call)
except Exception as e:
    raise ToolExecutionError(
        code="TOOL_EXECUTION_FAILED",
        message=f"Tool '{tool_call.name}' failed: {str(e)}",
        details={
            "tool_name": tool_call.name,
            "call_id": tool_call.call_id,
            "original_error": str(e)
        }
    ) from e
```

**Bad - Lose Context:**
```python
try:
    result = execute_tool(tool_call)
except Exception:
    raise Exception("Tool failed")  # Lost context!
```

### Graceful Degradation

**Continue on Non-Critical Errors:**

```python
def process_messages(messages):
    """Process messages, skip invalid ones"""
    results = []
    errors = []

    for msg in messages:
        try:
            result = process_message(msg)
            results.append(result)
        except ValidationError as e:
            # Log error, continue with next message
            errors.append({"message_id": msg.id, "error": e})
            continue

    return {
        "results": results,
        "errors": errors,
        "success_count": len(results),
        "error_count": len(errors)
    }
```

## Run Error Handling

### RunError Model

**TypeSpec**: See `RunError` model in `typespec/execution.tsp`

```typescript
model RunError {
  code: string;
  message: string;
  details?: Record<unknown>;
}
```

**Example:**
```json
{
  "runId": "run_123",
  "status": "failed",
  "error": {
    "code": "CONTEXT_LENGTH_EXCEEDED",
    "message": "Request exceeds maximum context length of 128,000 tokens",
    "details": {
      "max_tokens": 128000,
      "requested_tokens": 150000,
      "input_tokens": 140000,
      "output_tokens": 10000
    }
  }
}
```

### Run Failure Scenarios

**Max Turns Exceeded:**
```json
{
  "status": "incomplete",
  "error": {
    "code": "MAX_TURNS_EXCEEDED",
    "message": "Run exceeded maximum of 100 turns",
    "details": {
      "max_turns": 100,
      "turns_used": 100,
      "last_role": "assistant"
    }
  }
}
```

**Provider Error:**
```json
{
  "status": "failed",
  "error": {
    "code": "PROVIDER_ERROR",
    "message": "OpenAI API returned 500 Internal Server Error",
    "details": {
      "provider": "openai",
      "http_status": 500,
      "provider_error": "Internal server error"
    }
  }
}
```

## Monitoring & Alerting

### Error Metrics

**Track These Metrics:**
- Error rate by code
- Error rate by endpoint
- 4xx vs 5xx errors
- Retry success rate
- Provider error rate

**Example Metrics:**
```
errors_total{code="RATE_LIMIT_EXCEEDED"} 45
errors_total{code="PROVIDER_ERROR"} 12
errors_total{code="INVALID_INPUT"} 230

error_rate_4xx 0.15  # 15% client errors
error_rate_5xx 0.02  # 2% server errors

retry_success_rate 0.85  # 85% retries succeed
```

### Error Logging

**Structured Logging:**

```python
import logging
import json

def log_error(error, context):
    """Log error with structured context"""
    logging.error(json.dumps({
        "error_code": error.code,
        "error_message": error.message,
        "run_id": context.get("run_id"),
        "thread_id": context.get("thread_id"),
        "user_id": context.get("user_id"),
        "timestamp": time.time(),
        "details": error.details
    }))
```

**Example Log:**
```json
{
  "error_code": "TOOL_EXECUTION_FAILED",
  "error_message": "Tool 'search_web' failed: Network timeout",
  "run_id": "run_123",
  "thread_id": "thread_456",
  "user_id": "user_789",
  "timestamp": 1738761600,
  "details": {
    "tool_name": "search_web",
    "call_id": "call_1",
    "timeout_seconds": 30
  }
}
```

## Requirements

### Server Requirements

Servers MUST:

1. **Consistent Format**: Use consistent error response format
2. **HTTP Status Codes**: Return appropriate HTTP status codes
3. **Error Codes**: Include machine-readable error codes
4. **Actionable Messages**: Provide clear, actionable error messages
5. **Error Details**: Include relevant context in details field

Servers SHOULD:

1. **Log Errors**: Log all errors with structured logging
2. **Track Metrics**: Monitor error rates and patterns
3. **Rate Limit Headers**: Include Retry-After header for 429 errors
4. **Correlation IDs**: Include request ID for debugging

### Client Requirements

Clients MUST:

1. **Check Status Codes**: Check HTTP status before parsing response
2. **Parse Errors**: Parse error response structure
3. **Handle Errors**: Handle errors appropriately (retry or fail)
4. **Respect Retry-After**: Wait before retrying rate-limited requests

Clients SHOULD:

1. **Implement Retry**: Implement exponential backoff for retryable errors
2. **Log Errors**: Log errors for debugging
3. **Monitor Errors**: Track error rates
4. **User Feedback**: Show user-friendly error messages

## Best Practices

### Don't Swallow Errors

**Bad:**
```python
try:
    result = execute_tool(tool_call)
except Exception:
    pass  # Silently ignores error!
```

**Good:**
```python
try:
    result = execute_tool(tool_call)
except Exception as e:
    logging.error(f"Tool execution failed: {e}")
    raise
```

### Provide Context

**Bad:**
```json
{
  "error": {
    "code": "ERROR",
    "message": "Something went wrong"
  }
}
```

**Good:**
```json
{
  "error": {
    "code": "TOOL_EXECUTION_FAILED",
    "message": "Tool 'search_web' failed: Network timeout after 30 seconds",
    "details": {
      "tool_name": "search_web",
      "call_id": "call_1",
      "timeout_seconds": 30,
      "retry_suggested": true
    }
  }
}
```

### Fail Fast, Fail Clearly

**Bad - Fails late:**
```python
def create_run(request):
    run = Run(id=generate_id())
    save_to_db(run)
    # Validation after side effects!
    validate_request(request)
    ...
```

**Good - Fails fast:**
```python
def create_run(request):
    # Validate FIRST
    validate_request(request)
    # Only proceed if valid
    run = Run(id=generate_id())
    save_to_db(run)
    ...
```

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/execution.tsp` (RunError)
- **TypeSpec**: `typespec/messages.tsp` (ErrorContent)
- **RFC 7807**: Problem Details for HTTP APIs
- **HTTP Status Codes**: RFC 7231
- **Retry Best Practices**: Industry standards (exponential backoff, jitter)

## See Also

- [Run Lifecycle](./run-lifecycle.md) - Run error states
- [Validation](./validation.md) - Validation error codes
- [Authentication](./authentication.md) - Authentication error codes
- [Tool Execution](./tool-execution.md) - Tool execution errors
- [Streaming](./streaming.md) - Streaming error handling
