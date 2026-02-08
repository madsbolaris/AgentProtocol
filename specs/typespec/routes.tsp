/**
 * Stop in-progress runs with configurable cleanup behavior
 *
 * @usage
 * Stop in-progress runs with configurable cleanup behavior.
 *
 * @example Example 1
 * ```json
 * {
 *   "action": "interrupt",
 *   "reason": "User cancelled via UI"
 * }
 * ```
 *
 * @example Example 2
 * ```http
 * POST /runs/run-789/cancel
 * Content-Type: application/json
 * 
 * {
 *   "action": "interrupt",
 *   "reason": "User clicked stop button"
 * }
 * ```
 *
 * @example ```http
 * ```json
 * {
 *   "runId": "run-789",
 *   "status": "cancelled",
 *   "output": [
 *     {
 *       "role": "assistant",
 *       "contents": [
 *         {
 *           "kind": "text",
 *           "text": "Partial response before cancellation..."
 *         }
 *       ]
 *     }
 *   ],
 *   "cancelledAt": "2026-02-06T10:02:30Z",
 *   "cancellationReason": "User clicked stop button"
 * }
 * ```
 *
 * @example Example 4
 * ```http
 * POST /runs/run-789/cancel
 * Content-Type: application/json
 * 
 * {
 *   "action": "rollback",
 *   "reason": "Unwanted run, cleanup needed"
 * }
 * ```
 *
 * @example ```http
 * ```json
 * {
 *   "runId": "run-789",
 *   "status": "cancelled",
 *   "message": "Run cancelled and cleaned up (rollback)"
 * }
 * ```
 *
 * @response 200 OK
 * Run cancelled (status = "cancelled" for interrupt)
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run already completed/cancelled
 *
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./execution.tsp";
import "./messages.tsp";
import "./agents.tsp";
import "./subscriptions.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

/**
 * Agent Operations
 *
 * Endpoints for agent discovery and registration.
 *
 * INSPIRED BY: Google A2A Protocol Agent Card (.well-known/agent-card.json)
 * PURPOSE: Enable agent discovery, capability advertisement, and registration
 */
@route("/agents")
interface Agents {
  /**
 * Get agent card (discovery/registration metadata).
 *
 * @response 200 OK
 * Agent card with capabilities, tools, and M365/Entra integration
 *
 * @response 404 Not Found
 * Agent not found
 *
 * REQUEST:
 * - GET /agents/{agentId}/card
 *
 */
  @doc("Get agent card (discovery/registration metadata).")
  @get
  @route("{agentId}/card")
  getCard(@path agentId: string): AgentCard | NotFoundError;

  /**
 * Inspect ephemeral agent (capability discovery without persisting).
 *
 * @usage
 * - Capability discovery for anonymous/ephemeral agents
 * - Validate agent configuration before running
 * - Check model support (vision, tools, thinking, etc.) before creating run
 * - Preview agent capabilities without persisting to registry
 *
 *
 * Use Cases:
 * - "Does this model support vision?" - inspect({ agent: { model: "gpt-4o" } })
 * - "What are the token limits?" - inspect({ agent: { model: "claude-3-sonnet" } })
 * - "Can this agent use tools?" - inspect({ agent: { model: "...", tools: [...] } })
 * - "Validate agent config" - inspect({ agent: {...} }) before POST /runs
 *
 *
 * Rationale:
 * - Capabilities belong in AgentCard (not separate /models endpoint)
 * - Works for both named agents (GET /agents/{id}) and ephemeral agents (POST /agents/inspect)
 * - Single source of truth for agent capabilities
 * - No side effects - purely inspection (no persistence)
 *
 * DIFFERENCES FROM GET /agents/{agentId}:
 * - Does NOT persist agent
 * - agentId will be null in response
 * - Used for validation and capability discovery
 * - GET /agents/{agentId} retrieves persisted agents
 *
 * @example Check model capabilities
 * ```http
 * POST /agents/inspect
 * {
 * "agent": {
 * "model": "gpt-4o",
 * "instructions": "You are a helpful assistant"
 * }
 * }
 * Response: AgentCard with capabilities.vision=true, maxTokens=128000
 * ```
 *
 * @example Check Anthropic extended thinking support
 * ```http
 * POST /agents/inspect
 * {
 * "agent": {
 * "model": "claude-3-sonnet",
 * "instructions": "You are a research analyst"
 * }
 * }
 * Response: AgentCard with capabilities.thinking=true, maxTokens=200000
 * ```
 *
 * @example Inspect with full agent config
 * ```http
 * POST /agents/inspect
 * {
 * "agent": {
 * "model": { "id": "gpt-4o", "provider": "openai" },
 * "instructions": "You help with customer support",
 * "tools": [{ "type": "function", "function": {...} }]
 * }
 * }
 * Response: AgentCard with full capabilities, tool signatures, etc.
 * ```
 *
 * @response 200 OK
 * AgentCard with capabilities (agentId will be null - not persisted)
 *
 * @response 400 Bad Request
 * Invalid agent definition
 *
 * REQUEST:
 * - POST /agents/inspect
 * - Body: { agent: AgentDefinition } - inline agent configuration
 *
 */
  @doc("Inspect ephemeral agent (capability discovery without persisting).")
  @post
  @segment("inspect")
  inspect(@body request: { agent: AgentDefinition }): AgentCard;

