/**
 * Execution & Lifecycle Models
 *
 * This file defines the core execution primitives for agent runtime.
 *
 * BASE: Microsoft Agent Protocol (MAF)
 * - AIAgent: Core agent abstraction
 * - AgentResponse: Response model
 * - AgentSession: Session/thread abstraction
 *
 * ADDITIONS FROM:
 * - OpenAI Agents SDK: RunResult, Turn tracking, max_turns enforcement, guardrail results
 * - Azure Agent API: Run resource with status enum, visibility annotations
 * - A2A Protocol: 8-state lifecycle with interruption states
 *
 * M365 AGENT PLATFORM REQUIREMENTS SATISFIED:
 * - Conversation-centric model (via Thread)
 * - Run tracking for orchestration pipeline
 * - Support for both stateful (with session) and stateless (without session) modes
 * - Agent Journal integration (cross-conversation memory via journalId)
 * - Task dispatch support (via handoff tracking)
 */

import "@typespec/http";
import "@typespec/rest";
import "@typespec/versioning";
import "./common.tsp";
import "./messages.tsp";
import "./threads.tsp";
import "./tools.tsp";
import "./usage.tsp";
import "./agents.tsp";
import "./streaming.tsp";
import "./conditions.tsp";
import "./hooks.tsp";
import "./subscriptions.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;

namespace Microsoft.Agents.AI;

/**
 * Run - Execution Instance
 *
 * BASE: MAF ExecuteAsync interface (stateless execution)
 * FROM: OpenAI Agents SDK (RunResult) + Azure Agent API (Run resource)
 * MAPS TO: MAF IChatClient.ExecuteAsync(prompt, tools, options)
 *
 * MAF MAPPING:
 * - Run.input → ExecuteAsync prompt parameter (ChatMessage[])
 * - Run.agent → ExecuteAsync with inline agent configuration
 * - Run.options → ExecuteAsync ChatOptions parameter
 * - Run.output → ExecuteAsync returns ChatCompletion with Messages
 * - Run.usage → ChatCompletion.Usage (token counts)
 *
 * KEY DESIGN DECISIONS:
 * 1. Adopted 11-state lifecycle (expanded from OpenAI's 8 states and Azure's 5 states)
 *    - Added: queued, requires_action, input_required, auth_required, cancelling, timeout
 * 2. Added threadCleanup from LangChain Agent Protocol (ephemeral vs stateful runs)
 * 3. Made threadId optional (supports stateless execution without thread)
 *
 * M365 REQUIREMENTS:
 * - Supports orchestration pipeline tracking (runId, status, timestamps)
 * - Enables conversation-scoped execution (threadId)
 * - Tracks token usage for cost management (usage)
 * - Stores guardrail results for compliance (input/output/tool guardrails)
 *
 * PROACTIVE MESSAGING SUPPORT:
 * Runs can be triggered by user messages OR external events:
 *
 * 1. User-Initiated Run (Traditional):
 *    POST /runs
 *    { threadId: "...", input: [{ role: "user", contents: [{ kind: "text", text: "Hello" }] }] }
 *
 * 2. Agent-Initiated Run (Proactive):
 *    External event (timer, webhook, system alert) →
 *    POST /threads/{threadId}/messages (creates EventContent message with role="channel") →
 *    POST /runs { threadId: "...", input: [] } (agent processes trigger event from thread) →
 *    POST to ThreadSubscription.webhookUrl (notify client of completion)
 *
 * PATTERN: Like Bot Framework's ConversationReference but with webhook subscriptions
 * - Bot Framework: Stores ConversationReference, POSTs activity to serviceUrl
 * - Our Approach: Stores ThreadSubscription, POSTs notification to webhookUrl
 *
 * SEE ALSO:
 * - ThreadSubscription: Webhook registration for proactive notifications
 * - EventContent (messages.tsp): External trigger events with role="channel"
 * - Thread.lastActivityAt: Polling support for clients without webhooks
 *
 * @usage
 * Core execution model representing a single agent invocation within a conversation.
 * Tracks lifecycle, input/output messages, token usage, and execution results.
 * Supports both stateful (with thread) and stateless (without thread) execution.
 *
 * Key Capabilities:
 * - 11-state lifecycle (queued → in_progress → completed/failed/cancelled)
 * - Stateful execution with thread persistence (threadId)
 * - Stateless/ephemeral execution (threadId optional, threadCleanup=delete)
 * - Token usage tracking for cost management
 * - Webhook notifications for async completion
 * - Proactive messaging support (user-initiated or event-triggered)
 *
 * Execution Modes:
 * - Synchronous: POST /runs/wait (blocks until complete)
 * - Asynchronous: POST /runs (returns immediately, poll or webhook)
 * - Ephemeral: POST /runs/wait with threadCleanup=delete (no persistence)
 *
 * M365 Integration:
 * - Links to Thread for conversation tracking
 * - Links to Agent Journal for cross-conversation memory
 * - Stores guardrail results for compliance
 *
 * @example Stateful run with thread
 * ```json
 * {
 *   "agentId": "agent_001",
 *   "threadId": "thread_123",
 *   "input": [
 *     {
 *       "role": "user",
 *       "contents": [{ "kind": "text", "text": "What's 2+2?" }]
 *     }
 *   ]
 * }
 * ```
 *
 * @example Stateless run without thread
 * ```json
 * {
 *   "agentId": "agent_001",
 *   "input": [
 *     {
 *       "role": "user",
 *       "contents": [{ "kind": "text", "text": "Translate 'hello' to Spanish" }]
 *     }
 *   ],
 *   "threadCleanup": "delete"
 * }
 * ```
 *
 * @example Run with inline agent definition
 * ```json
 * {
 *   "agent": {
 *     "type": "prompt",
 *     "model": "gpt-4o",
 *     "instructions": "You are a math tutor"
 *   },
 *   "input": [
 *     {
 *       "role": "user",
 *       "contents": [{ "kind": "text", "text": "Explain calculus" }]
 *     }
 *   ]
 * }
 * ```
 *
 * @example Run with webhook notification
 * ```json
 * {
 *   "agentId": "agent_001",
 *   "threadId": "thread_123",
 *   "input": [
 *     {
 *       "role": "user",
 *       "contents": [{ "kind": "text", "text": "Generate report" }]
 *     }
 *   ],
 *   "webhook": "https://example.com/webhook"
 * }
 * ```
 */
