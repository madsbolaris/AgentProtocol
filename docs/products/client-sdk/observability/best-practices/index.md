# Observability Best Practices

Production-ready patterns and recommendations for monitoring and observability in Agent Protocol applications.

## Overview

This guide provides best practices for implementing comprehensive observability in your Agent Protocol applications, covering logging, metrics, tracing, and alerting strategies.

---

## Key Principles

### 1. Structured Logging

Use structured logging formats for easier parsing and analysis.

=== "Python"

    ```python
    import logging
    import json
    from microsoft.agents import AgentProtocolClient

    # Configure structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    class StructuredLogger:
        def __init__(self):
            self.logger = logging.getLogger(__name__)

        def log_event(self, event_type: str, **kwargs):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                **kwargs
            }
            self.logger.info(json.dumps(log_entry))

    # Usage
    logger = StructuredLogger()
    logger.log_event("message_sent", thread_id="thread-123", message_length=150)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import winston from 'winston';

    // Configure structured logging
    const logger = winston.createLogger({
      level: 'info',
      format: winston.format.json(),
      transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'agent-protocol.log' })
      ]
    });

    // Usage
    logger.info('message_sent', {
      timestamp: new Date().toISOString(),
      threadId: 'thread-123',
      messageLength: 150
    });
    ```

=== "C#"

    ```csharp
    using Microsoft.Extensions.Logging;
    using Microsoft.Agents.Client;
    using System.Text.Json;

    public class StructuredLogger
    {
        private readonly ILogger<StructuredLogger> _logger;

        public StructuredLogger(ILogger<StructuredLogger> logger)
        {
            _logger = logger;
        }

        public void LogEvent(string eventType, Dictionary<string, object> properties)
        {
            var logEntry = new Dictionary<string, object>
            {
                ["timestamp"] = DateTime.UtcNow,
                ["event_type"] = eventType
            };

            foreach (var kvp in properties)
            {
                logEntry[kvp.Key] = kvp.Value;
            }

            _logger.LogInformation(JsonSerializer.Serialize(logEntry));
        }
    }

    // Usage
    logger.LogEvent("message_sent", new Dictionary<string, object>
    {
        ["threadId"] = "thread-123",
        ["messageLength"] = 150
    });
    ```

### 2. Meaningful Metrics

Track business-relevant metrics, not just technical ones.

**Essential Metrics:**

- Message throughput (messages/minute)
- Response latency (p50, p95, p99)
- Error rates by type
- Token usage and costs
- Agent success/completion rates
- Tool execution success rates

### 3. Distributed Tracing

Implement correlation IDs to trace requests across services.

=== "Python"

    ```python
    import uuid
    from contextvars import ContextVar

    trace_id: ContextVar[str] = ContextVar('trace_id', default='')

    async def handle_request(message: str):
        # Generate or extract trace ID
        current_trace_id = trace_id.get() or str(uuid.uuid4())
        trace_id.set(current_trace_id)

        logger.log_event("request_started",
            trace_id=current_trace_id,
            message=message)

        try:
            response = await client.send_one_off(message)
            logger.log_event("request_completed",
                trace_id=current_trace_id,
                status="success")
            return response
        except Exception as e:
            logger.log_event("request_failed",
                trace_id=current_trace_id,
                error=str(e))
            raise
    ```

=== "TypeScript"

    ```typescript
    import { v4 as uuidv4 } from 'uuid';
    import { AsyncLocalStorage } from 'async_hooks';

    const traceContext = new AsyncLocalStorage<string>();

    async function handleRequest(message: string) {
      const traceId = uuidv4();

      return traceContext.run(traceId, async () => {
        logger.info('request_started', { traceId, message });

        try {
          const response = await client.sendOneOff(message);
          logger.info('request_completed', { traceId, status: 'success' });
          return response;
        } catch (error) {
          logger.error('request_failed', { traceId, error: error.message });
          throw error;
        }
      });
    }
    ```

=== "C#"

    ```csharp
    using System.Diagnostics;
    using Microsoft.Agents.Client;

    public async Task<Response> HandleRequest(string message)
    {
        var traceId = Activity.Current?.Id ?? Guid.NewGuid().ToString();

        _logger.LogInformation("Request started", new { traceId, message });

        try
        {
            var response = await _client.SendOneOffAsync(message);
            _logger.LogInformation("Request completed", new { traceId, status = "success" });
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Request failed", new { traceId });
            throw;
        }
    }
    ```

### 4. Error Context

Always include sufficient context when logging errors.

**Good Error Context Includes:**

- Trace/correlation ID
- User/session identifier
- Operation being performed
- Input parameters (sanitized)
- Environment information
- Timestamp and duration

### 5. Performance Monitoring

Monitor and alert on performance degradation.

