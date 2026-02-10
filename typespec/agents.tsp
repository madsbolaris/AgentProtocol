/**
 * Agent Models & Definitions
 *
 * This file defines agent-related models for discovery, configuration, and execution.
 *
 * CONTENTS:
 * - AgentDefinition: Union of agent types (PromptAgent, ContainerAgent, Workflow)
 * - AgentCard: Discovery and registration metadata
 * - AgentModel: LLM configuration
 * - Supporting models: PropertySchema, PromptTemplate
 *
 * ALIGNED WITH:
 * - Microsoft Agent Schema (AgentDefinition, PromptAgent, ContainerAgent, Workflow)
 * - Google A2A Protocol (Agent Card)
 * - Azure Agent API (AgentModel, ModelOptions)
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./messages.tsp";
import "./tools.tsp";
import "./conditions.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

/**
 * Agent Definition
 *
 * FROM: Azure Agent API (AgentOptions, referenced but not defined)
 * BASE: MAF does not have this (uses AIAgent directly)
 * ALIGNED WITH: Agent Schema AgentDefinition
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/agent.tsp)
 *
 * RATIONALE: Enables inline agent definition without creating persistent agent resource
 *
 * AGENT TYPES:
 * - PromptAgent: Direct execution with configured model and tools (available now)
 * - ContainerAgent: Container-based agent managed by external providers (coming soon)
 * - Workflow: Multi-step orchestrated agent (coming soon)
 *
 * NOTE: Currently only PromptAgent is fully specified. ContainerAgent and Workflow
 * will be added in future versions once their designs are validated.
 */
@discriminator("kind")
union AgentDefinition {
  PromptAgent,
  // ContainerAgent,  // Coming soon
  // Workflow,        // Coming soon
}

/**
 * Prompt Agent (Direct Execution)
 *
 * ALIGNED WITH: Agent Schema PromptAgent
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/agent.tsp)
 *
 * RATIONALE: Direct execution agent with configured tools and models
 */
model PromptAgent {
  /**
   * Agent type discriminator.
   * ALIGNED WITH: Agent Schema PromptAgent.kind
   */
  kind: "prompt";

  /**
   * Unique agent identifier.
   * ALIGNED WITH: Agent Schema PromptAgent.name
   */
  name?: string;

  /**
   * UI display name (human-friendly).
   * ALIGNED WITH: Agent Schema PromptAgent.displayName
   * ADDITION: Not in original design
   */
  displayName?: string;

  /**
   * Agent capabilities description.
   * ALIGNED WITH: Agent Schema PromptAgent.description
   */
  description?: string;

  /**
   * Model configuration.
   * ALIGNED WITH: Agent Schema PromptAgent.model
   * Accepts either a string shorthand (e.g., "gpt-4") or a full AgentModel object.
   */
  `model`: string | AgentModel;

  /**
   * System instructions (agent behavior directives).
   * ALIGNED WITH: Agent Schema PromptAgent.instructions
   */
  instructions?: string | ChatMessage[];

  /**
   * Additional guidance context.
   * ALIGNED WITH: Agent Schema PromptAgent.additionalInstructions
   * RENAMED FROM: closingInstructions (clearer naming)
   */
  additionalInstructions?: string | ChatMessage[];

  /**
   * Prompt template rendering configuration.
   * ALIGNED WITH: Agent Schema PromptAgent.template
   * ADDITION: Not in original design
   *
   * Supports Mustache, Jinja2, and Prompty template formats.
   */
  template?: PromptTemplate;

  /**
   * Input parameters structure.
   * ALIGNED WITH: Agent Schema PromptAgent.inputSchema
   * ADDITION: Not in original design
   *
   * RATIONALE: Enables structured inputs with validation
   */
  inputSchema?: JSONSchema;

  /**
   * Expected output format.
   * ALIGNED WITH: Agent Schema PromptAgent.outputSchema
   * ADDITION: Not in original design
   *
   * RATIONALE: Enables structured outputs (OpenAI structured outputs, etc.)
   */
  outputSchema?: JSONSchema;

  /**
   * Available tools.
   * ALIGNED WITH: Agent Schema PromptAgent.tools
   */
  tools?: AITool[];

  /**
   * Tool calling behavior.
   * FROM: Azure Agent API (ToolChoiceBehavior)
   */
  toolChoice?: ToolChoiceBehavior;

  /**
   * Custom metadata.
   * ALIGNED WITH: Agent Schema PromptAgent.metadata
   */
  metadata?: Record<unknown>;

  /**
 * Auto-response configuration for thread participation.
 *
 * @usage
 *
 * Use Cases:
 * - Support agents: Respond to user messages in support threads
 * - Specialized agents: Respond only when mentioned or when specific content appears
 * - Monitoring agents: React to video, files, or other content types
 *
 */
  autoResponse?: AutoResponseConfig;
}