@resource("runs")
model Run {
  /**
   * Unique identifier for this run.
   * FROM: Azure Agent API
   * GENERATED: Server-generated GUID
   */
  @key
  @visibility("read")
  runId: string;

  /**
   * Unique identifier for the agent that processed this run.
   * FROM: Azure Agent API
   * M365: Maps to Agent ID (Entra Object ID in Phase 2)
   */
  agentId: string;

  /**
   * Optional identifier for the conversation thread.
   * FROM: Azure Agent API (required) → Made optional for stateless support
   * M365: Links run to conversation in Conversation Store
   *
   * OPTIONAL: Allows stateless execution when omitted
   */
  threadId?: string;

  /**
   * Optional identifier for the agent's journal.
   * ADDITION: From M365 Agent Platform (cross-conversation memory)
   *
   * M365 REQUIREMENT: Links run to Agent Journal for memory substrate
   * - Agent Journal stores knowledge across conversations
   * - Different from threadId (single conversation) and sessionId (multi-conversation)
   */
  journalId?: string;

  /**
   * Current lifecycle status of the run.
   * FROM: Azure Agent API (5 states) + OpenAI Agents SDK (8 states) + A2A Protocol (interruption states)
   *
   * EXPANDED from Azure's 5 states to OpenAI's 8 states plus A2A interruption states:
   * - queued: Run is waiting to start (from OpenAI)
   * - in_progress: Run is executing (both)
   * - requires_action: Tool execution needed (from OpenAI)
   * - input_required: Human input needed (from A2A - HITL)
   * - auth_required: Authentication needed (from A2A)
   * - cancelling: User requested cancellation, run is stopping (from OpenAI)
   * - cancelled: Run was cancelled by user before completion (both)
   * - failed: Run encountered error (both)
   * - completed: Run finished successfully (both)
   * - incomplete: Run stopped before completion (both)
   *
   * CANCELLATION STATES:
   * - cancelling: Transitional state while stopping
   * - cancelled: Final state after cancellation complete
   *
   * M365: Enables orchestration pipeline to track run state
   */
  @visibility("read")
  status: RunStatus;

  /**
   * Messages generated during this run.
   * FROM: Azure Agent API (output) + MAF (AgentResponse.Messages)
   *
   * M365: These messages are stored in Conversation Store
   */
  @visibility("read")
  output: ChatMessage[];

  /**
   * Token usage statistics for this run.
   * FROM: Azure Agent API (CompletionUsage) + MAF (UsageDetails)
   *
   * M365: Tracked for cost management and quotas
   */
  @visibility("read")
  usage: CompletionUsage;

  /**
   * Timestamp when the run was created.
   * FROM: Azure Agent API (createdAt) + OpenAI Agents SDK
   */
  @visibility("read")
  createdAt: utcDateTime;

  /**
   * Timestamp of last status update.
   * FROM: OpenAI Agents SDK (updated_at)
   * ADDITION: Not in Azure Agent API
   */
  @visibility("read")
  updatedAt: utcDateTime;

  /**
   * Timestamp when the run finished (completed, failed, or cancelled).
   * FROM: Azure Agent API (completedAt)
   */
  @visibility("read")
  completedAt?: utcDateTime;

  /**
   * Timestamp when the run was cancelled (if status=cancelled).
   * ADDITION: User-initiated cancellation tracking
   *
   * PURPOSE: Tracks when user clicked "stop generating" or cancelled the run
   */
  @visibility("read")
  cancelledAt?: utcDateTime;

  /**
   * Reason for cancellation (if provided by user).
   * ADDITION: User-initiated cancellation tracking
   *
   * PURPOSE: Optional reason for analytics/debugging
   * EXAMPLES: "User changed mind", "Cost limit reached", "User navigated away"
   */
  @visibility("read")
  cancellationReason?: string;

  /**
   * Error details if run failed or completed incompletely.
   * FROM: Azure Agent API (incompleteDetails) - generalized
   *
   * GENERALIZED: Generic error model with code + message pattern
   * Like HTTP status codes or gRPC status - structured error codes
   * that clients can handle programmatically.
   *
   * M365: Provides user-facing error messages with machine-readable codes
   */
  @visibility("read")
  error?: RunError;

  /**
   * Input messages that started this run.
   * FROM: Azure Agent API (input)
   * NOTE: Only included in create requests, not responses
   */
  @visibility("create")
  input: ChatMessage[];

  /**
   * Agent configuration for this run.
   * FROM: Azure Agent API (agent)
   * ALIGNED WITH: Agent Schema AgentDefinition
   *
   * OPTIONAL: If omitted, uses existing agent (agentId)
   * If provided, executes with inline agent definition (stateless)
   *
   * MAPS TO: MAF ExecuteAsync with inline agent configuration
   */
  @visibility("create")
  agent?: AgentDefinition;

  /**
   * Optional overrides for existing agent configuration.
   * FROM: Azure Agent API (part of agent-based completion)
   *
   * M365: Enables per-request customization (e.g., different temperature for specific task)
   *
   * NOTE: Only applicable for PromptAgent types
   */
  @visibility("create")
  overrides?: PromptAgent;

  /**
   * Configuration options for run execution.
   * FROM: Azure Agent API (RunOptions)
   */
  @visibility("create")
  options?: RunOptions;

  /**
   * User who initiated this run.
   * FROM: Azure Agent API (userId)
   *
   * M365: Maps to Entra User ID (Object ID)
   */
  @visibility("create")
  userId?: string;

  /**
 * Thread cleanup strategy for this run.
 *
 * @usage
 *
 * Use Cases:
 * - POST /runs/wait with threadCleanup=delete: Ephemeral execution
 * - POST /runs with threadCleanup=keep: Background run with thread persistence
 * - POST /runs with threadCleanup=delete: Background run with auto-cleanup
 *
 * M365: Controls whether conversation thread is retained in Conversation Store
 *
 *
 * Rationale:
 * - keep: Stateful runs, multi-turn conversations (default)
 * - delete: Ephemeral runs, one-shot queries (auto-cleanup)
 *
 */
  @visibility("create")
  threadCleanup?: ThreadCleanup = ThreadCleanup.keep;

  /**
 * Webhook URL for run completion notification.
 *
 * @usage
 *
 * Use Cases:
 * - Background runs: Create run, return immediately, webhook on completion
 * - Long-running tasks: Avoid polling, get notified when done
 * - Serverless architectures: Trigger next step via webhook
 *
 */
  @visibility("create")
  webhook?: string;

  /**
   * Custom metadata for the run.
   * FROM: Azure Agent API (metadata)
   *
   * M365: Can store tenant ID, department, cost center, etc.
   */
  @visibility("create", "read")
  metadata?: Record<unknown>;

  /**
   * Underlying provider representation.
   * FROM: MAF (AgentResponse.RawRepresentation)
   *
   * Stores the original response from OpenAI/Anthropic/etc for debugging
   */
  @visibility("read")
  rawRepresentation?: unknown;
}

