# Error Handling & Resilience Guide

**Version**: 1.0

## Overview

This guide provides comprehensive strategies for building resilient agent integrations that gracefully handle failures, recover from errors, and maintain reliability in production environments. Whether you're handling run failures, implementing retry logic, or building circuit breakers for tool calls, this guide covers proven patterns for robust error handling.

**What You'll Learn:**
- Retry strategies with exponential backoff and jitter
- Handling run failures (failed, incomplete, timeout states)
- Tool execution error recovery
- Run cancellation patterns (interrupt vs rollback)
- Graceful degradation strategies
- Circuit breakers for tool calls
- Error monitoring and alerting
- Timeout handling and configuration

**Key Benefits:**
- **Reliability**: Automatic recovery from transient failures
- **User Experience**: Graceful degradation instead of hard failures
- **Observability**: Structured error logging and metrics
- **Cost Efficiency**: Smart retry logic prevents unnecessary API calls
- **Production-Ready**: Battle-tested patterns for enterprise deployments

## Use Cases

### 1. Transient Failure Recovery

**Scenario**: LLM provider experiences temporary outage or rate limiting.

**Solution**: Automatic retry with exponential backoff recovers without user intervention.

**Example**: OpenAI API returns 503 Service Unavailable → Retry after 100ms, 200ms, 400ms → Request succeeds on second retry.

### 2. Long-Running Task Management

**Scenario**: Data analysis agent processes large datasets that may timeout.

**Solution**: Implement timeout handling with graceful degradation to partial results.

**Example**: 5-minute timeout → Return partial analysis with warning instead of complete failure.

### 3. Tool Execution Resilience

**Scenario**: External tool APIs are unreliable (weather API, search API).

**Solution**: Circuit breaker pattern prevents cascade failures and provides fallback responses.

**Example**: After 3 consecutive weather API failures → Open circuit, return cached data for 60 seconds.

### 4. User-Initiated Cancellation

**Scenario**: User clicks "stop generating" during long response.

**Solution**: Clean cancellation with interrupt mode preserves partial output for review.

**Example**: User cancels 10-second generation → Agent stops immediately, returns first 5 seconds of output.

### 5. Multi-Agent Orchestration Errors

**Scenario**: Handoff to unavailable agent in multi-agent workflow.

**Solution**: Detect handoff failure, retry with backoff, or fallback to alternate agent.

**Example**: Handoff to `specialized_agent` fails → Retry 3 times → Fallback to `general_agent`.

### 6. Rate Limit Management

**Scenario**: High-volume API usage hits rate limits during peak hours.

**Solution**: Respect `Retry-After` headers and implement adaptive throttling.

**Example**: 429 Rate Limit → Wait 60 seconds → Resume with reduced concurrency.

---

## Architecture

### Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Error Handling Pipeline                     │
└─────────────────────────────────────────────────────────────────┘

Request → [Validation] → [Execution] → [Response]
              ↓              ↓             ↓
           [Error?]      [Error?]      [Error?]
              ↓              ↓             ↓
          ┌───┴──────────────┴─────────────┴───┐
          │        Error Classification         │
          └───┬──────────────┬─────────────┬───┘
              ↓              ↓             ↓
         Client Error   Server Error   Timeout
         (4xx - Don't   (5xx - Retry   (Retry with
          retry)         with backoff)  timeout inc)
              ↓              ↓             ↓
          ┌───┴──────────────┴─────────────┴───┐
          │         Recovery Strategy           │
          │  - Immediate Fail                   │
          │  - Exponential Backoff Retry        │
          │  - Circuit Breaker                  │
          │  - Graceful Degradation             │
          │  - Fallback Response                │
          └─────────────────────────────────────┘
```

### Error Categories

#### Client Errors (4xx)

**Characteristics:**
- Caused by invalid client request
- Should NOT retry without fixing request
- Client must change request to succeed

**HTTP Status Codes:**
- `400 Bad Request` - Invalid input, validation failure
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - State conflict
- `422 Unprocessable Entity` - Business logic error

**Strategy**: Fail immediately, log error, notify user

#### Server Errors (5xx)

**Characteristics:**
- Caused by server or provider issues
- MAY retry with exponential backoff
- Issue is transient or server-side

**HTTP Status Codes:**
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Temporary unavailable
- `504 Gateway Timeout` - Upstream timeout

**Strategy**: Retry with exponential backoff (max 3 attempts)

#### Run Status Errors

**Final Error States** (from `RunStatus` enum in `../typespec/execution.tsp`):

| Status | Description | Retry Strategy |
|--------|-------------|----------------|
| `failed` | Error occurred during execution | Check `error.code` for retry guidance |
| `cancelled` | User cancelled run | Don't retry (user action) |
| `incomplete` | Stopped before completion (max_turns) | Don't retry without config changes |
| `timeout` | Exceeded time limit | Retry with increased timeout |

### Retry Strategy Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  Exponential Backoff with Jitter               │
└────────────────────────────────────────────────────────────────┘

Attempt 1: Request
           ↓ [Fails]
           Wait: 100ms ± 50ms jitter
           ↓
Attempt 2: Request
           ↓ [Fails]
           Wait: 200ms ± 100ms jitter
           ↓
Attempt 3: Request
           ↓ [Fails]
           Wait: 400ms ± 200ms jitter
           ↓
Attempt 4: Request
           ↓ [Success or Final Failure]

Max Retries: 3
Base Delay: 100ms
Max Delay: 400ms
Jitter: ±50% to prevent thundering herd
```

### Circuit Breaker Pattern

```
┌────────────────────────────────────────────────────────────────┐
│                     Circuit Breaker States                     │
└────────────────────────────────────────────────────────────────┘

         ┌───────────┐
         │  CLOSED   │ ← Normal operation
         │ (Working) │
         └─────┬─────┘
               │
               │ Failure count exceeds threshold
               ↓
         ┌───────────┐
         │   OPEN    │ ← Fast-fail (reject immediately)
         │ (Failing) │
         └─────┬─────┘
               │
               │ After timeout period
               ↓
         ┌───────────┐
         │ HALF-OPEN │ ← Test recovery
         │ (Testing) │
         └─────┬─────┘
               │
         ┌─────┴──────┐
         ↓            ↓
    Success      Failure
         ↓            ↓
    [CLOSED]     [OPEN]

Configuration:
- Failure Threshold: 3 consecutive failures
- Timeout: 60 seconds
- Half-Open Test: 1 request
```

---

## Implementation

### Step 1: Basic Error Handling

#### Parse Error Responses

All errors follow consistent structure (from `../specifications/error-handling.md`):

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "field": "string",
    "details": {}
  }
}
```

**Python:**
```python
import requests
from typing import Optional, Dict, Any