/**
 * COMING SOON: Container Agent (Hosted Agent)
 *
 * ContainerAgent will support container-based agents managed by external providers.
 * Design is being validated and will be added in a future version.
 *
 * Planned alignment with Agent Schema ContainerAgent (HostedAgent).
 */

/**
 * COMING SOON: Workflow (Multi-Step Orchestration)
 *
 * Workflow will support multi-step orchestrated agents handling complex processes.
 * Design is being validated and will be added in a future version.
 *
 * Planned alignment with Agent Schema Workflow.
 */

/**
 * Agent Model Configuration
 *
 * FROM: Azure Agent API
 * ALIGNED WITH: Agent Schema Model
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/model.tsp)
 */
model AgentModel {
  /**
   * Model identifier (e.g., "gpt-4o", "claude-sonnet-4").
   * ALIGNED WITH: Agent Schema Model.id
   */
  id: string;

  /**
   * Provider name (e.g., "openai", "azure", "anthropic", "google").
   * ALIGNED WITH: Agent Schema Model.provider
   */
  provider?: string;

  /**
   * API type (e.g., "chat", "responses").
   * ALIGNED WITH: Agent Schema Model.apiType
   * ADDITION: Not in original design
   *
   * RATIONALE: Distinguishes between API patterns (chat completion vs response stream)
   */
  apiType?: string;

  /**
   * Model service authentication.
   * ALIGNED WITH: Agent Schema Model.connection
   * RENAMED FROM: endpoint (now part of connection)
   *
   * RATIONALE: Connection includes both endpoint and authentication
   */
  connection?: Connection;

  /**
   * Model behavior parameters.
   * ALIGNED WITH: Agent Schema Model.options
   */
  options?: ModelOptions;
}

/**
 * Model Options
 *
 * FROM: Azure Agent API (OpenAIModelOptions, AnthropicModelOptions, etc.)
 * ALIGNED WITH: Agent Schema ModelOptions
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/model.tsp)
 *
 * SIMPLIFIED: Single model covering all providers (was discriminated union)
 * RATIONALE: Most parameters are provider-agnostic
 *
 * EXTENSIBILITY: This model is extensible and accepts additional properties beyond
 * the standard fields listed below. Provider-specific options can be added directly
 * to the options object rather than nested in a separate field.
 *
 * EXAMPLES OF PROVIDER-SPECIFIC PROPERTIES:
 * - "reasoningEffort": "high" (OpenAI o1/o3 reasoning models)
 * - "extendedThinking": true (Anthropic extended thinking)
 * - "safetySettings": [...] (Gemini safety configuration)
 */