  /**
 * Stream agent events (all activity across all runs).
 *
 * @usage
 *
 * Use Cases:
 * - Agent monitoring dashboard
 * - Debugging agent behavior across multiple threads
 * - Analytics and usage tracking
 * - Real-time agent activity feeds
 *
 * @response 200 OK
 * SSE stream with agent events
 *
 * @response 404 Not Found
 * Agent not found
 *
 * REQUEST:
 * - GET /agents/{agentId}/stream
 *
 */
  @doc("Stream agent events (all activity across all runs).")
  @get
  @route("{agentId}/stream")
  streamAgent(
    @path agentId: string,
    @query events?: string,
    @query since?: utcDateTime,
    @query threadId?: string,
    @query roles?: string,
    @query userIds?: string,
    @query contentTypes?: string,
    @query audience?: string
  ): void | NotFoundError; // SSE stream response
}

/**
 * Run Operations
 *
 * Endpoints for creating and managing agent execution instances.
 */
@route("/runs")
interface Runs {
  /**
 * Create and execute an agent run.
 *
 * @response 201 Created
 * Run created and started
 *
 * @response 400 Bad Request
 * Invalid input
 *
 * @response 404 Not Found
 * Thread or agent not found
 *
 * @response 500 Internal Server Error
 * Execution error
 *
 * REQUEST:
 * - POST /runs
 * - Body: Run with input messages, agent configuration, and options
 *
 */
  @doc("Create and execute an agent run.")
  @post
  create(@body run: Run): Run;

  /**
 * Get a specific run by ID.
 *
 * @response 200 OK
 * Run details
 *
 * @response 404 Not Found
 * Run not found
 *
 * REQUEST:
 * - GET /runs/{runId}
 * - Query: format=xml for XML representation (pretty-printed)
 *
 */
  @doc("Get a specific run by ID.")
  @get
  get(@path runId: string, @query format?: "json" | "xml"): Run | NotFoundError;

  /**
 * List runs with optional filtering.
 *
 * @usage
 * Retrieve a paginated list of runs with optional filters.
 * Use for monitoring run history, filtering by thread/agent/status, or pagination.
 *
 * @example List all runs
 * ```http
 * GET /runs
 * ```
 *
 * @example Filter by thread
 * ```http
 * GET /runs?threadId=thread_123&limit=10
 * ```
 *
 * @response 200 OK
 * Array of runs
 *
 * REQUEST:
 * - GET /runs?threadId={threadId}&agentId={agentId}&status={status}&after={runId}&limit={limit}
 *
 */
  @doc("List runs with optional filtering.")
  @get
  list(
    @query threadId?: string,
    @query agentId?: string,
    @query status?: RunStatus,
    @query after?: string,
    @query limit?: int32 = 100
  ): Run[];

  /**
 * @example Example 1
 * ```http
 * GET /runs/run-123/subscriptions/sub-456
 * ```
 *
 * @response 200 OK
 * Subscription details
 *
 * @response 404 Not Found
 * Run or subscription not found
 *
 */
  @doc("Create ephemeral run and wait for completion (blocking).")
  @post
  @route("wait")
  createAndWait(@body run: Run, @query format?: "json" | "xml"): RunWaitResponse;

  /**
 * Create and stream agent run (non-blocking with SSE).
 *
 * @usage
 *
 * Use Cases:
 * - Chat UI with streaming text
 * - Interactive agents with real-time responses
 * - Simple streaming without managing runId
 *
 *
 * Rationale:
 * - Single request for create + stream (simpler client code)
 * - No need to track runId separately for simple streaming scenarios
 * - Common pattern for chat UIs with streaming responses
 *
 * @response 200 OK
 * SSE stream with run events
 *
 * @response 400 Bad Request
 * Invalid input
 *
 * @response 404 Not Found
 * Thread or agent not found
 *
 * @response 500 Internal Server Error
 * Execution error
 *
 * REQUEST:
 * - POST /runs/stream
 * - Body: Run with input messages and agent configuration
 *
 */
  @doc("Create and stream agent run (non-blocking with SSE).")
  @post
  @route("stream")
  createAndStream(
    @body run: Run,
    @query events?: string,
    @query since?: utcDateTime
  ): void;

  /**
 * Wait for run completion (blocking).
 *
 * @usage
 *
 * Use Cases:
 * - Background runs: Create run, return runId, client waits separately
 * - Async workflows: Trigger run, do other work, wait for completion
 * - Simple clients: No SSE support, prefer blocking wait over polling
 *
 *
 * Rationale:
 * - Polling alternative for clients without SSE support
 * - Background run pattern: POST /runs → GET /runs/{id}/wait
 * - Simplified response (no need to poll GET /runs/{id} repeatedly)
 *
 * @response 200 OK
 * RunWaitResponse with final run state
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run already completed (returns completed state)
 *
 * @response 408 Request Timeout
 * Run exceeded time limit
 *
 * REQUEST:
 * - GET /runs/{runId}/wait
 * - Query: format=xml for XML representation (pretty-printed)
 *
 */
  @doc("Wait for run completion (blocking).")
  @get
  @route("{runId}/wait")
  wait(@path runId: string, @query format?: "json" | "xml"): RunWaitResponse | NotFoundError;

