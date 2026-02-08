/**
 * Common Models & Shared Types
 *
 * This file defines types shared across multiple TypeSpec files.
 *
 * RATIONALE: Avoid duplication, enable reuse
 */

import "@typespec/http";
import "@typespec/rest";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

/**
 * Connection - Authentication Configuration
 *
 * @usage
 *
 * Rationale:
 * - Agent Schema provides richer connection model
 * - Supports multiple connection types (reference, remote, API key, anonymous)
 * - Includes authority (user vs system) for consent flows
 * - Provides usageDescription for transparency
 *
 */
@discriminator("kind")
union Connection {
  ReferenceConnection,
  RemoteConnection,
  ApiKeyConnection,
  AnonymousConnection,
}

/**
 * Reference Connection
 *
 * ALIGNED WITH: Agent Schema ReferenceConnection
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)
 *
 * RATIONALE: Named connection reference to pre-configured connections
 *
 * MESSAGING APP PATTERN:
 * - Like referencing a stored bot token by name
 * - Avoids credential duplication
 * - Enables connection reuse
 */
model ReferenceConnection {
  /**
   * Connection type discriminator.
   * ALIGNED WITH: Agent Schema Connection.kind
   */
  kind: "reference";

  /**
   * Connection reference name.
   * ALIGNED WITH: Agent Schema ReferenceConnection.name
   *
   * EXAMPLES: "myOpenAIConnection", "productionDB", "mcpServer"
   */
  name: string;

  /**
   * Authorization level.
   * ALIGNED WITH: Agent Schema Connection.authority
   *
   * GUIDANCE:
   * - "user": Connection uses user's credentials (user consent required)
   * - "system": Connection uses system credentials (no user consent)
   */
  authority?: "user" | "system";

  /**
   * Usage transparency description.
   * ALIGNED WITH: Agent Schema Connection.usageDescription
   *
   * RATIONALE: Shown to users for consent/transparency
   *
   * EXAMPLE: "Access your OneDrive files to search for relevant documents"
   */
  usageDescription?: string;
}

/**
 * API Key Connection
 *
 * ALIGNED WITH: Agent Schema ApiKeyConnection
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)
 *
 * RATIONALE: API key-based authentication
 *
 * MESSAGING APP PATTERN:
 * - Like Slack/Teams bot tokens
 * - Simple key-based auth
 */
model ApiKeyConnection {
  /**
   * Connection type discriminator.
   * ALIGNED WITH: Agent Schema Connection.kind
   */
  kind: "key";

  /**
   * API key value.
   * ALIGNED WITH: Agent Schema ApiKeyConnection.key
   *
   * EXAMPLES:
   * - "sk-proj-abc123..." (OpenAI)
   * - "xoxb-..." (Slack)
   * - Bearer token
   */
  key: string;

  /**
   * Optional header name.
   * DEFAULT: "Authorization"
   *
   * EXAMPLES:
   * - "Authorization" (most common)
   * - "X-API-Key" (some APIs)
   * - "X-Custom-Auth" (custom auth)
   */
  headerName?: string = "Authorization";

  /**
   * Authorization level.
   * ALIGNED WITH: Agent Schema Connection.authority
   */
  authority?: "user" | "system";

  /**
   * Usage transparency description.
   * ALIGNED WITH: Agent Schema Connection.usageDescription
   */
  usageDescription?: string;
}

/**
 * Remote Connection
 *
 * ALIGNED WITH: Agent Schema RemoteConnection
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)
 *
 * RATIONALE: Remote service connection with endpoint and credentials
 */