class AgentAPIError(Exception):
    """Base exception for Agent Runtime API errors"""
    def __init__(self, code: str, message: str, status_code: int,
                 field: Optional[str] = None, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details or {}
        super().__init__(f"[{code}] {message}")

class ValidationError(AgentAPIError):
    """Client-side validation error (4xx)"""
    pass

class AuthenticationError(AgentAPIError):
    """Authentication/authorization error (401/403)"""
    pass

class ResourceNotFoundError(AgentAPIError):
    """Resource not found error (404)"""
    pass

class RateLimitError(AgentAPIError):
    """Rate limit exceeded (429)"""
    def __init__(self, code: str, message: str, status_code: int,
                 retry_after: int, **kwargs):
        super().__init__(code, message, status_code, **kwargs)
        self.retry_after = retry_after

class ServerError(AgentAPIError):
    """Server-side error (5xx)"""
    pass

def parse_error_response(response: requests.Response) -> AgentAPIError:
    """Parse error response and return appropriate exception"""
    try:
        error_data = response.json().get('error', {})
    except ValueError:
        error_data = {'code': 'UNKNOWN_ERROR', 'message': response.text}

    code = error_data.get('code', 'UNKNOWN_ERROR')
    message = error_data.get('message', 'An error occurred')
    field = error_data.get('field')
    details = error_data.get('details', {})
    status = response.status_code

    # Classify error by status code
    if 400 <= status < 500:
        if status == 401 or status == 403:
            return AuthenticationError(code, message, status, field, details)
        elif status == 404:
            return ResourceNotFoundError(code, message, status, field, details)
        elif status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            return RateLimitError(code, message, status, retry_after, field=field, details=details)
        else:
            return ValidationError(code, message, status, field, details)
    elif 500 <= status < 600:
        return ServerError(code, message, status, field, details)
    else:
        return AgentAPIError(code, message, status, field, details)

# Usage
response = requests.post(url, json=data)
if not response.ok:
    error = parse_error_response(response)
    raise error
```

**JavaScript/TypeScript:**
```typescript
class AgentAPIError extends Error {
  code: string;
  statusCode: number;
  field?: string;
  details?: Record<string, any>;

  constructor(
    code: string,
    message: string,
    statusCode: number,
    field?: string,
    details?: Record<string, any>
  ) {
    super(`[${code}] ${message}`);
    this.code = code;
    this.statusCode = statusCode;
    this.field = field;
    this.details = details;
    this.name = 'AgentAPIError';
  }

  isRetryable(): boolean {
    // Server errors (5xx) and rate limits (429) are retryable
    return this.statusCode >= 500 || this.statusCode === 429;
  }
}

class ValidationError extends AgentAPIError {}
class AuthenticationError extends AgentAPIError {}
class ResourceNotFoundError extends AgentAPIError {}
class RateLimitError extends AgentAPIError {
  retryAfter: number;

  constructor(
    code: string,
    message: string,
    statusCode: number,
    retryAfter: number,
    field?: string,
    details?: Record<string, any>
  ) {
    super(code, message, statusCode, field, details);
    this.retryAfter = retryAfter;
  }
}
class ServerError extends AgentAPIError {}

function parseErrorResponse(response: Response): AgentAPIError {
  const errorData = response.json().error || {};
  const code = errorData.code || 'UNKNOWN_ERROR';
  const message = errorData.message || 'An error occurred';
  const field = errorData.field;
  const details = errorData.details;
  const status = response.status;

  if (status >= 400 && status < 500) {
    if (status === 401 || status === 403) {
      return new AuthenticationError(code, message, status, field, details);
    } else if (status === 404) {
      return new ResourceNotFoundError(code, message, status, field, details);
    } else if (status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
      return new RateLimitError(code, message, status, retryAfter, field, details);
    } else {
      return new ValidationError(code, message, status, field, details);
    }
  } else if (status >= 500) {
    return new ServerError(code, message, status, field, details);
  }

  return new AgentAPIError(code, message, status, field, details);
}

// Usage
const response = await fetch(url, { method: 'POST', body: JSON.stringify(data) });
if (!response.ok) {
  const error = parseErrorResponse(response);
  throw error;
}
```

### Step 2: Implement Exponential Backoff

Based on retry specification from `../specifications/error-handling.md` (lines 296-344):

**Configuration:**
- Max Retries: 3
- Base Delay: 100ms
- Delays: 100ms → 200ms → 400ms
- Jitter: ±50% to prevent thundering herd

**Python:**
```python
import time
import random
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

def retry_with_exponential_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 0.1,  # 100ms
    max_delay: float = 0.4,    # 400ms
    jitter: float = 0.5        # ±50%
) -> T:
    """
    Retry function with exponential backoff and jitter.

    Implements retry strategy from error-handling.md:
    - Attempt 1: Immediate
    - Attempt 2: 100ms ± 50ms
    - Attempt 3: 200ms ± 100ms
    - Attempt 4: 400ms ± 200ms

    Args:
        func: Function to retry
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 0.1 = 100ms)
        max_delay: Maximum delay in seconds (default: 0.4 = 400ms)
        jitter: Jitter factor (default: 0.5 = ±50%)

    Returns:
        Result from successful function call

    Raises:
        Last exception if all retries exhausted
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except AgentAPIError as e:
            last_exception = e

            # Check if error is retryable
            if not is_retryable(e):
                raise

            # Last attempt - don't sleep
            if attempt == max_retries:
                raise

            # Calculate delay with exponential backoff
            delay = min(base_delay * (2 ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            jitter_amount = delay * jitter
            jittered_delay = delay + random.uniform(-jitter_amount, jitter_amount)

            print(f"Retry {attempt + 1}/{max_retries} after {jittered_delay*1000:.0f}ms (error: {e.code})")
            time.sleep(jittered_delay)

    # Should never reach here, but for type safety
    raise last_exception

def is_retryable(error: AgentAPIError) -> bool:
    """
    Check if error is retryable based on error-handling.md specification.

    Retryable errors:
    - RATE_LIMIT_EXCEEDED (429)
    - TOKEN_EXPIRED (401)
    - PROVIDER_ERROR (500)
    - SERVICE_UNAVAILABLE (503)
    - TIMEOUT (504)
    - INTERNAL_ERROR (500)
    """
    retryable_codes = {
        'RATE_LIMIT_EXCEEDED',
        'TOKEN_EXPIRED',
        'PROVIDER_ERROR',
        'PROVIDER_UNAVAILABLE',
        'SERVICE_UNAVAILABLE',
        'TIMEOUT',
        'INTERNAL_ERROR',
        'TOOL_TIMEOUT'
    }

    # Check by error code
    if error.code in retryable_codes:
        return True

    # Check by status code (5xx and 429 are retryable)
    if error.status_code >= 500 or error.status_code == 429:
        return True

    return False

# Usage
def create_run_with_retry(client, request):
    """Create run with automatic retry"""
    return retry_with_exponential_backoff(
        lambda: client.create_run(request),
        max_retries=3
    )

# Example
try:
    run = create_run_with_retry(client, {
        'agentId': 'agent_123',
        'input': [{'role': 'user', 'contents': [{'kind': 'text', 'text': 'Hello'}]}]
    })
    print(f"Run created: {run['runId']}")
except AgentAPIError as e:
    print(f"Failed after retries: {e.code} - {e.message}")
```

**JavaScript/TypeScript:**
```typescript
async function retryWithExponentialBackoff<T>(
  func: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 100,    // milliseconds
  maxDelay: number = 400,     // milliseconds
  jitter: number = 0.5        // ±50%
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await func();
    } catch (error) {
      lastError = error as Error;

      // Check if error is retryable
      if (!(error instanceof AgentAPIError) || !isRetryable(error)) {
        throw error;
      }

      // Last attempt - don't wait
      if (attempt === maxRetries) {
        throw error;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);

      // Add jitter to prevent thundering herd
      const jitterAmount = delay * jitter;
      const jitteredDelay = delay + (Math.random() * 2 - 1) * jitterAmount;

      console.log(`Retry ${attempt + 1}/${maxRetries} after ${jitteredDelay.toFixed(0)}ms (error: ${error.code})`);
      await sleep(jitteredDelay);
    }
  }

  throw lastError!;
}

function isRetryable(error: AgentAPIError): boolean {
  const retryableCodes = new Set([
    'RATE_LIMIT_EXCEEDED',
    'TOKEN_EXPIRED',
    'PROVIDER_ERROR',
    'PROVIDER_UNAVAILABLE',
    'SERVICE_UNAVAILABLE',
    'TIMEOUT',
    'INTERNAL_ERROR',
    'TOOL_TIMEOUT'
  ]);

  return retryableCodes.has(error.code) ||
         error.statusCode >= 500 ||
         error.statusCode === 429;
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage
async function createRunWithRetry(client: AgentClient, request: CreateRunRequest) {
  return retryWithExponentialBackoff(
    () => client.createRun(request),
    3 // max retries
  );
}

// Example
try {
  const run = await createRunWithRetry(client, {
    agentId: 'agent_123',
    input: [{ role: 'user', contents: [{ kind: 'text', text: 'Hello' }] }]
  });
  console.log(`Run created: ${run.runId}`);
} catch (error) {
  console.error(`Failed after retries: ${error.code} - ${error.message}`);
}
```

### Step 3: Handle Rate Limits

Respect `Retry-After` header from 429 responses (from `../specifications/error-handling.md`, lines 356-377):

**Python:**
```python
def handle_rate_limit(func: Callable[[], T], max_retries: int = 3) -> T:
    """
    Handle rate limits with Retry-After header.

    Implements rate limit handling from error-handling.md:
    - Parse Retry-After header (default 60s)
    - Wait specified duration
    - Retry request
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries:
                raise

            retry_after = e.retry_after
            print(f"Rate limited. Waiting {retry_after}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(retry_after)

    raise RuntimeError("Should not reach here")

# Usage with combined retry logic
def create_run_robust(client, request):
    """Create run with rate limit and transient error handling"""

    def attempt_create():
        # Inner retry for transient errors (with exponential backoff)
        return retry_with_exponential_backoff(
            lambda: client.create_run(request),
            max_retries=3
        )

    # Outer retry for rate limits (with Retry-After)
    return handle_rate_limit(attempt_create, max_retries=2)
```

**JavaScript/TypeScript:**
```typescript
async function handleRateLimit<T>(
  func: () => Promise<T>,
  maxRetries: number = 3
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await func();
    } catch (error) {
      if (!(error instanceof RateLimitError) || attempt === maxRetries) {
        throw error;
      }

      const retryAfter = error.retryAfter * 1000; // Convert to ms
      console.log(`Rate limited. Waiting ${error.retryAfter}s before retry ${attempt + 1}/${maxRetries}...`);
      await sleep(retryAfter);
    }
  }

  throw new Error('Should not reach here');
}

// Usage with combined retry logic
async function createRunRobust(client: AgentClient, request: CreateRunRequest) {
  return handleRateLimit(
    () => retryWithExponentialBackoff(
      () => client.createRun(request),
      3 // max retries for transient errors
    ),
    2 // max retries for rate limits
  );
}
```

### Step 4: Handle Run Failures

Handle different run failure states (from `../typespec/execution.tsp`, lines 481-514):

**RunStatus enum states:**
- `failed` - Error occurred
- `cancelled` - User cancelled
- `incomplete` - Stopped before completion (max_turns exceeded)
- `timeout` - Exceeded time limit

**Python:**
```python
from typing import Dict, Any, Optional
from enum import Enum

class RunStatus(Enum):
    """Run status enum from execution.tsp"""
    QUEUED = 'queued'
    IN_PROGRESS = 'in_progress'
    REQUIRES_ACTION = 'requires_action'
    INPUT_REQUIRED = 'input_required'
    AUTH_REQUIRED = 'auth_required'
    CANCELLING = 'cancelling'
    CANCELLED = 'cancelled'
    FAILED = 'failed'
    COMPLETED = 'completed'
    INCOMPLETE = 'incomplete'
    TIMEOUT = 'timeout'

class RunError:
    """Run error model from execution.tsp (lines 581-604)"""
    def __init__(self, code: str, message: str, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}

    @classmethod
    def from_dict(cls, data: Dict) -> 'RunError':
        return cls(
            code=data['code'],
            message=data['message'],
            details=data.get('details')
        )

def handle_run_failure(run: Dict[str, Any]) -> None:
    """
    Handle run failure based on status and error code.

    From run-lifecycle.md (lines 1189-1226) and error-handling.md (lines 616-679)
    """
    status = run['status']
    error = RunError.from_dict(run['error']) if run.get('error') else None

    if status == RunStatus.FAILED.value:
        if not error:
            raise RuntimeError("Run failed without error details")

        # Handle specific error codes
        if error.code == 'MAX_TURNS_EXCEEDED':
            print(f"Run hit max turns limit: {error.details.get('max_turns')}")
            print("Solution: Increase max_turns or simplify task")
            # Don't retry - configuration issue

        elif error.code == 'CONTEXT_LENGTH_EXCEEDED':
            print(f"Context too large: {error.details.get('requested_tokens')} tokens")
            print("Solution: Reduce input or use model with larger context")
            # Could retry with truncated context

        elif error.code == 'TOOL_EXECUTION_FAILED':
            tool_name = error.details.get('tool_name')
            print(f"Tool '{tool_name}' failed: {error.message}")
            # Could retry with different tool or skip tool

        elif error.code == 'PROVIDER_ERROR':
            provider = error.details.get('provider')
            print(f"Provider {provider} error: {error.message}")
            # Should retry with exponential backoff

        elif error.code == 'RATE_LIMIT_EXCEEDED':
            print(f"Rate limit hit: {error.message}")
            # Should retry after Retry-After period

        else:
            print(f"Run failed: {error.code} - {error.message}")

    elif status == RunStatus.CANCELLED.value:
        print("Run was cancelled by user")
        cancelled_at = run.get('cancelledAt')
        reason = run.get('cancellationReason', 'No reason provided')
        print(f"Cancelled at: {cancelled_at}, Reason: {reason}")
        # Don't retry - user action

    elif status == RunStatus.INCOMPLETE.value:
        if error and error.code == 'MAX_TURNS_EXCEEDED':
            max_turns = error.details.get('max_turns')
            turns_used = error.details.get('turns_used')
            print(f"Run incomplete: Used {turns_used}/{max_turns} turns")
            print("Solution: Increase max_turns in RunOptions")
        else:
            print(f"Run incomplete: {error.message if error else 'Unknown reason'}")
        # Don't retry without config changes

    elif status == RunStatus.TIMEOUT.value:
        print("Run exceeded execution time limit")
        print("Solution: Increase timeout or optimize agent")
        # Could retry with increased timeout

