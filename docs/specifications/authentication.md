# Authentication Specification

**Version**: 1.0

## Overview

This specification defines authentication flows, connection types, OAuth2 scope enforcement, and authorization patterns for the Agent Runtime API.

**Key Concepts:**
- **Connection**: Authentication configuration (reference, remote, API key, anonymous)
- **Scopes**: OAuth2 permissions required by agents and tools
- **Authority**: Authorization level (user vs system credentials)
- **Consent**: User authorization for agent access

## Connection Model

### Connection Types

**TypeSpec**: See `Connection` union in `typespec/common.tsp`

```typescript
union Connection {
  ReferenceConnection,  // Named connection reference
  RemoteConnection,     // Remote service endpoint
  ApiKeyConnection,     // API key authentication
  AnonymousConnection,  // No authentication
}
```

### ReferenceConnection

**Purpose**: Reference to pre-configured named connection

**TypeSpec**: See `ReferenceConnection` model in `typespec/common.tsp`

```typescript
model ReferenceConnection {
  kind: "reference";
  name: string;                         // Connection reference name
  authority?: "user" | "system";        // Authorization level
  usageDescription?: string;            // Transparency text
}
```

**Example:**
```json
{
  "kind": "reference",
  "name": "myOpenAIConnection",
  "authority": "user",
  "usageDescription": "Access OpenAI API to generate responses"
}
```

**Use Cases:**
- Reuse configured connections
- Avoid credential duplication
- Centralized connection management

### ApiKeyConnection

**Purpose**: API key-based authentication

**TypeSpec**: See `ApiKeyConnection` model in `typespec/common.tsp`

```typescript
model ApiKeyConnection {
  kind: "key";
  key: string;                          // API key value
  headerName?: string = "Authorization"; // Header name
  authority?: "user" | "system";
  usageDescription?: string;
}
```

**Example:**
```json
{
  "kind": "key",
  "key": "sk-proj-abc123...",
  "headerName": "Authorization",
  "authority": "system",
  "usageDescription": "Access LLM provider API"
}
```

**Use Cases:**
- OpenAI API keys
- Slack bot tokens
- Custom API authentication

### RemoteConnection

**Purpose**: Remote service with endpoint and credentials

**TypeSpec**: See `RemoteConnection` model in `typespec/common.tsp`

```typescript
model RemoteConnection {
  kind: "remote";
  endpoint: string;                     // Service URL
  credentials?: Record<unknown>;        // Flexible credentials
  authority?: "user" | "system";
  usageDescription?: string;
}
```

**Example:**
```json
{
  "kind": "remote",
  "endpoint": "https://api.example.com",
  "credentials": {
    "clientId": "client_123",
    "clientSecret": "secret_456"
  },
  "authority": "user",
  "usageDescription": "Access company API for data retrieval"
}
```

**Use Cases:**
- MCP servers
- Custom enterprise APIs
- Microservice authentication

### AnonymousConnection

**Purpose**: No authentication required

**TypeSpec**: See `AnonymousConnection` model in `typespec/common.tsp`

```typescript
model AnonymousConnection {
  kind: "anonymous";
  authority?: "user" | "system";
  usageDescription?: string;
}
```

**Example:**
```json
{
  "kind": "anonymous",
  "authority": "system",
  "usageDescription": "Access public weather API"
}
```

**Use Cases:**
- Public APIs
- No authentication needed
- Anonymous tool execution

## HTTP Authentication Headers

**Connection Type to HTTP Header Mapping:**

This section shows how each `Connection` type maps to HTTP authentication headers when making requests to remote services (hooks, conditions, tools, MCP servers).

**Source**: agent-auto-response.md, hooks.md - Connection types used for remote endpoints

### ApiKeyConnection HTTP Headers

**Pattern 1: Custom Header (default):**
```http
X-API-Key: sk-proj-abc123...
```

**Pattern 2: Authorization Header:**
```http
Authorization: sk-proj-abc123...
```

**Pattern 3: Bearer Token:**
```http
Authorization: Bearer sk-proj-abc123...
```

**Connection Config:**
```json
{
  "kind": "key",
  "key": "sk-proj-abc123...",
  "headerName": "X-API-Key"  // or "Authorization"
}
```