  /**
 * Stream run output (reconnectable).
 *
 * @usage
 *
 * Use Cases:
 * - Reconnection after network failure
 * - Multiple observers: Dashboard + CLI both streaming same run
 * - Late joining: Start run, navigate away, return and stream remaining output
 *
 *
 * Rationale:
 * - Reconnection pattern for resilient streaming
 * - Background run pattern: POST /runs → GET /runs/{id}/stream
 * - Multiple clients can stream same run (monitoring, debugging)
 *
 * @response 200 OK
 * SSE stream with run events
 *
 * @response 404 Not Found
 * Run not found
 *
 * REQUEST:
 * - GET /runs/{runId}/stream
 *
 */
  @doc("Stream run output (reconnectable).")
  @get
  @route("{runId}/stream")
  stream(
    @path runId: string,
    @query events?: string,
    @query since?: utcDateTime
  ): void | NotFoundError; // SSE stream response

  /**
 * Cancel a running execution.
 *
 * @usage
 *
 * Use Cases:
 * - interrupt: User stops generation but wants to see partial output
 * - rollback: Clean up failed/unwanted run completely
 *
 * @response 200 OK
 * Run cancelled
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run already completed/cancelled
 *
 * REQUEST:
 * - POST /runs/{runId}/cancel
 * - Body (optional): { action?: CancelAction, reason?: string }
 *
 */
  @doc("Cancel a running execution.")
  @post
  @route("{runId}/cancel")
  cancel(
    @path runId: string,
    @body request?: {
      /**
 * Human-in-the-loop tool approval workflow - agent requests tools, human reviews/executes, submits results
 *
 * @usage
 * Human-in-the-loop tool approval workflow - agent requests tools, human reviews/executes, submits results.
 *
 * Use Cases:
 * - **Tool approval**: Human reviews `delete_file` call before execution
 * - **Tool modification**: Human modifies tool arguments before execution
 * - **External execution**: Tools executed by external system, results submitted back
 *
 * @example Example 1
 * ```json
 * {
 *   "tool_outputs": [
 *     {
 *       "tool_call_id": "call_abc123",
 *       "output": "File deleted successfully"
 *     }
 *   ]
 * }
 * ```
 *
 * @example :
 * ```json
 * {
 *   "runId": "run-123",
 *   "status": "requires_action",
 *   "required_action": {
 *     "type": "submit_tool_outputs",
 *     "tool_calls": [
 *       {
 *         "id": "call_abc",
 *         "type": "function",
 *         "function": {
 *           "name": "delete_file",
 *           "arguments": "{\"path\":\"/important.txt\"}"
 *         }
 *       }
 *     ]
 *   }
 * }
 * ```
 *
 * @example Example 3
 * ```http
 * POST /runs/run-123/submit_tool_outputs
 * Content-Type: application/json
 * 
 * {
 *   "tool_outputs": [
 *     {
 *       "tool_call_id": "call_abc",
 *       "output": "File deleted successfully"
 *     }
 *   ]
 * }
 * ```
 *
 * @example Example 4
 * ```json
 * {
 *   "runId": "run-123",
 *   "status": "in_progress",
 *   "output": [
 *     {
 *       "role": "tool",
 *       "contents": [
 *         {
 *           "kind": "functionResult",
 *           "callId": "call_abc",
 *           "name": "delete_file",
 *           "result": "File deleted successfully"
 *         }
 *       ]
 *     }
 *   ]
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with submitted tool outputs (status transitions to "in_progress")
 *
 * @response 400 Bad Request
 * Invalid tool outputs (mismatched IDs, missing required outputs)
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in requires_action state
 *
 */
      action?: CancelAction;
      /** Optional reason for cancellation (for analytics/debugging) */
      reason?: string;
    }
  ): Run | NotFoundError | ConflictError;

  /**
 * Submit tool execution results to continue run.
 *
 * @usage
 *
 * Use Cases:
 * - Tool approval: Human reviews and approves tool calls before execution
 * - Tool modification: Human modifies tool arguments before execution
 * - External execution: Tools executed by external system, results submitted back
 *
 * @example Example 1
 * ```http
 * // Run enters requires_action state
 * {
 * "runId": "run-123",
 * "status": "requires_action",
 * "required_action": {
 * "type": "submit_tool_outputs",
 * "tool_calls": [
 * { "id": "call_abc", "function": "delete_file", "arguments": { "path": "/important.txt" } }
 * ]
 * }
 * }
 * 
 * // Human approves and submits results
 * POST /runs/run-123/submit_tool_outputs
 * {
 * "tool_outputs": [
 * { "tool_call_id": "call_abc", "output": "File deleted successfully" }
 * ]
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with submitted tool outputs
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in requires_action state
 *
 * @response 400 Bad Request
 * Invalid tool outputs (mismatched IDs, missing required outputs)
 *
 * REQUEST:
 * - POST /runs/{runId}/submit_tool_outputs
 * - Body: Tool outputs for pending tool calls
 *
 */
  @doc("Submit tool execution results to continue run.")
  @post
  @route("{runId}/submit_tool_outputs")
  submit_tool_outputs(
    @path runId: string,
    @body request: {
      /**
 * Human-in-the-loop input collection - agent requests clarification, disambiguation, or additional info from user
 *
 * @usage
 * Human-in-the-loop input collection - agent requests clarification, disambiguation, or additional info from user.
 *
 * Use Cases:
 * - **Disambiguation**: "Which John Smith? (1) Marketing (2) Engineering"
 * - **Clarification**: "What date range for the report?"
 * - **Confirmation**: "Delete 50 files - are you sure? (yes/no)"
 * - **Additional info**: "Please provide the project ID"
 *
 * @example Example 1
 * ```json
 * {
 *   "value": "1"
 * }
 * ```
 *
 * @example :
 * ```json
 * {
 *   "runId": "run-456",
 *   "status": "input_required",
 *   "required_input": {
 *     "type": "disambiguation",
 *     "prompt": "Which John Smith?\n(1) John Smith (Marketing)\n(2) John Smith (Engineering)",
 *     "options": ["1", "2"]
 *   }
 * }
 * ```
 *
 * @example Example 3
 * ```http
 * POST /runs/run-456/submit_input
 * Content-Type: application/json
 * 
 * {
 *   "value": "1"
 * }
 * ```
 *
 * @example User responds
 * ```json
 * {
 *   "runId": "run-456",
 *   "status": "in_progress",
 *   "output": [
 *     {
 *       "role": "user",
 *       "contents": [
 *         {
 *           "kind": "text",
 *           "text": "1"
 *         }
 *       ]
 *     }
 *   ]
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with submitted input (status transitions to "in_progress")
 *
 * @response 400 Bad Request
 * Invalid input
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in input_required state
 *
 */
      tool_outputs: ToolOutput[];
    }
  ): Run | NotFoundError | ConflictError;

