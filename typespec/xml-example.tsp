/**
 * XML Decorator Usage Examples
 *
 * This file demonstrates how to use AgentXml decorators to map TypeSpec models
 * to XML elements with proper serialization attributes.
 */

import "./xml-decorators.tsp";
import "@typespec/http";

using TypeSpec.Http;
using AgentXml.Decorators;

namespace AgentXml.Examples;

// ============================================
// EXAMPLE 1: Simple Message with Attributes
// ============================================

/**
 * Example of a message with XML attributes and elements.
 *
 * XML Output:
 * ```xml
 * <user message-id="msg_123" created-at="2026-02-07T10:00:00Z">
 *   <text>Hello world</text>
 * </user>
 * ```
 */
@xmlRoot("user")
@xmlNamespace("http://schemas.agent.ai/messages/v1")
model UserMessage {
  @xmlAttribute("message-id")
  messageId: string;

  @xmlAttribute("created-at")
  createdAt: utcDateTime;

  @xmlElement("text")
  text: string;
}

// ============================================
// EXAMPLE 2: Tool Definition with Arrays
// ============================================

/**
 * Example of a tool with nested input parameters.
 *
 * XML Output:
 * ```xml
 * <tool name="get_weather" description="Get weather data">
 *   <inputs>
 *     <input name="location" type="text" required="true" />
 *     <input name="units" type="text" value="fahrenheit" />
 *   </inputs>
 * </tool>
 * ```
 */
@xmlElement("tool")
model ToolDefinition {
  @xmlAttribute
  name: string;

  @xmlAttribute
  description: string;

  @xmlArray("inputs", "input")
  inputs: InputParameter[];
}

@xmlElement("input")
model InputParameter {
  @xmlAttribute
  name: string;

  @xmlAttribute
  type: string;

  @xmlAttribute
  required?: boolean;

  @xmlAttribute
  value?: string;

  @xmlAttribute
  placeholder?: string;
}

// ============================================
// EXAMPLE 3: Polymorphic Content Union
// ============================================

/**
 * Example of polymorphic content using discriminator.
 *
 * XML Output:
 * ```xml
 * <content kind="text">
 *   <text>Hello world</text>
 * </content>
 *
 * <content kind="image">
 *   <uri>https://example.com/image.jpg</uri>
 *   <mime-type>image/jpeg</mime-type>
 * </content>
 * ```
 */
@xmlDiscriminator("kind")
union ContentType {
  TextContent,
  ImageContent,
  AudioContent,
}

@xmlElement("content")
model TextContent {
  @xmlAttribute
  kind: "text";

  @xmlElement("text")
  text: string;
}

@xmlElement("content")
model ImageContent {
  @xmlAttribute
  kind: "image";

  @xmlElement("uri")
  uri: string;

  @xmlElement("mime-type")
  mimeType?: string;

  @xmlAttribute
  width?: int32;

  @xmlAttribute
  height?: int32;
}

@xmlElement("content")
model AudioContent {
  @xmlAttribute
  kind: "audio";

  @xmlElement("uri")
  uri: string;

  @xmlElement("mime-type")
  mimeType?: string;

  @xmlAttribute
  duration?: int32;
}

// ============================================
// EXAMPLE 4: Text Content (Inner Text Node)
// ============================================

/**
 * Example of content with inner text (no wrapper element).
 *
 * XML Output:
 * ```xml
 * <thinking exposed="false">
 *   Analyzing user intent and planning response...
 * </thinking>
 * ```
 */
@xmlElement("thinking")
model ThinkingContent {
  @xmlAttribute
  exposed: boolean;

  @xmlText
  text: string;
}

// ============================================
// EXAMPLE 5: Enum with Custom XML Names
// ============================================

/**
 * Example of enum with XML serialization names.
 *
 * XML Output:
 * ```xml
 * <role>assistant</role>
 * ```
 */
@xmlTypeName("chat-role")
enum ChatRole {
  system,
  developer,
  user,
  assistant,
  tool,
  channel,
}

// ============================================
// EXAMPLE 6: Complex Message with Mixed Content
// ============================================

/**
 * Example of a complex agent message with function calls.
 *
 * XML Output:
 * ```xml
 * <agent
 *   message-id="msg_456"
 *   thread-id="thread_123"
 *   agent-id="agent_001"
 *   model="claude-sonnet-4.5"
 *   created-at="2026-02-07T10:00:00Z">
 *   <thinking exposed="false">
 *     Need to call weather API for Seattle
 *   </thinking>
 *   <function-call call-id="call_001" name="get_weather">
 *     {"location": "Seattle, WA", "units": "fahrenheit"}
 *   </function-call>
 * </agent>
 * ```
 */
@xmlRoot("agent")
@xmlNamespace("http://schemas.agent.ai/messages/v1")
model AgentMessage {
  @xmlAttribute("message-id")
  messageId: string;

  @xmlAttribute("thread-id")
  threadId?: string;

  @xmlAttribute("agent-id")
  agentId?: string;

  @xmlAttribute
  model?: string;

  @xmlAttribute("created-at")
  createdAt: utcDateTime;

  @xmlAttribute("completed-at")
  completedAt?: utcDateTime;

  @xmlArray("contents", "content")
  contents: ContentType[];
}

// ============================================
// EXAMPLE 7: Function Call with JSON Content
// ============================================

/**
 * Example of function call with JSON arguments as text.
 *
 * XML Output:
 * ```xml
 * <function-call call-id="call_001" name="get_weather">
 *   {"location": "Seattle, WA", "units": "fahrenheit"}
 * </function-call>
 * ```
 */
@xmlElement("function-call")
model FunctionCall {
  @xmlAttribute("call-id")
  callId: string;

  @xmlAttribute
  name: string;

  @xmlText
  arguments: string; // JSON as text
}

// ============================================
// EXAMPLE 8: Metadata with Ignored Properties
// ============================================

/**
 * Example showing properties that are ignored in XML.
 *
 * XML Output:
 * ```xml
 * <message message-id="msg_789" created-at="2026-02-07T10:00:00Z">
 *   <text>Hello</text>
 * </message>
 * ```
 */
@xmlRoot("message")
model MessageWithMetadata {
  @xmlAttribute("message-id")
  messageId: string;

  @xmlAttribute("created-at")
  createdAt: utcDateTime;

  @xmlElement
  text: string;

  // This property is NOT serialized to XML
  @xmlIgnore
  rawRepresentation?: unknown;

  // This property is NOT serialized to XML
  @xmlIgnore
  metadata?: Record<unknown>;
}

// ============================================
// EXAMPLE 9: Optional Properties with Defaults
// ============================================

/**
 * Example showing optional properties with default values.
 *
 * XML Output:
 * ```xml
 * <reasoning exposed="false">
 *   Internal thinking process...
 * </reasoning>
 * ```
 */
@xmlElement("reasoning")
model ReasoningContent {
  @xmlAttribute
  @xmlDefault(false)
  exposed?: boolean;

  @xmlText
  text: string;
}
