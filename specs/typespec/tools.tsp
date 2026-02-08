/**
 * Tools & Function Calling Models
 *
 * This file defines tool abstractions for agent capabilities.
 *
 * BASE: Microsoft.Extensions.AI.AITool
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Tools/AITool.cs
 *
 * SIMPLIFIED FROM ORIGINAL DESIGN:
 * - Removed tool type discriminator (all tools are essentially functions)
 * - Removed specialized tool types (MCPTool, HandoffTool, RecallTool, etc.)
 * - Modeling all tools as functions with optional lifecycle hooks
 * - Remote execution via endpoint property (like MCP)
 * - Lifecycle hooks for guardrails/memory via optional configuration
 *
 * MESSAGING APP LITMUS TEST:
 * - Tools = Actions/Commands (like Slack slash commands, bot commands)
 * - Simple function signature: name, description, parameters, execute
 * - Special behavior (lifecycle hooks) via optional configuration, not separate types
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./agents.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

/**
 * AI Tool
 *
 * @usage
 * Tool definition for agent capabilities. Represents callable functions that agents can invoke.
 * Supports both local (in-process) and remote (endpoint-based) execution.
 *
 * Key Capabilities:
 * - JSON Schema parameter validation
 * - Remote tool execution via endpoint URLs
 * - Lifecycle hooks for guardrails and audit logging
 * - Human-in-the-loop approval for sensitive operations
 * - OAuth2 scope requirements per tool
 *
 * Unified Design:
 * - All tools are callable functions (no type discriminator)
 * - Remote execution via endpoint property (no separate MCPTool type)
 * - Lifecycle hooks via optional config (no separate GuardrailTool type)
 * - Handoff/dispatch via regular function calls (no special HandoffTool type)
 *
 * @example Simple local tool
 * ```json
 * {
 *   "name": "get_current_time",
 *   "description": "Get the current time in a specified timezone",
 *   "parameters": {
 *     "type": "object",
 *     "properties": {
 *       "timezone": {
 *         "type": "string",
 *         "description": "IANA timezone (e.g., 'America/New_York')"
 *       }
 *     },
 *     "required": ["timezone"]
 *   }
 * }
 * ```
 *
 * @example Remote tool with authentication
 * ```json
 * {
 *   "name": "send_email",
 *   "description": "Send an email via Microsoft Graph API",
 *   "parameters": {
 *     "type": "object",
 *     "properties": {
 *       "to": { "type": "string" },
 *       "subject": { "type": "string" },
 *       "body": { "type": "string" }
 *     },
 *     "required": ["to", "subject", "body"]
 *   },
 *   "endpoint": "https://graph.microsoft.com/v1.0/me/sendMail",
 *   "scopes": {
 *     "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user"
 *   },
 *   "requiresApproval": true
 * }
 * ```
 *
 * @example Tool with lifecycle hooks
 * ```json
 * {
 *   "name": "search_documents",
 *   "description": "Search company documents with content filtering",
 *   "parameters": {
 *     "type": "object",
 *     "properties": {
 *       "query": { "type": "string" }
 *     },
 *     "required": ["query"]
 *   },
 *   "lifecycleHooks": {
 *     "beforeExecute": {
 *       "name": "validate_search_query",
 *       "endpoint": "https://guardrails.example.com/validate"
 *     },
 *     "afterExecute": {
 *       "name": "log_search_audit",
 *       "endpoint": "https://audit.example.com/log"
 *     }
 *   }
 * }
 * ```
 */