/**
 * Run Wait Response
 *
 * FROM: LangChain Agent Protocol (wait endpoints)
 *
 * Response model for POST /runs/wait and GET /runs/{runId}/wait
 * Returns final run state after completion (blocking until done).
 *
 * RATIONALE: Simplified response model for wait endpoints
 * - Only includes final state fields (no create-only fields)
 * - Optimized for ephemeral runs (threadId is optional)
 * - Focused on completion data (status, output, error)
 *
 * WAIT PATTERN:
 * - POST /runs/wait: Create ephemeral run and wait for completion
 * - GET /runs/{runId}/wait: Wait for existing run to complete
 * - Both return this response model when run finishes
 *
 * DIFFERENCE FROM Run:
 * - Run: Full model with create/read visibility annotations
 * - RunWaitResponse: Simplified read-only completion state
 */
model RunWaitResponse {
  /**
   * Unique identifier for the completed run.
   */
  runId: string;

  /**
   * Thread ID if run was stateful (null for ephemeral runs).
   * OPTIONAL: Omitted when threadCleanup=delete
   */
  threadId?: string;

  /**
   * Final run status (completed, failed, cancelled, timeout, incomplete).
   */
  status: RunStatus;

  /**
   * Messages generated during the run.
   */
  output: ChatMessage[];

  /**
   * Token usage statistics.
   */
  usage?: CompletionUsage;

  /**
   * Error details if run failed or completed incompletely.
   */
  error?: RunError;

  /**
   * Timestamp when run was created.
   */
  createdAt: utcDateTime;

  /**
   * Timestamp when run finished.
   */
  completedAt?: utcDateTime;
}

