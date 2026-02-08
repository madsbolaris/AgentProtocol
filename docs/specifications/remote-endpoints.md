# Remote Endpoints Specification

**Version**: 1.0

## Overview

This specification defines the WebSocket and HTTP protocols for remote condition evaluators and remote hook handlers.

**Key Concepts:**
- **Remote Condition**: External service evaluates whether agent should participate
- **Remote Hook**: External service intercepts and responds to runtime events
- **WebSocket Protocol**: Persistent connection for run-scoped evaluation (preferred)
- **HTTP Fallback**: Per-request evaluation when WebSocket unavailable
- **Connection Types**: Authentication patterns for remote endpoints

**Use Cases:**
- Custom authorization logic
- External system integration
- Complex business rules
- Compliance requirements
- Multi-system workflows

## Protocol Selection

### WebSocket (Preferred)

**When to Use:**
- Run-scoped evaluation (multiple events per run)
- Real-time streaming scenarios
- Low-latency requirements
- Stateful evaluation logic

**Advantages:**
- Single connection per run (lower overhead)
- Lower latency (no connection setup per event)
- Bidirectional communication
- Connection state awareness

**Disadvantages:**
- More complex implementation
- Requires WebSocket support
- Connection management overhead

### HTTP (Fallback)

**When to Use:**
- WebSocket unavailable (network restrictions, client limitations)
- Stateless evaluation logic
- Simple request/response scenarios
- Testing and development

**Advantages:**
- Simple implementation
- Universal support
- Stateless (no connection management)
- Easy debugging

**Disadvantages:**
- Higher latency (connection setup per request)
- Higher overhead (more network round-trips)
- No connection state

### Automatic Fallback

**Server Behavior:**
1. Attempt WebSocket connection first
2. If WebSocket fails (handshake timeout, connection refused):
   - Fall back to HTTP POST for each evaluation
   - Log fallback event
3. If HTTP also fails: Apply timeout fallback behavior

**Fallback Triggers:**
- WebSocket handshake timeout (5s)
- WebSocket connection refused
- Network restrictions (firewall blocks WebSocket)
- Server doesn't support WebSocket upgrade

## WebSocket Protocol

### Connection Lifecycle

#### 1. Handshake

**Client → Server:**
```http
GET /evaluate HTTP/1.1
Host: conditions.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Version: 13
Authorization: Bearer hook_secret_123
```