model AITool {
  /**
   * Tool name (unique identifier).
   * BASE: MAF AITool.Name (virtual, defaults to GetType().Name)
   *
   * EXAMPLES: "search_memory", "send_email", "get_calendar", "web_search"
   */
  name: string;

  /**
   * Tool description for LLM.
   * BASE: MAF AITool.Description (virtual, defaults to empty string)
   *
   * IMPORTANT: This is shown to the LLM to decide when to call the tool
   *
   * GUIDANCE: Be specific about:
   * - What the tool does
   * - When to use it
   * - What parameters it expects
   *
   * EXAMPLE: "Search the agent's long-term memory for relevant information
   * from previous conversations. Use this when the user asks about past
   * interactions or stored preferences."
   */
  description: string;

  /**
   * Tool parameters (JSON Schema).
   * FROM: Azure Agent API (FunctionTool.parameters)
   *
   * RATIONALE: JSON Schema is universal standard for describing parameters
   * - Used by OpenAI, Anthropic, Azure, etc.
   * - Enables validation and IDE autocomplete
   *
   * MESSAGING APP PATTERN:
   * Like command syntax: /command <required> [optional]
   */
  parameters?: JSONSchema;

  /**
   * Strict schema validation (OpenAI-specific).
   * FROM: OpenAI structured outputs
   *
   * When true, enforces exact schema adherence (no additional properties)
   */
  strict?: boolean;

  /**
 * Execution endpoint for remote tools.
 *
 * @usage
 *
 * Rationale:
 * - Local tools: endpoint is omitted (executed in-process)
 * - Remote tools: endpoint specifies URL (like MCP server, webhooks, APIs)
 * - No need for separate MCPTool type - just a tool with an endpoint
 *
 * EXAMPLES:
 * - "https://mcp-server.example.com/tools/search" (MCP)
 * - "https://api.example.com/webhooks/action" (Webhook)
 * - null (local execution)
 *
 */
  endpoint?: string;

  /**
   * Authentication for remote endpoint.
   * FROM: MCP pattern + A2A Protocol
   * ALIGNED WITH: Agent Schema Tool.connection
   *
   * RATIONALE: Remote tools need authentication
   */
  connection?: Connection;

  /**
 * OAuth2 scopes required for this tool.
 *
 * @usage
 *
 * Rationale:
 * - Fine-grained permissions per tool (vs agent-wide scopes)
 * - Runtime can validate if agent has required scopes before tool execution
 * - Enables dynamic consent flows (request scopes only when tool is used)
 * - Follows OpenAPI 3.0 OAuth2 security scheme format
 *
 * EXAMPLES:
 * - { "https://graph.microsoft.com/Calendars.ReadWrite": "Read and write calendar events" }
 * - { "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user" }
 * - { "read:pets": "Read pet information", "write:pets": "Modify pet information" }
 *
 */
  scopes?: Scopes;

  /**
 * Lifecycle hooks for this tool.
 *
 * @usage
 *
 * Rationale:
 * - Some tools need lifecycle hooks (before_execute, after_execute, on_error)
 * - Enables guardrails, memory persistence, audit logging
 * - Generic pattern vs separate GuardrailTool/MemoryTool types
 *
 * EXAMPLES:
 * - Guardrails: before_execute validates parameters, after_execute validates output
 * - Memory: after_execute persists result to journal
 * - Audit: before_execute logs invocation
 *
 */
  lifecycleHooks?: ToolLifecycleHooks;

  /**
   * Requires user approval before execution (HITL).
   * FROM: AG-UI pattern
   *
   * RATIONALE: Sensitive operations need human-in-the-loop approval
   *
   * M365: Critical for operations like:
   * - Sending emails
   * - Deleting files
   * - Making purchases
   * - Modifying permissions
   */
  requiresApproval?: boolean;

  /**
   * Additional properties.
   * BASE: MAF AITool.AdditionalProperties (IReadOnlyDictionary<string, object?>)
   *
   * FLEXIBLE: Store tool-specific metadata
   *
   * EXAMPLES:
   * - { "category": "productivity", "icon": "calendar" }
   * - { "rateLimit": 10, "rateLimitPeriod": "1m" }
   * - { "journalThreadId": "thread-123" } (for recall tool)
   */
  metadata?: Record<unknown>;
}

/**
 * Tool Lifecycle Hooks
 *
 * ADDITION: Not in any framework (generic pattern)
 *
 * RATIONALE: Some tools need lifecycle-aware behavior without being separate types
 *
 * EXAMPLES:
 * 1. Guardrails:
 *    - before_execute: Validate input parameters
 *    - after_execute: Validate output content
 *    - on_error: Log security violations
 *
 * 2. Memory persistence:
 *    - after_execute: Write result to journal thread
 *
 * 3. Audit logging:
 *    - before_execute: Log invocation with user/agent IDs
 *    - after_execute: Log result with timing
 *    - on_error: Log error with context
 *
 * MESSAGING APP ANALOGY:
 * - Like middleware in web frameworks (Express, ASP.NET)
 * - Hooks wrap tool execution with custom logic
 */