model ModelOptions {
  /**
   * Sampling temperature (0-2).
   * ALIGNED WITH: Agent Schema ModelOptions.temperature
   *
   * GUIDANCE: 0 = deterministic, 1 = balanced, 2 = creative
   */
  temperature?: float32;

  /**
   * Top-P sampling (nucleus sampling, 0-1).
   * ALIGNED WITH: Agent Schema ModelOptions.topP
   *
   * GUIDANCE: Probability mass threshold
   */
  topP?: float32;

  /**
   * Top-K sampling.
   * ALIGNED WITH: Agent Schema ModelOptions.topK
   *
   * GUIDANCE: Consider top K tokens (Anthropic, Gemini)
   */
  topK?: int32;

  /**
   * Maximum generation length (tokens).
   * ALIGNED WITH: Agent Schema ModelOptions.maxOutputTokens
   *
   * NOTE: Replaces maxTokens (Anthropic) and maxOutputTokens (OpenAI)
   */
  maxOutputTokens?: int32;

  /**
   * Frequency penalty (-2 to 2).
   * ALIGNED WITH: Agent Schema ModelOptions.frequencyPenalty
   *
   * GUIDANCE: Penalizes token frequency (OpenAI, Azure)
   */
  frequencyPenalty?: float32;

  /**
   * Presence penalty (-2 to 2).
   * ALIGNED WITH: Agent Schema ModelOptions.presencePenalty
   *
   * GUIDANCE: Penalizes token presence (OpenAI, Azure)
   */
  presencePenalty?: float32;

  /**
   * Deterministic generation seed.
   * ALIGNED WITH: Agent Schema ModelOptions.seed
   *
   * GUIDANCE: Same seed + params = same output
   */
  seed?: int32;

  /**
   * Stop sequences.
   * ALIGNED WITH: Agent Schema ModelOptions.stopSequences
   *
   * NOTE: Unified name (was stop for OpenAI, stopSequences for Anthropic/Gemini)
   */
  stopSequences?: string[];

  /**
   * Enable parallel tool calling.
   * ALIGNED WITH: Agent Schema ModelOptions.allowMultipleToolCalls
   *
   * GUIDANCE: Multiple tools in single turn (OpenAI)
   */
  allowMultipleToolCalls?: boolean;

  ...Record<unknown>;
}

/**
 * Model Capabilities
 *
 * FROM: Azure AI Foundry SDK capability discovery
 * PURPOSE: Describes what a model can do (features, limits, content types)
 *
 * RATIONALE: Enables clients to:
 * - Validate requests before sending (avoid errors)
 * - Discover model features programmatically
 * - Make intelligent model selection decisions
 *
 * USAGE: Included in AgentCard, computed from model configuration
 *
 * @usage
 * Describes the capabilities and limits of an AI model.
 * Used for capability discovery, request validation, and intelligent model selection.
 * Computed from model configuration and included in AgentCard responses.
 *
 * Key Capabilities:
 * - Feature flags (vision, tools, structured output, streaming, thinking)
 * - Token limits (context window, input, output)
 * - Content type support (text, image, audio, video)
 * - Provider and model family information
 *
 * Use Cases:
 * - "Does this model support vision?" - Check capabilities.vision
 * - "What's the context window?" - Check capabilities.maxTokens
 * - "Can I use tools?" - Check capabilities.functionCalling
 * - "Validate request before sending" - Check against capabilities
 *
 * @example GPT-4o capabilities
 * ```json
 * {
 *   "vision": true,
 *   "functionCalling": true,
 *   "structuredOutput": true,
 *   "streaming": true,
 *   "thinking": false,
 *   "parallelToolCalls": true,
 *   "maxTokens": 128000,
 *   "maxInputTokens": 128000,
 *   "maxOutputTokens": 16384,
 *   "supportedContentTypes": ["text", "image"],
 *   "provider": "openai",
 *   "modelFamily": "gpt-4"
 * }
 * ```
 *
 * @example Claude 3 Sonnet capabilities
 * ```json
 * {
 *   "vision": true,
 *   "functionCalling": true,
 *   "structuredOutput": true,
 *   "streaming": true,
 *   "thinking": true,
 *   "parallelToolCalls": true,
 *   "maxTokens": 200000,
 *   "maxInputTokens": 200000,
 *   "maxOutputTokens": 4096,
 *   "supportedContentTypes": ["text", "image"],
 *   "provider": "anthropic",
 *   "modelFamily": "claude-3"
 * }
 * ```
 *
 * @example Text-only model capabilities
 * ```json
 * {
 *   "vision": false,
 *   "functionCalling": true,
 *   "structuredOutput": true,
 *   "streaming": true,
 *   "thinking": false,
 *   "parallelToolCalls": false,
 *   "maxTokens": 4096,
 *   "maxInputTokens": 4096,
 *   "maxOutputTokens": 2048,
 *   "supportedContentTypes": ["text"],
 *   "provider": "openai",
 *   "modelFamily": "gpt-3.5"
 * }
 * ```
 */
