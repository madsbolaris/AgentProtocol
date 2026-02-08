# Production Deployment Guide

**Version**: 1.0
**Date**: 2026-02-07

## Overview

This guide provides comprehensive patterns and best practices for deploying Agent Runtime API applications to production environments. It covers monitoring, observability, performance optimization, scaling, security, and operational excellence.

**What You'll Learn:**
- Production-ready monitoring and observability setup
- Performance optimization strategies (token management, caching, batching)
- Horizontal scaling and load balancing patterns
- Rate limiting and quota management
- Resource management (memory, connections, threads)
- Logging and debugging strategies for production
- Health checks and readiness probes
- Deployment strategies (blue-green, canary)
- Container deployment (Docker, Kubernetes)
- Configuration and secret management
- Circuit breakers and resilience patterns

## Use Cases

This guide is for:
- **DevOps engineers** deploying agent applications to production
- **Platform engineers** building agent infrastructure
- **SREs** managing agent system reliability
- **Solution architects** designing production deployments
- **Engineering teams** scaling agent applications

## Architecture

### High-Level Production Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                            │
│                    (Rate Limiting, SSL/TLS)                      │
└────────────────┬────────────────────────┬───────────────────────┘
                 │                        │
    ┌────────────▼──────────┐  ┌─────────▼──────────┐
    │   Agent API Server 1  │  │  Agent API Server 2 │
    │  - Health checks      │  │  - Health checks    │
    │  - Metrics exporter   │  │  - Metrics exporter │
    │  - Connection pool    │  │  - Connection pool  │
    └────────┬──────────────┘  └──────────┬──────────┘
             │                            │
    ┌────────▼────────────────────────────▼────────┐
    │           Message Queue / Cache              │
    │        (Redis, RabbitMQ, Kafka)              │
    └────────┬─────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────┐
    │        Database Cluster             │
    │   (Threads, Runs, Messages)         │
    └─────────────────────────────────────┘

    ┌─────────────────────────────────────┐
    │      Observability Stack            │
    │  - Prometheus (metrics)             │
    │  - Grafana (dashboards)             │
    │  - Loki/ELK (logs)                  │
    │  - Jaeger/Tempo (traces)            │
    └─────────────────────────────────────┘
```

### Production Deployment Layers

```
┌─────────────────────────────────────────────────────┐
│                  API Gateway Layer                   │
│  - Rate limiting                                     │
│  - Authentication/Authorization                      │
│  - Request validation                                │
│  - SSL termination                                   │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│               Application Layer                      │
│  - Agent API servers (stateless)                     │
│  - Connection pooling                                │
│  - Circuit breakers                                  │
│  - Caching layer                                     │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│                  Data Layer                          │
│  - Primary database (reads + writes)                 │
│  - Read replicas (reads only)                        │
│  - Cache (Redis/Memcached)                           │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│              External Services                       │
│  - LLM providers (OpenAI, Anthropic, Azure)         │
│  - Message queues                                    │
│  - Object storage                                    │
└─────────────────────────────────────────────────────┘
```

## Implementation

### Step 1: Monitoring and Observability

#### Prometheus Metrics Collection

Export metrics from your Agent API server for Prometheus scraping.

**Metrics to Track:**

```typescript
// Core run metrics
agent_runs_total{status="completed|failed|cancelled", agent_id="..."}
agent_runs_duration_seconds{agent_id="...", quantile="0.5|0.9|0.99"}
agent_runs_active{agent_id="..."}

// Token usage metrics
agent_tokens_total{type="input|output|cached|reasoning", agent_id="..."}
agent_tokens_cost_usd{agent_id="..."}

// Rate limiting metrics
agent_rate_limit_hits_total{agent_id="..."}
agent_rate_limit_rejected_total{agent_id="..."}

// Tool execution metrics
agent_tool_calls_total{tool_name="...", status="success|failed"}
agent_tool_duration_seconds{tool_name="...", quantile="0.5|0.9|0.99"}

// Connection pool metrics
agent_db_connections_active
agent_db_connections_idle
agent_llm_connections_active

// Stream metrics
agent_streams_active
agent_stream_duration_seconds{quantile="0.5|0.9|0.99"}

// Error metrics
agent_errors_total{error_code="..."}
agent_hook_failures_total{hook_id="..."}
```

**Python Implementation:**

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
runs_total = Counter(
    'agent_runs_total',
    'Total number of agent runs',
    ['status', 'agent_id']
)

run_duration = Histogram(
    'agent_runs_duration_seconds',
    'Agent run duration in seconds',
    ['agent_id'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

active_runs = Gauge(
    'agent_runs_active',
    'Number of currently active runs',
    ['agent_id']
)

tokens_total = Counter(
    'agent_tokens_total',
    'Total tokens used',
    ['type', 'agent_id']
)

tokens_cost = Counter(
    'agent_tokens_cost_usd',
    'Total cost in USD',
    ['agent_id']
)

errors_total = Counter(
    'agent_errors_total',
    'Total errors',
    ['error_code']
)

# Instrument run execution
class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['path'] == '/runs':
            agent_id = scope.get('agent_id', 'unknown')

            # Track active runs
            active_runs.labels(agent_id=agent_id).inc()

            start_time = time.time()
            try:
                await self.app(scope, receive, send)

                # Success metrics
                duration = time.time() - start_time
                run_duration.labels(agent_id=agent_id).observe(duration)
                runs_total.labels(status='completed', agent_id=agent_id).inc()

            except Exception as e:
                # Error metrics
                error_code = getattr(e, 'code', 'unknown')
                errors_total.labels(error_code=error_code).inc()
                runs_total.labels(status='failed', agent_id=agent_id).inc()
                raise
            finally:
                active_runs.labels(agent_id=agent_id).dec()
        else:
            await self.app(scope, receive, send)

# Track token usage
def record_token_usage(usage: dict, agent_id: str):
    """Record token usage metrics"""
    tokens_total.labels(type='input', agent_id=agent_id).inc(
        usage.get('inputTokens', 0)
    )
    tokens_total.labels(type='output', agent_id=agent_id).inc(
        usage.get('outputTokens', 0)
    )

    if usage.get('inputTokenDetails', {}).get('cachedTokens'):
        tokens_total.labels(type='cached', agent_id=agent_id).inc(
            usage['inputTokenDetails']['cachedTokens']
        )

    if usage.get('outputTokenDetails', {}).get('reasoningTokens'):
        tokens_total.labels(type='reasoning', agent_id=agent_id).inc(
            usage['outputTokenDetails']['reasoningTokens']
        )

    # Cost estimation (example rates)
    input_cost = usage.get('inputTokens', 0) * 0.000003  # $0.003 per 1K tokens
    output_cost = usage.get('outputTokens', 0) * 0.000015  # $0.015 per 1K tokens
    total_cost = input_cost + output_cost

    tokens_cost.labels(agent_id=agent_id).inc(total_cost)

# Start Prometheus HTTP server
start_http_server(9090)
```

**Prometheus Configuration:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'agent-api'
    static_configs:
      - targets: ['agent-api-1:9090', 'agent-api-2:9090']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