  /**
 * Submit user input to continue run.
 *
 * @usage
 *
 * Use Cases:
 * - Disambiguation: "Which John Smith? (1) Marketing (2) Engineering"
 * - Clarification: "What date range for the report?"
 * - Confirmation: "Delete 50 files - are you sure? (yes/no)"
 * - Additional info: "Please provide the project ID"
 *
 * @example Example 1
 * ```http
 * // Run enters input_required state
 * {
 * "runId": "run-123",
 * "status": "input_required",
 * "required_input": {
 * "type": "disambiguation",
 * "prompt": "Which John Smith? (1) John Smith (Marketing) (2) John Smith (Engineering)",
 * "options": ["1", "2"]
 * }
 * }
 * 
 * // User responds
 * POST /runs/run-123/submit_input
 * {
 * "value": "1"
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with submitted input
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in input_required state
 *
 * @response 400 Bad Request
 * Invalid input
 *
 * REQUEST:
 * - POST /runs/{runId}/submit_input
 * - Body: User's response to agent's request
 *
 */
  @doc("Submit user input to continue run.")
  @post
  @route("{runId}/submit_input")
  submit_input(
    @path runId: string,
    @body request: {
      /**
 * Human-in-the-loop authentication - agent needs user credentials to access protected resources (M365, Google, etc
 *
 * @usage
 * Human-in-the-loop authentication - agent needs user credentials to access protected resources (M365, Google, etc.).
 *
 * Use Cases:
 * - **OAuth flow**: Agent needs user to authenticate with Microsoft Graph, Google, etc.
 * - **Calendar access**: "Please sign in to access your calendar"
 * - **Email access**: "Authenticate to read your inbox"
 * - **SharePoint**: "Sign in to access company documents"
 *
 * @example Example 1
 * ```json
 * {
 *   "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
 *   "tokenType": "Bearer"
 * }
 * ```
 *
 * @example :
 * ```json
 * {
 *   "runId": "run-789",
 *   "status": "auth_required",
 *   "required_auth": {
 *     "type": "oauth",
 *     "service": "microsoft_graph",
 *     "scopes": ["Calendars.Read", "Mail.Read"],
 *     "authUrl": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=..."
 *   }
 * }
 * ```
 *
 * @example Example 3
 * ```http
 * POST /runs/run-789/submit_auth
 * Content-Type: application/json
 * 
 * {
 *   "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik...",
 *   "tokenType": "Bearer"
 * }
 * ```
 *
 * @example Example 4
 * ```json
 * {
 *   "runId": "run-789",
 *   "status": "in_progress",
 *   "metadata": {
 *     "authStatus": "authenticated",
 *     "service": "microsoft_graph"
 *   }
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with authentication (status transitions to "in_progress")
 *
 * @response 400 Bad Request
 * Invalid credentials
 *
 * @response 401 Unauthorized
 * Authentication failed (token invalid/expired)
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in auth_required state
 *
 */
      value: string;
    }
  ): Run | NotFoundError | ConflictError;

