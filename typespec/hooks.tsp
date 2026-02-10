/**
 * Hook Types & Responses
 *
 * This file defines the hook system for intercepting and modifying runtime behavior.
 *
 * CONTENTS:
 * - Hook union: All hook types (Remote, Block, Modify, Telemetry, SendMessage)
 * - HookActionResponse union: All response types for RemoteHook callbacks
 *
 * SOURCE: hooks-design.md
 *
 * @usage
 * Hooks intercept and modify runtime behavior at specific lifecycle points.
 * They can block, modify, observe, or inject additional logic into the execution flow.
 *
 * Hook Lifecycle Points:
 * - beforeRun: Before agent execution starts
 * - afterRun: After agent execution completes
 * - beforeToolExecution: Before each tool call
 * - afterToolExecution: After each tool call
 *
 * Hook Types:
 * - RemoteHook: Delegate to external service via HTTP/WebSocket
 * - BlockHook: Reject events based on conditions
 * - ModifyHook: Transform content inline
 * - TelemetryHook: Observe events without modification
 * - SendMessageHook: Inject additional messages (e.g., system prompts)
 */

import "@typespec/http";
import "./common.tsp";
import "./conditions.tsp";
import "./messages.tsp";

namespace Microsoft.Agents.AI;

/**
 * Hook Types
 *
 * SOURCE: hooks-design.md lines 44-137
 *
 * RATIONALE: Hooks enable interception and modification of execution events
 * SCOPE: Run-scoped (per-run lifecycle)
 *
 * HOOK TYPES:
 * - RemoteHook: External service hook via WebSocket or HTTP
 * - BlockHook: Block events matching condition with predefined message
 * - ModifyHook: Modify content matching condition (redaction, transformation)
 * - TelemetryHook: Emit telemetry events for matching events
 * - SendMessageHook: Inject additional messages (afterRun only)
 */
@discriminator("kind")
union Hook {
  RemoteHook,
  BlockHook,
  ModifyHook,
  TelemetryHook,
  SendMessageHook,
}

/**
 * Remote Hook
 *
 * @usage
 *
 * Use Cases:
 * - Content moderation and filtering
 * - Dynamic guardrails
 * - Custom logging and telemetry
 * - Integration with external systems
 *
 */
model RemoteHook {
  /**
   * Hook type discriminator.
   */
  kind: "remote";

  /**
   * Hook name (unique per run).
   */
  name: string;

  /**
   * Remote endpoint URL.
   * PROTOCOL: WebSocket (ws:// or wss://) or HTTP (http:// or https://)
   */
  endpoint: string;

  /**
   * Authentication for remote endpoint.
   */
  connection?: Connection;

  /**
   * Optional client-side filtering before remote call.
   * RATIONALE: Reduce unnecessary network calls for irrelevant events
   */
  condition?: RunCondition;

  /**
   * Hook-specific configuration sent in handshake.
   */
  config?: Record<unknown>;
}

/**
 * Block Hook
 *
 * RATIONALE: Block events matching condition with predefined message
 * USE CASES: Content filtering, policy enforcement, safety guardrails
 */
model BlockHook {
  /**
   * Hook type discriminator.
   */
  kind: "block";

  /**
   * Hook name (unique per run).
   */
  name: string;

  /**
   * Condition for when to block.
   */
  condition?: RunCondition;

  /**
   * Message explaining why content was blocked.
   */
  message: string;
}

/**
 * Modify Hook
 *
 * RATIONALE: Modify content matching condition (redaction, transformation)
 * USE CASES: PII redaction, content transformation, sanitization
 */
model ModifyHook {
  /**
   * Hook type discriminator.
   */
  kind: "modify";

  /**
   * Hook name (unique per run).
   */
  name: string;

  /**
   * Condition for when to modify.
   */
  condition?: RunCondition;

  /**
   * Predefined redaction patterns.
   * EXAMPLES: ["email", "phone", "ssn"]
   */
  predefinedPatterns?: string[];

  /**
   * Custom regex patterns for redaction.
   */
  regexPatterns?: string[];

  /**
   * Replacement text for redacted content.
   * DEFAULT: "[REDACTED]"
   */
  replacement?: string = "[REDACTED]";
}

/**
 * Telemetry Hook
 *
 * RATIONALE: Emit telemetry events for matching events
 * USE CASES: Custom logging, metrics, analytics
 */