model ToolLifecycleHooks {
  /**
   * Executed before tool invocation.
   * EXAMPLES:
   * - Validate parameters
   * - Check permissions
   * - Log invocation
   * - Apply input guardrails
   */
  beforeExecute?: LifecycleHook;

  /**
   * Executed after successful tool invocation.
   * EXAMPLES:
   * - Validate output
   * - Persist result to memory
   * - Log completion
   * - Apply output guardrails
   */
  afterExecute?: LifecycleHook;

  /**
   * Executed when tool invocation fails.
   * EXAMPLES:
   * - Log error
   * - Send alert
   * - Fallback behavior
   */
  onError?: LifecycleHook;
}

/**
 * Lifecycle Hook
 *
 * ADDITION: Not in any framework (generic pattern)
 *
 * REPRESENTS: Executable hook in tool lifecycle
 *
 * PATTERN: Same as AITool - callable function with parameters
 */
model LifecycleHook {
  /**
   * Hook name (for debugging/logging).
   */
  name: string;

  /**
   * Hook implementation endpoint.
   * - Local hooks: omitted (executed in-process)
   * - Remote hooks: URL to hook implementation
   *
   * EXAMPLES:
   * - null: In-process guardrail function
   * - "https://guardrails.example.com/validate": Remote guardrail service
   */
  endpoint?: string;

  /**
   * Authentication for remote hook.
   */
  connection?: Connection;

  /**
   * Hook-specific configuration.
   * FLEXIBLE: Each hook can have its own config
   *
   * EXAMPLES:
   * - { "maxTokens": 1000 } for output validator
   * - { "journalThreadId": "thread-123" } for memory persistence
   * - { "policyId": "policy-456" } for guardrail
   */
  config?: Record<unknown>;
}

/**
 * RECALL TOOL PATTERN (M365 Requirement)
 *
 * @example Example 1
 * ```typescript
 * const recallTool: AITool = {
 * name: "recall",
 * description: "Search agent's long-term memory for relevant information from previous conversations",
 * parameters: {
 * type: "object",
 * properties: {
 * query: {
 * type: "string",
 * description: "Natural language query to search memory"
 * },
 * maxResults: {
 * type: "integer",
 * description: "Maximum number of results to return",
 * default: 5
 * }
 * },
 * required: ["query"]
 * },
 * metadata: {
 * journalThreadId: "thread-journal-123", // Points to journal thread
 * minRelevance: 0.7 // Minimum semantic similarity score
 * }
 * };
 * ```
 *
 */

/**
 * HANDOFF TOOL PATTERN
 *
 * @example Example 1
 * ```typescript
 * const handoffTool: AITool = {
 * name: "handoff_to_sales_agent",
 * description: "Transfer conversation to sales specialist for product inquiries and pricing",
 * parameters: {
 * type: "object",
 * properties: {
 * context: {
 * type: "string",
 * description: "Context summary to pass to sales agent"
 * }
 * }
 * },
 * metadata: {
 * targetAgentId: "agent-sales-456",
 * contextFilter: { includeRoles: ["user", "assistant"], maxMessages: 10 }
 * }
 * };
 * ```
 *
 */

/**
 * MCP TOOL PATTERN
 *
 * @example Example 1
 * ```typescript
 * const mcpTool: AITool = {
 * name: "filesystem_search",
 * description: "Search filesystem for files matching criteria",
 * endpoint: "https://mcp-filesystem.example.com/search",
 * connection: {
 * kind: "key",
 * key: "Bearer eyJhbGc...",
 * headerName: "Authorization"
 * },
 * parameters: {
 * type: "object",
 * properties: {
 * path: { type: "string" },
 * pattern: { type: "string" }
 * },
 * required: ["path", "pattern"]
 * }
 * };
 * ```
 *
 */

/**
 * GUARDRAIL PATTERN
 *
 * @example Example 1
 * ```typescript
 * const sendEmailTool: AITool = {
 * name: "send_email",
 * description: "Send email to specified recipient",
 * parameters: { ... },
 * lifecycleHooks: {
 * beforeExecute: {
 * name: "content_filter_input",
 * config: { policyId: "email-policy-v1" }
 * },
 * afterExecute: {
 * name: "audit_log",
 * config: { logLevel: "info" }
 * }
 * },
 * requiresApproval: true // HITL for sensitive operation
 * };
 * ```
 *
 */

/**
 * Tool Choice Behavior
 *
 * FROM: Azure Agent API (ToolChoiceBehavior)
 *
 * CONTROLS: How agent uses tools
 *
 * MESSAGING APP ANALOGY:
 * - "auto": Bot decides when to use commands
 * - "required": Bot must use a command
 * - "none": Bot cannot use commands (text-only response)
 * - "specific": Force specific command (like /help shortcut)
 */