def is_run_retryable(run: Dict[str, Any]) -> bool:
    """Check if run failure is retryable"""
    status = run['status']
    error = RunError.from_dict(run['error']) if run.get('error') else None

    # Never retry user cancellations
    if status == RunStatus.CANCELLED.value:
        return False

    # Don't retry incomplete without config changes
    if status == RunStatus.INCOMPLETE.value:
        return False

    # Timeout could be retried with increased timeout
    if status == RunStatus.TIMEOUT.value:
        return True

    # For failed runs, check error code
    if status == RunStatus.FAILED.value and error:
        retryable_codes = {
            'RATE_LIMIT_EXCEEDED',
            'PROVIDER_ERROR',
            'PROVIDER_UNAVAILABLE',
            'SERVICE_UNAVAILABLE',
            'TIMEOUT',
            'TOOL_TIMEOUT',
            'CONTEXT_LENGTH_EXCEEDED'  # Can retry with truncated context
        }
        return error.code in retryable_codes

    return False

# Usage
def create_and_wait_for_run(client, request, max_retries=3):
    """Create run and wait for completion with retry logic"""

    for attempt in range(max_retries + 1):
        try:
            # Create run with retry for transient errors
            run = retry_with_exponential_backoff(
                lambda: client.create_run(request)
            )

            # Poll until terminal state
            while run['status'] in ['queued', 'in_progress', 'requires_action']:
                time.sleep(1)
                run = client.get_run(run['runId'])

            # Check final status
            if run['status'] == 'completed':
                return run

            # Handle failure
            handle_run_failure(run)

            # Check if retryable
            if not is_run_retryable(run) or attempt == max_retries:
                raise RuntimeError(f"Run failed with status: {run['status']}")

            print(f"Retrying run (attempt {attempt + 2}/{max_retries + 1})...")
            time.sleep(2 ** attempt)  # Exponential backoff between run retries

        except AgentAPIError as e:
            if not is_retryable(e) or attempt == max_retries:
                raise
            print(f"API error, retrying: {e.code}")
            time.sleep(2 ** attempt)

    raise RuntimeError("Max retries exceeded")
```

**JavaScript/TypeScript:**
```typescript
enum RunStatus {
  QUEUED = 'queued',
  IN_PROGRESS = 'in_progress',
  REQUIRES_ACTION = 'requires_action',
  INPUT_REQUIRED = 'input_required',
  AUTH_REQUIRED = 'auth_required',
  CANCELLING = 'cancelling',
  CANCELLED = 'cancelled',
  FAILED = 'failed',
  COMPLETED = 'completed',
  INCOMPLETE = 'incomplete',
  TIMEOUT = 'timeout'
}

interface RunError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

interface Run {
  runId: string;
  status: string;
  error?: RunError;
  output: any[];
  cancelledAt?: string;
  cancellationReason?: string;
}

function handleRunFailure(run: Run): void {
  const { status, error } = run;

  if (status === RunStatus.FAILED) {
    if (!error) {
      throw new Error('Run failed without error details');
    }

    switch (error.code) {
      case 'MAX_TURNS_EXCEEDED':
        console.log(`Run hit max turns limit: ${error.details?.max_turns}`);
        console.log('Solution: Increase max_turns or simplify task');
        break;

      case 'CONTEXT_LENGTH_EXCEEDED':
        console.log(`Context too large: ${error.details?.requested_tokens} tokens`);
        console.log('Solution: Reduce input or use model with larger context');
        break;

      case 'TOOL_EXECUTION_FAILED':
        console.log(`Tool '${error.details?.tool_name}' failed: ${error.message}`);
        break;

      case 'PROVIDER_ERROR':
        console.log(`Provider ${error.details?.provider} error: ${error.message}`);
        break;

      case 'RATE_LIMIT_EXCEEDED':
        console.log(`Rate limit hit: ${error.message}`);
        break;

      default:
        console.log(`Run failed: ${error.code} - ${error.message}`);
    }
  } else if (status === RunStatus.CANCELLED) {
    console.log('Run was cancelled by user');
    console.log(`Cancelled at: ${run.cancelledAt}, Reason: ${run.cancellationReason || 'No reason provided'}`);
  } else if (status === RunStatus.INCOMPLETE) {
    if (error?.code === 'MAX_TURNS_EXCEEDED') {
      console.log(`Run incomplete: Used ${error.details?.turns_used}/${error.details?.max_turns} turns`);
      console.log('Solution: Increase max_turns in RunOptions');
    } else {
      console.log(`Run incomplete: ${error?.message || 'Unknown reason'}`);
    }
  } else if (status === RunStatus.TIMEOUT) {
    console.log('Run exceeded execution time limit');
    console.log('Solution: Increase timeout or optimize agent');
  }
}

function isRunRetryable(run: Run): boolean {
  const { status, error } = run;

  if (status === RunStatus.CANCELLED || status === RunStatus.INCOMPLETE) {
    return false;
  }

  if (status === RunStatus.TIMEOUT) {
    return true;
  }

  if (status === RunStatus.FAILED && error) {
    const retryableCodes = new Set([
      'RATE_LIMIT_EXCEEDED',
      'PROVIDER_ERROR',
      'PROVIDER_UNAVAILABLE',
      'SERVICE_UNAVAILABLE',
      'TIMEOUT',
      'TOOL_TIMEOUT',
      'CONTEXT_LENGTH_EXCEEDED'
    ]);
    return retryableCodes.has(error.code);
  }

  return false;
}

async function createAndWaitForRun(
  client: AgentClient,
  request: CreateRunRequest,
  maxRetries: number = 3
): Promise<Run> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Create run with retry for transient errors
      let run = await retryWithExponentialBackoff(
        () => client.createRun(request)
      );

      // Poll until terminal state
      while (['queued', 'in_progress', 'requires_action'].includes(run.status)) {
        await sleep(1000);
        run = await client.getRun(run.runId);
      }

      // Check final status
      if (run.status === RunStatus.COMPLETED) {
        return run;
      }

      // Handle failure
      handleRunFailure(run);

      // Check if retryable
      if (!isRunRetryable(run) || attempt === maxRetries) {
        throw new Error(`Run failed with status: ${run.status}`);
      }

      console.log(`Retrying run (attempt ${attempt + 2}/${maxRetries + 1})...`);
      await sleep(Math.pow(2, attempt) * 1000);

    } catch (error) {
      if (!(error instanceof AgentAPIError) || !isRetryable(error) || attempt === maxRetries) {
        throw error;
      }
      console.log(`API error, retrying: ${error.code}`);
      await sleep(Math.pow(2, attempt) * 1000);
    }
  }

  throw new Error('Max retries exceeded');
}
```

### Step 5: Implement Tool Error Handling

Handle tool execution failures gracefully:

**Python:**
```python
def execute_tool_with_fallback(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute tool with error handling and fallback.

    Handles tool execution errors from error-handling.md (lines 172-182)
    """
    try:
        # Execute tool
        result = execute_tool(tool_name, arguments)
        return result

    except TimeoutError as e:
        # Tool timeout - could retry with longer timeout
        print(f"Tool '{tool_name}' timed out: {e}")
        return json.dumps({
            'error': 'TOOL_TIMEOUT',
            'message': f"Tool execution exceeded timeout",
            'retry_suggested': True
        })

    except ConnectionError as e:
        # Network error - could retry
        print(f"Tool '{tool_name}' connection failed: {e}")
        return json.dumps({
            'error': 'TOOL_CONNECTION_ERROR',
            'message': f"Failed to connect to tool service",
            'retry_suggested': True
        })

    except ValidationError as e:
        # Invalid arguments - don't retry
        print(f"Tool '{tool_name}' validation error: {e}")
        return json.dumps({
            'error': 'TOOL_ARGUMENT_INVALID',
            'message': str(e),
            'retry_suggested': False
        })

    except Exception as e:
        # Unknown error - return graceful failure
        print(f"Tool '{tool_name}' execution failed: {e}")
        return json.dumps({
            'error': 'TOOL_EXECUTION_FAILED',
            'message': str(e),
            'retry_suggested': False
        })

def submit_tool_outputs_with_retry(client, run_id: str, tool_calls: list, max_retries: int = 3):
    """
    Submit tool outputs with individual tool error handling.

    Even if some tools fail, submit partial results to continue run.
    """
    tool_outputs = []

    for tool_call in tool_calls:
        call_id = tool_call['callId']
        tool_name = tool_call['name']
        arguments = tool_call.get('arguments', {})

        # Execute tool with fallback
        output = execute_tool_with_fallback(tool_name, arguments)

        tool_outputs.append({
            'tool_call_id': call_id,
            'output': output
        })

    # Submit all outputs (including errors) to continue run
    return retry_with_exponential_backoff(
        lambda: client.submit_tool_outputs(run_id, tool_outputs),
        max_retries=max_retries
    )
```

**JavaScript/TypeScript:**
```typescript
async function executeToolWithFallback(
  toolName: string,
  args: Record<string, any>
): Promise<string> {
  try {
    const result = await executeTool(toolName, args);
    return result;
  } catch (error) {
    if (error instanceof TimeoutError) {
      console.log(`Tool '${toolName}' timed out`);
      return JSON.stringify({
        error: 'TOOL_TIMEOUT',
        message: 'Tool execution exceeded timeout',
        retry_suggested: true
      });
    } else if (error instanceof NetworkError) {
      console.log(`Tool '${toolName}' connection failed`);
      return JSON.stringify({
        error: 'TOOL_CONNECTION_ERROR',
        message: 'Failed to connect to tool service',
        retry_suggested: true
      });
    } else if (error instanceof ValidationError) {
      console.log(`Tool '${toolName}' validation error`);
      return JSON.stringify({
        error: 'TOOL_ARGUMENT_INVALID',
        message: error.message,
        retry_suggested: false
      });
    } else {
      console.log(`Tool '${toolName}' execution failed`);
      return JSON.stringify({
        error: 'TOOL_EXECUTION_FAILED',
        message: String(error),
        retry_suggested: false
      });
    }
  }
}

async function submitToolOutputsWithRetry(
  client: AgentClient,
  runId: string,
  toolCalls: ToolCall[],
  maxRetries: number = 3
): Promise<void> {
  const toolOutputs = await Promise.all(
    toolCalls.map(async (toolCall) => {
      const output = await executeToolWithFallback(
        toolCall.name,
        toolCall.arguments || {}
      );

      return {
        tool_call_id: toolCall.callId,
        output
      };
    })
  );

  // Submit all outputs (including errors) to continue run
  await retryWithExponentialBackoff(
    () => client.submitToolOutputs(runId, toolOutputs),
    maxRetries
  );
}
```

### Step 6: Implement Circuit Breaker

Circuit breaker pattern prevents cascade failures (from `../specifications/error-handling.md`, lines 498-513):

**Python:**
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Callable, TypeVar

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = 'closed'      # Normal operation
    OPEN = 'open'          # Fast-fail mode
    HALF_OPEN = 'half_open'  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3      # Consecutive failures before opening
    timeout: int = 60               # Seconds before trying half-open
    success_threshold: int = 1      # Successes in half-open before closing

class CircuitBreaker:
    """
    Circuit breaker for tool calls and external services.

    Prevents cascade failures by fast-failing when service is down.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = Lock()

    def call(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self._should_attempt_reset():
                    print(f"Circuit breaker '{self.name}': OPEN → HALF_OPEN (testing recovery)")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    # Fast-fail without calling function
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable. Try again in {self._time_until_retry()}s"
                    )

        # Execute function
        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful execution"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    print(f"Circuit breaker '{self.name}': HALF_OPEN → CLOSED (recovered)")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.last_failure_time = None
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed execution"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitState.HALF_OPEN:
                print(f"Circuit breaker '{self.name}': HALF_OPEN → OPEN (still failing)")
                self.state = CircuitState.OPEN
                self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    print(f"Circuit breaker '{self.name}': CLOSED → OPEN ({self.failure_count} failures)")
                    self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open"""
        if not self.last_failure_time:
            return False
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout

    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed"""
        if not self.last_failure_time:
            return 0
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, int(self.config.timeout - elapsed))

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else None
            }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