**Server → Client:**
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
```

**Timeout**: 5s (not configurable)

**Authentication**: Provided via HTTP headers during handshake (Authorization, X-API-Key, etc.)

**Failure Handling**: If handshake fails, fall back to HTTP

#### 2. Initialization Message

**Purpose**: Establish context for subsequent evaluations

**Client → Server:**
```json
{
  "type": "init",
  "runId": "run_123",
  "threadId": "thread_456",
  "agentId": "agent_789",
  "context": {
    "userId": "user_1",
    "tenantId": "tenant_1"
  }
}
```

**Server → Client:**
```json
{
  "type": "init_ack",
  "status": "ready"
}
```

**Timing**: Sent immediately after handshake completes

**Buffering**: Server buffers events during initialization (max 1000 events or 10s)

#### 3. Event Messages

**Purpose**: Evaluate conditions or process hook events

**Client → Server (Condition Evaluation):**
```json
{
  "type": "evaluate",
  "eventSeq": 1,
  "threadId": "thread_456",
  "agentId": "agent_789",
  "lastMessage": {
    "role": "user",
    "contents": [
      {
        "kind": "text",
        "text": "Hello, I need help"
      }
    ]
  },
  "context": {
    "messageCount": 5,
    "participants": ["user_1", "agent_789"]
  }
}
```

**Server → Client (Condition Response):**
```json
{
  "type": "evaluate_response",
  "eventSeq": 1,
  "shouldRun": true,
  "reason": "User message detected"
}
```

**Client → Server (Hook Event):**
```json
{
  "kind": "event",
  "eventSeq": 2,
  "eventType": "content.created",
  "runId": "run_123",
  "content": [
    {
      "kind": "text",
      "text": "Here's how to reset your password..."
    }
  ],
  "context": {
    "userId": "user_1",
    "timestamp": "2026-02-06T10:00:00Z"
  }
}
```

**Server → Client (Hook Response):**
```json
{
  "type": "event_response",
  "eventSeq": 2,
  "action": {
    "kind": "allow",
    "reason": "Content approved"
  }
}
```

**Event Sequencing:**
- `eventSeq` field monotonically increases per connection
- Server must respond with same `eventSeq`
- Client may send next event before receiving response (pipelining)

**Timeout**: 5s default, 30s max (configurable per event)

#### 4. Cleanup Message

**Purpose**: Notify server that run/evaluation is complete

**Client → Server:**
```json
{
  "type": "cleanup",
  "runId": "run_123",
  "status": "completed"
}
```

**Server → Client:**
```json
{
  "type": "cleanup_ack"
}
```

**Timing**: Sent when run reaches terminal status (completed, failed, cancelled)

**Connection Close**: After cleanup_ack, client closes connection with code 1000 (normal closure)

### Message Types

| Type | Direction | Purpose | Response Required |
|------|-----------|---------|-------------------|
| `init` | Client → Server | Initialize connection | Yes (`init_ack`) |
| `init_ack` | Server → Client | Acknowledge initialization | No |
| `evaluate` | Client → Server | Evaluate condition | Yes (`evaluate_response`) |
| `evaluate_response` | Server → Client | Condition result | No |
| `event` | Client → Server | Hook event | Yes (`event_response`) |
| `event_response` | Server → Client | Hook action | No |
| `cleanup` | Client → Server | Run complete | Yes (`cleanup_ack`) |
| `cleanup_ack` | Server → Client | Acknowledge cleanup | No |
| `error` | Server → Client | Error occurred | No |
| `ping` | Client ↔ Server | Keep-alive | Yes (`pong`) |
| `pong` | Client ↔ Server | Keep-alive response | No |

### Error Messages

**Server → Client:**
```json
{
  "type": "error",
  "eventSeq": 3,
  "code": "INVALID_REQUEST",
  "message": "Missing required field: lastMessage"
}
```

**Error Codes:**
- `INVALID_REQUEST` - Malformed request
- `UNAUTHORIZED` - Authentication failed
- `EVALUATION_FAILED` - Evaluation error
- `TIMEOUT` - Evaluation timeout
- `INTERNAL_ERROR` - Server error

**Behavior:**
- For recoverable errors (TIMEOUT, INTERNAL_ERROR): Client may retry
- For non-recoverable errors (INVALID_REQUEST, UNAUTHORIZED): Client applies fallback immediately

### Keep-Alive

**Purpose**: Detect connection failures, prevent idle timeouts

**Ping Interval**: 30s (recommended)

**Client → Server:**
```json
{
  "type": "ping",
  "timestamp": "2026-02-06T10:00:00Z"
}
```

**Server → Client:**
```json
{
  "type": "pong",
  "timestamp": "2026-02-06T10:00:01Z"
}
```

**Timeout**: 10s (if no pong received, close connection and apply fallback)

### Connection Close

**Normal Closure (Code 1000):**
```javascript
websocket.close(1000, "Run completed successfully");
```

**Going Away (Code 1001):**
```javascript
websocket.close(1001, "Server maintenance - please reconnect");
// Client attempts reconnection or HTTP fallback
```

**Unsupported Data (Code 1003):**
```javascript
websocket.close(1003, "Invalid JSON format");
// Client applies fallback immediately
```

**Policy Violation (Code 1008):**
```javascript
websocket.close(1008, "Invalid eventSeq reference");
// Client applies fallback immediately
```

**Server Error (Code 1011):**
```javascript
websocket.close(1011, "Internal server error");
// Client retries connection with backoff
```

**Source**: [Error Handling Specification](./error-handling.md) - WebSocket Close Codes

## HTTP Protocol

### Request Format

**Condition Evaluation:**
```http
POST /evaluate HTTP/1.1
Host: conditions.example.com
Content-Type: application/json
Authorization: Bearer hook_secret_123