/**
 * Run Status Enum
 *
 * FROM: OpenAI Agents SDK (8 states) + A2A Protocol (interruption states) + LangChain Agent Protocol
 * EXPANDED from Azure Agent API (5 states)
 */
enum RunStatus {
  /** Run is queued and waiting to start */
  queued,

  /** Run is currently executing */
  in_progress,

  /** Run is waiting for tool execution results */
  requires_action,

  /** Run is waiting for human input (HITL) */
  input_required,

  /** Run is waiting for authentication/authorization */
  auth_required,

  /** User requested cancellation, run is stopping (transitional state) */
  cancelling,

  /** Run was cancelled by user before completion (final state) */
  cancelled,

  /** Run encountered an error */
  failed,

  /** Run finished successfully */
  completed,

  /** Run stopped before completion */
  incomplete,

  /** Run exceeded time limit (from LangChain Agent Protocol) */
  timeout,
}


/**
 * Cancel Action
 *
 * @usage
 *
 * Use Cases:
 * - interrupt: User stops generation, wants to see partial output
 * - rollback: Clean up failed/unwanted run completely (like "undo")
 *
 */
enum CancelAction {
  /** Stop run but preserve state and history */
  interrupt,

  /** Stop run and delete run record + messages created by this run */
  rollback,
}

/**
 * Run Error
 *
 * FROM: Azure Agent API (IncompleteDetails) - generalized
 *
 * GENERALIZED: Standard error model with code + message pattern
 * Like HTTP status codes, gRPC status codes, or messaging app error codes
 */
model RunError {
  /**
   * Machine-readable error code.
   * EXAMPLES:
   * - "max_turns_exceeded": Run hit max_turns limit
   * - "tool_execution_failed": Tool execution error
   * - "rate_limit_exceeded": API rate limit hit
   * - "context_length_exceeded": Token limit exceeded
   * - "auth_required": Authentication needed
   * - "user_cancelled": User cancelled the run
   */
  code: string;

  /**
   * Human-readable error message.
   */
  message: string;

  /**
   * Optional additional error details.
   * FLEXIBLE: Can include stack traces, request IDs, etc.
   */
  details?: Record<unknown>;
}

/**
 * Tool Output
 *
 * @usage
 *
 * Use Cases:
 * - Tool approval: Human reviews delete_file before execution
 * - External execution: Tools executed by external system, results fed back
 * - Modified execution: Human modifies tool arguments before running
 *
 */