**Implementation:**
```typescript
// Client-side request
const headers = {
  [connection.headerName || "Authorization"]: connection.key
};

fetch(endpoint, { headers });
```

### RemoteConnection HTTP Headers

**OAuth2 Bearer Token:**
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Basic Authentication:**
```http
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

**Custom Credentials:**
```http
X-Client-ID: client_123
X-Client-Secret: secret_456
```

**Connection Config Examples:**

**OAuth2:**
```json
{
  "kind": "remote",
  "endpoint": "https://hooks.example.com",
  "credentials": {
    "tokenEndpoint": "https://login.example.com/token",
    "clientId": "client_123",
    "clientSecret": "secret_456",
    "scope": "hooks:execute"
  }
}
```

**Basic Auth:**
```json
{
  "kind": "remote",
  "endpoint": "https://api.example.com",
  "credentials": {
    "username": "user",
    "password": "pass"
  }
}
```

**Implementation:**
```typescript
// OAuth2 flow
const token = await getOAuth2Token(connection.credentials);
const headers = {
  "Authorization": `Bearer ${token}`
};

// Basic auth
const credentials = btoa(`${username}:${password}`);
const headers = {
  "Authorization": `Basic ${credentials}`
};
```

### ReferenceConnection HTTP Headers

**Behavior**: Resolves to one of the above connection types

**Example:**
```json
{
  "kind": "reference",
  "name": "myOpenAIConnection"
}
```

Resolves to underlying connection (e.g., `ApiKeyConnection`), then follows that type's header pattern.

### AnonymousConnection HTTP Headers

**No Authentication Headers:**
```http
GET /public-api/data HTTP/1.1
Host: api.example.com
```

**Connection Config:**
```json
{
  "kind": "anonymous"
}
```

### Use Cases by Context

**Hooks (Remote Endpoints):**
```json
{
  "kind": "remote",
  "hooks": [{
    "kind": "remote",
    "endpoint": "https://hooks.example.com/content-filter",
    "connection": {
      "kind": "key",
      "key": "Bearer hook_secret_123",
      "headerName": "Authorization"
    }
  }]
}
```

**HTTP Request:**
```http
POST /content-filter HTTP/1.1
Host: hooks.example.com
Authorization: Bearer hook_secret_123
Content-Type: application/json

{"event": "content.created", ...}
```

**Remote Conditions (Agent Auto-Response):**
```json
{
  "runCondition": {
    "kind": "remote",
    "endpoint": "https://conditions.example.com/check",
    "connection": {
      "kind": "key",
      "key": "condition_api_key_456",
      "headerName": "X-API-Key"
    }
  }
}
```

**HTTP Request:**
```http
POST /check HTTP/1.1
Host: conditions.example.com
X-API-Key: condition_api_key_456
Content-Type: application/json

{"threadId": "thread_123", ...}
```

**MCP Tools:**
```json
{
  "connection": {
    "kind": "remote",
    "endpoint": "https://mcp.example.com",
    "credentials": {
      "clientId": "mcp_client",
      "clientSecret": "mcp_secret"
    }
  }
}
```

**HTTP Request (OAuth2):**
```http
POST /tools/search HTTP/1.1
Host: mcp.example.com
Authorization: Bearer <access_token_from_oauth2_flow>
Content-Type: application/json