{
  "threadId": "thread_456",
  "agentId": "agent_789",
  "lastMessage": {
    "role": "user",
    "contents": [
      {
        "kind": "text",
        "text": "Hello, I need help"
      }
    ]
  },
  "context": {
    "messageCount": 5,
    "participants": ["user_1", "agent_789"]
  }
}
```

**Hook Event:**
```http
POST /hook HTTP/1.1
Host: hooks.example.com
Content-Type: application/json
X-API-Key: hook_api_key_456

{
  "eventType": "content.created",
  "runId": "run_123",
  "content": [
    {
      "kind": "text",
      "text": "Here's how to reset your password..."
    }
  ],
  "context": {
    "userId": "user_1",
    "timestamp": "2026-02-06T10:00:00Z"
  }
}
```

### Response Format

**Condition Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "shouldRun": true,
  "reason": "User message detected"
}
```

**Hook Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "action": {
    "kind": "allow",
    "reason": "Content approved"
  }
}
```

### HTTP Status Codes

| Status | Meaning | Client Behavior |
|--------|---------|-----------------|
| 200 OK | Success | Use response |
| 400 Bad Request | Invalid request | Apply fallback immediately |
| 401 Unauthorized | Auth failed | Apply fallback immediately |
| 403 Forbidden | Permission denied | Apply fallback immediately |
| 404 Not Found | Endpoint not found | Try WebSocket if HTTP |
| 408 Timeout | Server timeout | Retry up to 3x, then fallback |
| 429 Rate Limited | Too many requests | Retry with backoff, then fallback |
| 500 Internal Server Error | Server error | Retry up to 3x, then fallback |
| 503 Service Unavailable | Temporarily unavailable | Retry up to 3x, then fallback |

**Retry Strategy**: Exponential backoff (100ms, 200ms, 400ms) for 408, 429, 500, 503

**Source**: [Error Handling Specification](./error-handling.md)

### HTTP Headers

**Authentication Headers:**

**Bearer Token:**
```http
Authorization: Bearer hook_secret_123
```

**API Key:**
```http
X-API-Key: api_key_456
```

**Basic Auth:**
```http
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

**Source**: [Authentication Specification](./authentication.md) - Connection HTTP Headers

## Connection Types

**TypeSpec**: See `Connection` union in `typespec/common.tsp`

### ApiKeyConnection

**Used For**: API key authentication

```json
{
  "kind": "key",
  "key": "Bearer hook_secret_123",
  "headerName": "Authorization"
}
```

**HTTP Header:**
```http
Authorization: Bearer hook_secret_123
```

**WebSocket Handshake:**
```http
Authorization: Bearer hook_secret_123
```

### RemoteConnection

**Used For**: OAuth2, Basic Auth, custom credentials

```json
{
  "kind": "remote",
  "endpoint": "https://hooks.example.com",
  "credentials": {
    "clientId": "client_123",
    "clientSecret": "secret_456",
    "tokenEndpoint": "https://auth.example.com/token"
  }
}
```

**OAuth2 Flow:**
1. Request access token from token endpoint
2. Use access token in requests

**HTTP Header:**
```http
Authorization: Bearer <access_token>
```

### ReferenceConnection

**Used For**: Named connection reference

```json
{
  "kind": "reference",
  "name": "myHookConnection"
}
```

**Behavior**: Resolves to underlying connection (ApiKey or Remote), then uses that connection's authentication

### AnonymousConnection

**Used For**: No authentication

```json
{
  "kind": "anonymous"
}
```

**HTTP Headers**: None

## Timeout Configuration

| Operation | Default | Maximum | Configurable |
|-----------|---------|---------|--------------|
| WebSocket handshake | 5s | - | No |
| WebSocket event | 5s | 30s | Yes |
| HTTP request | 2s | 10s | Yes |
| Keep-alive ping | 10s | - | No |

**Source**: [Error Handling Specification](./error-handling.md) - Timeout Values

**Configuration Example:**
```json
{
  "remoteCondition": {
    "kind": "remote",
    "endpoint": "https://conditions.example.com",
    "timeout": 10000  // 10s (milliseconds)
  }
}
```

## Error Handling

### Network Errors

| Error | Retry | Fallback |
|-------|-------|----------|
| Connection refused | Yes (3x) | HTTP → Fail-closed |
| DNS failure | No | Fail-closed immediately |
| Timeout | Yes (3x) | Event-type-based (hooks) / Fail-closed (conditions) |
| SSL/TLS error | No | Fail-closed immediately |