# Usage - Protect tool execution with circuit breaker
weather_api_breaker = CircuitBreaker(
    'weather_api',
    CircuitBreakerConfig(
        failure_threshold=3,
        timeout=60,
        success_threshold=2
    )
)

def get_weather_with_circuit_breaker(city: str) -> dict:
    """Get weather with circuit breaker protection"""
    try:
        return weather_api_breaker.call(
            lambda: call_weather_api(city)
        )
    except CircuitBreakerOpenError as e:
        # Circuit is open - return cached data or fallback
        print(f"Weather API unavailable: {e}")
        return get_cached_weather(city) or {
            'error': 'SERVICE_UNAVAILABLE',
            'message': 'Weather service temporarily unavailable',
            'fallback': True
        }

# Check circuit breaker state
state = weather_api_breaker.get_state()
print(f"Circuit breaker state: {state}")
```

**JavaScript/TypeScript:**
```typescript
enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half_open'
}

interface CircuitBreakerConfig {
  failureThreshold: number;  // Consecutive failures before opening
  timeout: number;           // Milliseconds before trying half-open
  successThreshold: number;  // Successes in half-open before closing
}

class CircuitBreakerOpenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CircuitBreakerOpenError';
  }
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime: number | null = null;

  constructor(
    private name: string,
    private config: CircuitBreakerConfig = {
      failureThreshold: 3,
      timeout: 60000,
      successThreshold: 1
    }
  ) {}

  async call<T>(func: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (this.shouldAttemptReset()) {
        console.log(`Circuit breaker '${this.name}': OPEN → HALF_OPEN (testing recovery)`);
        this.state = CircuitState.HALF_OPEN;
        this.successCount = 0;
      } else {
        throw new CircuitBreakerOpenError(
          `Circuit breaker '${this.name}' is OPEN. ` +
          `Service unavailable. Try again in ${this.timeUntilRetry()}ms`
        );
      }
    }

    try {
      const result = await func();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.config.successThreshold) {
        console.log(`Circuit breaker '${this.name}': HALF_OPEN → CLOSED (recovered)`);
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        this.successCount = 0;
        this.lastFailureTime = null;
      }
    } else if (this.state === CircuitState.CLOSED) {
      this.failureCount = 0;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.state === CircuitState.HALF_OPEN) {
      console.log(`Circuit breaker '${this.name}': HALF_OPEN → OPEN (still failing)`);
      this.state = CircuitState.OPEN;
      this.successCount = 0;
    } else if (this.state === CircuitState.CLOSED) {
      if (this.failureCount >= this.config.failureThreshold) {
        console.log(`Circuit breaker '${this.name}': CLOSED → OPEN (${this.failureCount} failures)`);
        this.state = CircuitState.OPEN;
      }
    }
  }

  private shouldAttemptReset(): boolean {
    if (!this.lastFailureTime) return false;
    const elapsed = Date.now() - this.lastFailureTime;
    return elapsed >= this.config.timeout;
  }

  private timeUntilRetry(): number {
    if (!this.lastFailureTime) return 0;
    const elapsed = Date.now() - this.lastFailureTime;
    return Math.max(0, this.config.timeout - elapsed);
  }

  getState(): {
    name: string;
    state: string;
    failureCount: number;
    successCount: number;
    lastFailureTime: string | null;
    timeUntilRetry: number | null;
  } {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime ? new Date(this.lastFailureTime).toISOString() : null,
      timeUntilRetry: this.state === CircuitState.OPEN ? this.timeUntilRetry() : null
    };
  }
}

// Usage
const weatherApiBreaker = new CircuitBreaker('weather_api', {
  failureThreshold: 3,
  timeout: 60000,
  successThreshold: 2
});

async function getWeatherWithCircuitBreaker(city: string): Promise<any> {
  try {
    return await weatherApiBreaker.call(() => callWeatherApi(city));
  } catch (error) {
    if (error instanceof CircuitBreakerOpenError) {
      console.log(`Weather API unavailable: ${error.message}`);
      return getCachedWeather(city) || {
        error: 'SERVICE_UNAVAILABLE',
        message: 'Weather service temporarily unavailable',
        fallback: true
      };
    }
    throw error;
  }
}

// Check circuit breaker state
const state = weatherApiBreaker.getState();
console.log('Circuit breaker state:', state);
```

### Step 7: Implement Run Cancellation

Handle user-initiated cancellation with interrupt and rollback modes (from `../typespec/execution.tsp`, lines 494-571):

**Python:**
```python
from enum import Enum

class CancelAction(Enum):
    """Cancel action enum from execution.tsp"""
    INTERRUPT = 'interrupt'  # Stop but preserve state
    ROLLBACK = 'rollback'    # Stop and delete run

def cancel_run(
    client,
    run_id: str,
    action: CancelAction = CancelAction.INTERRUPT,
    reason: Optional[str] = None
) -> dict:
    """
    Cancel run with specified action.

    From run-lifecycle.md (lines 462-594):
    - interrupt: Preserves partial output and run record
    - rollback: Deletes run record and removes messages

    Args:
        client: API client
        run_id: Run to cancel
        action: Cancel action (interrupt or rollback)
        reason: Optional cancellation reason

    Returns:
        Cancelled run details
    """
    try:
        response = client.cancel_run(
            run_id,
            action=action.value,
            reason=reason
        )

        if action == CancelAction.INTERRUPT:
            print(f"Run {run_id} cancelled (preserved)")
            print(f"Partial output: {len(response.get('output', []))} messages")
            print(f"Can retrieve via GET /runs/{run_id}")
        else:  # ROLLBACK
            print(f"Run {run_id} cancelled (deleted)")
            print(f"Run record removed, messages deleted from thread")
            print(f"GET /runs/{run_id} will return 404")

        return response

    except AgentAPIError as e:
        if e.code == 'INVALID_STATE':
            print(f"Cannot cancel run {run_id}: {e.message}")
            print("Run may already be in terminal state (completed, failed, cancelled)")
        else:
            print(f"Cancellation failed: {e.code} - {e.message}")
        raise

# Usage - Cancel long-running generation
def monitor_and_cancel_on_timeout(client, run_id: str, max_duration: int = 30):
    """
    Monitor run and cancel if exceeds max duration.

    Args:
        client: API client
        run_id: Run to monitor
        max_duration: Max duration in seconds
    """
    start_time = time.time()

    while True:
        # Check run status
        run = client.get_run(run_id)

        # Terminal state - done
        if run['status'] in ['completed', 'failed', 'cancelled', 'timeout', 'incomplete']:
            return run

        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > max_duration:
            print(f"Run exceeded {max_duration}s, cancelling...")
            cancel_run(
                client,
                run_id,
                action=CancelAction.INTERRUPT,
                reason=f"Exceeded maximum duration of {max_duration}s"
            )
            # Wait for cancellation to complete
            time.sleep(1)
            return client.get_run(run_id)

        time.sleep(1)

# Usage - User clicks "stop"
def handle_user_stop(client, run_id: str):
    """Handle user clicking stop button"""
    return cancel_run(
        client,
        run_id,
        action=CancelAction.INTERRUPT,
        reason="User clicked stop generation"
    )

# Usage - Cleanup accidental run
def cleanup_accidental_run(client, run_id: str):
    """Remove accidental duplicate run completely"""
    return cancel_run(
        client,
        run_id,
        action=CancelAction.ROLLBACK,
        reason="Accidental duplicate run, cleanup required"
    )
```

**JavaScript/TypeScript:**
```typescript
enum CancelAction {
  INTERRUPT = 'interrupt',
  ROLLBACK = 'rollback'
}

interface CancelRunOptions {
  action?: CancelAction;
  reason?: string;
}

async function cancelRun(
  client: AgentClient,
  runId: string,
  options: CancelRunOptions = {}
): Promise<Run> {
  const { action = CancelAction.INTERRUPT, reason } = options;

  try {
    const response = await client.cancelRun(runId, { action, reason });

    if (action === CancelAction.INTERRUPT) {
      console.log(`Run ${runId} cancelled (preserved)`);
      console.log(`Partial output: ${response.output?.length || 0} messages`);
      console.log(`Can retrieve via GET /runs/${runId}`);
    } else {
      console.log(`Run ${runId} cancelled (deleted)`);
      console.log('Run record removed, messages deleted from thread');
      console.log(`GET /runs/${runId} will return 404`);
    }

    return response;
  } catch (error) {
    if (error instanceof AgentAPIError && error.code === 'INVALID_STATE') {
      console.log(`Cannot cancel run ${runId}: ${error.message}`);
      console.log('Run may already be in terminal state');
    } else {
      console.log(`Cancellation failed: ${error}`);
    }
    throw error;
  }
}

async function monitorAndCancelOnTimeout(
  client: AgentClient,
  runId: string,
  maxDuration: number = 30000
): Promise<Run> {
  const startTime = Date.now();

  while (true) {
    const run = await client.getRun(runId);

    // Terminal state
    if (['completed', 'failed', 'cancelled', 'timeout', 'incomplete'].includes(run.status)) {
      return run;
    }

    // Check timeout
    const elapsed = Date.now() - startTime;
    if (elapsed > maxDuration) {
      console.log(`Run exceeded ${maxDuration}ms, cancelling...`);
      await cancelRun(client, runId, {
        action: CancelAction.INTERRUPT,
        reason: `Exceeded maximum duration of ${maxDuration}ms`
      });
      await sleep(1000);
      return await client.getRun(runId);
    }

    await sleep(1000);
  }
}