  /**
 * Submit authentication credentials to continue run.
 *
 * @usage
 *
 * Use Cases:
 * - OAuth flow: Agent needs user to authenticate with Microsoft/Google/etc.
 * - Calendar access: "Please sign in to access your calendar"
 * - Email access: "Authenticate to read your inbox"
 * - SharePoint: "Sign in to access company documents"
 *
 * @example Example 1
 * ```http
 * // Run enters auth_required state
 * {
 * "runId": "run-123",
 * "status": "auth_required",
 * "required_auth": {
 * "type": "oauth",
 * "service": "microsoft_graph",
 * "scopes": ["Calendars.Read", "Mail.Read"],
 * "authUrl": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?..."
 * }
 * }
 * 
 * // User authenticates and submits token
 * POST /runs/run-123/submit_auth
 * {
 * "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
 * "tokenType": "Bearer"
 * }
 * ```
 *
 * @response 200 OK
 * Run continues with authentication
 *
 * @response 404 Not Found
 * Run not found
 *
 * @response 409 Conflict
 * Run not in auth_required state
 *
 * @response 400 Bad Request
 * Invalid credentials
 *
 * @response 401 Unauthorized
 * Authentication failed
 *
 * REQUEST:
 * - POST /runs/{runId}/submit_auth
 * - Body: Authentication token or credentials
 *
 */
  @doc("Submit authentication credentials to continue run.")
  @post
  @route("{runId}/submit_auth")
  submit_auth(
    @path runId: string,
    @body request: {
      /**
 * @example Example 1
 * ```json
 * {
 *   "type": "agent.activity",
 *   "resourceId": "agent-123",
 *   "subscriptionId": "sub-456",
 *   "eventType": "run.started",
 *   "sequenceNumber": 42,
 *   "eventSeq": 1587,
 *   "timestamp": "2026-02-06T10:00:00Z",
 *   "data": {
 *     "runId": "run-789",
 *     "threadId": "thread-456"
 *   }
 * }
 * ```
 *
 * @example Example 2
 * ```http
 * POST /agents/agent-123/subscriptions
 * Content-Type: application/json
 * 
 * {
 *   "webhookUrl": "https://client.example.com/webhooks/agent-notifications",
 *   "webhookSecret": "secret-for-hmac-validation",
 *   "events": ["run.completed", "agent.updated", "agent.error"],
 *   "threadId": "thread-456",
 *   "active": true
 * }
 * ```
 *
 * @response 201 Created
 * Subscription created
 *
 * @response 400 Bad Request
 * Invalid webhookUrl or configuration
 *
 * @response 404 Not Found
 * Agent not found
 *
 */
      token: string;
      /** Token type (e.g., "Bearer") */
      tokenType?: string;
    }
  ): Run | NotFoundError | ConflictError;
}

/**
 * Run Subscription Operations
 *
 * Endpoints for managing webhook subscriptions (nested under runs).
 *
 * PURPOSE: Monitor specific run activity via webhooks
 * - Client registers webhook URL for run notifications
 * - Server POSTs to webhook URL when activity occurs
 * - Client fetches latest data via GET /runs/{runId}
 */
@route("/runs/{runId}/subscriptions")
interface RunSubscriptions {
  /**
 * Create a webhook subscription for a run.
 *
 * @response 201 Created
 * Subscription created
 *
 * @response 400 Bad Request
 * Invalid webhookUrl or configuration
 *
 * @response 404 Not Found
 * Run not found
 *
 * REQUEST:
 * - POST /runs/{runId}/subscriptions
 * - Body: RunSubscription with webhookUrl and optional config
 *
 */
  @doc("Create a webhook subscription for a run.")
  @post
  create(
    @path runId: string,
    @body subscription: RunSubscription
  ): RunSubscription | NotFoundError;

  /**
 * List subscriptions for a run.
 *
 * @response 200 OK
 * Array of subscriptions
 *
 * @response 404 Not Found
 * Run not found
 *
 * REQUEST:
 * - GET /runs/{runId}/subscriptions?after={subscriptionId}&limit={limit}
 *
 */
  @doc("List subscriptions for a run.")
  @get
  list(
    @path runId: string,
    @query after?: string,
    @query limit?: int32 = 100
  ): RunSubscription[] | NotFoundError;

  /**
 * Get a specific subscription.
 *
 * @response 200 OK
 * Subscription details
 *
 * @response 404 Not Found
 * Run or subscription not found
 *
 * REQUEST:
 * - GET /runs/{runId}/subscriptions/{subscriptionId}
 *
 */
  @doc("Get a specific subscription.")
  @get
  get(
    @path runId: string,
    @path subscriptionId: string
  ): RunSubscription | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * GET /agents/agent-123/subscriptions/sub-456
 * ```
 *
 * @response 200 OK
 * Subscription details
 *
 * @response 404 Not Found
 * Agent or subscription not found
 *
 */
  @doc("Update a subscription.")
  @patch
  update(
    @path runId: string,
    @path subscriptionId: string,
    @body subscription: RunSubscription
  ): RunSubscription | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * PATCH /agents/agent-123/subscriptions/sub-456
 * Content-Type: application/json
 * 
 * {
 *   "active": false
 * }
 * ```
 *
 * @response 200 OK
 * Updated subscription
 *
 * @response 404 Not Found
 * Agent or subscription not found
 *
 */
  @doc("Delete a subscription.")
  @delete
  delete(@path runId: string, @path subscriptionId: string): void | NotFoundError;
}

/**
 * Agent Subscription Operations
 *
 * Endpoints for managing webhook subscriptions for agents.
 *
 * PURPOSE: Monitor agent activity across all runs via webhooks
 * - Client registers webhook URL for agent notifications
 * - Server POSTs to webhook URL when activity occurs
 * - Client fetches latest data via GET /agents/{agentId} or GET /runs/{runId}
 */
@route("/agents/{agentId}/subscriptions")
interface AgentSubscriptions {
  /**
 * Create a webhook subscription for an agent.
 *
 * @response 201 Created
 * Subscription created
 *
 * @response 400 Bad Request
 * Invalid webhookUrl or configuration
 *
 * @response 404 Not Found
 * Agent not found
 *
 * REQUEST:
 * - POST /agents/{agentId}/subscriptions
 * - Body: AgentSubscription with webhookUrl and optional config
 *
 */
  @doc("Create a webhook subscription for an agent.")
  @post
  create(
    @path agentId: string,
    @body subscription: AgentSubscription
  ): AgentSubscription | NotFoundError;