### Protocol Errors

| Error | HTTP Status | WebSocket Close | Behavior |
|-------|-------------|-----------------|----------|
| Invalid JSON | 400 | 1003 | Apply fallback immediately |
| Missing required field | 400 | 1008 | Apply fallback immediately |
| Invalid eventSeq | 400 | 1008 | Apply fallback immediately |
| Unauthorized | 401 | 1008 | Apply fallback immediately |

### Fallback Behavior

**Conditions**: Always fail-closed (return `false`)

**Hooks**: Event-type-based
- Early events (run.started, content.created): BLOCK
- Late events (content.updated, message.completed): ALLOW

**Source**: [Error Handling Specification](./error-handling.md) - Fallback Strategies

## Security Requirements

### HTTPS/WSS Only

**Requirement**: All remote endpoints MUST use HTTPS or WSS

**Rationale**: Protects sensitive data (PII, credentials) in transit

**Enforcement**: Server rejects HTTP/WS endpoints

### Endpoint Validation

**Restrictions:**
- No localhost/127.0.0.1
- No internal IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Must be valid URL format
- Must use standard ports (443 for HTTPS, 443 for WSS) or explicit port

**Rationale**: Prevents SSRF attacks, internal network access

### Authentication Required

**Requirement**: Remote endpoints SHOULD require authentication

**Supported Methods:**
- Bearer tokens
- API keys
- OAuth2
- Basic authentication
- Custom headers

**Anonymous Endpoints**: Allowed but discouraged (security risk)

### Rate Limiting

**Recommendation**: Implement rate limiting on remote endpoints

**Typical Limits:**
- 100 requests/minute per tenant
- 10 concurrent connections per tenant

**Behavior on Rate Limit**: Return 429, client retries with backoff

## Requirements

### Server Requirements

Servers MUST:

1. **WebSocket Support**: Implement WebSocket protocol for run-scoped evaluation
2. **HTTP Fallback**: Fall back to HTTP when WebSocket unavailable
3. **Authentication**: Support all Connection types
4. **Timeout Enforcement**: Enforce configurable timeouts
5. **Retry Logic**: Retry failed requests up to 3 times
6. **Fallback Behavior**: Apply correct fallback (fail-closed for conditions, event-type-based for hooks)
7. **HTTPS/WSS Only**: Reject non-secure endpoints

Servers SHOULD:

1. **Connection Pooling**: Reuse connections where possible
2. **Error Logging**: Log all remote endpoint failures
3. **Metrics**: Track endpoint success/failure rates
4. **Circuit Breaker**: Implement circuit breaker for failing endpoints

### Remote Endpoint Requirements

Remote endpoints MUST:

1. **Protocol Support**: Support WebSocket OR HTTP (WebSocket preferred)
2. **Response Format**: Return valid JSON responses
3. **Timeout Compliance**: Respond within timeout period
4. **Authentication**: Validate authentication on every request
5. **Error Handling**: Return appropriate HTTP status codes or WebSocket close codes

Remote endpoints SHOULD:

1. **Keep-Alive**: Respond to ping messages (WebSocket)
2. **Stateless**: Design for stateless evaluation (easier failover)
3. **Idempotent**: Support retries (same request may arrive multiple times)
4. **Logging**: Log all evaluation requests for debugging

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/common.tsp` (Connection types, RemoteCondition)
- **TypeSpec**: `typespec/execution.tsp` (RemoteHook)
- **WebSocket**: RFC 6455 (The WebSocket Protocol)
- **HTTP**: RFC 7231 (HTTP/1.1 Semantics and Content)
- **Error Handling**: [Error Handling Specification](./error-handling.md)
- **Authentication**: [Authentication Specification](./authentication.md)

## See Also

- [Agent Auto-Response Specification](./agent-auto-response.md) - Remote conditions
- [Hooks Specification](./hooks.md) - Remote hooks
- [Error Handling](./error-handling.md) - Timeout and fallback behavior
- [Authentication](./authentication.md) - Connection types and authentication patterns