// Usage - User clicks "stop"
async function handleUserStop(client: AgentClient, runId: string): Promise<Run> {
  return cancelRun(client, runId, {
    action: CancelAction.INTERRUPT,
    reason: 'User clicked stop generation'
  });
}

// Usage - Cleanup accidental run
async function cleanupAccidentalRun(client: AgentClient, runId: string): Promise<Run> {
  return cancelRun(client, runId, {
    action: CancelAction.ROLLBACK,
    reason: 'Accidental duplicate run, cleanup required'
  });
}
```

### Step 8: Implement Graceful Degradation

Handle partial failures gracefully instead of complete failure:

**Python:**
```python
from typing import List, Dict, Any, Optional

def process_with_degradation(
    client,
    request: Dict[str, Any],
    fallback_models: List[str] = None
) -> Dict[str, Any]:
    """
    Process request with graceful degradation through model fallback.

    Strategy:
    1. Try primary model
    2. On provider error, try fallback models
    3. On context length error, truncate and retry
    4. Return partial results if complete processing fails
    """
    fallback_models = fallback_models or ['gpt-4o-mini', 'gpt-3.5-turbo']
    models = [request.get('agent', {}).get('model')] + fallback_models

    last_error = None

    for i, model in enumerate(models):
        if not model:
            continue

        try:
            # Update model in request
            if 'agent' in request:
                request['agent']['model'] = model

            print(f"Attempting with model: {model}")

            # Try to create run
            run = retry_with_exponential_backoff(
                lambda: client.create_run(request)
            )

            # Wait for completion
            while run['status'] in ['queued', 'in_progress']:
                time.sleep(1)
                run = client.get_run(run['runId'])

            if run['status'] == 'completed':
                if i > 0:
                    print(f"⚠ Degraded: Using fallback model {model}")
                return {
                    **run,
                    'degraded': i > 0,
                    'fallback_model': model if i > 0 else None
                }

            # Handle run failure
            error = run.get('error')
            if error and error['code'] == 'CONTEXT_LENGTH_EXCEEDED':
                # Try with truncated context
                print("Context too long, truncating...")
                request['input'] = truncate_input(request['input'], 0.5)
                continue

            last_error = error

        except AgentAPIError as e:
            last_error = e
            if e.code in ['PROVIDER_ERROR', 'PROVIDER_UNAVAILABLE']:
                print(f"Provider error with {model}, trying fallback...")
                continue
            else:
                # Non-retryable error
                raise

    # All attempts failed - return error response with context
    raise RuntimeError(
        f"All models failed. Last error: {last_error}"
    )

def truncate_input(messages: List[Dict], ratio: float = 0.5) -> List[Dict]:
    """Truncate input messages to reduce context length"""
    if not messages:
        return messages

    # Keep system messages and recent user messages
    system_messages = [m for m in messages if m.get('role') == 'system']
    other_messages = [m for m in messages if m.get('role') != 'system']

    # Keep last N messages based on ratio
    keep_count = max(1, int(len(other_messages) * ratio))
    truncated = other_messages[-keep_count:]

    return system_messages + truncated

def execute_tools_with_degradation(
    tool_calls: List[Dict],
    timeout: int = 30
) -> List[Dict]:
    """
    Execute tools with graceful degradation.

    Returns partial results even if some tools fail.
    """
    results = []

    for tool_call in tool_calls:
        call_id = tool_call['callId']
        tool_name = tool_call['name']
        arguments = tool_call.get('arguments', {})

        try:
            # Execute with timeout
            output = execute_with_timeout(
                lambda: execute_tool(tool_name, arguments),
                timeout=timeout
            )

            results.append({
                'tool_call_id': call_id,
                'output': output,
                'success': True
            })

        except TimeoutError:
            # Tool timed out - return timeout error
            results.append({
                'tool_call_id': call_id,
                'output': json.dumps({
                    'error': 'TOOL_TIMEOUT',
                    'message': f"Tool '{tool_name}' exceeded {timeout}s timeout",
                    'partial': True
                }),
                'success': False
            })

        except Exception as e:
            # Tool failed - return error but continue
            results.append({
                'tool_call_id': call_id,
                'output': json.dumps({
                    'error': 'TOOL_EXECUTION_FAILED',
                    'message': str(e),
                    'partial': True
                }),
                'success': False
            })

    # Log degradation
    failed_count = sum(1 for r in results if not r['success'])
    if failed_count > 0:
        print(f"⚠ Degraded: {failed_count}/{len(results)} tools failed")

    return results