{"query": "search term"}
```

## OAuth2 Scopes

### Scope Model

**TypeSpec**: See `Scopes` alias in `typespec/common.tsp`

```typescript
alias Scopes = Record<string>;  // Scope name → description
```

**Example:**
```json
{
  "https://graph.microsoft.com/Calendars.ReadWrite": "Read and write calendar events",
  "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user",
  "https://graph.microsoft.com/User.Read": "Read user profile"
}
```

### Scope Declaration

**Agent-Level Scopes** (See `AgentCard` model in `typespec/agents.tsp`):
```typescript
model AgentCard {
  scopes?: Scopes;  // Scopes agent requires
}
```

**Tool-Level Scopes** (See `AITool` model in `typespec/tools.tsp`):
```typescript
model AITool {
  scopes?: Scopes;  // Scopes tool requires
}
```

### Scope Examples

**Microsoft Graph:**
```json
{
  "https://graph.microsoft.com/Calendars.Read": "Read user calendar events",
  "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user",
  "https://graph.microsoft.com/Files.ReadWrite.All": "Read and write all files"
}
```

**Azure Resource Manager:**
```json
{
  "https://management.azure.com/user_impersonation": "Access Azure Service Management"
}
```

**Custom API:**
```json
{
  "https://api.example.com/read:pets": "Read pet information",
  "https://api.example.com/write:pets": "Modify pet information"
}
```

## Authority Model

### Authorization Levels

**User Authority** (`authority: "user"`):
- Uses user's credentials
- Requires user consent
- Access on behalf of user

**System Authority** (`authority: "system"`):
- Uses system credentials
- No user consent needed
- Access as application

### Examples

**User Authority:**
```json
{
  "kind": "reference",
  "name": "microsoftGraphConnection",
  "authority": "user",
  "usageDescription": "Access your calendar to schedule meetings"
}
```
- Agent accesses user's calendar
- User must consent to `Calendars.ReadWrite` scope

**System Authority:**
```json
{
  "kind": "key",
  "key": "sk-proj-abc123",
  "authority": "system",
  "usageDescription": "Access OpenAI API for text generation"
}
```
- Agent uses system API key
- No user consent needed

## Authentication Flows

### OAuth2 Authorization Code Flow

**Scenario**: Agent needs to access user's Microsoft Graph data

**Flow:**

```
1. Agent Declaration
   AgentCard.scopes = {
     "https://graph.microsoft.com/Calendars.ReadWrite": "...",
     "https://graph.microsoft.com/Mail.Read": "..."
   }

2. Run Creation
   POST /runs
   {
     "agentId": "agent_123",
     "input": [...]
   }

3. Scope Validation
   Server checks: Does user have required scopes?
   If NOT: Status → auth_required

4. Client Initiates OAuth2 Flow
   Redirect to: https://login.microsoftonline.com/authorize
   Parameters:
     - client_id: Application ID
     - scope: "Calendars.ReadWrite Mail.Read"
     - response_type: "code"
     - redirect_uri: "https://client.example.com/callback"

5. User Consents
   Microsoft shows consent screen
   User approves: "Allow agent to read calendar and mail?"

6. Authorization Code Returned
   Redirect to: https://client.example.com/callback?code=abc123

7. Client Exchanges Code for Token
   POST https://login.microsoftonline.com/token
   {
     "code": "abc123",
     "client_id": "...",
     "client_secret": "...",
     "grant_type": "authorization_code"
   }
   Response: { "access_token": "eyJ...", "refresh_token": "..." }

8. Client Submits Auth
   POST /runs/{runId}/submit_auth
   {
     "connection": {
       "kind": "key",
       "key": "Bearer eyJ...",
       "authority": "user"
     }
   }

9. Run Resumes
   Status: auth_required → in_progress
   Agent can now call Microsoft Graph APIs
```

#### OAuth2 Sequence Diagram

```
OAuth2 Authorization Code Flow - Actors and Message Flow
═══════════════════════════════════════════════════════════════════════════════

  Client           Server          OAuth Provider      User Browser
    │                │                    │                  │
    │ POST /runs     │                    │                  │
    ├───────────────>│                    │                  │
    │                │                    │                  │
    │                │ Check Scopes       │                  │
    │                │ (missing!)         │                  │
    │                │                    │                  │
    │ 200 OK         │                    │                  │
    │ status:        │                    │                  │
    │ auth_required  │                    │                  │
    │<───────────────┤                    │                  │
    │                │                    │                  │
    │ authUrl        │                    │                  │
    │ in response    │                    │                  │
    │                │                    │                  │
    │ Redirect User ──────────────────────────────────────────>│
    │                │                    │                  │
    │                │                    │ GET /authorize   │
    │                │                    │<─────────────────┤
    │                │                    │                  │
    │                │                    │ Consent Screen   │
    │                │                    │ (show scopes)    │
    │                │                    │───────────────────>
    │                │                    │                  │
    │                │                    │ User Approves    │
    │                │                    │<──────────────────
    │                │                    │                  │
    │                │                    │ 302 Redirect     │
    │                │                    │ callback?code=ABC│
    │                │                    │───────────────────>
    │<───────────────────────────────────────────────────────┤
    │ (callback)     │                    │                  │
    │                │                    │                  │
    │ POST /token    │                    │                  │
    │ (exchange code)────────────────────>│                  │
    │                │                    │                  │
    │                │  access_token,     │                  │
    │                │  refresh_token     │                  │
    │<───────────────────────────────────┤                  │
    │                │                    │                  │
    │ POST /runs/{id}/submit_auth         │                  │
    │ { connection: { ... }}              │                  │
    ├───────────────>│                    │                  │
    │                │                    │                  │
    │                │ Store Connection   │                  │
    │                │ (access_token,     │                  │
    │                │  refresh_token)    │                  │
    │                │                    │                  │
    │ 200 OK         │                    │                  │
    │ status:        │                    │                  │
    │ in_progress    │                    │                  │
    │<───────────────┤                    │                  │
    │                │                    │                  │
    │ SSE: run.started                    │                  │
    │<───────────────┤                    │                  │
    │                │                    │                  │
    │                │ Call External API  │                  │
    │                │ (with access_token)│                  │
    │                ├────────────────────>                  │
    │                │                    │                  │
    │                │ API Response       │                  │
    │                │<────────────────────                  │
    │                │                    │                  │
    │ SSE: run.completed                  │                  │
    │<───────────────┤                    │                  │
    │                │                    │                  │

