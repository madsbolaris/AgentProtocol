# Troubleshooting Guide

**Version**: 1.0

This guide helps you diagnose and resolve common issues when working with the Agent Runtime API.

---

## Quick Diagnostics

!!! tip "Start Here"

    Before diving into specific issues, run these quick checks:

**1. Verify API Connectivity**
```bash
curl -I https://your-api-endpoint.com/health
```

**2. Check Authentication**
```python
import requests

response = requests.get(
    f"{API_BASE}/agents",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
print(f"Status: {response.status_code}")
```

**3. Validate Request Format**
```python
# Ensure proper JSON structure
import json
payload = {"agent": {...}, "messages": [...]}
print(json.dumps(payload, indent=2))  # Should not raise exception
```

**4. Check API Status**
Visit your API provider's status page or check for service announcements.

---

## Common Issues

### Issue 1: 401 Unauthorized

!!! danger "Authentication Failed"

    **Problem**: API returns 401 status code

**Symptoms:**
- All API requests fail immediately
- Error message: "Unauthorized" or "Invalid API key"
- No response data returned

**Solutions:**

```python
# Check API key is properly set
print(f"API Key: {API_KEY[:10]}...")  # First 10 chars

# Check headers
print(headers)

# Try with explicit auth
response = requests.post(
    f"{API_BASE}/runs",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={...}
)
```

**Common Causes:**
- API key not set in environment variables
- Incorrect header format (missing "Bearer" prefix)
- Expired or revoked API key
- API key copied with extra whitespace

**Prevention:**
```python
# Load API key safely
import os
API_KEY = os.getenv("AGENT_API_KEY", "").strip()
if not API_KEY:
    raise ValueError("AGENT_API_KEY environment variable not set")
```

---

### Issue 2: 429 Rate Limited

!!! warning "Too Many Requests"

    **Problem**: API returns 429 status code

**Symptoms:**
- Intermittent failures during high-volume operations
- Error message: "Rate limit exceeded"
- `Retry-After` header present in response

**Solutions:**

```python
# Implement backoff
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request

# Or use exponential backoff (see Example 1)
```

**Advanced Rate Limiting Handler:**

```python
import time
from functools import wraps

def with_retry(max_retries=3, base_delay=1):
    """Decorator for automatic retry with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                response = func(*args, **kwargs)

                if response.status_code != 429:
                    return response

                if attempt < max_retries - 1:
                    # Exponential backoff
                    delay = base_delay * (2 ** attempt)
                    retry_after = int(response.headers.get('Retry-After', delay))
                    print(f"Rate limited. Retrying in {retry_after}s...")
                    time.sleep(retry_after)
                else:
                    raise Exception(f"Max retries ({max_retries}) exceeded")

            return response
        return wrapper
    return decorator

# Usage
@with_retry(max_retries=5, base_delay=2)
def create_run(payload):
    return requests.post(f"{API_BASE}/runs", headers=headers, json=payload)
```

**Prevention:**
- Implement request queuing
- Use batch operations where available
- Cache responses when appropriate
- Monitor your rate limit usage

---

### Issue 3: Run Stuck in `in_progress`

!!! warning "Common Issue"

    **Problem**: Run never completes and stays in `in_progress` status indefinitely

**Symptoms:**
- Run status remains `in_progress` for extended period
- No error messages
- Polling continues without completion
- No timeout mechanism in place

**Solutions:**

```python
import time

def wait_for_completion(run_id: str, timeout: int = 300):
    """Poll run until completion"""
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(
            f"{API_BASE}/runs/{run_id}",
            headers=headers
        )
        result = response.json()

        if result['status'] in ['completed', 'failed', 'cancelled']:
            return result

        print(f"Status: {result['status']} (elapsed: {time.time() - start:.1f}s)")
        time.sleep(2)

    raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")

# Usage
result = wait_for_completion("run_123")
```

**Enhanced Version with Progress Tracking:**