@discriminator("kind")
union ToolChoiceBehavior {
  AutoToolChoice,
  RequiredToolChoice,
  NoneToolChoice,
  SpecificToolChoice,
}

model AutoToolChoice {
  kind: "auto";
  // Model decides which tools to call
}

model RequiredToolChoice {
  kind: "required";
  // Model must call at least one tool
}

model NoneToolChoice {
  kind: "none";
  // Disable tool calling
}

model SpecificToolChoice {
  kind: "specific";
  // Force specific tool call
  toolName: string;
}

/**
 * JSON Schema
 *
 * FROM: Azure Agent API + JSON Schema Draft 7
 *
 * REPRESENTS: Parameter schema for tool validation
 *
 * UNIVERSAL STANDARD: Used by OpenAI, Anthropic, Azure, etc.
 */
model JSONSchema {
  /** Schema type */
  type?: "object" | "string" | "number" | "integer" | "boolean" | "array" | "null";

  /** Object properties */
  properties?: Record<JSONSchema>;

  /** Array item schema */
  items?: JSONSchema;

  /** Required properties */
  required?: string[];

  /** Property description */
  description?: string;

  /** Enum values */
  `enum`?: unknown[];

  /** Format hint */
  format?: string;

  /** Minimum value */
  minimum?: float64;

  /** Maximum value */
  maximum?: float64;

  /** Minimum array length */
  minItems?: int32;

  /** Maximum array length */
  maxItems?: int32;

  /** Pattern (regex) */
  pattern?: string;

  /** Additional properties */
  additionalProperties?: JSONSchema | boolean;
}

/**
 * NOTE: Connection (authentication configuration) imported from common.tsp
 * IMPORTED: via "./common.tsp"
 * ALIGNED WITH: Agent Schema Connection system
 */

/**
 * MAF TOOL ABSTRACTIONS NOT IN PUBLIC CONTRACT
 *
 * The following MAF tool abstractions are implementation details or
 * covered by existing models:
 *
 * 1. **AIFunction** (Function-Based Tools)
 *    - BASE: Microsoft.Extensions.AI.AIFunction
 *    - SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Tools/AIFunction.cs
 *    - PURPOSE: Tool created from C# methods with automatic schema generation
 *    - RATIONALE: Implementation detail (how tools are created server-side)
 *    - MAPPING: Exposed as AITool with JSON Schema parameters
 *    - USAGE: CreateFromMethod(), CreateFromLambda() - server-side only
 *
 * 2. **AIFunctionMetadata** (Tool Metadata)
 *    - BASE: Microsoft.Extensions.AI.AIFunctionMetadata
 *    - SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Tools/AIFunctionMetadata.cs
 *    - PURPOSE: Rich metadata for tools (name, description, schema, etc.)
 *    - RATIONALE: Implementation detail
 *    - MAPPING: Properties exposed in AITool model
 *    - PROPERTIES: Name, Description, Parameters (JSON Schema), ReturnType
 *
 * 3. **HostedCodeInterpreterTool** (Provider-Side Execution)
 *    - BASE: Microsoft.Extensions.AI.HostedCodeInterpreterTool (conceptual)
 *    - SOURCE: MAF concepts document (code interpreter abstraction)
 *    - PURPOSE: Server-side code execution tools (Python, sandboxed environments)
 *    - RATIONALE: Provider-specific implementation (OpenAI Code Interpreter, Azure Container Apps)
 *    - MAPPING: Modeled as AITool with appropriate metadata
 *    - EXAMPLE:
 *      ```typescript
 *      const codeInterpreterTool: AITool = {
 *        name: "code_interpreter",
 *        description: "Execute Python code in sandboxed environment",
 *        parameters: {
 *          type: "object",
 *          properties: {
 *            code: { type: "string", description: "Python code to execute" }
 *          },
 *          required: ["code"]
 *        },
 *        metadata: {
 *          executionEnvironment: "python3.11",
 *          sandboxed: true,
 *          allowedPackages: ["numpy", "pandas", "matplotlib"]
 *        }
 *      };
 *      ```
 *
 * 4. **AITool vs AIFunction Distinction**
 *    - MAF: AITool is abstract base, AIFunction is concrete implementation
 *    - TypeSpec: Single AITool model covers both
 *    - RATIONALE: Wire protocol doesn't distinguish creation method
 *    - CLIENT PERSPECTIVE: All tools look the same (name, description, parameters)
 */