model ToolOutput {
  /**
   * Tool call ID this output corresponds to.
   * MUST: Match callId from FunctionCallContent in required_action.tool_calls
   */
  tool_call_id: string;

  /**
   * Tool execution result.
   * FLEXIBLE: String output or structured data (serialized to string)
   *
   * EXAMPLES:
   * - Simple: "File deleted successfully"
   * - JSON: "{\"status\":\"success\",\"files_deleted\":3}"
   * - Error: "Permission denied: /protected/file.txt"
   */
  output: string;
}

/**
 * NOTE: Turn model removed - redundant with ChatMessage
 *
 * @usage
 *
 * Rationale:
 * - ChatMessage already captures: role, content, tool calls/results, timestamp
 * - Turn-by-turn analysis can be derived from message sequence
 * - Usage tracking can be per-message or aggregated at Run level
 * - Simpler model = easier to understand and implement
 *
 */

/**
 * Run Options
 *
 * FROM: Azure Agent API (RunOptions) + OpenAI Agents SDK (RunOptions/RunConfig)
 */
model RunOptions {
  /**
   * Continuation token for resuming background responses.
   * FROM: MAF (AgentRunOptions.ContinuationToken)
   */
  continuationToken?: string;
}






/**
 * Hook Types & Responses
 *
 * NOTE: Hook and HookActionResponse types have been moved to hooks.tsp.
 * Import hooks.tsp to use RemoteHook, BlockHook, ModifyHook, TelemetryHook, SendMessageHook,
 * and their corresponding response types.
 */


/**
 * Run Subscription - Webhook Notification Registration
 *
 * @usage
 *
 * Use Cases:
 * - Monitor long-running executions
 * - Track run lifecycle for orchestration
 * - Get notified when specific runs complete
 * - Build run activity dashboards
 *
 */

/**
 * Agent Subscription - Webhook Notification Registration
 *
 * @usage
 *
 * Use Cases:
 * - Monitor agent activity across all threads
 * - Track agent configuration changes
 * - Build agent analytics dashboards
 * - Debug agent behavior in production
 * - Track agent errors and failures
 *
 */

/**
 * Chat History Provider Configuration
 *
 * BASE: MAF ChatHistoryProvider (abstract base class)
 * SOURCE: /agent-framework/dotnet/src/Microsoft.Agents.AI.Abstractions/ChatHistoryProvider.cs
 *
 * REPRESENTS: Configuration for pluggable conversation history storage
 *
 * MAF PATTERN:
 * - GetHistoryAsync(session, additionalMessages?) - Retrieve conversation history
 * - UpdateHistoryAsync(session, response) - Store new messages
 * - Apply filters: token limits, message count, time windows
 *
 * MESSAGING APP ANALOGY:
 * Like configuring where your chat history is stored:
 * - In-memory (ephemeral)
 * - Database (persistent)
 * - Service (like Microsoft Graph API for Teams/Outlook)
 */
model ChatHistoryProviderConfig {
  /**
   * Provider type.
   */
  providerType: "inMemory" | "cosmosDb" | "sqlServer" | "serviceApi" | "custom";

  /**
   * Connection configuration (for database/service providers).
   * ALIGNED WITH: Agent Schema Connection system
   */
  connection?: Connection;

  /**
   * History retrieval options.
   */
  retrievalOptions?: HistoryRetrievalOptions;

  /**
   * Custom provider configuration.
   */
  config?: Record<unknown>;
}

/**
 * History Retrieval Options
 *
 * FROM: MAF ChatHistoryProvider filters
 * SOURCE: /agent-framework/dotnet/src/Microsoft.Agents.AI.Abstractions/ChatHistoryProvider.cs
 *
 * REPRESENTS: Filters applied when retrieving conversation history
 *
 * MAF PATTERN: Filter chain to control which history is included
 */
model HistoryRetrievalOptions {
  /**
   * Maximum messages to retrieve.
   * MAF: Message count filter
   */
  maxMessages?: int32;

  /**
   * Maximum tokens to include (context window management).
   * MAF: Token budget filter
   */
  maxTokens?: int32;

  /**
   * Time range filter.
   * MAF: Time-based filter
   */
  timeRange?: {
    start?: utcDateTime;
    end?: utcDateTime;
  };

  /**
   * Filter by message roles.
   * EXAMPLES: Only include user/assistant messages, exclude system
   */
  includeRoles?: ChatRole[];

  /**
   * Filter by message roles to exclude.
   */
  excludeRoles?: ChatRole[];
}