model RemoteConnection {
  /**
   * Connection type discriminator.
   * ALIGNED WITH: Agent Schema Connection.kind
   */
  kind: "remote";

  /**
   * Service endpoint URL.
   * ALIGNED WITH: Agent Schema RemoteConnection.endpoint
   *
   * EXAMPLES:
   * - "https://api.example.com"
   * - "https://mcp-server.example.com"
   */
  endpoint: string;

  /**
   * Authentication credentials.
   * ALIGNED WITH: Agent Schema RemoteConnection.credentials
   *
   * FLEXIBLE: Arbitrary credential formats
   *
   * EXAMPLES:
   * - { "token": "Bearer abc123" }
   * - { "username": "user", "password": "pass" }
   * - { "clientId": "...", "clientSecret": "..." }
   */
  credentials?: Record<unknown>;

  /**
   * Authorization level.
   * ALIGNED WITH: Agent Schema Connection.authority
   */
  authority?: "user" | "system";

  /**
   * Usage transparency description.
   * ALIGNED WITH: Agent Schema Connection.usageDescription
   */
  usageDescription?: string;
}

/**
 * Anonymous Connection
 *
 * ALIGNED WITH: Agent Schema AnonymousConnection
 * SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)
 *
 * RATIONALE: No authentication required (public endpoints)
 */
model AnonymousConnection {
  /**
   * Connection type discriminator.
   * ALIGNED WITH: Agent Schema Connection.kind
   */
  kind: "anonymous";

  /**
   * Authorization level.
   * ALIGNED WITH: Agent Schema Connection.authority
   */
  authority?: "user" | "system";

  /**
   * Usage transparency description.
   * ALIGNED WITH: Agent Schema Connection.usageDescription
   */
  usageDescription?: string;
}

/**
 * OAuth2 Scopes
 *
 * @usage
 *
 * Rationale:
 * - Follows OpenAPI 3.0 standard format
 * - Simple key-value mapping: scope name → description
 * - Compatible with OAuth2 flows
 *
 * EXAMPLES:
 * - { "https://graph.microsoft.com/Calendars.Read": "Read user calendar events" }
 * - { "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user" }
 * - { "read:pets": "Read pet information", "write:pets": "Modify pet information" }
 *
 */
alias Scopes = Record<string>;

/**
 * NOTE: TruncationStrategy removed - too opinionated
 *
 * @usage
 *
 * Rationale:
 * - Truncation/compaction is server-side implementation detail
 * - Messaging apps don't expose truncation strategies in wire protocol
 * - Just use maxMessages or maxTokens parameters where needed
 *
 */

/**
 * Participant - User or Agent in a Conversation
 *
 * ADDITION: Not in any framework
 *
 * RATIONALE: Unified model for conversation participants
 *
 * USED BY:
 * - execution.tsp (Session.participants, Thread.participants)
 * - messages.tsp (aligns with ChatMessage.userId, ChatMessage.agentId)
 *
 * MESSAGING APP PATTERN:
 * Every messaging app has participants/members in conversations
 *
 * ALIGNMENT WITH CHATMESSAGE:
 * - Participant.id → ChatMessage.userId or ChatMessage.agentId
 * - Participant.type → determines which ID field to use
 * - Participant.name → ChatMessage.authorName
 */
model Participant {
  /**
   * Participant identifier.
   * - For users: Entra User ID (Object ID)
   * - For agents: Agent ID (Service Principal Object ID)
   * - For system: "system"
   *
   * ALIGNMENT: Maps to ChatMessage.userId (if type=user) or ChatMessage.agentId (if type=agent)
   */
  id: string;

  /**
   * Participant type.
   */
  kind: "user" | "agent" | "system";

  /**
   * Display name.
   *
   * ALIGNMENT: Maps to ChatMessage.authorName
   */
  name?: string;

  /**
   * Role in the conversation.
   * EXAMPLES: "user", "assistant", "system"
   *
   * FROM: OpenAI LLM APIs - standard conversation roles
   *
   * NOTE: This is the same as ChatRole for participants
   * - Participant identifies WHO is in the conversation
   * - role identifies their function (user, assistant, system)
   */
  role?: string;

  /**
   * Participant metadata.
   * FLEXIBLE: Avatar URL, status, preferences, etc.
   */
  metadata?: Record<unknown>;
}

/**
 * Base Condition Types
 *
 * NOTE: Condition types have been moved to conditions.tsp for better organization.
 * Import conditions.tsp to use AlwaysCondition, RolesCondition, ContentCondition,
 * ExpressionCondition, RemoteCondition, RunCondition, HookCondition, etc.
 */