def execute_with_timeout(func: Callable, timeout: int) -> Any:
    """Execute function with timeout"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Function exceeded {timeout}s timeout")

    # Set timeout alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        result = func()
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError:
        signal.alarm(0)  # Cancel alarm
        raise
```

**JavaScript/TypeScript:**
```typescript
interface DegradedResponse extends Run {
  degraded: boolean;
  fallbackModel?: string;
}

async function processWithDegradation(
  client: AgentClient,
  request: CreateRunRequest,
  fallbackModels: string[] = ['gpt-4o-mini', 'gpt-3.5-turbo']
): Promise<DegradedResponse> {
  const models = [request.agent?.model, ...fallbackModels].filter(Boolean);
  let lastError: any;

  for (let i = 0; i < models.length; i++) {
    const model = models[i];

    try {
      // Update model in request
      if (request.agent) {
        request.agent.model = model;
      }

      console.log(`Attempting with model: ${model}`);

      // Try to create run
      let run = await retryWithExponentialBackoff(() => client.createRun(request));

      // Wait for completion
      while (['queued', 'in_progress'].includes(run.status)) {
        await sleep(1000);
        run = await client.getRun(run.runId);
      }

      if (run.status === 'completed') {
        if (i > 0) {
          console.log(`⚠ Degraded: Using fallback model ${model}`);
        }
        return {
          ...run,
          degraded: i > 0,
          fallbackModel: i > 0 ? model : undefined
        };
      }

      // Handle run failure
      if (run.error?.code === 'CONTEXT_LENGTH_EXCEEDED') {
        console.log('Context too long, truncating...');
        request.input = truncateInput(request.input, 0.5);
        continue;
      }

      lastError = run.error;
    } catch (error) {
      lastError = error;
      if (
        error instanceof AgentAPIError &&
        ['PROVIDER_ERROR', 'PROVIDER_UNAVAILABLE'].includes(error.code)
      ) {
        console.log(`Provider error with ${model}, trying fallback...`);
        continue;
      }
      throw error;
    }
  }

  throw new Error(`All models failed. Last error: ${lastError}`);
}

function truncateInput(messages: ChatMessage[], ratio: number = 0.5): ChatMessage[] {
  if (!messages.length) return messages;

  const systemMessages = messages.filter((m) => m.role === 'system');
  const otherMessages = messages.filter((m) => m.role !== 'system');

  const keepCount = Math.max(1, Math.floor(otherMessages.length * ratio));
  const truncated = otherMessages.slice(-keepCount);

  return [...systemMessages, ...truncated];
}

interface ToolResult {
  tool_call_id: string;
  output: string;
  success: boolean;
}

async function executeToolsWithDegradation(
  toolCalls: ToolCall[],
  timeout: number = 30000
): Promise<ToolResult[]> {
  const results = await Promise.all(
    toolCalls.map(async (toolCall) => {
      try {
        const output = await executeWithTimeout(
          () => executeTool(toolCall.name, toolCall.arguments || {}),
          timeout
        );

        return {
          tool_call_id: toolCall.callId,
          output,
          success: true
        };
      } catch (error) {
        if (error instanceof TimeoutError) {
          return {
            tool_call_id: toolCall.callId,
            output: JSON.stringify({
              error: 'TOOL_TIMEOUT',
              message: `Tool '${toolCall.name}' exceeded ${timeout}ms timeout`,
              partial: true
            }),
            success: false
          };
        }

        return {
          tool_call_id: toolCall.callId,
          output: JSON.stringify({
            error: 'TOOL_EXECUTION_FAILED',
            message: String(error),
            partial: true
          }),
          success: false
        };
      }
    })
  );

  const failedCount = results.filter((r) => !r.success).length;
  if (failedCount > 0) {
    console.log(`⚠ Degraded: ${failedCount}/${results.length} tools failed`);
  }

  return results;
}

async function executeWithTimeout<T>(func: () => Promise<T>, timeout: number): Promise<T> {
  return Promise.race([
    func(),
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new TimeoutError(`Function exceeded ${timeout}ms timeout`)), timeout)
    )
  ]);
}

class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TimeoutError';
  }
}
```

---

## Examples

### Example 1: Complete Resilient Client

Full-featured client with all error handling patterns:

**Python:**
```python
import requests
import time
import random
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ClientConfig:
    """Configuration for resilient client"""
    base_url: str
    api_key: str
    max_retries: int = 3
    base_delay: float = 0.1
    max_delay: float = 0.4
    request_timeout: int = 30
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 3
    circuit_breaker_timeout: int = 60

class ResilientAgentClient:
    """
    Production-ready agent client with comprehensive error handling.

    Features:
    - Exponential backoff retry
    - Rate limit handling
    - Circuit breaker for tool calls
    - Graceful degradation
    - Run failure handling
    - Cancellation support
    - Structured logging
    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })

        # Circuit breakers for external services
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def _get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name,
                CircuitBreakerConfig(
                    failure_threshold=self.config.circuit_breaker_threshold,
                    timeout=self.config.circuit_breaker_timeout
                )
            )
        return self.circuit_breakers[name]

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.config.base_url}{path}"

        def make_request():
            response = self.session.request(
                method,
                url,
                timeout=self.config.request_timeout,
                **kwargs
            )

            if not response.ok:
                error = parse_error_response(response)
                raise error

            return response.json()

        # Handle rate limits specially
        try:
            return retry_with_exponential_backoff(
                make_request,
                max_retries=self.config.max_retries,
                base_delay=self.config.base_delay,
                max_delay=self.config.max_delay
            )
        except RateLimitError as e:
            print(f"Rate limited. Waiting {e.retry_after}s...")
            time.sleep(e.retry_after)
            return make_request()

    def create_run(
        self,
        agent_id: str,
        input_messages: List[Dict],
        thread_id: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create run with error handling"""
        request_data = {
            'agentId': agent_id,
            'input': input_messages
        }

        if thread_id:
            request_data['threadId'] = thread_id
        if options:
            request_data['options'] = options

        return self._request('POST', '/runs', json=request_data)

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run status"""
        return self._request('GET', f'/runs/{run_id}')

    def cancel_run(
        self,
        run_id: str,
        action: str = 'interrupt',
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel run"""
        request_data = {'action': action}
        if reason:
            request_data['reason'] = reason

        return self._request('POST', f'/runs/{run_id}/cancel', json=request_data)

    def submit_tool_outputs(
        self,
        run_id: str,
        tool_outputs: List[Dict]
    ) -> Dict[str, Any]:
        """Submit tool outputs"""
        return self._request(
            'POST',
            f'/runs/{run_id}/submit_tool_outputs',
            json={'tool_outputs': tool_outputs}
        )

    def wait_for_run(
        self,
        run_id: str,
        poll_interval: float = 1.0,
        max_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Wait for run to complete with timeout and cancellation.

        Args:
            run_id: Run to wait for
            poll_interval: Seconds between polls
            max_duration: Max seconds to wait (None = no limit)

        Returns:
            Completed run
        """
        start_time = time.time()

        while True:
            run = self.get_run(run_id)

            # Check terminal states
            if run['status'] in ['completed', 'failed', 'cancelled', 'timeout', 'incomplete']:
                if run['status'] != 'completed':
                    handle_run_failure(run)
                return run

            # Check timeout
            if max_duration:
                elapsed = time.time() - start_time
                if elapsed > max_duration:
                    print(f"Run exceeded {max_duration}s, cancelling...")
                    self.cancel_run(
                        run_id,
                        action='interrupt',
                        reason=f"Exceeded maximum duration of {max_duration}s"
                    )
                    time.sleep(poll_interval)
                    return self.get_run(run_id)

            time.sleep(poll_interval)

    def execute_tool_with_circuit_breaker(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """Execute tool with circuit breaker protection"""
        if not self.config.enable_circuit_breaker:
            return execute_tool(tool_name, arguments)

        breaker = self._get_circuit_breaker(f"tool_{tool_name}")

        try:
            return breaker.call(lambda: execute_tool(tool_name, arguments))
        except CircuitBreakerOpenError as e:
            # Circuit open - return fallback
            return json.dumps({
                'error': 'SERVICE_UNAVAILABLE',
                'message': f"Tool '{tool_name}' temporarily unavailable",
                'details': str(e)
            })

    def create_run_with_degradation(
        self,
        request: Dict[str, Any],
        fallback_models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create run with model fallback on provider errors.

        Implements graceful degradation through model fallback.
        """
        fallback_models = fallback_models or ['gpt-4o-mini', 'gpt-3.5-turbo']
        original_model = request.get('agent', {}).get('model')
        models = [original_model] + fallback_models

        last_error = None

        for i, model in enumerate(models):
            if not model:
                continue

            try:
                # Update model
                if 'agent' not in request:
                    request['agent'] = {}
                request['agent']['model'] = model

                print(f"Attempting with model: {model}")

                # Create run
                run = self.create_run(**request)

                # Wait for completion
                run = self.wait_for_run(run['runId'])

                if run['status'] == 'completed':
                    if i > 0:
                        print(f"⚠ Degraded: Using fallback model {model}")
                        run['degraded'] = True
                        run['fallback_model'] = model
                    return run

                # Handle failure
                error = run.get('error', {})
                if error.get('code') == 'CONTEXT_LENGTH_EXCEEDED':
                    # Truncate and retry
                    request['input'] = truncate_input(request['input'], 0.5)
                    continue

                last_error = error

            except AgentAPIError as e:
                last_error = e
                if e.code in ['PROVIDER_ERROR', 'PROVIDER_UNAVAILABLE']:
                    print(f"Provider error with {model}, trying fallback...")
                    continue
                raise

        raise RuntimeError(f"All models failed. Last error: {last_error}")

    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get stats for all circuit breakers"""
        return {
            name: breaker.get_state()
            for name, breaker in self.circuit_breakers.items()
        }

# Usage
config = ClientConfig(
    base_url='https://agents.example.com/v1',
    api_key='your-api-key',
    max_retries=3,
    enable_circuit_breaker=True
)

client = ResilientAgentClient(config)

try:
    # Create run with automatic retries, rate limit handling, and degradation
    run = client.create_run_with_degradation({
        'agentId': 'agent_123',
        'input': [
            {
                'role': 'user',
                'contents': [{'kind': 'text', 'text': 'Analyze this data...'}]
            }
        ],
        'agent': {'model': 'gpt-4o'}
    }, fallback_models=['gpt-4o-mini', 'gpt-3.5-turbo'])

    print(f"Run completed: {run['runId']}")
    print(f"Output: {len(run['output'])} messages")

    if run.get('degraded'):
        print(f"⚠ Used fallback model: {run['fallback_model']}")

    # Check circuit breaker stats
    stats = client.get_circuit_breaker_stats()
    print(f"Circuit breaker stats: {json.dumps(stats, indent=2)}")

except AgentAPIError as e:
    print(f"API Error: {e.code} - {e.message}")
    if e.details:
        print(f"Details: {json.dumps(e.details, indent=2)}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Example 2: Streaming with Error Recovery

Handle streaming responses with error recovery:

**Python:**
```python
import json
from typing import Iterator, Dict, Any

def stream_run_with_retry(
    client,
    request: Dict[str, Any],
    max_retries: int = 3
) -> Iterator[Dict[str, Any]]:
    """
    Stream run with automatic reconnection on network errors.

    Yields:
        Streaming events
    """
    retry_count = 0
    last_event_id = None

    while retry_count <= max_retries:
        try:
            # Add last event ID for resume
            params = {'stream': 'true'}
            if last_event_id:
                params['lastEventId'] = last_event_id
                print(f"Resuming stream from event {last_event_id}")

            response = client.session.post(
                f"{client.config.base_url}/runs",
                json=request,
                params=params,
                stream=True,
                timeout=None
            )

            if not response.ok:
                error = parse_error_response(response)
                raise error

            # Parse SSE stream
            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode('utf-8')

                # Parse SSE format
                if line.startswith('data: '):
                    data = line[6:]

                    if data == '[DONE]':
                        return

                    try:
                        event = json.loads(data)
                        last_event_id = event.get('eventId')
                        yield event
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse event: {e}")
                        continue

            # Stream completed successfully
            return

        except (requests.ConnectionError, requests.Timeout) as e:
            retry_count += 1
            if retry_count > max_retries:
                raise RuntimeError(f"Stream failed after {max_retries} retries: {e}")

            print(f"Stream connection lost, retrying ({retry_count}/{max_retries})...")
            time.sleep(2 ** retry_count)

        except AgentAPIError as e:
            # Don't retry client errors
            if not is_retryable(e):
                raise

            retry_count += 1
            if retry_count > max_retries:
                raise

            print(f"Stream error: {e.code}, retrying ({retry_count}/{max_retries})...")
            time.sleep(2 ** retry_count)

# Usage
client = ResilientAgentClient(config)

try:
    for event in stream_run_with_retry(client, {
        'agentId': 'agent_123',
        'input': [
            {
                'role': 'user',
                'contents': [{'kind': 'text', 'text': 'Tell me a story'}]
            }
        ]
    }):
        event_type = event.get('type')

        if event_type == 'content.updated':
            # Print streaming text
            for content in event.get('content', {}).get('contents', []):
                if content.get('kind') == 'text':
                    print(content.get('text', ''), end='', flush=True)

        elif event_type == 'run.completed':
            print("\n\n✓ Run completed")

        elif event_type == 'run.failed':
            error = event.get('error', {})
            print(f"\n\n✗ Run failed: {error.get('code')} - {error.get('message')}")

except Exception as e:
    print(f"\n\nStream error: {e}")
```

### Example 3: Multi-Agent with Error Handling

Handle errors in multi-agent orchestration:

**Python:**
```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AgentHandoff:
    """Represents a handoff to another agent"""
    target_agent_id: str
    reason: str
    context: Dict[str, Any]

def execute_multi_agent_workflow(
    client: ResilientAgentClient,
    initial_agent_id: str,
    user_input: str,
    max_handoffs: int = 5
) -> Dict[str, Any]:
    """
    Execute multi-agent workflow with handoff error handling.

    Handles:
    - Agent unavailability (fallback to general agent)
    - Handoff failures (retry with backoff)
    - Circular handoffs (detect and break)
    - Max handoff limit
    """
    thread_id = None
    current_agent_id = initial_agent_id
    handoff_count = 0
    agent_history = [initial_agent_id]

    input_messages = [
        {
            'role': 'user',
            'contents': [{'kind': 'text', 'text': user_input}]
        }
    ]

    while handoff_count < max_handoffs:
        print(f"\n{'='*60}")
        print(f"Agent: {current_agent_id} (Handoff {handoff_count}/{max_handoffs})")
        print(f"{'='*60}")

        try:
            # Create run with current agent
            run = client.create_run(
                agent_id=current_agent_id,
                input_messages=input_messages,
                thread_id=thread_id
            )

            thread_id = run.get('threadId')

            # Wait for completion
            run = client.wait_for_run(run['runId'], max_duration=60)

            # Check for handoff in output
            handoff = extract_handoff_from_output(run['output'])

            if not handoff:
                # No handoff - workflow complete
                print(f"\n✓ Workflow completed with {current_agent_id}")
                return run

            # Detect circular handoff
            if handoff.target_agent_id in agent_history:
                print(f"\n⚠ Circular handoff detected: {' → '.join(agent_history)} → {handoff.target_agent_id}")
                print("Breaking loop and returning current result")
                return run

            # Prepare for handoff
            handoff_count += 1
            current_agent_id = handoff.target_agent_id
            agent_history.append(current_agent_id)

            print(f"\n→ Handoff to {current_agent_id}: {handoff.reason}")

            # Prepare input for next agent (include context)
            input_messages = [
                {
                    'role': 'user',
                    'contents': [
                        {
                            'kind': 'text',
                            'text': f"[Handoff from {agent_history[-2]}]\n{handoff.reason}\n\nContext: {json.dumps(handoff.context)}"
                        }
                    ]
                }
            ]

        except AgentAPIError as e:
            if e.code == 'AGENT_NOT_FOUND':
                # Target agent unavailable - fallback
                print(f"\n⚠ Agent {current_agent_id} not found, falling back to general agent")
                current_agent_id = 'general_agent'
                continue

            elif e.code == 'RATE_LIMIT_EXCEEDED':
                # Rate limited - wait and retry
                print(f"\n⚠ Rate limited, waiting {e.retry_after}s...")
                time.sleep(e.retry_after)
                continue

            else:
                # Unrecoverable error
                print(f"\n✗ Workflow failed: {e.code} - {e.message}")
                raise

        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            raise

    # Max handoffs reached
    print(f"\n⚠ Max handoffs ({max_handoffs}) reached")
    print(f"Agent chain: {' → '.join(agent_history)}")
    raise RuntimeError("Max handoff limit exceeded")

def extract_handoff_from_output(output: List[Dict]) -> Optional[AgentHandoff]:
    """Extract handoff instruction from agent output"""
    for message in output:
        for content in message.get('contents', []):
            if content.get('kind') == 'handoff':
                return AgentHandoff(
                    target_agent_id=content['targetAgentId'],
                    reason=content.get('reason', 'No reason provided'),
                    context=content.get('context', {})
                )
    return None

# Usage
client = ResilientAgentClient(config)

try:
    result = execute_multi_agent_workflow(
        client,
        initial_agent_id='triage_agent',
        user_input='I need help with my billing issue',
        max_handoffs=5
    )

    print(f"\nFinal output:")
    for message in result['output']:
        for content in message.get('contents', []):
            if content.get('kind') == 'text':
                print(content['text'])

except Exception as e:
    print(f"Workflow error: {e}")
```

### Example 4: Error Monitoring Dashboard

Monitor and alert on error patterns:

**Python:**
```python
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Deque

@dataclass
class ErrorMetrics:
    """Track error metrics over time"""
    total_requests: int = 0
    total_errors: int = 0
    errors_by_code: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    recent_errors: Deque = field(default_factory=lambda: deque(maxlen=100))

    def record_request(self):
        """Record successful request"""
        self.total_requests += 1

    def record_error(self, error: AgentAPIError):
        """Record error"""
        self.total_requests += 1
        self.total_errors += 1
        self.errors_by_code[error.code] += 1
        self.errors_by_status[error.status_code] += 1
        self.recent_errors.append({
            'timestamp': datetime.now(),
            'code': error.code,
            'message': error.message,
            'status': error.status_code
        })

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.total_errors / self.total_requests

    def get_recent_error_rate(self, minutes: int = 5) -> float:
        """Calculate error rate for recent window"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [e for e in self.recent_errors if e['timestamp'] > cutoff]

        if len(self.recent_errors) == 0:
            return 0.0

        return len(recent) / len(self.recent_errors)

    def get_top_errors(self, limit: int = 5) -> List[tuple]:
        """Get most common error codes"""
        return sorted(
            self.errors_by_code.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    def should_alert(self, threshold: float = 0.1) -> bool:
        """Check if error rate exceeds threshold"""
        return self.get_error_rate() > threshold

    def to_dict(self) -> Dict:
        """Export metrics as dict"""
        return {
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'error_rate': self.get_error_rate(),
            'recent_error_rate_5m': self.get_recent_error_rate(5),
            'errors_by_code': dict(self.errors_by_code),
            'errors_by_status': dict(self.errors_by_status),
            'top_errors': self.get_top_errors()
        }

class MonitoredAgentClient(ResilientAgentClient):
    """Agent client with error monitoring"""

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.metrics = ErrorMetrics()

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Override request to record metrics"""
        try:
            result = super()._request(method, path, **kwargs)
            self.metrics.record_request()
            return result
        except AgentAPIError as e:
            self.metrics.record_error(e)

            # Check if alert threshold exceeded
            if self.metrics.should_alert(threshold=0.1):
                self._send_alert(
                    f"Error rate exceeded 10%: {self.metrics.get_error_rate():.1%}"
                )

            raise

    def _send_alert(self, message: str):
        """Send alert notification"""
        print(f"\n{'!'*60}")
        print(f"ALERT: {message}")
        print(f"{'!'*60}")
        print(f"Recent errors: {len(self.metrics.recent_errors)}")
        print(f"Top errors:")
        for code, count in self.metrics.get_top_errors():
            print(f"  - {code}: {count}")
        print(f"{'!'*60}\n")

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics.to_dict()

    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = ErrorMetrics()

# Usage - Monitor errors over time
client = MonitoredAgentClient(config)

# Simulate requests
for i in range(100):
    try:
        run = client.create_run(
            agent_id='agent_123',
            input_messages=[
                {
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': f'Request {i}'}]
                }
            ]
        )
        print(f"Request {i}: Success")
    except AgentAPIError as e:
        print(f"Request {i}: Error - {e.code}")

    time.sleep(0.1)

# Print final metrics
metrics = client.get_metrics()
print(f"\n{'='*60}")
print("Final Metrics")
print(f"{'='*60}")
print(f"Total requests: {metrics['total_requests']}")
print(f"Total errors: {metrics['total_errors']}")
print(f"Error rate: {metrics['error_rate']:.1%}")
print(f"Recent error rate (5m): {metrics['recent_error_rate_5m']:.1%}")
print(f"\nTop errors:")
for code, count in metrics['top_errors']:
    print(f"  - {code}: {count}")
print(f"\nErrors by status:")
for status, count in metrics['errors_by_status'].items():
    print(f"  - {status}: {count}")
```

---

## Troubleshooting

### Issue 1: Requests Timing Out

**Symptoms:**
- Requests consistently timeout after 30 seconds
- `TIMEOUT` errors in logs
- Run status stuck in `in_progress`

**Causes:**
1. Model taking longer than expected to generate
2. Large context exceeding processing time
3. Network latency
4. Tool execution taking too long

**Solutions:**

```python
# Solution 1: Increase request timeout
config = ClientConfig(
    base_url='https://agents.example.com/v1',
    api_key='your-api-key',
    request_timeout=120  # Increase from 30s to 120s
)

# Solution 2: Use streaming to avoid timeout
def create_run_streaming(client, request):
    """Use streaming to avoid timeout on long responses"""
    for event in stream_run_with_retry(client, request):
        if event.get('type') == 'run.completed':
            return event.get('run')
    raise RuntimeError("Stream ended without completion")

# Solution 3: Monitor and cancel long-running runs
def create_run_with_timeout_cancel(client, request, max_duration=60):
    """Create run and cancel if exceeds max duration"""
    run = client.create_run(**request)

    try:
        return client.wait_for_run(
            run['runId'],
            max_duration=max_duration
        )
    except RuntimeError as e:
        if "exceeded" in str(e):
            print(f"Run timed out, cancelled: {e}")
            return client.get_run(run['runId'])
        raise
```

### Issue 2: Rate Limit Errors

**Symptoms:**
- `RATE_LIMIT_EXCEEDED` errors
- 429 HTTP status codes
- Intermittent failures during peak usage

**Causes:**
1. Too many concurrent requests
2. Burst traffic exceeding rate limit
3. Not respecting `Retry-After` header

**Solutions:**

```python
# Solution 1: Implement request throttling
from threading import Semaphore
import threading

class ThrottledClient(ResilientAgentClient):
    """Client with request throttling"""

    def __init__(self, config: ClientConfig, max_concurrent: int = 10):
        super().__init__(config)
        self.semaphore = Semaphore(max_concurrent)
        self.request_times = deque(maxlen=100)

    def _request(self, method: str, path: str, **kwargs):
        """Throttled request"""
        # Wait for semaphore
        with self.semaphore:
            # Track request rate
            now = time.time()
            self.request_times.append(now)

            # Check if exceeding rate (100 req/min)
            recent = [t for t in self.request_times if now - t < 60]
            if len(recent) >= 100:
                sleep_time = 60 - (now - recent[0])
                print(f"Rate limit approaching, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

            return super()._request(method, path, **kwargs)

# Solution 2: Adaptive backoff on rate limits
def create_run_with_adaptive_retry(client, request):
    """Retry with adaptive backoff on rate limits"""
    backoff = 1
    max_backoff = 120

    while True:
        try:
            return client.create_run(**request)
        except RateLimitError as e:
            wait_time = min(e.retry_after, max_backoff)
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            backoff = min(backoff * 2, max_backoff)
        except AgentAPIError as e:
            if e.status_code != 429:
                raise
            # Fallback if no Retry-After header
            print(f"Rate limited (no header), waiting {backoff}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
```

### Issue 3: Circuit Breaker Stuck Open

**Symptoms:**
- Circuit breaker remains in OPEN state
- Fast-fail errors even after service recovers
- `CircuitBreakerOpenError` exceptions

**Causes:**
1. Timeout too long (service recovers before half-open)
2. Success threshold too high
3. Service is genuinely down

**Solutions:**

```python
# Solution 1: Adjust circuit breaker config
breaker = CircuitBreaker(
    'api',
    CircuitBreakerConfig(
        failure_threshold=3,
        timeout=30,  # Reduce from 60s to 30s
        success_threshold=1  # Lower threshold
    )
)

# Solution 2: Manual circuit breaker reset
def reset_circuit_breaker(client, service_name: str):
    """Manually reset circuit breaker"""
    if service_name in client.circuit_breakers:
        breaker = client.circuit_breakers[service_name]
        breaker.state = CircuitState.CLOSED
        breaker.failure_count = 0
        breaker.last_failure_time = None
        print(f"Circuit breaker '{service_name}' manually reset to CLOSED")

# Solution 3: Monitor and alert on circuit state
def monitor_circuit_breakers(client):
    """Monitor circuit breaker health"""
    while True:
        stats = client.get_circuit_breaker_stats()

        for name, state in stats.items():
            if state['state'] == 'open':
                print(f"⚠ Circuit '{name}' is OPEN")
                print(f"  Failure count: {state['failure_count']}")
                print(f"  Time until retry: {state['time_until_retry']}s")

                # Alert if open for too long
                if state['time_until_retry'] == 0:
                    print(f"  Testing recovery...")

        time.sleep(10)
```

### Issue 4: Tool Execution Failures

**Symptoms:**
- `TOOL_EXECUTION_FAILED` errors
- Runs failing in `requires_action` state
- Partial tool results

**Causes:**
1. Tool timeout
2. Invalid tool arguments
3. External API unavailable
4. Network issues

**Solutions:**

```python
# Solution 1: Implement tool retry with timeout increase
def execute_tool_with_progressive_timeout(tool_name, arguments):
    """Execute tool with increasing timeout on failure"""
    timeouts = [5, 10, 30]  # Progressive timeouts

    for timeout in timeouts:
        try:
            return execute_with_timeout(
                lambda: execute_tool(tool_name, arguments),
                timeout=timeout
            )
        except TimeoutError:
            if timeout == timeouts[-1]:
                raise
            print(f"Tool timeout at {timeout}s, retrying with {timeouts[timeouts.index(timeout) + 1]}s...")

# Solution 2: Validate tool arguments before execution
def validate_and_execute_tool(tool_name, arguments, schema):
    """Validate arguments against schema before execution"""
    try:
        # Validate against JSON schema
        jsonschema.validate(arguments, schema)
    except jsonschema.ValidationError as e:
        return json.dumps({
            'error': 'TOOL_ARGUMENT_INVALID',
            'message': f"Invalid arguments: {e.message}",
            'path': list(e.path)
        })

    # Execute tool
    return execute_tool(tool_name, arguments)

# Solution 3: Implement tool fallback chain
def execute_tool_with_fallback(tool_name, arguments, fallback_tools=None):
    """Execute tool with fallback alternatives"""
    tools = [tool_name] + (fallback_tools or [])

    for tool in tools:
        try:
            result = execute_tool(tool, arguments)
            if tool != tool_name:
                print(f"⚠ Used fallback tool: {tool}")
            return result
        except Exception as e:
            if tool == tools[-1]:
                raise
            print(f"Tool '{tool}' failed: {e}, trying fallback...")

    raise RuntimeError("All tools failed")
```

### Issue 5: Memory Leaks in Long-Running Clients

**Symptoms:**
- Memory usage grows over time
- Client becomes slow after many requests
- Out of memory errors

**Causes:**
1. Circuit breaker history not cleaned
2. Metrics accumulating indefinitely
3. Session not closed properly

**Solutions:**

```python
# Solution 1: Periodic cleanup
class CleanupClient(ResilientAgentClient):
    """Client with automatic cleanup"""

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.request_count = 0
        self.cleanup_interval = 1000

    def _request(self, method: str, path: str, **kwargs):
        result = super()._request(method, path, **kwargs)

        self.request_count += 1
        if self.request_count % self.cleanup_interval == 0:
            self._cleanup()

        return result

    def _cleanup(self):
        """Periodic cleanup"""
        print("Running cleanup...")

        # Reset circuit breakers in CLOSED state
        for name, breaker in list(self.circuit_breakers.items()):
            if breaker.state == CircuitState.CLOSED:
                breaker.failure_count = 0

        # Reset metrics if needed
        if hasattr(self, 'metrics'):
            if self.metrics.total_requests > 10000:
                self.metrics = ErrorMetrics()

        print(f"Cleanup complete (requests: {self.request_count})")

# Solution 2: Context manager for client lifecycle
from contextlib import contextmanager

@contextmanager
def agent_client(config: ClientConfig):
    """Context manager for client lifecycle"""
    client = ResilientAgentClient(config)
    try:
        yield client
    finally:
        # Cleanup
        client.session.close()
        client.circuit_breakers.clear()

# Usage
with agent_client(config) as client:
    run = client.create_run(
        agent_id='agent_123',
        input_messages=[...]
    )
# Client automatically cleaned up
```

### Issue 6: Inconsistent Error Codes

**Symptoms:**
- Different error codes for same failure
- Difficulty classifying errors
- Retry logic not triggering

**Causes:**
1. Provider returns different error formats
2. Network errors not normalized
3. Custom error codes not documented

**Solutions:**

```python
# Solution 1: Normalize error codes
def normalize_error_code(error: AgentAPIError) -> str:
    """Normalize error codes across providers"""
    # Map provider-specific codes to standard codes
    code_mapping = {
        # OpenAI codes
        'context_length_exceeded': 'CONTEXT_LENGTH_EXCEEDED',
        'rate_limit': 'RATE_LIMIT_EXCEEDED',
        'invalid_api_key': 'AUTH_REQUIRED',

        # Anthropic codes
        'overloaded_error': 'PROVIDER_UNAVAILABLE',
        'invalid_request_error': 'INVALID_INPUT',

        # Network errors
        'connection_error': 'SERVICE_UNAVAILABLE',
        'timeout_error': 'TIMEOUT'
    }

    return code_mapping.get(error.code.lower(), error.code)

# Solution 2: Error code classification
class ErrorClassifier:
    """Classify errors by type"""

    CLIENT_ERRORS = {
        'INVALID_INPUT', 'VALIDATION_FAILED', 'REQUIRED_FIELD_MISSING',
        'INVALID_FIELD_TYPE', 'INVALID_ENUM_VALUE', 'INVALID_FORMAT',
        'SCHEMA_VALIDATION_FAILED', 'TEXT_TOO_LONG', 'IMAGE_TOO_LARGE'
    }

    AUTH_ERRORS = {
        'AUTH_REQUIRED', 'INVALID_TOKEN', 'TOKEN_EXPIRED',
        'PERMISSION_DENIED', 'INSUFFICIENT_SCOPES', 'CONSENT_DENIED'
    }

    RETRYABLE_ERRORS = {
        'RATE_LIMIT_EXCEEDED', 'TOKEN_EXPIRED', 'PROVIDER_ERROR',
        'PROVIDER_UNAVAILABLE', 'SERVICE_UNAVAILABLE', 'TIMEOUT',
        'INTERNAL_ERROR', 'TOOL_TIMEOUT'
    }

    @classmethod
    def is_client_error(cls, code: str) -> bool:
        return code in cls.CLIENT_ERRORS

    @classmethod
    def is_auth_error(cls, code: str) -> bool:
        return code in cls.AUTH_ERRORS

    @classmethod
    def is_retryable(cls, code: str) -> bool:
        return code in cls.RETRYABLE_ERRORS

    @classmethod
    def get_user_message(cls, code: str) -> str:
        """Get user-friendly error message"""
        messages = {
            'INVALID_INPUT': 'Please check your input and try again.',
            'AUTH_REQUIRED': 'Please sign in to continue.',
            'RATE_LIMIT_EXCEEDED': 'Too many requests. Please wait a moment and try again.',
            'PROVIDER_ERROR': 'Service temporarily unavailable. Please try again.',
            'CONTEXT_LENGTH_EXCEEDED': 'Your request is too long. Please shorten it and try again.'
        }
        return messages.get(code, 'An error occurred. Please try again.')
```

---

## Best Practices

### 1. Always Implement Retry Logic

**DO:**
```python
# Wrap all API calls with retry logic
run = retry_with_exponential_backoff(
    lambda: client.create_run(request),
    max_retries=3
)
```

**DON'T:**
```python
# Direct call without retry
run = client.create_run(request)  # Fails on transient errors
```

### 2. Respect Rate Limits

**DO:**
```python
# Check Retry-After header and wait
except RateLimitError as e:
    time.sleep(e.retry_after)
    retry()
```

**DON'T:**
```python
# Ignore rate limits and retry immediately
except RateLimitError:
    retry()  # Will hit rate limit again
```

### 3. Use Circuit Breakers for External Services

**DO:**
```python
# Protect external tool calls with circuit breaker
breaker = CircuitBreaker('weather_api')
result = breaker.call(lambda: call_weather_api(city))
```

**DON'T:**
```python
# Call external service without protection
result = call_weather_api(city)  # Can cause cascade failures
```

### 4. Log Errors with Context

**DO:**
```python
# Structured logging with context
logging.error(json.dumps({
    'error_code': e.code,
    'error_message': e.message,
    'run_id': run_id,
    'thread_id': thread_id,
    'timestamp': time.time(),
    'details': e.details
}))
```

**DON'T:**
```python
# Generic logging without context
logging.error(f"Error: {e}")  # Hard to debug
```

### 5. Implement Graceful Degradation

**DO:**
```python
# Try primary model, fall back to smaller model
try:
    run = create_run(model='gpt-4o')
except ProviderError:
    run = create_run(model='gpt-3.5-turbo')
    run['degraded'] = True
```

**DON'T:**
```python
# Fail completely on provider error
run = create_run(model='gpt-4o')  # No fallback
```

### 6. Cancel Long-Running Runs

**DO:**
```python
# Monitor and cancel if exceeds timeout
run = create_run(request)
run = wait_for_run(run_id, max_duration=60)
```

**DON'T:**
```python
# Wait indefinitely
run = create_run(request)
while run['status'] != 'completed':
    time.sleep(1)  # Could wait forever
```

### 7. Handle Partial Tool Failures

**DO:**
```python
# Submit all tool results, even errors
tool_outputs = []
for tool_call in tool_calls:
    try:
        output = execute_tool(tool_call)
    except Exception as e:
        output = json.dumps({'error': str(e)})
    tool_outputs.append({'tool_call_id': tool_call.id, 'output': output})
```

**DON'T:**
```python
# Stop on first tool failure
for tool_call in tool_calls:
    output = execute_tool(tool_call)  # Fails on first error
```

### 8. Monitor Error Rates

**DO:**
```python
# Track and alert on error rate
metrics.record_error(error)
if metrics.error_rate() > 0.1:
    send_alert("Error rate exceeded 10%")
```

**DON'T:**
```python
# Ignore error patterns
try:
    run = create_run(request)
except Exception:
    pass  # Silent failures accumulate
```

### 9. Validate Before Sending

**DO:**
```python
# Validate input before API call
if len(messages) > 100:
    raise ValueError("Too many messages")
run = create_run(messages)
```

**DON'T:**
```python
# Let server validate (wastes round-trip)
run = create_run(messages)  # Server returns 400
```

### 10. Use Timeouts Everywhere

**DO:**
```python
# Set timeout on all operations
response = requests.post(url, json=data, timeout=30)
run = wait_for_run(run_id, max_duration=60)
```

**DON'T:**
```python
# No timeouts (can hang forever)
response = requests.post(url, json=data)
run = wait_for_run(run_id)
```

---

## Related Documentation

- **Error Handling Specification**: `../specifications/error-handling.md` - Error codes, retry strategies, fallback behavior
- **Run Lifecycle Specification**: `../specifications/run-lifecycle.md` - Run states, transitions, cancellation
- **Tool Execution Specification**: `../specifications/tool-execution.md` - Tool error handling, timeout behavior
- **Streaming Specification**: `../specifications/streaming.md` - Streaming error recovery
- **TypeSpec Models**: `../typespec/execution.tsp` - RunStatus, RunError, CancelAction enums

---

## Summary

This guide covered comprehensive error handling strategies for production agent integrations:

1. **Error Classification**: Distinguish client (4xx) vs server (5xx) errors
2. **Retry Strategies**: Exponential backoff with jitter for transient failures
3. **Rate Limit Handling**: Respect Retry-After headers and implement throttling
4. **Run Failure Handling**: Handle failed, incomplete, timeout, cancelled states
5. **Tool Error Recovery**: Graceful fallback for tool execution failures
6. **Circuit Breakers**: Prevent cascade failures from external services
7. **Cancellation Patterns**: Interrupt vs rollback modes
8. **Graceful Degradation**: Fallback models and partial results
9. **Error Monitoring**: Track metrics, alert on thresholds
10. **Best Practices**: Always retry, respect limits, log with context

**Key Takeaways:**

- **Retry transient errors** (5xx, 429) with exponential backoff
- **Don't retry client errors** (4xx) without fixing the request
- **Use circuit breakers** to protect external services
- **Implement graceful degradation** instead of complete failures
- **Monitor error rates** and alert on anomalies
- **Cancel long-running operations** to prevent resource exhaustion
- **Handle partial failures** gracefully (tool execution, multi-agent)

With these patterns, your agent integration will be resilient, observable, and production-ready.