═══════════════════════════════════════════════════════════════════════════════

Legend:
  ──────>  = HTTP Request
  <──────  = HTTP Response
  ═══════> = User Interaction (Browser)

Key Observations:
  1. User consent happens in separate OAuth Provider flow (steps 4-7)
  2. Client handles token exchange (step 8) - Server never sees client_secret
  3. Connection stored server-side after submit_auth (step 9)
  4. Subsequent runs reuse stored connection (no re-auth needed)
```

### Tool-Level Authorization

**Scenario**: Tool requires specific scope not in agent's scopes

**Flow:**

```
1. Agent Generates Tool Call
   Tool: send_email
   Tool.scopes = { "Mail.Send": "..." }

2. Server Validates Scopes
   Check: Does agent have "Mail.Send" scope?
   If NOT: Status → auth_required

3. Dynamic Consent
   Client requests additional consent
   Scope: "Mail.Send" (incremental)

4. User Consents
   "Allow agent to send email on your behalf?"

5. Client Submits Auth
   POST /runs/{runId}/submit_auth
   { connection: { ... } }

6. Tool Execution Proceeds
   Server validates scope, executes tool
```

### API Key Authentication

**Scenario**: Agent uses API key for external service

**Flow:**

```
1. Agent Configuration
   AgentCard.connections = [{
     "kind": "key",
     "key": "sk-proj-abc123",
     "authority": "system"
   }]

2. Run Creation
   POST /runs
   No additional auth needed (system authority)

3. Tool Execution
   Server includes API key in tool requests
   Header: Authorization: Bearer sk-proj-abc123
```

## Scope Enforcement

### Validation Flow

**Server-Side Validation:**

```
1. Extract Required Scopes
   - Agent scopes: AgentCard.scopes
   - Tool scopes: AITool.scopes
   - Union: all_required_scopes

2. Check Available Scopes
   - User has granted: user_scopes
   - System has access: system_scopes
   - Available: user_scopes ∪ system_scopes

3. Validate Permission
   IF all_required_scopes ⊆ available_scopes:
     ALLOW execution
   ELSE:
     DENY execution
     Status → auth_required
     Missing scopes → required scopes - available scopes

4. Return Missing Scopes
   Error: {
     "code": "AUTH_REQUIRED",
     "message": "Missing required scopes",
     "details": {
       "missing_scopes": ["Mail.Send", "Calendars.ReadWrite"]
     }
   }