model TelemetryHook {
  /**
   * Hook type discriminator.
   */
  kind: "telemetry";

  /**
   * Hook name (unique per run).
   */
  name: string;

  /**
   * Condition for when to emit telemetry.
   */
  condition?: RunCondition;

  /**
   * Telemetry event name.
   */
  event: string;

  /**
   * Telemetry event properties.
   */
  properties?: Record<string>;
}

/**
 * Send Message Hook
 *
 * RATIONALE: Inject additional messages (afterRun only)
 * USE CASES: LLM regeneration, correction, additional context
 *
 * NOTE: Only available for afterRun lifecycle hook
 */
model SendMessageHook {
  /**
   * Hook type discriminator.
   */
  kind: "sendMessage";

  /**
   * Hook name (unique per run).
   */
  name: string;

  /**
   * Condition for when to send message.
   */
  condition?: RunCondition;

  /**
   * Message to inject (for LLM regeneration).
   * NOTE: Only valid in afterRun lifecycle hook
   */
  message: ChatMessage;
}

/**
 * Hook Action Response
 *
 * SOURCE: hooks-design.md lines 557-603
 *
 * RATIONALE: Actions that RemoteHook can take on streaming events
 *
 * RESPONSE TYPES:
 * - AllowResponse: Allow events to pass through
 * - BlockResponse: Block events from reaching client
 * - ModifyResponse: Modify event content
 * - SendMessageResponse: Inject new message events (afterRun only)
 * - TelemetryResponse: Emit telemetry event
 */
@discriminator("kind")
union HookActionResponse {
  AllowResponse,
  BlockResponse,
  ModifyResponse,
  SendMessageResponse,
  TelemetryResponse,
}

/**
 * Allow Response
 *
 * RATIONALE: Explicitly allow events to pass through
 */
model AllowResponse {
  /**
   * Response type discriminator.
   */
  kind: "allow";

  /**
   * Event sequence numbers to allow.
   * REQUIRED: Which events to allow
   */
  eventSeqs: int64[];
}

/**
 * Block Response
 *
 * RATIONALE: Block events from reaching client
 * USE CASES: Content filtering, policy violations
 */
model BlockResponse {
  /**
   * Response type discriminator.
   */
  kind: "block";

  /**
   * Event sequence numbers to block.
   * REQUIRED: Which events to block
   */
  eventSeqs: int64[];

  /**
   * Reason for blocking (optional).
   */
  message?: string;
}

/**
 * Modify Response
 *
 * RATIONALE: Modify event content
 * USE CASES: PII redaction, content transformation
 *
 * CONTENT TYPE CHANGES:
 * - Framework allows changing content types (e.g., functionCall → text)
 * - Changing types effectively replaces the content's purpose
 * - Framework validates that modifiedContent is valid AIContent structure
 */
model ModifyResponse {
  /**
   * Response type discriminator.
   */
  kind: "modify";

  /**
   * Event sequence numbers this replaces.
   * REQUIRED: Which events this modifies
   */
  eventSeqs: int64[];

  /**
   * Content index within message.
   * REQUIRED: Which content piece this modifies
   */
  contentIndex: int32;

  /**
   * Complete modified content (not deltas).
   * REQUIRED: Complete replacement content
   */
  modifiedContent: AIContent;
}

/**
 * Send Message Response
 *
 * RATIONALE: Inject additional messages (afterRun only)
 * USE CASES: LLM regeneration, correction, additional context
 *
 * NOTE: Only valid in afterRun lifecycle hook
 */
model SendMessageResponse {
  /**
   * Response type discriminator.
   */
  kind: "sendMessage";

  /**
   * Event sequence numbers after which to insert message.
   * REQUIRED: After which events to insert the new message events
   */
  eventSeqs: int64[];

  /**
   * Message to inject.
   * REQUIRED: Message to inject (afterRun only)
   */
  injectedMessage: ChatMessage;
}

/**
 * Telemetry Response
 *
 * RATIONALE: Emit telemetry event
 * USE CASES: Custom logging, metrics, analytics
 */
model TelemetryResponse {
  /**
   * Response type discriminator.
   */
  kind: "telemetry";

  /**
   * Event sequence numbers after which to insert telemetry.
   * REQUIRED: After which events to insert the telemetry event
   */
  eventSeqs: int64[];

  /**
   * Telemetry event name.
   * REQUIRED: Event name (e.g., "hook.warning", "content.processed")
   */
  telemetryEvent: string;

  /**
   * Telemetry event properties (optional).
   */
  telemetryProperties?: Record<unknown>;
}