  /**
 * List subscriptions for an agent.
 *
 * @response 200 OK
 * Array of subscriptions
 *
 * @response 404 Not Found
 * Agent not found
 *
 * REQUEST:
 * - GET /agents/{agentId}/subscriptions?after={subscriptionId}&limit={limit}
 *
 */
  @doc("List subscriptions for an agent.")
  @get
  list(
    @path agentId: string,
    @query after?: string,
    @query limit?: int32 = 100
  ): AgentSubscription[] | NotFoundError;

  /**
 * Get a specific subscription.
 *
 * @response 200 OK
 * Subscription details
 *
 * @response 404 Not Found
 * Agent or subscription not found
 *
 * REQUEST:
 * - GET /agents/{agentId}/subscriptions/{subscriptionId}
 *
 */
  @doc("Get a specific subscription.")
  @get
  get(
    @path agentId: string,
    @path subscriptionId: string
  ): AgentSubscription | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * GET /threads/thread-123
 * ```
 *
 * @response 200 OK
 * Thread details with messages
 *
 * @response 404 Not Found
 * Thread not found
 *
 */
  @doc("Update a subscription.")
  @patch
  update(
    @path agentId: string,
    @path subscriptionId: string,
    @body subscription: AgentSubscription
  ): AgentSubscription | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * PATCH /threads/thread-123
 * Content-Type: application/json
 * 
 * {
 *   "status": "closed"
 * }
 * ```
 *
 * @response 200 OK
 * Updated thread
 *
 * @response 404 Not Found
 * Thread not found
 *
 * @response 409 Conflict
 * Update conflict
 *
 */
  @doc("Delete a subscription.")
  @delete
  delete(@path agentId: string, @path subscriptionId: string): void | NotFoundError;
}

/**
 * Thread Operations
 *
 * Endpoints for managing conversation threads.
 */
@route("/threads")
interface Threads {
  /**
 * Create a new conversation thread.
 *
 * @response 201 Created
 * Thread created
 *
 * @response 400 Bad Request
 * Invalid input
 *
 * REQUEST:
 * - POST /threads
 * - Body: Thread with participants and optional metadata
 *
 */
  @doc("Create a new conversation thread.")
  @post
  create(@body thread: Thread): Thread;

  /**
 * Get a specific thread by ID.
 *
 * @response 200 OK
 * Thread details with messages
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - GET /threads/{threadId}
 * - Query: format=xml for XML representation (pretty-printed)
 *
 */
  @doc("Get a specific thread by ID.")
  @get
  get(@path threadId: string, @query format?: "json" | "xml"): Thread | NotFoundError;

  /**
 * List threads with optional filtering.
 *
 * @response 200 OK
 * Array of threads
 *
 * REQUEST:
 * - GET /threads?updatedSince={timestamp}&status={status}&after={threadId}&limit={limit}
 *
 */
  @doc("List threads with optional filtering.")
  @get
  list(
    @query updatedSince?: utcDateTime,
    @query status?: ThreadStatus,
    @query after?: string,
    @query limit?: int32 = 100
  ): Thread[];

  /**
 * @example Example 1
 * ```http
 * GET /threads/thread-123/messages
 * ```
 *
 * @example Example 2
 * ```http
 * GET /threads/thread-123/messages?branch=msg-2b
 * ```
 *
 * @response 200 OK
 * Array of messages
 *
 * @response 404 Not Found
 * Thread not found
 *
 */
  @doc("Update thread metadata or status.")
  @patch
  update(@path threadId: string, @body thread: Thread): Thread | NotFoundError | ConflictError;

  /**
 * @example Example 1
 * ```http
 * PATCH /threads/thread-123/subscriptions/sub-456
 * Content-Type: application/json
 * 
 * {
 *   "active": false
 * }
 * ```
 *
 */
  @doc("Delete a thread.")
  @delete
  delete(@path threadId: string): void | NotFoundError | ConflictError;

  /**
 * Mark thread as read.
 *
 * @response 200 OK
 * Thread with unreadCount reset to 0
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - POST /threads/{threadId}/read
 *
 */
  @doc("Mark thread as read.")
  @post
  @route("{threadId}/read")
  markAsRead(@path threadId: string): Thread | NotFoundError;

  /**
 * Add a message to a thread.
 *
 * @response 201 Created
 * Message added
 *
 * @response 404 Not Found
 * Thread not found
 *
 * @response 400 Bad Request
 * Invalid message
 *
 * @response 409 Conflict
 * Message ID already exists (if client-provided)
 *
 * REQUEST:
 * - POST /threads/{threadId}/messages
 * - Body: ChatMessage to add to thread
 *
 */
  @doc("Add a message to a thread.")
  @post
  @route("{threadId}/messages")
  addMessage(@path threadId: string, @body message: ChatMessage): ChatMessage | NotFoundError | ConflictError;