```

### Enforcement Points

**Run Creation:**
- Validate agent has required scopes
- Block run if scopes missing

**Tool Execution:**
- Validate tool has required scopes
- Block tool call if scopes missing

**Resource Access:**
- Check scope before API call
- Return 403 Forbidden if scope missing

## Requirements

### Server Requirements

Servers MUST:

1. **Validate Connections**: Ensure connection type is valid
2. **Enforce Scopes**: Check OAuth2 scopes before execution
3. **Handle Auth Required**: Transition to `auth_required` when scopes missing
4. **Store Connections**: Persist connection configuration securely
5. **Encrypt Credentials**: Encrypt API keys and credentials at rest

Servers SHOULD:

1. **Cache Tokens**: Cache OAuth2 access tokens (respect expiry)
2. **Refresh Tokens**: Automatically refresh expired tokens
3. **Audit Access**: Log scope usage for compliance

### Client Requirements

Clients MUST:

1. **Handle Auth Required**: Detect `auth_required` status
2. **Initiate OAuth2**: Redirect user to authorization endpoint
3. **Submit Auth**: Provide connection after consent
4. **Handle Rejection**: Show error if user denies consent

Clients SHOULD:

1. **Cache Consent**: Remember granted scopes
2. **Incremental Consent**: Request only needed scopes
3. **Explain Permissions**: Show why scopes are needed

## Connection Storage

### Secure Storage

**Requirements:**

Servers MUST:

1. **Encrypt at Rest**: Encrypt connection credentials
2. **Access Control**: Restrict access to connections
3. **Audit Trail**: Log connection access

**Encryption:**
```
Connection credentials encrypted with:
- Algorithm: AES-256-GCM
- Key: Managed by KMS (Azure Key Vault, AWS KMS)
- Rotation: Keys rotated every 90 days
```

### Connection References

**Named Connections:**

```json
{
  "name": "myOpenAIConnection",
  "type": "apiKey",
  "config": {
    "kind": "key",
    "key": "encrypted_key_data",
    "headerName": "Authorization"
  }
}
```

**Usage:**
```json
{
  "kind": "reference",
  "name": "myOpenAIConnection",
  "authority": "system"
}
```

## Validation Rules

### Connection Validation

Servers MUST validate connections:

1. **Kind Field**: Must be valid enum value
2. **Required Fields**: Kind-specific required fields present
3. **API Key Format**: Validate key format (if applicable)
4. **Endpoint URL**: Validate URL format (for remote connections)

### Scope Validation

Servers MUST validate scopes:

1. **Scope Format**: URI format (https://domain/scope)
2. **Scope Descriptions**: Non-empty descriptions
3. **Duplicate Scopes**: No duplicate scope names

## Error Handling

### Authentication Errors

| Error Code | Description | Recovery |
|------------|-------------|----------|
| `AUTH_REQUIRED` | Authentication needed | Provide connection |
| `INVALID_CONNECTION` | Connection config invalid | Fix connection |
| `PERMISSION_DENIED` | Missing required scopes | Request consent |
| `TOKEN_EXPIRED` | Access token expired | Refresh token |
| `INVALID_TOKEN` | Token invalid/revoked | Re-authenticate |
| `CONSENT_DENIED` | User denied consent | Explain and retry |

### Error Response

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

## Security Considerations

### Credential Protection

**API Keys:**
- Never log API keys in plaintext
- Never expose in error messages
- Encrypt at rest
- Rotate regularly

**OAuth2 Tokens:**
- Store refresh tokens securely
- Encrypt access tokens
- Clear from memory after use
- Respect token expiry

### Scope Minimization

**Principle**: Request only needed scopes

**Good:**
```json
{
  "scopes": {
    "https://graph.microsoft.com/Calendars.Read": "..."
  }
}
```

**Bad:**
```json
{
  "scopes": {
    "https://graph.microsoft.com/.default": "..."  // Too broad
  }
}
```

### Connection Isolation

**Tenant Isolation:**
- Isolate connections by tenant
- No cross-tenant access
- Validate tenant ID

**User Isolation:**
- User connections inaccessible to other users
- System connections isolated from user data

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/common.tsp` (Connection, Scopes)
- **TypeSpec**: `typespec/agents.tsp` (AgentCard.scopes)
- **TypeSpec**: `typespec/tools.tsp` (AITool.scopes)
- **Agent Schema**: Connection model
- **OpenAPI 3.0**: OAuth2 security scheme scopes
- **OAuth 2.0**: RFC 6749 (authorization framework)

## See Also

- [Tools](../api-reference/tools.md) - Tool scope requirements
- [Agents](../api-reference/agents.md) - Agent scope requirements
- [Run Lifecycle](./run-lifecycle.md) - auth_required state
- [Tool Execution](./tool-execution.md) - Tool-level authorization
- [Error Handling](./error-handling.md) - Authentication error codes