model ModelCapabilities {
  /**
   * Vision support (image understanding).
   *
   * EXAMPLES:
   * - gpt-4o: true
   * - gpt-3.5-turbo: false
   * - claude-3-sonnet: true
   */
  vision: boolean;

  /**
   * Function/tool calling support.
   *
   * EXAMPLES:
   * - gpt-4o: true
   * - gpt-3.5-turbo: true
   * - claude-3-sonnet: true
   */
  functionCalling: boolean;

  /**
   * Structured output support (JSON schema validation).
   *
   * EXAMPLES:
   * - gpt-4o: true (native JSON mode)
   * - claude-3-sonnet: true (via tools)
   */
  structuredOutput: boolean;

  /**
   * Streaming support (incremental token generation).
   *
   * RATIONALE: All modern models support streaming
   */
  streaming: boolean;

  /**
   * Extended thinking/reasoning support.
   *
   * EXAMPLES:
   * - o1/o3 models: true (reasoning tokens)
   * - claude-3 with extended thinking: true
   * - gpt-4o: false
   */
  thinking: boolean;

  /**
   * Parallel tool calling support (multiple tools in one turn).
   *
   * EXAMPLES:
   * - gpt-4o: true
   * - claude-3-sonnet: true (default behavior)
   */
  parallelToolCalls: boolean;

  /**
   * Maximum total tokens (context window).
   *
   * EXAMPLES:
   * - gpt-4o: 128000
   * - claude-3-sonnet: 200000
   */
  maxTokens: int32;

  /**
   * Maximum input tokens.
   *
   * RATIONALE: Some models have separate input/output limits
   */
  maxInputTokens: int32;

  /**
   * Maximum output tokens (generation limit).
   *
   * EXAMPLES:
   * - gpt-4o: 16384
   * - claude-3-sonnet: 4096
   */
  maxOutputTokens: int32;

  /**
   * Supported content types.
   *
   * EXAMPLES:
   * - ["text", "image"]: Vision models
   * - ["text", "image", "audio"]: Multimodal models
   * - ["text"]: Text-only models
   */
  supportedContentTypes: string[];

  /**
   * Provider name.
   *
   * EXAMPLES: "openai", "anthropic", "azure-openai", "google"
   */
  provider: string;

  /**
   * Model family/series.
   *
   * EXAMPLES: "gpt-4", "claude-3", "gemini-pro"
   *
   * RATIONALE: Useful for grouping similar models
   */
  modelFamily: string;
}

/**
 * Prompt Template
 *
 * ALIGNED WITH: Agent Schema Template
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/template.tsp)
 *
 * RATIONALE: Specifies how to render and parse instructions/additionalInstructions
 *
 * NOTE: The template content itself is in the instructions/additionalInstructions fields.
 * This object specifies the rendering engine and parser.
 */
model PromptTemplate {
  /**
   * Template rendering engine for slot filling prompts.
   * ALIGNED WITH: Agent Schema Template.format
   *
   * SUPPORTED FORMATS:
   * - mustache: Handlebars-style {{variable}}
   * - jinja2: Python Jinja2 templates
   * - prompty: Prompty format (.prompty files)
   *
   * USAGE: Specifies how to render the instructions/additionalInstructions strings
   */
  format: string;

  /**
   * Parser to process the rendered template into API-compatible format.
   * ALIGNED WITH: Agent Schema Template.parser
   *
   * RATIONALE: After rendering the template with variable substitution,
   * the parser processes the result into the format expected by the LLM API.
   *
   * EXAMPLES:
   * - prompty: Parse Prompty format into messages
   * - markdown: Parse markdown sections into structured content
   * - json: Parse JSON structure
   */
  parser?: string;
}

/**
 * Property Schema
 *
 * ALIGNED WITH: JSON Schema Draft 7
 * SOURCE: https://json-schema.org/
 *
 * RATIONALE: Use standard JSON Schema for input/output validation
 *
 * NOTE: PropertySchema is an alias to JSONSchema (defined in tools.tsp)
 * This provides a semantic name for agent input/output schemas while
 * maintaining compatibility with the universal JSON Schema standard.
 */
alias PropertySchema = JSONSchema;