```python
def wait_for_completion_advanced(run_id: str, timeout: int = 300, poll_interval: int = 2):
    """Poll run with detailed progress tracking"""
    start = time.time()
    last_status = None

    while time.time() - start < timeout:
        response = requests.get(
            f"{API_BASE}/runs/{run_id}",
            headers=headers
        )

        if response.status_code != 200:
            print(f"Warning: Got status {response.status_code}")
            time.sleep(poll_interval)
            continue

        result = response.json()
        current_status = result['status']

        # Detect status changes
        if current_status != last_status:
            print(f"Status changed: {last_status} -> {current_status}")
            last_status = current_status

        if current_status in ['completed', 'failed', 'cancelled']:
            elapsed = time.time() - start
            print(f"Run {current_status} in {elapsed:.1f}s")
            return result

        # Check for requires_action
        if current_status == 'requires_action':
            print("Warning: Run requires action (tool execution needed)")
            return result

        time.sleep(poll_interval)

    raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")
```

**Common Causes:**
- Tool execution required but not submitted
- Backend service issues
- Very long-running operations
- Network connectivity problems

**Prevention:**
- Always set reasonable timeouts
- Monitor run status transitions
- Handle `requires_action` status appropriately
- Implement cancellation logic for stuck runs

---

### Issue 4: Tool Results Not Accepted

!!! danger "Critical: Match Tool Call IDs"

    **Problem**: `submit_tool_outputs` returns error or tool results are rejected

    **Common Cause**: Tool output `callId` doesn't match the original tool call's `callId`

**Symptoms:**
- 400 Bad Request when submitting tool outputs
- Error: "Invalid tool call ID"
- Run fails after tool submission
- Missing or mismatched tool results

**Solutions:**

```python
# Ensure all tool calls have results
tool_calls = [c for c in output['contents'] if c['kind'] == 'functionCall']
tool_outputs = []

for call in tool_calls:
    tool_outputs.append({
        "tool_call_id": call['callId'],  # Must match exactly
        "output": execute_tool(call['name'], call['arguments'])
    })

# Check all callIds are provided
call_ids = {c['callId'] for c in tool_calls}
output_ids = {o['tool_call_id'] for o in tool_outputs}
assert call_ids == output_ids, f"Missing results for: {call_ids - output_ids}"
```

**Robust Tool Execution Handler:**

```python
def execute_and_submit_tools(run_id: str, output: dict):
    """Execute all tool calls and submit results safely"""
    tool_calls = [c for c in output['contents'] if c['kind'] == 'functionCall']

    if not tool_calls:
        print("No tool calls to execute")
        return None

    print(f"Executing {len(tool_calls)} tool call(s)...")
    tool_outputs = []

    for call in tool_calls:
        try:
            # Execute the tool
            result = execute_tool(call['name'], call['arguments'])

            tool_outputs.append({
                "tool_call_id": call['callId'],
                "output": str(result)  # Ensure output is string
            })
            print(f"✓ Executed {call['name']}")

        except Exception as e:
            # Return error as tool output
            tool_outputs.append({
                "tool_call_id": call['callId'],
                "output": f"Error: {str(e)}"
            })
            print(f"✗ Failed {call['name']}: {e}")

    # Validate before submission
    call_ids = {c['callId'] for c in tool_calls}
    output_ids = {o['tool_call_id'] for o in tool_outputs}

    if call_ids != output_ids:
        missing = call_ids - output_ids
        raise ValueError(f"Missing tool outputs for call IDs: {missing}")

    # Submit results
    response = requests.post(
        f"{API_BASE}/runs/{run_id}/submit_tool_outputs",
        headers=headers,
        json={"tool_outputs": tool_outputs}
    )

    response.raise_for_status()
    return response.json()
```

**Validation Checklist:**
- [ ] Every `functionCall` has a corresponding tool output
- [ ] `callId` matches exactly (case-sensitive)
- [ ] Output is a string (not an object)
- [ ] No duplicate `callId` values
- [ ] All tool calls from the same run step

---

### Issue 5: Context Length Exceeded

!!! danger "Token Limit Exceeded"

    **Problem**: 422 error with "CONTEXT_LENGTH_EXCEEDED"

**Symptoms:**
- Error on long conversations
- 422 Unprocessable Entity status
- Error message contains "context" or "token limit"
- Occurs after multiple turns in conversation

**Solutions:**

```python
# Option 1: Truncate history (see Example 4)

# Option 2: Use smaller model
agent['model'] = "gpt-4o-mini"  # Has larger context

# Option 3: Summarize old messages
def summarize_history(messages: list) -> list:
    """Summarize old messages to reduce tokens"""
    if len(messages) < 10:
        return messages

    # Keep system + recent 5
    system = messages[0] if messages[0]['role'] == 'system' else None
    recent = messages[-5:]

    # Summarize middle
    middle = messages[1:-5] if system else messages[:-5]
    summary_text = "Previous conversation summary: " + summarize(middle)

    result = []
    if system:
        result.append(system)
    result.append({
        "role": "system",
        "contents": [{"kind": "text", "text": summary_text}]
    })
    result.extend(recent)

    return result
```