```yaml
# Example alerting rules
alerts:
  - name: high_latency
    condition: p95_latency > 5000ms
    duration: 5m
    action: page_oncall

  - name: high_error_rate
    condition: error_rate > 5%
    duration: 3m
    action: notify_team

  - name: token_usage_spike
    condition: tokens_per_minute > 10000
    duration: 5m
    action: notify_billing
```

---

## Production Patterns

### Health Checks

Implement comprehensive health checks.

=== "Python"

    ```python
    from fastapi import FastAPI
    from microsoft.agents import AgentProtocolClient

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        checks = {
            "database": await check_database(),
            "agent_service": await check_agent_service(),
            "dependencies": await check_dependencies()
        }

        is_healthy = all(checks.values())
        status_code = 200 if is_healthy else 503

        return {"status": "healthy" if is_healthy else "unhealthy", "checks": checks}

    async def check_agent_service() -> bool:
        try:
            # Ping the agent service
            await client.send_one_off("health check")
            return True
        except Exception:
            return False
    ```

=== "TypeScript"

    ```typescript
    import express from 'express';
    import { AgentProtocolClient } from '@microsoft/agents-client';

    const app = express();

    app.get('/health', async (req, res) => {
      const checks = {
        database: await checkDatabase(),
        agentService: await checkAgentService(),
        dependencies: await checkDependencies()
      };

      const isHealthy = Object.values(checks).every(Boolean);
      const statusCode = isHealthy ? 200 : 503;

      res.status(statusCode).json({
        status: isHealthy ? 'healthy' : 'unhealthy',
        checks
      });
    });

    async function checkAgentService(): Promise<boolean> {
      try {
        await client.sendOneOff('health check');
        return true;
      } catch {
        return false;
      }
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.AspNetCore.Mvc;
    using Microsoft.Agents.Client;

    [ApiController]
    [Route("[controller]")]
    public class HealthController : ControllerBase
    {
        private readonly AgentProtocolClient _client;

        [HttpGet]
        public async Task<IActionResult> Get()
        {
            var checks = new Dictionary<string, bool>
            {
                ["database"] = await CheckDatabase(),
                ["agentService"] = await CheckAgentService(),
                ["dependencies"] = await CheckDependencies()
            };

            var isHealthy = checks.Values.All(v => v);
            var statusCode = isHealthy ? 200 : 503;

            return StatusCode(statusCode, new
            {
                status = isHealthy ? "healthy" : "unhealthy",
                checks
            });
        }

        private async Task<bool> CheckAgentService()
        {
            try
            {
                await _client.SendOneOffAsync("health check");
                return true;
            }
            catch
            {
                return false;
            }
        }
    }
    ```

### Graceful Degradation

Design for partial failures and degraded operation.

```python
# Example: Fallback to cached responses when service is slow
async def get_response_with_fallback(message: str, timeout: float = 5.0):
    try:
        response = await asyncio.wait_for(
            client.send_one_off(message),
            timeout=timeout
        )
        await cache.set(message, response)
        return response
    except asyncio.TimeoutError:
        logger.warning(f"Request timed out, checking cache")
        cached = await cache.get(message)
        if cached:
            return cached
        raise
```

### Rate Limiting

Protect your services with rate limiting.

```python
from functools import wraps
import time
from collections import deque

def rate_limit(max_calls: int, time_window: int):
    calls = deque()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls outside time window
            while calls and calls[0] < now - time_window:
                calls.popleft()

            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")

            calls.append(now)
            return await func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_calls=100, time_window=60)
async def handle_message(message: str):
    return await client.send_one_off(message)
```

---

## Security Considerations

### Sensitive Data

Never log sensitive information.

```python
# Bad - logs sensitive data
logger.info(f"User {email} logged in with password {password}")

# Good - sanitizes sensitive data
logger.info(f"User {email[:3]}***@{email.split('@')[1]} logged in")
```

### Audit Trails

Maintain audit logs for compliance.

```python
audit_logger.log_event("user_action",
    user_id=user_id,
    action="delete_thread",
    resource_id=thread_id,
    ip_address=request.remote_addr,
    timestamp=datetime.utcnow())
```

---

## Common Pitfalls

1. **Over-logging**: Don't log every event; focus on actionable data
2. **Missing context**: Always include trace IDs and relevant identifiers
3. **Ignoring costs**: Monitor token usage and API costs
4. **No alerting**: Metrics without alerts are just dashboard decorations
5. **Blocking operations**: Use async logging to avoid performance impact

---

## See Also

- [Logging Guide](../logging/index.md)
- [Metrics Guide](../metrics/index.md)
- [Tracing Guide](../tracing/index.md)
- [Observability Integrations](../integrations/index.md)
- [Observability Overview](../index.md)