/**
 * Agent Participation Types
 *
 * @usage
 *
 * DESIGN:
 * - RunCondition determines when agent should respond to thread activity
 * - AutoResponseConfig provides participation configuration
 * - MentionCondition is RunCondition-specific (not shared with HookCondition)
 *
 */

/**
 * Run Condition
 *
 * NOTE: RunCondition and MentionCondition have been moved to conditions.tsp.
 * Import conditions.tsp to use these types.
 */

/**
 * Auto Response Configuration
 *
 * @usage
 * Configuration for automatic agent participation in threads.
 * Determines when and how agents should respond to thread activity.
 * Prevents infinite loops with maxConsecutiveRuns limit.
 *
 * Key Capabilities:
 * - Condition-based participation (always, roles, content, mentions)
 * - Loop prevention via maxConsecutiveRuns
 * - Thread cleanup strategy (keep or delete)
 *
 * Use Cases:
 * - Support agents: Respond to all user messages
 * - Specialized agents: Respond only when mentioned
 * - Monitoring agents: React to specific content types (video, files)
 * - Multi-agent conversations: Limit consecutive runs to prevent loops
 *
 * @example Always respond to user messages
 * ```json
 * {
 *   "runCondition": {
 *     "kind": "roles",
 *     "roles": ["user"]
 *   },
 *   "maxConsecutiveRuns": 1,
 *   "threadCleanup": "keep"
 * }
 * ```
 *
 * @example Respond only when mentioned
 * ```json
 * {
 *   "runCondition": {
 *     "kind": "mention",
 *     "requireExplicitMention": true
 *   },
 *   "maxConsecutiveRuns": 1,
 *   "threadCleanup": "keep"
 * }
 * ```
 *
 * @example Multi-agent with loop prevention
 * ```json
 * {
 *   "runCondition": {
 *     "kind": "roles",
 *     "roles": ["user", "assistant"]
 *   },
 *   "maxConsecutiveRuns": 2,
 *   "threadCleanup": "keep"
 * }
 * ```
 *
 * @example React to video content
 * ```json
 * {
 *   "runCondition": {
 *     "kind": "content",
 *     "contentTypes": ["video"]
 *   },
 *   "maxConsecutiveRuns": 1,
 *   "threadCleanup": "keep"
 * }
 * ```
 */
model AutoResponseConfig {
  /**
   * Condition for when agent should participate.
   *
   * DEFAULT: If omitted, responds to messages with role="user"
   *
   * DETERMINES: If/when agent should create run in response to thread activity
   */
  runCondition?: RunCondition;

  /**
   * Maximum consecutive runs before requiring user message.
   *
   * DEFAULT: 1 (hard limit to prevent endless loops)
   *
   * RATIONALE: Prevents agents from getting into endless loops
   * - 1: Agent runs once, then waits for user message (default)
   * - 2: Agent can respond to another agent once, then needs user input
   * - 0: Unlimited (dangerous - can create infinite loops)
   *
   * COUNTER RESET: Counter resets when a message with role="user" arrives
   *
   * EXAMPLES:
   * - maxConsecutiveRuns=1: User → Agent A → [STOP, wait for user]
   * - maxConsecutiveRuns=2: User → Agent A → Agent B → [STOP, wait for user]
   * - maxConsecutiveRuns=0: User → Agent A → Agent B → Agent A → ... [INFINITE LOOP]
   */
  maxConsecutiveRuns?: int32 = 1;

  /**
 * Thread cleanup after participation.
 *
 * @usage
 *
 * Use Cases:
 * - Stateful conversations: Use keep (default)
 * - Ephemeral queries: Use delete
 * - One-shot tasks: Use delete
 *
 */
  threadCleanup?: ThreadCleanup;
}