**Advanced Context Management:**

```python
def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4

def smart_truncate_messages(messages: list, max_tokens: int = 4000) -> list:
    """Intelligently truncate messages to fit context window"""

    # Always keep system message
    system_msg = messages[0] if messages[0]['role'] == 'system' else None
    user_messages = messages[1:] if system_msg else messages

    # Start with most recent messages
    result = []
    total_tokens = 0

    if system_msg:
        system_tokens = estimate_tokens(str(system_msg))
        total_tokens += system_tokens
        result.append(system_msg)

    # Add messages from most recent backwards
    for msg in reversed(user_messages):
        msg_tokens = estimate_tokens(str(msg))

        if total_tokens + msg_tokens > max_tokens:
            # Add truncation notice
            result.append({
                "role": "system",
                "contents": [{
                    "kind": "text",
                    "text": f"[Earlier messages truncated - {len(user_messages) - len(result) + 1} messages omitted]"
                }]
            })
            break

        total_tokens += msg_tokens
        result.insert(1 if system_msg else 0, msg)  # Insert after system

    print(f"Truncated to {len(result)} messages (~{total_tokens} tokens)")
    return result
```

**Alternative Strategies:**

```python
# Option 4: Use thread cleanup
response = requests.post(
    f"{API_BASE}/runs",
    headers=headers,
    json={
        "agent": agent,
        "messages": messages[-10:],  # Only last 10 messages
        "threadCleanup": "delete"  # Don't persist thread
    }
)

# Option 5: Split into multiple threads
def split_conversation(messages: list, chunk_size: int = 20):
    """Split long conversation into multiple threads"""
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i + chunk_size]
        # Process chunk as separate thread
        process_chunk(chunk)
```

**Prevention:**
- Monitor conversation length
- Implement automatic summarization
- Use appropriate models for your use case
- Set up alerts for context warnings
- Test with long conversations

---

## Additional Tips

!!! tip "Best Practices"

    **Error Handling:**
    ```python
    try:
        response = requests.post(f"{API_BASE}/runs", headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    ```

    **Logging:**
    ```python
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.debug(f"Request: {payload}")
    logger.debug(f"Response: {response.json()}")
    ```

    **Response Validation:**
    ```python
    def validate_response(response):
        if 'status' not in response:
            raise ValueError("Invalid response: missing 'status' field")
        if 'output' not in response and response['status'] == 'completed':
            raise ValueError("Completed run missing 'output' field")
        return True
    ```

---

## Getting Help

!!! info "Support Resources"

    Still stuck? Here's where to get help:

**1. Check Documentation:**
- [Getting Started Guide](index.md) - Core concepts
- [API Reference](../api-reference/index.md) - Full API details
- [Run Lifecycle](../specifications/run-lifecycle.md) - Run state machine

**2. Review Specifications:**
- [Tool Execution](../specifications/tool-execution.md) - Tool flow details
- [Streaming](../specifications/streaming.md) - Streaming patterns
- [Agent Auto-Response](../specifications/agent-auto-response.md) - Remote tools

**3. Community Support:**
- GitHub Issues - Report bugs
- Discussion Forums - Ask questions
- Stack Overflow - Community help

**4. Enable Debug Mode:**
```python
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

---

## Related Guides

**Advanced Features:**
- [Proactive Messaging](proactive-messaging.md) - Event-driven agents
- [Voice Integration](voice-integration.md) - Audio streaming
- [Multi-Agent](multi-agent.md) - Agent orchestration
- [Human-in-Loop](human-in-loop.md) - Approval workflows
- [Webhooks](webhooks.md) - Real-time notifications

**API Documentation:**
- [API Reference](../api-reference/index.md) - Complete endpoint documentation
- [Specifications](../specifications/index.md) - Technical requirements

---

!!! success "Troubleshooting Complete"

    If you've worked through this guide and resolved your issue:

    - Consider documenting your solution for others
    - Share your experience in community forums
    - Report documentation gaps or unclear instructions

    Happy building!