```

#### Grafana Dashboards

**Example Dashboard JSON:**

```json
{
  "dashboard": {
    "title": "Agent Runtime API - Production",
    "panels": [
      {
        "title": "Active Runs",
        "targets": [
          {
            "expr": "sum(agent_runs_active) by (agent_id)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Run Success Rate",
        "targets": [
          {
            "expr": "sum(rate(agent_runs_total{status=\"completed\"}[5m])) / sum(rate(agent_runs_total[5m]))"
          }
        ],
        "type": "singlestat"
      },
      {
        "title": "P99 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(agent_runs_duration_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Token Usage (Last Hour)",
        "targets": [
          {
            "expr": "sum(increase(agent_tokens_total[1h])) by (type)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Cost per Hour",
        "targets": [
          {
            "expr": "sum(increase(agent_tokens_cost_usd[1h]))"
          }
        ],
        "type": "singlestat"
      }
    ]
  }
}
```

#### Structured Logging with Correlation IDs

Use structured logging with correlation IDs to trace requests across services.

**Python Implementation:**

```python
import logging
import json
import uuid
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs):
        """Log structured message with correlation ID"""
        correlation_id = correlation_id_var.get()

        log_data = {
            'timestamp': time.time(),
            'level': level,
            'message': message,
            'correlation_id': correlation_id,
            **kwargs
        }

        getattr(self.logger, level.lower())(json.dumps(log_data))

    def info(self, message: str, **kwargs):
        self._log('INFO', message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log('ERROR', message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, **kwargs)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return record.getMessage()

# Middleware to inject correlation ID
class CorrelationIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Extract or generate correlation ID
        headers = dict(scope.get('headers', []))
        correlation_id = headers.get(b'x-correlation-id', str(uuid.uuid4()).encode()).decode()

        # Set in context
        correlation_id_var.set(correlation_id)

        # Add to response headers
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                message['headers'].append((b'x-correlation-id', correlation_id.encode()))
            await send(message)

        await self.app(scope, receive, send_wrapper)

# Usage
logger = StructuredLogger(__name__)

async def create_run(request):
    logger.info(
        'Creating run',
        agent_id=request.agent_id,
        thread_id=request.thread_id,
        user_id=request.user_id
    )

    try:
        run = await execute_run(request)
        logger.info(
            'Run completed',
            run_id=run.run_id,
            status=run.status,
            duration=run.duration,
            tokens=run.usage.total_tokens
        )
        return run
    except Exception as e:
        logger.error(
            'Run failed',
            error=str(e),
            error_type=type(e).__name__,
            traceback=traceback.format_exc()
        )
        raise
```

**Example Log Output:**

```json
{"timestamp": 1707307200.123, "level": "INFO", "message": "Creating run", "correlation_id": "abc-123-def-456", "agent_id": "agent-1", "thread_id": "thread-1", "user_id": "user-1"}
{"timestamp": 1707307202.456, "level": "INFO", "message": "Run completed", "correlation_id": "abc-123-def-456", "run_id": "run-1", "status": "completed", "duration": 2.333, "tokens": 234}
```

**Loki Query (to trace single request):**

```logql
{job="agent-api"} | json | correlation_id="abc-123-def-456"
```

#### OpenTelemetry Tracing

Implement distributed tracing with OpenTelemetry to track requests across services.

**Python Implementation:**

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger',
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Auto-instrument FastAPI and requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Manual instrumentation for custom spans
async def execute_run(run_request):
    with tracer.start_as_current_span("execute_run") as span:
        span.set_attribute("run.agent_id", run_request.agent_id)
        span.set_attribute("run.thread_id", run_request.thread_id)

        # LLM call span
        with tracer.start_as_current_span("llm.generate") as llm_span:
            llm_span.set_attribute("llm.model", run_request.agent.model)
            llm_span.set_attribute("llm.provider", "openai")

            response = await llm_client.generate(run_request)

            llm_span.set_attribute("llm.input_tokens", response.usage.input_tokens)
            llm_span.set_attribute("llm.output_tokens", response.usage.output_tokens)

        # Tool execution span (if needed)
        if response.requires_action:
            with tracer.start_as_current_span("tool.execute") as tool_span:
                tool_span.set_attribute("tool.name", response.tool_calls[0].name)

                result = await execute_tool(response.tool_calls[0])

                tool_span.set_attribute("tool.duration", result.duration)

        span.set_attribute("run.status", "completed")
        span.set_attribute("run.total_tokens", response.usage.total_tokens)

        return response
```

**Jaeger UI Query:**

```
Service: agent-api
Operation: execute_run
Tags: run.agent_id = agent-1
```

### Step 2: Performance Optimization

#### Token Management and Budget Enforcement

Implement token budget tracking and enforcement to control costs.

**Python Implementation:**

```python
from dataclasses import dataclass
from typing import Optional
import asyncio

@dataclass
class TokenBudget:
    """Token budget configuration"""
    max_input_tokens: int
    max_output_tokens: int
    max_total_tokens: int
    max_cost_usd: float

@dataclass
class TokenUsageTracker:
    """Track token usage across requests"""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost(self) -> float:
        """Estimate cost in USD (example rates for GPT-4)"""
        input_cost = self.input_tokens * 0.00003  # $0.03 per 1K tokens
        output_cost = self.output_tokens * 0.00006  # $0.06 per 1K tokens
        cached_cost = self.cached_tokens * 0.000015  # 50% discount for cached
        reasoning_cost = self.reasoning_tokens * 0.00012  # 2x for reasoning

        return input_cost + output_cost + cached_cost + reasoning_cost

class TokenBudgetEnforcer:
    """Enforce token budgets for runs"""

    def __init__(self, budget: TokenBudget):
        self.budget = budget
        self.usage = TokenUsageTracker()
        self.lock = asyncio.Lock()

    async def check_budget(self, estimated_tokens: int) -> bool:
        """Check if request is within budget"""
        async with self.lock:
            if self.usage.total_tokens + estimated_tokens > self.budget.max_total_tokens:
                return False

            if self.usage.estimated_cost > self.budget.max_cost_usd:
                return False

            return True

    async def record_usage(self, usage: dict):
        """Record actual token usage"""
        async with self.lock:
            self.usage.input_tokens += usage.get('inputTokens', 0)
            self.usage.output_tokens += usage.get('outputTokens', 0)

            if usage.get('inputTokenDetails', {}).get('cachedTokens'):
                self.usage.cached_tokens += usage['inputTokenDetails']['cachedTokens']

            if usage.get('outputTokenDetails', {}).get('reasoningTokens'):
                self.usage.reasoning_tokens += usage['outputTokenDetails']['reasoningTokens']

    def get_remaining_budget(self) -> dict:
        """Get remaining budget"""
        return {
            'tokens_used': self.usage.total_tokens,
            'tokens_remaining': self.budget.max_total_tokens - self.usage.total_tokens,
            'cost_used': self.usage.estimated_cost,
            'cost_remaining': self.budget.max_cost_usd - self.usage.estimated_cost,
            'budget_percentage': (self.usage.total_tokens / self.budget.max_total_tokens) * 100
        }

# Usage in API
budgets = {}  # user_id -> TokenBudgetEnforcer

async def create_run_with_budget(request, user_id: str):
    # Get or create budget for user
    if user_id not in budgets:
        budgets[user_id] = TokenBudgetEnforcer(TokenBudget(
            max_input_tokens=100000,
            max_output_tokens=50000,
            max_total_tokens=150000,
            max_cost_usd=10.0
        ))

    enforcer = budgets[user_id]

    # Estimate tokens for this request
    estimated_tokens = estimate_tokens(request.input)

    # Check budget
    if not await enforcer.check_budget(estimated_tokens):
        remaining = enforcer.get_remaining_budget()
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'token_budget_exceeded',
                'message': 'Token budget exceeded',
                'remaining': remaining
            }
        )

    # Execute run
    run = await execute_run(request)

    # Record actual usage
    await enforcer.record_usage(run.usage)

    # Add budget info to response
    run.budget_info = enforcer.get_remaining_budget()

    return run
```

#### Prompt Caching Strategy

Leverage prompt caching to reduce costs and improve latency.

**Caching Strategies:**

1. **System Message Caching** - Cache static system instructions
2. **Context Caching** - Cache conversation history
3. **Tool Definition Caching** - Cache tool schemas
4. **Knowledge Base Caching** - Cache static knowledge content

**Python Implementation:**

```python
import hashlib
import json
from typing import List, Dict, Optional

class PromptCacheManager:
    """Manage prompt caching for LLM requests"""

    def __init__(self, cache_ttl: int = 3600):
        self.cache = {}  # In production, use Redis
        self.cache_ttl = cache_ttl

    def compute_cache_key(self, messages: List[Dict]) -> str:
        """Compute cache key for messages"""
        # Create stable hash of message content
        content = json.dumps(messages, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def mark_cacheable_prefix(self, messages: List[Dict]) -> List[Dict]:
        """Mark prefix of messages as cacheable

        Anthropic Claude supports caching message prefixes.
        Mark system message + context as cacheable.
        """
        if not messages:
            return messages

        # System message is cacheable
        if messages[0]['role'] == 'system':
            messages[0]['cache_control'] = {'type': 'ephemeral'}

        # Tool definitions are cacheable (if present)
        for msg in messages:
            if msg['role'] == 'system' and 'tools' in msg:
                msg['cache_control'] = {'type': 'ephemeral'}

        # Conversation history up to last 2 messages is cacheable
        if len(messages) > 3:
            messages[-3]['cache_control'] = {'type': 'ephemeral'}

        return messages

    def optimize_for_caching(self, messages: List[Dict], agent_config: Dict) -> List[Dict]:
        """Optimize message structure for maximum caching"""
        # Strategy 1: Move static content to front
        static_messages = []
        dynamic_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                static_messages.append(msg)
            elif msg.get('metadata', {}).get('static', False):
                static_messages.append(msg)
            else:
                dynamic_messages.append(msg)

        # Reconstruct with static content first
        optimized = static_messages + dynamic_messages

        # Mark cache boundaries
        return self.mark_cacheable_prefix(optimized)

# Usage
cache_manager = PromptCacheManager()

async def execute_run_with_caching(request):
    # Optimize messages for caching
    optimized_messages = cache_manager.optimize_for_caching(
        request.input,
        request.agent
    )

    # Send to LLM with cache markers
    response = await llm_client.generate(
        messages=optimized_messages,
        model=request.agent.model
    )

    # Log cache performance
    if response.usage.get('inputTokenDetails', {}).get('cachedTokens'):
        cached_pct = (
            response.usage['inputTokenDetails']['cachedTokens'] /
            response.usage['inputTokens']
        ) * 100

        logger.info(
            'Prompt cache hit',
            cached_tokens=response.usage['inputTokenDetails']['cachedTokens'],
            cache_percentage=cached_pct,
            cost_saved=calculate_cache_savings(response.usage)
        )

    return response

def calculate_cache_savings(usage: dict) -> float:
    """Calculate cost savings from caching"""
    cached_tokens = usage.get('inputTokenDetails', {}).get('cachedTokens', 0)

    # Cached tokens typically cost 50% of regular input tokens
    regular_cost = cached_tokens * 0.00003  # $0.03 per 1K
    cached_cost = cached_tokens * 0.000015  # $0.015 per 1K (50% discount)

    return regular_cost - cached_cost
```

#### Request Batching

Batch multiple requests to reduce overhead and improve throughput.

**Python Implementation:**

```python
import asyncio
from typing import List, Dict
from dataclasses import dataclass
import time

@dataclass
class BatchRequest:
    """Single request in batch"""
    request_id: str
    agent_id: str
    input: List[Dict]
    future: asyncio.Future

class RequestBatcher:
    """Batch requests for efficient processing"""

    def __init__(
        self,
        max_batch_size: int = 10,
        max_wait_time: float = 0.1  # 100ms
    ):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending: List[BatchRequest] = []
        self.lock = asyncio.Lock()
        self.batch_task = None

    async def add_request(self, request: BatchRequest) -> Dict:
        """Add request to batch and return result"""
        async with self.lock:
            self.pending.append(request)

            # Start batch timer if not running
            if not self.batch_task:
                self.batch_task = asyncio.create_task(self._wait_and_flush())

            # Flush immediately if batch is full
            if len(self.pending) >= self.max_batch_size:
                asyncio.create_task(self._flush_batch())

        # Wait for result
        return await request.future

    async def _wait_and_flush(self):
        """Wait for max_wait_time, then flush"""
        await asyncio.sleep(self.max_wait_time)
        await self._flush_batch()

    async def _flush_batch(self):
        """Process pending batch"""
        async with self.lock:
            if not self.pending:
                return

            batch = self.pending
            self.pending = []
            self.batch_task = None

        logger.info(f'Processing batch of {len(batch)} requests')

        # Group by agent_id for efficiency
        by_agent = {}
        for req in batch:
            if req.agent_id not in by_agent:
                by_agent[req.agent_id] = []
            by_agent[req.agent_id].append(req)

        # Process each agent's batch
        tasks = []
        for agent_id, requests in by_agent.items():
            tasks.append(self._process_agent_batch(agent_id, requests))

        await asyncio.gather(*tasks)

    async def _process_agent_batch(self, agent_id: str, requests: List[BatchRequest]):
        """Process batch for single agent"""
        try:
            # Execute requests in parallel
            results = await asyncio.gather(*[
                execute_run_internal(req.input, agent_id)
                for req in requests
            ])

            # Set results
            for req, result in zip(requests, results):
                req.future.set_result(result)

        except Exception as e:
            # Set error for all requests
            for req in requests:
                req.future.set_exception(e)

# Usage
batcher = RequestBatcher(max_batch_size=10, max_wait_time=0.1)

async def create_run_batched(request):
    """Create run with automatic batching"""
    request_id = str(uuid.uuid4())
    future = asyncio.Future()

    batch_request = BatchRequest(
        request_id=request_id,
        agent_id=request.agent_id,
        input=request.input,
        future=future
    )

    # Add to batch and wait for result
    result = await batcher.add_request(batch_request)

    return result
```

### Step 3: Scaling Patterns

#### Horizontal Scaling Architecture

Design stateless API servers that can scale horizontally.

**Stateless Server Requirements:**

```python
class StatelessAgentAPIServer:
    """Stateless API server design for horizontal scaling"""

    def __init__(self, config):
        # Externalize all state
        self.db = DatabaseClient(config.db_url)  # Shared database
        self.cache = RedisClient(config.redis_url)  # Shared cache
        self.queue = MessageQueueClient(config.queue_url)  # Shared queue

        # Connection pools (per-process, but stateless)
        self.llm_clients = LLMConnectionPool(config)

        # No in-memory state between requests
        # Each request is independent

    async def create_run(self, request):
        """Stateless run creation"""
        # 1. Validate request (no server state)
        self.validate_request(request)

        # 2. Check rate limits (from Redis, not memory)
        if not await self.check_rate_limit(request.user_id):
            raise HTTPException(429, "Rate limit exceeded")

        # 3. Create run record (in database)
        run = await self.db.create_run(request)

        # 4. Queue for execution (async processing)
        await self.queue.publish('run.created', run.run_id)

        # 5. Return immediately (don't wait for completion)
        return run

    async def check_rate_limit(self, user_id: str) -> bool:
        """Check rate limit using shared Redis"""
        key = f'rate_limit:{user_id}'

        # Sliding window rate limit
        now = time.time()
        window = 60  # 60 seconds
        limit = 100  # 100 requests per minute

        # Remove old entries
        await self.cache.zremrangebyscore(key, 0, now - window)

        # Count current requests
        count = await self.cache.zcard(key)

        if count >= limit:
            return False

        # Add this request
        await self.cache.zadd(key, {str(uuid.uuid4()): now})
        await self.cache.expire(key, window)

        return True
```

**Kubernetes Deployment:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
spec:
  replicas: 3  # Horizontal scaling
  selector:
    matchLabels:
      app: agent-api
  template:
    metadata:
      labels:
        app: agent-api
    spec:
      containers:
      - name: agent-api
        image: agent-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: redis_url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: agent-api
spec:
  selector:
    app: agent-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### Load Balancing Strategy

Implement intelligent load balancing for agent workloads.

**Nginx Load Balancer Configuration:**

```nginx
# nginx.conf
upstream agent_api_backend {
    least_conn;  # Route to server with fewest connections

    server agent-api-1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server agent-api-2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server agent-api-3:8000 weight=1 max_fails=3 fail_timeout=30s;

    # Health check
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Timeouts for long-running requests
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;  # 5 minutes for LLM generation
    proxy_read_timeout 300s;

    location / {
        proxy_pass http://agent_api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Correlation ID
        proxy_set_header X-Correlation-ID $request_id;
    }

    # SSE streaming endpoint (no buffering)
    location /runs/stream {
        proxy_pass http://agent_api_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
    }

    # Health check endpoint (bypass rate limit)
    location /health {
        proxy_pass http://agent_api_backend;
        access_log off;
    }
}
```

### Step 4: Rate Limiting and Quotas

#### Token Bucket Rate Limiter

Implement token bucket algorithm for rate limiting.

**Python Implementation:**

```python
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int  # Maximum tokens
    refill_rate: float  # Tokens per second
    tokens: float  # Current tokens
    last_refill: float  # Last refill timestamp

    def refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: int) -> bool:
        """Try to consume tokens"""
        self.refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def get_wait_time(self, tokens: int) -> float:
        """Get time to wait for tokens to be available"""
        self.refill()

        if self.tokens >= tokens:
            return 0.0

        deficit = tokens - self.tokens
        return deficit / self.refill_rate

class RateLimiter:
    """Multi-tier rate limiter"""

    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = asyncio.Lock()

    def get_bucket(self, key: str, tier: str) -> TokenBucket:
        """Get or create bucket for key and tier"""
        bucket_key = f'{key}:{tier}'

        if bucket_key not in self.buckets:
            # Tier-based limits
            if tier == 'free':
                capacity = 100
                refill_rate = 1.0  # 1 request per second
            elif tier == 'pro':
                capacity = 1000
                refill_rate = 10.0  # 10 requests per second
            elif tier == 'enterprise':
                capacity = 10000
                refill_rate = 100.0  # 100 requests per second
            else:
                capacity = 10
                refill_rate = 0.1

            self.buckets[bucket_key] = TokenBucket(
                capacity=capacity,
                refill_rate=refill_rate,
                tokens=capacity,
                last_refill=time.time()
            )

        return self.buckets[bucket_key]

    async def check_limit(self, user_id: str, tier: str, cost: int = 1) -> tuple[bool, Optional[float]]:
        """Check if request is within rate limit

        Returns: (allowed, retry_after_seconds)
        """
        async with self.lock:
            bucket = self.get_bucket(user_id, tier)

            if bucket.consume(cost):
                return True, None

            # Calculate retry-after
            wait_time = bucket.get_wait_time(cost)
            return False, wait_time

# Usage
rate_limiter = RateLimiter()

async def create_run_with_rate_limit(request, user_id: str, tier: str):
    # Check rate limit
    allowed, retry_after = await rate_limiter.check_limit(user_id, tier, cost=1)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                'error': 'rate_limit_exceeded',
                'message': 'Rate limit exceeded',
                'retry_after': retry_after
            },
            headers={'Retry-After': str(int(retry_after))}
        )

    # Execute run
    return await execute_run(request)
```

#### Quota Management

Implement quota tracking and enforcement for usage limits.

**Python Implementation:**

```python
from datetime import datetime, timedelta
from typing import Dict, Optional

@dataclass
class Quota:
    """Usage quota configuration"""
    period: str  # 'hourly', 'daily', 'monthly'
    max_requests: int
    max_tokens: int
    max_cost_usd: float

@dataclass
class QuotaUsage:
    """Current quota usage"""
    requests: int = 0
    tokens: int = 0
    cost_usd: float = 0.0
    period_start: datetime = None
    period_end: datetime = None

class QuotaManager:
    """Manage user quotas"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def get_quota(self, tier: str, period: str) -> Quota:
        """Get quota limits for tier and period"""
        quotas = {
            'free': {
                'hourly': Quota('hourly', 100, 100000, 1.0),
                'daily': Quota('daily', 1000, 1000000, 10.0),
                'monthly': Quota('monthly', 10000, 10000000, 100.0)
            },
            'pro': {
                'hourly': Quota('hourly', 1000, 1000000, 10.0),
                'daily': Quota('daily', 10000, 10000000, 100.0),
                'monthly': Quota('monthly', 100000, 100000000, 1000.0)
            },
            'enterprise': {
                'hourly': Quota('hourly', 10000, 10000000, 100.0),
                'daily': Quota('daily', 100000, 100000000, 1000.0),
                'monthly': Quota('monthly', 1000000, 1000000000, 10000.0)
            }
        }

        return quotas.get(tier, quotas['free']).get(period)

    async def get_usage(self, user_id: str, period: str) -> QuotaUsage:
        """Get current usage for period"""
        key = f'quota:{user_id}:{period}'

        data = await self.redis.hgetall(key)

        if not data:
            # Initialize new period
            now = datetime.utcnow()
            period_start, period_end = self._get_period_bounds(period, now)

            usage = QuotaUsage(
                period_start=period_start,
                period_end=period_end
            )
        else:
            usage = QuotaUsage(
                requests=int(data.get(b'requests', 0)),
                tokens=int(data.get(b'tokens', 0)),
                cost_usd=float(data.get(b'cost_usd', 0.0)),
                period_start=datetime.fromisoformat(data[b'period_start'].decode()),
                period_end=datetime.fromisoformat(data[b'period_end'].decode())
            )

        # Check if period expired
        if datetime.utcnow() > usage.period_end:
            usage = QuotaUsage(
                period_start=usage.period_end,
                period_end=self._get_next_period_end(period, usage.period_end)
            )

        return usage

    async def check_quota(self, user_id: str, tier: str, estimated_tokens: int) -> tuple[bool, Dict]:
        """Check if request is within quota

        Returns: (allowed, quota_info)
        """
        # Check all periods
        for period in ['hourly', 'daily', 'monthly']:
            quota = self.get_quota(tier, period)
            usage = await self.get_usage(user_id, period)

            # Check request limit
            if usage.requests + 1 > quota.max_requests:
                return False, {
                    'error': 'quota_exceeded',
                    'period': period,
                    'limit_type': 'requests',
                    'current': usage.requests,
                    'limit': quota.max_requests,
                    'reset_at': usage.period_end.isoformat()
                }

            # Check token limit
            if usage.tokens + estimated_tokens > quota.max_tokens:
                return False, {
                    'error': 'quota_exceeded',
                    'period': period,
                    'limit_type': 'tokens',
                    'current': usage.tokens,
                    'limit': quota.max_tokens,
                    'reset_at': usage.period_end.isoformat()
                }

            # Check cost limit
            estimated_cost = estimated_tokens * 0.00003  # Example rate
            if usage.cost_usd + estimated_cost > quota.max_cost_usd:
                return False, {
                    'error': 'quota_exceeded',
                    'period': period,
                    'limit_type': 'cost',
                    'current': usage.cost_usd,
                    'limit': quota.max_cost_usd,
                    'reset_at': usage.period_end.isoformat()
                }

        # All quotas OK
        return True, {}

    async def record_usage(self, user_id: str, requests: int, tokens: int, cost_usd: float):
        """Record actual usage"""
        for period in ['hourly', 'daily', 'monthly']:
            key = f'quota:{user_id}:{period}'
            usage = await self.get_usage(user_id, period)

            await self.redis.hset(key, mapping={
                'requests': usage.requests + requests,
                'tokens': usage.tokens + tokens,
                'cost_usd': usage.cost_usd + cost_usd,
                'period_start': usage.period_start.isoformat(),
                'period_end': usage.period_end.isoformat()
            })

            # Set expiry
            ttl = int((usage.period_end - datetime.utcnow()).total_seconds())
            await self.redis.expire(key, ttl + 86400)  # +1 day buffer

    def _get_period_bounds(self, period: str, now: datetime) -> tuple[datetime, datetime]:
        """Get period start and end times"""
        if period == 'hourly':
            start = now.replace(minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)
        elif period == 'daily':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == 'monthly':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
        else:
            raise ValueError(f'Invalid period: {period}')

        return start, end

    def _get_next_period_end(self, period: str, current_end: datetime) -> datetime:
        """Get next period end time"""
        if period == 'hourly':
            return current_end + timedelta(hours=1)
        elif period == 'daily':
            return current_end + timedelta(days=1)
        elif period == 'monthly':
            if current_end.month == 12:
                return current_end.replace(year=current_end.year + 1, month=1)
            else:
                return current_end.replace(month=current_end.month + 1)

# Usage
quota_manager = QuotaManager(redis_client)

async def create_run_with_quota(request, user_id: str, tier: str):
    # Estimate tokens
    estimated_tokens = estimate_tokens(request.input)

    # Check quota
    allowed, quota_info = await quota_manager.check_quota(user_id, tier, estimated_tokens)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=quota_info
        )

    # Execute run
    run = await execute_run(request)

    # Record actual usage
    await quota_manager.record_usage(
        user_id,
        requests=1,
        tokens=run.usage.total_tokens,
        cost_usd=calculate_cost(run.usage)
    )

    return run
```

### Step 5: Resource Management

#### Connection Pooling

Implement connection pooling for database and LLM API connections.

**Python Implementation:**

```python
from typing import Optional
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class PoolConfig:
    """Connection pool configuration"""
    min_size: int = 10
    max_size: int = 100
    acquire_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes

class LLMConnectionPool:
    """Connection pool for LLM API requests"""

    def __init__(self, config: PoolConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_size)
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_connections = 0
        self.total_requests = 0

    async def __aenter__(self):
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=self.config.max_size,
                limit_per_host=self.config.max_size,
                ttl_dns_cache=300
            )

            timeout = aiohttp.ClientTimeout(
                total=None,  # No total timeout
                connect=10.0,
                sock_read=300.0  # 5 minutes for generation
            )

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )

        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def execute(self, request):
        """Execute LLM request with connection pooling"""
        async with self.semaphore:
            self.active_connections += 1
            self.total_requests += 1

            try:
                # Use shared session from pool
                async with self.session.post(
                    url=request.url,
                    headers=request.headers,
                    json=request.body
                ) as response:
                    return await response.json()

            finally:
                self.active_connections -= 1

    def get_stats(self) -> dict:
        """Get pool statistics"""
        return {
            'active_connections': self.active_connections,
            'total_requests': self.total_requests,
            'max_size': self.config.max_size,
            'utilization': self.active_connections / self.config.max_size
        }

# Database connection pool (using asyncpg)
import asyncpg

class DatabasePool:
    """Database connection pool"""

    def __init__(self, config: PoolConfig, db_url: str):
        self.config = config
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize pool"""
        self.pool = await asyncpg.create_pool(
            self.db_url,
            min_size=self.config.min_size,
            max_size=self.config.max_size,
            max_queries=50000,
            max_inactive_connection_lifetime=self.config.idle_timeout
        )

    async def execute(self, query: str, *args):
        """Execute query with connection from pool"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def close(self):
        """Close pool"""
        if self.pool:
            await self.pool.close()

    def get_stats(self) -> dict:
        """Get pool statistics"""
        if not self.pool:
            return {}

        return {
            'size': self.pool.get_size(),
            'free': self.pool.get_idle_size(),
            'used': self.pool.get_size() - self.pool.get_idle_size(),
            'max_size': self.pool.get_max_size(),
            'utilization': (self.pool.get_size() - self.pool.get_idle_size()) / self.pool.get_max_size()
        }

# Usage
llm_pool = LLMConnectionPool(PoolConfig(max_size=100))
db_pool = DatabasePool(PoolConfig(min_size=10, max_size=50), db_url)

async def create_run_with_pools(request):
    # Use connection pools
    async with llm_pool:
        # LLM request uses pooled connection
        response = await llm_pool.execute(llm_request)

        # Database query uses pooled connection
        await db_pool.execute(
            'INSERT INTO runs (run_id, status, output) VALUES ($1, $2, $3)',
            response.run_id,
            'completed',
            response.output
        )

    return response
```

#### Memory Management

Monitor and manage memory usage to prevent OOM errors.

**Python Implementation:**

```python
import psutil
import gc
import sys
from typing import Dict, List
import asyncio

class MemoryMonitor:
    """Monitor and manage memory usage"""

    def __init__(
        self,
        warning_threshold: float = 0.80,  # 80% of available memory
        critical_threshold: float = 0.90  # 90% of available memory
    ):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.process = psutil.Process()

    def get_memory_info(self) -> Dict:
        """Get current memory usage"""
        # System memory
        system_memory = psutil.virtual_memory()

        # Process memory
        process_memory = self.process.memory_info()

        return {
            'system': {
                'total': system_memory.total,
                'available': system_memory.available,
                'used': system_memory.used,
                'percent': system_memory.percent
            },
            'process': {
                'rss': process_memory.rss,  # Resident Set Size
                'vms': process_memory.vms,  # Virtual Memory Size
                'percent': self.process.memory_percent()
            }
        }

    def check_memory_pressure(self) -> tuple[str, Dict]:
        """Check if memory pressure is high

        Returns: (level, memory_info)
        level: 'normal', 'warning', 'critical'
        """
        info = self.get_memory_info()
        percent = info['system']['percent'] / 100.0

        if percent >= self.critical_threshold:
            return 'critical', info
        elif percent >= self.warning_threshold:
            return 'warning', info
        else:
            return 'normal', info

    def force_gc(self):
        """Force garbage collection"""
        collected = gc.collect()
        return {
            'collected': collected,
            'memory_before': self.get_memory_info(),
            'memory_after': self.get_memory_info()
        }

    def get_large_objects(self, limit: int = 10) -> List[Dict]:
        """Get largest objects in memory (debugging)"""
        objects = []

        for obj in gc.get_objects():
            try:
                size = sys.getsizeof(obj)
                objects.append({
                    'type': type(obj).__name__,
                    'size': size,
                    'repr': repr(obj)[:100]
                })
            except:
                pass

        # Sort by size descending
        objects.sort(key=lambda x: x['size'], reverse=True)

        return objects[:limit]

# Memory-aware request handler
memory_monitor = MemoryMonitor()

async def create_run_with_memory_check(request):
    """Create run with memory pressure check"""
    # Check memory before processing
    level, info = memory_monitor.check_memory_pressure()

    if level == 'critical':
        # Force GC
        gc_result = memory_monitor.force_gc()

        # Re-check after GC
        level, info = memory_monitor.check_memory_pressure()

        if level == 'critical':
            # Still critical - reject request
            raise HTTPException(
                status_code=503,
                detail={
                    'error': 'memory_pressure',
                    'message': 'Server memory pressure too high',
                    'memory_percent': info['system']['percent'],
                    'retry_after': 60
                }
            )

    elif level == 'warning':
        # Log warning
        logger.warning(
            'High memory pressure',
            memory_percent=info['system']['percent'],
            process_memory_mb=info['process']['rss'] / 1024 / 1024
        )

    # Execute run
    try:
        run = await execute_run(request)
        return run

    finally:
        # Check memory after processing
        level, info = memory_monitor.check_memory_pressure()

        if level in ['warning', 'critical']:
            # Trigger async GC
            asyncio.create_task(async_gc())

async def async_gc():
    """Asynchronous garbage collection"""
    await asyncio.sleep(0)  # Yield to event loop
    gc.collect()
```

### Step 6: Health Checks and Readiness Probes

#### Health Check Endpoint

Implement comprehensive health checks for monitoring.

**Python Implementation:**

```python
from enum import Enum
from typing import Dict, List, Optional
import asyncio

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    """Single health check result"""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    details: Optional[Dict] = None

class HealthChecker:
    """Comprehensive health checking"""

    def __init__(
        self,
        db_pool,
        redis_client,
        llm_pool
    ):
        self.db_pool = db_pool
        self.redis_client = redis_client
        self.llm_pool = llm_pool

    async def check_database(self) -> HealthCheck:
        """Check database connectivity"""
        start = time.time()

        try:
            # Simple ping query
            result = await self.db_pool.execute('SELECT 1')

            latency = (time.time() - start) * 1000

            # Check pool stats
            stats = self.db_pool.get_stats()

            if stats['utilization'] > 0.9:
                return HealthCheck(
                    name='database',
                    status=HealthStatus.DEGRADED,
                    message='Connection pool near capacity',
                    latency_ms=latency,
                    details=stats
                )

            return HealthCheck(
                name='database',
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                details=stats
            )

        except Exception as e:
            return HealthCheck(
                name='database',
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )

    async def check_redis(self) -> HealthCheck:
        """Check Redis connectivity"""
        start = time.time()

        try:
            # Ping Redis
            await self.redis_client.ping()

            latency = (time.time() - start) * 1000

            # Check memory usage
            info = await self.redis_client.info('memory')
            used_memory_pct = info['used_memory'] / info['maxmemory'] if info.get('maxmemory') else 0

            if used_memory_pct > 0.9:
                return HealthCheck(
                    name='redis',
                    status=HealthStatus.DEGRADED,
                    message='Redis memory usage high',
                    latency_ms=latency,
                    details={'memory_percent': used_memory_pct * 100}
                )

            return HealthCheck(
                name='redis',
                status=HealthStatus.HEALTHY,
                latency_ms=latency
            )

        except Exception as e:
            return HealthCheck(
                name='redis',
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )

    async def check_llm_provider(self) -> HealthCheck:
        """Check LLM provider connectivity"""
        start = time.time()

        try:
            # Simple test request
            async with self.llm_pool:
                response = await self.llm_pool.execute({
                    'url': 'https://api.openai.com/v1/models',
                    'headers': {'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'},
                    'body': {}
                })

            latency = (time.time() - start) * 1000

            # Check pool stats
            stats = self.llm_pool.get_stats()

            if stats['utilization'] > 0.9:
                return HealthCheck(
                    name='llm_provider',
                    status=HealthStatus.DEGRADED,
                    message='LLM connection pool near capacity',
                    latency_ms=latency,
                    details=stats
                )

            return HealthCheck(
                name='llm_provider',
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                details=stats
            )

        except Exception as e:
            return HealthCheck(
                name='llm_provider',
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )

    async def check_memory(self) -> HealthCheck:
        """Check memory usage"""
        memory_info = memory_monitor.get_memory_info()

        percent = memory_info['system']['percent']

        if percent > 90:
            status = HealthStatus.UNHEALTHY
            message = 'Critical memory pressure'
        elif percent > 80:
            status = HealthStatus.DEGRADED
            message = 'High memory usage'
        else:
            status = HealthStatus.HEALTHY
            message = None

        return HealthCheck(
            name='memory',
            status=status,
            message=message,
            details=memory_info
        )

    async def check_all(self) -> Dict:
        """Run all health checks"""
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_llm_provider(),
            self.check_memory()
        )

        # Overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            'status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': [
                {
                    'name': c.name,
                    'status': c.status.value,
                    'message': c.message,
                    'latency_ms': c.latency_ms,
                    'details': c.details
                }
                for c in checks
            ]
        }

# FastAPI endpoints
health_checker = HealthChecker(db_pool, redis_client, llm_pool)

@app.get('/health')
async def health_check():
    """Health check endpoint (for load balancer)"""
    result = await health_checker.check_all()

    # Return 200 if healthy or degraded, 503 if unhealthy
    status_code = 200 if result['status'] != 'unhealthy' else 503

    return JSONResponse(content=result, status_code=status_code)

@app.get('/ready')
async def readiness_check():
    """Readiness probe (for Kubernetes)"""
    # Check if server is ready to accept traffic
    result = await health_checker.check_all()

    # Only ready if all checks are healthy
    is_ready = result['status'] == 'healthy'

    status_code = 200 if is_ready else 503

    return JSONResponse(
        content={'ready': is_ready, 'checks': result['checks']},
        status_code=status_code
    )

@app.get('/live')
async def liveness_check():
    """Liveness probe (for Kubernetes)"""
    # Simple check - is process alive?
    return {'alive': True}
```

### Step 7: Circuit Breakers and Resilience

#### Circuit Breaker Pattern

Implement circuit breakers to prevent cascading failures.

**Python Implementation:**

```python
from enum import Enum
from dataclasses import dataclass
import time
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes before closing
    timeout: float = 60.0  # Seconds before trying half-open

class CircuitBreaker:
    """Circuit breaker for external service calls"""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if time.time() - self.last_failure_time >= self.config.timeout:
                logger.info(f'Circuit breaker {self.name}: transitioning to half-open')
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                # Still open - reject immediately
                raise CircuitBreakerOpenError(
                    f'Circuit breaker {self.name} is open',
                    retry_after=self.config.timeout - (time.time() - self.last_failure_time)
                )

        try:
            # Execute function
            result = func(*args, **kwargs)

            # Success
            self._on_success()

            return result

        except Exception as e:
            # Failure
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.config.success_threshold:
                logger.info(f'Circuit breaker {self.name}: closing (recovered)')
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery - back to open
            logger.warning(f'Circuit breaker {self.name}: failed during half-open, reopening')
            self.state = CircuitState.OPEN
            self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                logger.error(f'Circuit breaker {self.name}: opening due to failures')
                self.state = CircuitState.OPEN

    def get_state(self) -> Dict:
        """Get circuit breaker state"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time,
            'time_until_half_open': (
                self.config.timeout - (time.time() - self.last_failure_time)
                if self.state == CircuitState.OPEN and self.last_failure_time
                else 0
            )
        }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    def __init__(self, message: str, retry_after: float):
        super().__init__(message)
        self.retry_after = retry_after

# Circuit breakers for external services
llm_circuit_breaker = CircuitBreaker(
    'llm_provider',
    CircuitBreakerConfig(failure_threshold=5, timeout=60.0)
)

db_circuit_breaker = CircuitBreaker(
    'database',
    CircuitBreakerConfig(failure_threshold=3, timeout=30.0)
)

# Usage
async def execute_run_with_circuit_breaker(request):
    """Execute run with circuit breaker protection"""
    try:
        # Call LLM with circuit breaker
        response = await llm_circuit_breaker.call(
            llm_client.generate,
            request
        )

        # Store in database with circuit breaker
        await db_circuit_breaker.call(
            db_pool.execute,
            'INSERT INTO runs (...) VALUES (...)',
            response.run_id,
            response.status
        )

        return response

    except CircuitBreakerOpenError as e:
        # Circuit breaker open - return graceful error
        raise HTTPException(
            status_code=503,
            detail={
                'error': 'service_unavailable',
                'message': str(e),
                'retry_after': e.retry_after
            }
        )

# Monitor circuit breaker state
@app.get('/circuit-breakers')
async def get_circuit_breaker_states():
    """Get all circuit breaker states"""
    return {
        'circuit_breakers': [
            llm_circuit_breaker.get_state(),
            db_circuit_breaker.get_state()
        ]
    }
```

### Step 8: Configuration and Secret Management

#### Environment-Based Configuration

Implement configuration management for different environments.

**Python Implementation:**

```python
from pydantic import BaseSettings, SecretStr, validator
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Environment
    environment: str = 'development'

    # Server
    host: str = '0.0.0.0'
    port: int = 8000
    workers: int = 4

    # Database
    database_url: SecretStr
    database_pool_min: int = 10
    database_pool_max: int = 100

    # Redis
    redis_url: str
    redis_max_connections: int = 50

    # LLM Provider
    openai_api_key: SecretStr
    anthropic_api_key: Optional[SecretStr] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[SecretStr] = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_free_tier: int = 100
    rate_limit_pro_tier: int = 1000

    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    jaeger_agent_host: str = 'localhost'
    jaeger_agent_port: int = 6831

    # Logging
    log_level: str = 'INFO'
    structured_logging: bool = True

    # Performance
    max_concurrent_runs: int = 100
    request_timeout: int = 300
    connection_pool_size: int = 100

    # Security
    cors_origins: list = ['http://localhost:3000']
    api_key_required: bool = True

    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'Environment must be one of {allowed}')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of {allowed}')
        return v.upper()

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

# Load settings
settings = Settings()

# Environment-specific overrides
if settings.environment == 'production':
    # Production-specific settings
    settings.log_level = 'WARNING'
    settings.workers = 8
    settings.database_pool_max = 200
    settings.api_key_required = True

elif settings.environment == 'staging':
    # Staging-specific settings
    settings.log_level = 'INFO'
    settings.workers = 4

elif settings.environment == 'development':
    # Development-specific settings
    settings.log_level = 'DEBUG'
    settings.workers = 1
    settings.api_key_required = False
```

**Example .env file:**

```bash
# .env
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@db-host:5432/agent_runtime
DATABASE_POOL_MIN=20
DATABASE_POOL_MAX=200

# Redis
REDIS_URL=redis://redis-host:6379/0

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_OPENAI_ENDPOINT=https://my-resource.openai.azure.com
AZURE_OPENAI_API_KEY=...

# Rate Limiting
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PRO_TIER=1000

# Monitoring
PROMETHEUS_ENABLED=true
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831

# Logging
LOG_LEVEL=WARNING
STRUCTURED_LOGGING=true

# Performance
MAX_CONCURRENT_RUNS=100
CONNECTION_POOL_SIZE=200

# Security
CORS_ORIGINS=["https://app.example.com"]
API_KEY_REQUIRED=true
```

#### Kubernetes Secrets

**Kubernetes Secret Definition:**

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-api-secrets
type: Opaque
stringData:
  database-url: postgresql://user:pass@postgres:5432/agent_runtime
  openai-api-key: sk-...
  anthropic-api-key: sk-ant-...
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-api-config
data:
  environment: production
  redis-url: redis://redis:6379/0
  log-level: WARNING
  max-concurrent-runs: "100"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
spec:
  template:
    spec:
      containers:
      - name: agent-api
        image: agent-api:latest
        env:
        # From ConfigMap
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: agent-api-config
              key: environment
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: agent-api-config
              key: redis-url
        # From Secret
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agent-api-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-api-secrets
              key: openai-api-key
```

## Examples

### Example 1: Complete Docker Deployment

**Dockerfile:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

**docker-compose.yml:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent-api:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://agent:agent@postgres:5432/agent_runtime
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - agent-network
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=agent_runtime
      - POSTGRES_USER=agent
      - POSTGRES_PASSWORD=agent
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - agent-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - agent-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - agent-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - agent-network
    restart: unless-stopped

networks:
  agent-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:
```

**Run:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f agent-api

# Scale API servers
docker-compose up -d --scale agent-api=3

# Check health
curl http://localhost:8000/health

# View metrics
curl http://localhost:9090/metrics
```

### Example 2: Kubernetes Production Deployment

**Complete Kubernetes manifest:**

```yaml
# kubernetes-production.yaml

# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: agent-runtime

---
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-api-config
  namespace: agent-runtime
data:
  environment: "production"
  redis-url: "redis://redis:6379/0"
  log-level: "WARNING"
  max-concurrent-runs: "100"
  prometheus-port: "9090"

---
# Secrets (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: agent-api-secrets
  namespace: agent-runtime
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bob3N0OjU0MzIvZGI=
  openai-api-key: c2stLi4u

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
  namespace: agent-runtime
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-api
  template:
    metadata:
      labels:
        app: agent-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: agent-api
        image: agent-api:v1.0.0
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: agent-api-config
              key: environment
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agent-api-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-api-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: agent-api
  namespace: agent-runtime
spec:
  selector:
    app: agent-api
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer

---
# HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-api-hpa
  namespace: agent-runtime
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max

---
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: agent-api-pdb
  namespace: agent-runtime
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: agent-api
```

**Deploy:**

```bash
# Apply manifests
kubectl apply -f kubernetes-production.yaml

# Check deployment
kubectl -n agent-runtime get pods
kubectl -n agent-runtime get svc

# View logs
kubectl -n agent-runtime logs -f deployment/agent-api

# Scale manually
kubectl -n agent-runtime scale deployment agent-api --replicas=5

# Check HPA status
kubectl -n agent-runtime get hpa

# Port forward for testing
kubectl -n agent-runtime port-forward svc/agent-api 8000:80
```

### Example 3: Blue-Green Deployment

**Blue-Green deployment strategy:**

```yaml
# blue-green-deployment.yaml

# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api-blue
  namespace: agent-runtime
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-api
      version: blue
  template:
    metadata:
      labels:
        app: agent-api
        version: blue
    spec:
      containers:
      - name: agent-api
        image: agent-api:v1.0.0  # Current version
        # ... same config as before

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api-green
  namespace: agent-runtime
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-api
      version: green
  template:
    metadata:
      labels:
        app: agent-api
        version: green
    spec:
      containers:
      - name: agent-api
        image: agent-api:v1.1.0  # New version
        # ... same config as before

---
# Service (routes to blue initially)
apiVersion: v1
kind: Service
metadata:
  name: agent-api
  namespace: agent-runtime
spec:
  selector:
    app: agent-api
    version: blue  # Currently pointing to blue
  ports:
  - port: 80
    targetPort: 8000
```

**Deployment script:**

```bash
#!/bin/bash
# blue-green-deploy.sh

# Deploy green (new version)
kubectl apply -f blue-green-deployment.yaml

# Wait for green to be ready
kubectl -n agent-runtime rollout status deployment/agent-api-green

# Run smoke tests on green
echo "Running smoke tests on green deployment..."
GREEN_POD=$(kubectl -n agent-runtime get pod -l version=green -o jsonpath='{.items[0].metadata.name}')
kubectl -n agent-runtime port-forward $GREEN_POD 8001:8000 &
PF_PID=$!

sleep 5
curl http://localhost:8001/health || {
    echo "Health check failed on green deployment"
    kill $PF_PID
    exit 1
}

kill $PF_PID

# Switch traffic to green
echo "Switching traffic to green..."
kubectl -n agent-runtime patch service agent-api -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for 5 minutes
echo "Monitoring green deployment..."
sleep 300

# Check error rate
ERROR_RATE=$(kubectl -n agent-runtime exec deployment/agent-api-green -- curl -s http://localhost:9090/metrics | grep error_rate | awk '{print $2}')

if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
    echo "Error rate too high, rolling back..."
    kubectl -n agent-runtime patch service agent-api -p '{"spec":{"selector":{"version":"blue"}}}'
    exit 1
fi

# Success - delete blue deployment
echo "Deployment successful, removing blue deployment..."
kubectl -n agent-runtime delete deployment agent-api-blue

# Rename green to blue for next deployment
kubectl -n agent-runtime patch deployment agent-api-green --type json -p '[{"op": "replace", "path": "/metadata/name", "value": "agent-api-blue"}]'
kubectl -n agent-runtime patch deployment agent-api-green --type json -p '[{"op": "replace", "path": "/spec/selector/matchLabels/version", "value": "blue"}]'

echo "Blue-green deployment complete!"
```

## Troubleshooting

### Issue 1: High Memory Usage

**Problem**: API servers running out of memory

**Diagnosis:**

```python
# Check memory usage
memory_info = memory_monitor.get_memory_info()
print(f"Memory usage: {memory_info['process']['percent']}%")

# Find memory leaks
large_objects = memory_monitor.get_large_objects(limit=20)
for obj in large_objects:
    print(f"{obj['type']}: {obj['size'] / 1024 / 1024:.2f} MB")

# Check connection pools
print(f"DB pool: {db_pool.get_stats()}")
print(f"LLM pool: {llm_pool.get_stats()}")
```

**Solutions:**

1. **Enable connection pooling limits**
2. **Implement request timeout limits**
3. **Add memory-based request rejection**
4. **Increase container memory limits**
5. **Enable aggressive garbage collection**

### Issue 2: Rate Limit Exceeded

**Problem**: Users hitting rate limits frequently

**Diagnosis:**

```bash
# Check rate limit metrics
curl http://localhost:9090/metrics | grep rate_limit

# Check Redis rate limit keys
redis-cli --scan --pattern 'rate_limit:*'
```

**Solutions:**

1. **Adjust rate limit tiers**
2. **Implement request queueing**
3. **Add burst capacity**
4. **Upgrade user tier**

### Issue 3: Database Connection Pool Exhausted

**Problem**: "Too many database connections" errors

**Diagnosis:**

```python
# Check pool stats
stats = db_pool.get_stats()
print(f"Pool utilization: {stats['utilization'] * 100}%")
print(f"Active: {stats['used']}, Free: {stats['free']}")
```

**Solutions:**

1. **Increase pool size**
2. **Reduce connection idle timeout**
3. **Implement connection queuing**
4. **Add read replicas**

### Issue 4: Circuit Breaker Open

**Problem**: Circuit breaker preventing requests

**Diagnosis:**

```python
# Check circuit breaker state
state = llm_circuit_breaker.get_state()
print(f"State: {state['state']}")
print(f"Failures: {state['failure_count']}")
print(f"Time until retry: {state['time_until_half_open']}s")
```

**Solutions:**

1. **Wait for automatic recovery**
2. **Manually reset circuit breaker**
3. **Check LLM provider status**
4. **Increase failure threshold**

### Issue 5: Slow Response Times

**Problem**: High P99 latency

**Diagnosis:**

```bash
# Check latency metrics
curl http://localhost:9090/metrics | grep duration_seconds

# Check traces in Jaeger
# Look for slow spans
```

**Solutions:**

1. **Enable prompt caching**
2. **Implement request batching**
3. **Add more workers**
4. **Optimize database queries**
5. **Use faster LLM models**

## Next Steps

**Advanced Topics:**

1. **[Multi-Region Deployment](multi-region-deployment.md)** - Global distribution
2. **[Disaster Recovery](disaster-recovery.md)** - Backup and recovery
3. **[Security Hardening](security-hardening.md)** - Production security
4. **[Cost Optimization](cost-optimization.md)** - Reduce operational costs
5. **[Performance Tuning](performance-tuning.md)** - Advanced optimization

**Related Documentation:**

- **[Getting Started](getting-started.md)** - Basic integration
- **[Run Lifecycle Specification](../specifications/run-lifecycle.md)** - Run states
- **[Streaming Specification](../specifications/streaming.md)** - SSE patterns
- **[Usage Tracking](../typespec/usage.tsp)** - Token tracking models
- **[Error Handling](../specifications/error-handling.md)** - Error strategies