  /**
 * Get messages from a thread.
 *
 * @response 200 OK
 * Array of messages
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - GET /threads/{threadId}/messages?branch={messageId}&after={messageId}&limit={limit}
 * - Query: format=xml for XML representation (pretty-printed)
 *
 */
  @doc("Get messages from a thread.")
  @get
  @route("{threadId}/messages")
  getMessages(
    @path threadId: string,
    @query branch?: string,
    @query after?: string,
    @query limit?: int32 = 100,
    @query format?: "json" | "xml"
  ): ChatMessage[] | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * GET /threads/thread-123/messages/msg-456
 * ```
 *
 * @example ```http
 * ```json
 * {
 *   "messageId": "msg-456",
 *   "role": "assistant",
 *   "contents": [
 *     {
 *       "kind": "text",
 *       "text": "Here's the analysis you requested..."
 *     }
 *   ],
 *   "createdAt": "2026-02-07T10:00:00Z"
 * }
 * ```
 *
 * @response 200 OK
 * Message details
 *
 * @response 404 Not Found
 * Thread or message not found
 *
 */
  @doc("Get a specific message by ID.")
  @get
  @route("{threadId}/messages/{messageId}")
  getMessage(
    @path threadId: string,
    @path messageId: string,
    @query format?: "json" | "xml"
  ): ChatMessage | NotFoundError;

  /**
 * RESTful resource nesting for thread-scoped run listing
 *
 * @usage
 * RESTful resource nesting for thread-scoped run listing.
 *
 * Use Cases:
 * - View conversation history (all runs in thread)
 * - Run debugging and analytics for specific thread
 * - Natural API navigation (threads → runs)
 *
 * @example Example 1
 * ```http
 * GET /threads/thread-123/runs?limit=50
 * ```
 *
 * @example ```http
 * ```json
 * [
 *   {
 *     "runId": "run-abc123",
 *     "threadId": "thread-123",
 *     "status": "completed",
 *     "createdAt": "2026-02-06T10:00:00Z",
 *     "completedAt": "2026-02-06T10:00:05Z"
 *   },
 *   {
 *     "runId": "run-def456",
 *     "threadId": "thread-123",
 *     "status": "completed",
 *     "createdAt": "2026-02-06T10:01:00Z",
 *     "completedAt": "2026-02-06T10:01:03Z"
 *   }
 * ]
 * ```
 *
 * @example Example 3
 * ```http
 * GET /threads/thread-123/runs?status=completed&limit=100
 * ```
 *
 * @example ```http
 * ```http
 * # Page 1
 * GET /threads/thread-123/runs?limit=100
 * 
 * # Page 2
 * GET /threads/thread-123/runs?after=run-abc123&limit=100
 * ```
 *
 * @response 200 OK
 * Array of runs in thread
 *
 * @response 404 Not Found
 * Thread not found
 *
 */
  @doc("Copy a thread to create an independent copy.")
  @post
  @route("{threadId}/copy")
  copy(
    @path threadId: string,
    @body request?: ThreadCopyRequest
  ): Thread | NotFoundError;

  /**
 * Create a run within the thread context.
 *
 * @usage
 *
 * Use Cases:
 * - Multi-turn conversations: POST /threads/{id}/runs for each turn
 * - Explicit thread context: More discoverable than threadId in body
 * - RESTful clients: Prefer nested resources over query params
 *
 *
 * Rationale:
 * - REST conventions: Resource nesting (threads → runs)
 * - Discoverability: Clearer API surface
 * - Context clarity: Explicit thread scope
 * - LangChain alignment: Industry standard pattern
 *
 * @response 201 Created
 * Run created in thread
 *
 * @response 404 Not Found
 * Thread not found
 *
 * @response 400 Bad Request
 * Invalid run configuration
 *
 * REQUEST:
 * - POST /threads/{threadId}/runs
 * - Body: Run with agent and input configuration
 *
 */
  @doc("Create a run within the thread context.")
  @post
  @route("{threadId}/runs")
  createRun(
    @path threadId: string,
    @body run: Run
  ): Run | NotFoundError;

  /**
 * List runs within the thread.
 *
 * @usage
 *
 * Use Cases:
 * - Conversation history: View all agent interactions in thread
 * - Run debugging: Inspect all executions for specific thread
 * - Analytics: Analyze run patterns per conversation
 *
 *
 * Rationale:
 * - REST conventions: Resource nesting (threads → runs)
 * - Discoverability: Natural API navigation
 * - Thread-centric view: All runs for conversation in one call
 * - LangChain alignment: Industry standard pattern
 *
 * @response 200 OK
 * Array of runs in thread
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - GET /threads/{threadId}/runs?status={status}&after={runId}&limit={limit}
 *
 */
  @doc("List runs within the thread.")
  @get
  @route("{threadId}/runs")
  listRuns(
    @path threadId: string,
    @query status?: RunStatus,
    @query after?: string,
    @query limit?: int32 = 100
  ): Run[] | NotFoundError;

  /**
 * @example Example 1
 * ```http
 * GET /threads/thread-123/subscriptions?limit=50
 * ```
 *
 */
  @doc("Stream thread events (real-time updates).")
  @get
  @route("{threadId}/stream")
  streamThread(
    @path threadId: string,
    @query events?: string,
    @query since?: utcDateTime,
    @query roles?: string,
    @query userIds?: string,
    @query agentIds?: string,
    @query contentTypes?: string,
    @query audience?: string
  ): void | NotFoundError; // SSE stream response