/**
 * Agent Card (Discovery/Registration Metadata)
 *
 * @usage
 * Metadata card describing an agent's capabilities for discovery and registration.
 * Used for agent marketplace listing, capability queries, and M365/Entra integration.
 *
 * Rationale:
 * - Separates discovery (what agents advertise) from execution (how they run)
 * - A2A cards enable interoperability across frameworks
 * - Extended with M365/Entra-specific fields for enterprise integration
 *
 * @example Agent card with capabilities
 * ```json
 * {
 *   "agentId": "support-agent-123",
 *   "displayName": "Customer Support Agent",
 *   "description": "Handles customer inquiries and support tickets",
 *   "capabilities": {
 *     "vision": false,
 *     "audio": false,
 *     "tools": true,
 *     "streaming": true,
 *     "thinking": false
 *   },
 *   "scopes": {
 *     "https://graph.microsoft.com/Mail.Read": "Read user emails"
 *   },
 *   "tags": ["support", "customer-service"],
 *   "iconUrl": "https://example.com/icon.png"
 * }
 * ```
 *
 * A2A COMPATIBILITY NOTES:
 * - A2A uses "skills" (discrete capabilities) - we use agent definition
 * - A2A has "supportedInterfaces" (endpoints) - we have single REST/gRPC API
 * - A2A uses "securitySchemes" - we use Connection union (reference, remote, apiKey, anonymous)
 * - A2A uses MIME types for input/output - we use AIContent type discriminators
 *
 * DIFFERENCES FROM A2A:
 * - We don't expose internal execution details (instructions, model params)
 * - We include M365/Entra integration fields (blueprintId, agentUserId, scopes)
 * - We align with existing TypeSpec patterns (Connection, AIContent)
 * - We support both REST and gRPC from single card
 *
 */

/**
 * Contact Information
 */
model ContactInfo {
  /** Contact name (person or team) */
  name?: string;
  /** Support website URL */
  url?: string;
  /** Support email address */
  email?: string;
}

/**
 * External Documentation Link
 */
model ExternalDocLink {
  /** Documentation URL */
  url: string;
  /** Human-readable description */
  description: string;
  /** Documentation type for categorization */
  type?: "reference" | "guide" | "tutorial" | "video" | "example" | "changelog";
}

