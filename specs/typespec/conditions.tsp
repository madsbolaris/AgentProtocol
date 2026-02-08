import "@typespec/http";
import "./common.tsp";
import "./messages.tsp";

namespace Microsoft.Agents.AI;

/**
 * Base condition types used for filtering and matching.
 *
 * Conditions are used by:
 * - RunCondition (agent auto-response participation)
 *
 * @usage
 * Base conditions provide reusable filtering logic for determining
 * when agents should participate in thread activity.
 *
 * Common Patterns:
 * - AlwaysCondition: Always match (no filtering)
 * - RolesCondition: Filter by message role (user, assistant, system)
 * - ContentCondition: Filter by content types (text, image, video, etc.)
 * - ExpressionCondition: In-process evaluation using Power Fx or CEL
 * - RemoteCondition: Custom logic via external endpoint
 *
 * @example AlwaysCondition - Always match
 * ```json
 * {
 *   "kind": "always"
 * }
 * ```
 *
 * @example RolesCondition - Match user messages
 * ```json
 * {
 *   "kind": "roles",
 *   "roles": ["user"]
 * }
 * ```
 *
 * @example ContentCondition - Match video content
 * ```json
 * {
 *   "kind": "content",
 *   "contentTypes": ["video"]
 * }
 * ```
 */

/**
 * Always Condition
 *
 * RATIONALE: Always matches - agent always participates or hook always evaluates
 */
model AlwaysCondition {
  /**
   * Condition type discriminator.
   */
  kind: "always";
}

/**
 * Roles Condition
 *
 * RATIONALE: Match based on message role (user, assistant, system, etc.)
 */
model RolesCondition {
  /**
   * Condition type discriminator.
   */
  kind: "roles";

  /**
   * Message roles that trigger match.
   *
   * EXAMPLES:
   * - ["user"]: Match only user messages
   * - ["user", "system"]: Match user or system messages
   */
  roles: ChatRole[];
}

/**
 * Content Condition
 *
 * RATIONALE: Match based on content types in message
 */
model ContentCondition {
  /**
   * Condition type discriminator.
   */
  kind: "content";

  /**
   * Content types that trigger match.
   *
   * EXAMPLES:
   * - ["video"]: Match only video messages
   * - ["image", "file"]: Match media uploads
   */
  contentTypes: string[];
}

/**
 * Expression Condition
 *
 * RATIONALE: In-process evaluation using Power Fx or CEL
 */
model ExpressionCondition {
  /**
   * Condition type discriminator.
   */
  kind: "expression";

  /**
 * Expression for in-process evaluation.
 *
 * @usage
 *
 * Use Cases:
 * - Keyword matching and pattern detection
 * - Content type and role combinations
 * - Simple boolean logic without external state
 *
 */
  expression: string;
}

/**
 * Remote Condition
 *
 * RATIONALE: Custom evaluation logic via remote endpoint
 */
model RemoteCondition {
  /**
   * Condition type discriminator.
   */
  kind: "remote";

  /**
 * Remote endpoint for custom evaluation logic.
 *
 * @usage
 *
 * Use Cases:
 * - Complex business logic (checking external state, database queries)
 * - Turn-taking coordination between multiple agents
 * - Time-based or rate-limited participation
 *
 */
  endpoint: string;

  /**
   * Authentication for remote endpoint.
   */
  connection?: Connection;
}

/**
 * Mention Condition (RunCondition-specific)
 *
 * RATIONALE: Agent participates when explicitly mentioned in message
 * PATTERN: @agent-name or explicit agent reference
 *
 * NOTE: Only explicit mentions are supported. Context-relevance
 * cannot be deterministically evaluated.
 */
model MentionCondition {
  /**
   * Condition type discriminator.
   */
  kind: "mention";

  /**
   * Respond when agent is explicitly mentioned in message.
   *
   * DEFAULT: true (only respond to explicit @mentions)
   *
   * EXAMPLES:
   * - true: Requires "@AgentName" in message
   * - false: Any reference to agent name triggers participation
   */
  requireExplicitMention?: boolean = true;
}

/**
 * Similarity Condition
 *
 * RATIONALE: Match content based on similarity to reference texts
 * USE CASES: Intent matching, topic detection, semantic filtering
 */
model SimilarityCondition {
  /**
   * Condition type discriminator.
   */
  kind: "similarity";

  /**
   * Similarity matching method.
   *
   * METHODS:
   * - fuzzy: String similarity using Levenshtein distance
   * - semantic: Semantic similarity using embeddings
   * - keyword: Keyword-based similarity
   */
  method: "fuzzy" | "semantic" | "keyword";

  /**
   * Reference texts for similarity comparison.
   *
   * EXAMPLES:
   * - ["help", "support", "assistance"] for help intent
   * - ["urgent", "critical", "emergency"] for priority detection
   */
  referenceTexts: string[];

  /**
   * Similarity threshold (0.0 to 1.0).
   *
   * DEFAULT: 0.7
   *
   * EXAMPLES:
   * - 0.9: Very high similarity required (strict matching)
   * - 0.7: Moderate similarity (recommended)
   * - 0.5: Low similarity (loose matching)
   */
  threshold: float32 = 0.7;
}

/**
 * Run Condition
 *
 * RATIONALE: Determines when agent should create run in response to thread activity
 * SCOPE: Thread-scoped (applies to all messages in thread)
 * STATE: Stateful (64KB limit for RemoteCondition state)
 *
 * SOURCE: agent-participation-design.md lines 132-148
 *
 * CONDITION TYPES:
 * - AlwaysCondition: Always participate
 * - RolesCondition: Match message role (user, assistant, system)
 * - ContentCondition: Match content types (video, image, file)
 * - MentionCondition: Match explicit @mentions (RunCondition-specific)
 * - ExpressionCondition: In-process Power Fx/CEL evaluation
 * - RemoteCondition: Custom logic via remote endpoint (WebSocket or HTTP)
 * - SimilarityCondition: Match based on text similarity
 */
@discriminator("kind")
union RunCondition {
  AlwaysCondition,
  RolesCondition,
  ContentCondition,
  MentionCondition,
  ExpressionCondition,
  RemoteCondition,
  SimilarityCondition,
}