  /**
 * Subscribe agent to watch thread.
 *
 * @usage
 *
 * Use Cases:
 * - Support agents: Watch support threads for user messages
 * - Monitoring agents: Watch threads for specific content types
 * - Multi-agent: Multiple agents watching same thread with different conditions
 *
 * @example Example 1
 * ```http
 * POST /threads/thread-123/watch
 * { "agentId": "agent-support" }
 * ```
 *
 * @response 201 Created
 * ThreadWatch created (agent now watching thread)
 *
 * @response 404 Not Found
 * Thread or agent not found
 *
 * @response 400 Bad Request
 * Agent missing AutoResponseConfig
 *
 * @response 409 Conflict
 * Agent already watching this thread
 *
 * REQUEST:
 * - POST /threads/{threadId}/watch
 * - Body: { agentId: string }
 *
 */
  @doc("Subscribe agent to watch thread.")
  @post
  @route("{threadId}/watch")
  watchThread(
    @path threadId: string,
    @body request: { agentId: string }
  ): ThreadWatch | NotFoundError | ConflictError;

  /**
 * Unsubscribe agent from watching thread.
 *
 * @usage
 *
 * Use Cases:
 * - Remove agent from thread
 * - Temporary disable agent participation
 * - Clean up after thread completion
 *
 * @example Example 1
 * ```http
 * DELETE /threads/thread-123/watch/agent-support
 * ```
 *
 * @response 204 No Content
 * Watch deleted (agent no longer watching)
 *
 * @response 404 Not Found
 * Thread, agent, or watch not found
 *
 * REQUEST:
 * - DELETE /threads/{threadId}/watch/{agentId}
 *
 */
  @doc("Unsubscribe agent from watching thread.")
  @delete
  @route("{threadId}/watch/{agentId}")
  unwatchThread(
    @path threadId: string,
    @path agentId: string
  ): void | NotFoundError;

  /**
 * List agents watching thread.
 *
 * @usage
 *
 * Use Cases:
 * - View which agents are watching thread
 * - Check agent participation status
 * - Monitor auto-response activity
 *
 * @example Example 1
 * ```http
 * GET /threads/thread-123/watch
 * // Returns: [
 * //   { "watchId": "watch-456", "agentId": "agent-support", "active": true, ... },
 * //   { "watchId": "watch-789", "agentId": "agent-monitor", "active": true, ... }
 * // ]
 * ```
 *
 * @response 200 OK
 * Array of ThreadWatch records
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - GET /threads/{threadId}/watch
 *
 */
  @doc("List agents watching thread.")
  @get
  @route("{threadId}/watch")
  listWatchers(
    @path threadId: string
  ): ThreadWatch[] | NotFoundError;
}

/**
 * @example Example 1
 * ```http
 * GET /threads/thread-123/subscriptions/sub-456
 * ```
 *
 */
@route("/threads/{threadId}/subscriptions")
interface ThreadSubscriptions {
  /**
 * Create a webhook subscription.
 *
 * @response 201 Created
 * Subscription created
 *
 * @response 400 Bad Request
 * Invalid webhookUrl or configuration
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - POST /threads/{threadId}/subscriptions
 * - Body: ThreadSubscription with webhookUrl and optional config
 *
 */
  @doc("Create a webhook subscription.")
  @post
  create(
    @path threadId: string,
    @body subscription: ThreadSubscription
  ): ThreadSubscription | NotFoundError;

  /**
 * List subscriptions for a thread.
 *
 * @response 200 OK
 * Array of subscriptions
 *
 * @response 404 Not Found
 * Thread not found
 *
 * REQUEST:
 * - GET /threads/{threadId}/subscriptions?after={subscriptionId}&limit={limit}
 *
 */
  @doc("List subscriptions for a thread.")
  @get
  list(
    @path threadId: string,
    @query after?: string,
    @query limit?: int32 = 100
  ): ThreadSubscription[] | NotFoundError;

  /**
 * Get a specific subscription.
 *
 * @response 200 OK
 * Subscription details
 *
 * @response 404 Not Found
 * Thread or subscription not found
 *
 * REQUEST:
 * - GET /threads/{threadId}/subscriptions/{subscriptionId}
 *
 */
  @doc("Get a specific subscription.")
  @get
  get(
    @path threadId: string,
    @path subscriptionId: string
  ): ThreadSubscription | NotFoundError;

  /**
 * Update a subscription.
 *
 * @response 200 OK
 * Updated subscription
 *
 * @response 404 Not Found
 * Thread or subscription not found
 *
 * REQUEST:
 * - PATCH /threads/{threadId}/subscriptions/{subscriptionId}
 * - Body: Partial ThreadSubscription with fields to update
 *
 */
  @doc("Update a subscription.")
  @patch
  update(
    @path threadId: string,
    @path subscriptionId: string,
    @body subscription: ThreadSubscription
  ): ThreadSubscription | NotFoundError;

  /**
 * Delete a subscription.
 *
 * @response 204 No Content
 * Subscription deleted
 *
 * @response 404 Not Found
 * Thread or subscription not found
 *
 * REQUEST:
 * - DELETE /threads/{threadId}/subscriptions/{subscriptionId}
 *
 */
  @doc("Delete a subscription.")
  @delete
  delete(@path threadId: string, @path subscriptionId: string): void | NotFoundError;
}


/**
 * Error Models
 *
 * Standard error responses for REST API.
 */

/**
 * 404 Not Found Error
 */
@error
model NotFoundError {
  @statusCode statusCode: 404;
  code: "not_found";
  message: string;
}

/**
 * 409 Conflict Error
 */
@error
model ConflictError {
  @statusCode statusCode: 409;
  code: "conflict";
  message: string;
}