model AgentCard {
  /**
   * Unique agent identifier.
   * FROM: Agent Schema PromptAgent.name
   *
   * USAGE: Client uses this to reference agent in Run.agentId
   *
   * M365/ENTRA: This is also the Entra ID Application (Client) ID for the agent
   * EXAMPLE: "12345678-1234-1234-1234-123456789012"
   */
  agentId: string;

  /**
   * Human-readable agent name.
   * A2A EQUIVALENT: Agent Card "name"
   */
  name: string;

  /**
   * UI display name (localized, friendly).
   * ADDITION: Not in A2A
   */
  displayName?: string;

  /**
   * Agent capabilities description.
   * A2A EQUIVALENT: Agent Card "description"
   *
   * GUIDANCE: 1-3 sentences explaining what agent does
   */
  description: string;

  /**
   * Agent version (semantic versioning).
   * A2A EQUIVALENT: Agent Card "version"
   *
   * EXAMPLES: "1.0.0", "2.1.3-beta"
   */
  version?: string;

  /**
   * Agent icon/logo URL.
   * A2A EQUIVALENT: Agent Card "iconUrl"
   */
  iconUrl?: string;

  /**
 * Contact information for agent support.
 *
 * @usage
 *
 * Use Cases:
 * - Report bugs or issues with the agent
 * - Request features or enhancements
 * - Get help with agent integration
 * - Contact agent maintainers
 *
 */
  contact?: ContactInfo;

  /**
 * External documentation resources.
 *
 * @usage
 *
 * Rationale:
 * - More discoverable than single URL
 * - Categorized by type (reference, guide, tutorial, video)
 * - Descriptions help users find relevant docs
 *
 * EXAMPLES:
 * - { url: "https://docs.example.com/api", description: "API Reference", type: "reference" }
 * - { url: "https://docs.example.com/guide", description: "User Guide", type: "guide" }
 * - { url: "https://youtube.com/watch?v=...", description: "Tutorial Video", type: "video" }
 *
 */
  externalDocs?: Array<ExternalDocLink>;

  /**
   * Supported input content types.
   * ALIGNED WITH: AIContent union type discriminators
   * A2A INSPIRED BY: Agent Card "defaultInputModes" (but using our content types)
   *
   * EXAMPLES:
   * - ["text"] - Text-only agent
   * - ["text", "image", "audio"] - Multi-modal agent
   * - ["text", "image", "video", "file"] - Rich media agent
   *
   * REFERENCE: See AIContent union in messages.tsp for all content types:
   * text, image, audio, video, file, data, uri, adaptiveCard, etc.
   */
  inputModes?: string[];

  /**
   * Supported output content types.
   * ALIGNED WITH: AIContent union type discriminators
   * A2A INSPIRED BY: Agent Card "defaultOutputModes" (but using our content types)
   *
   * EXAMPLES:
   * - ["text"] - Text-only responses
   * - ["text", "image"] - Can generate images
   * - ["text", "audio", "video"] - Multi-modal outputs
   * - ["text", "adaptiveCard", "suggestedActions"] - Rich UX responses
   *
   * REFERENCE: See AIContent union in messages.tsp for all content types
   */
  outputModes?: string[];


  /**
   * Required connections for this agent.
   * ALIGNED WITH: Connection union (common.tsp)
   *
   * RATIONALE: Uses existing TypeSpec Connection pattern instead of A2A's securitySchemes
   *
   * EXAMPLES:
   * - Reference connection to pre-configured service
   * - API key connection for external API
   * - Remote connection with endpoint and credentials
   * - Anonymous connection (no auth required)
   *
   * USAGE: Agent declares what connections it needs; runtime validates access
   */
  connections?: Connection[];

  /**
   * Tags for discovery and filtering.
   * A2A INSPIRED: Similar to skill tags
   *
   * EXAMPLES: ["productivity", "calendar", "scheduling", "teams"]
   */
  tags?: string[];

  /**
   * M365/Entra Blueprint ID.
   * ADDITION: M365-specific
   *
   * PURPOSE: Links to Copilot Studio/M365 Agent Blueprint
   * EXAMPLE: "blueprint-abc123"
   */
  blueprintId?: string;

  /**
   * M365/Entra Agent User ID.
   * ADDITION: M365-specific
   *
   * PURPOSE: Entra ID Object ID for the agent's service principal/managed identity
   * EXAMPLE: "87654321-4321-4321-4321-210987654321"
   *
   * USAGE: For agent-to-agent auth, permission grants, audit trails
   *
   * NOTE: Different from agentId (Application/Client ID) - this is the Object ID
   */
  agentUserId?: string;

  /**
 * OAuth2 scopes this agent requires.
 *
 * @usage
 *
 * Rationale:
 * - Scopes communicate what the agent can do
 * - Follows OpenAPI 3.0 OAuth2 security scheme format
 * - Fully-qualified URIs prevent scope name collisions
 * - Descriptions aid consent UI and documentation
 * - Simpler than advertising individual tools
 *
 * EXAMPLES:
 * - { "https://graph.microsoft.com/Calendars.Read": "Read user calendar events" }
 * - { "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user" }
 * - { "https://graph.microsoft.com/User.Read.All": "Read all users' profiles" }
 * - { "read:pets": "Read pet information", "write:pets": "Modify pet information" }
 *
 */
  scopes?: Record<string>;

  /**
 * Model capabilities (computed from agent's model configuration).
 *
 * @usage
 * - Enables clients to validate requests before sending
 * - Allows programmatic feature discovery
 * - Supports intelligent model selection
 *
 *
 * Rationale:
 * - Capabilities are part of agent discovery, not a separate endpoint
 * - Computed from AgentModel when AgentCard is retrieved
 * - Single source of truth for what the agent can do
 *
 * EXAMPLES:
 * - gpt-4o agent: vision=true, thinking=false, maxTokens=128000
 * - claude-3-sonnet agent: vision=true, thinking=true, maxTokens=200000
 * - gpt-3.5-turbo agent: vision=false, thinking=false, maxTokens=16385
 *
 */
  @visibility("read")
  capabilities?: ModelCapabilities;

  /**
   * Custom metadata.
   */
  metadata?: Record<unknown>;

  /**
   * Timestamp when agent was registered.
   */
  @visibility("read")
  createdAt?: utcDateTime;

  /**
   * Timestamp of last update to agent card.
   */
  @visibility("read")
  updatedAt?: utcDateTime;
}
