/**
 * Messages & Content Models
 *
 * This file defines message structures and multi-modal content types.
 *
 * BASE: Microsoft.Extensions.AI
 * - ChatMessage: Core message model
 * - ChatRole: Message role enum
 * - AIContent: Polymorphic content base class
 * - TextContent, FunctionCallContent, FunctionResultContent, etc.
 *
 * ADDITIONS FROM:
 * - Azure Agent API: Multi-modal content (Image, Audio, Video, File)
 * - LLMProxy: Citable content (SearchResultContent, DocumentContent)
 * - Activity Protocol: Rich cards (AdaptiveCardContent)
 * - Anthropic: Extended thinking (TextReasoningContent)
 *
 * M365 AGENT PLATFORM REQUIREMENTS SATISFIED:
 * - Canonical Event format (Activity Protocol structure)
 * - Multi-modal support for future scenarios
 * - Citation support for RAG and grounding
 * - Metadata injection for orchestration
 */

import "@typespec/http";
import "@typespec/rest";
import "./xml-decorators.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using AgentXml.Decorators;

namespace Microsoft.Agents.AI;

// ============================================
// SECTION 1: CORE MESSAGE MODEL
// ============================================

/**
 * Chat Message
 *
 * BASE: Microsoft.Extensions.AI.ChatMessage
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/ChatCompletion/ChatMessage.cs
 *
 * MODIFICATIONS:
 * 1. Made role discriminator explicit (MAF uses ChatRole struct, we use enum)
 * 2. Added threadId (from Azure Agent API) - marked @xmlIgnore for XML
 * 3. Added completionId (from Azure Agent API - links to run)
 * 4. Kept MAF's Content list pattern (vs Azure's content: string | AIContent[])
 *
 * M365: Maps to Canonical Event in Conversation Store
 *
 * @usage
 * Core message model representing a single message in a conversation thread.
 * Supports multi-modal content (text, images, audio, video, files) and rich metadata.
 * Used for both user messages and agent responses.
 *
 * Key Capabilities:
 * - Multi-modal content via AIContent[] array
 * - Message branching via parentMessageId (conversation tree)
 * - Audit trail via userId, agentId, completionId
 * - Bidirectional presence (typing indicators)
 * - Social interactions (reactions)
 *
 * M365 Integration:
 * - Maps to Canonical Event in Conversation Store
 * - Supports Entra User ID and Agent ID
 * - Links to Run for execution tracking
 *
 * @example User text message
 * ```json
 * {
 *   "messageId": "msg_123",
 *   "role": "user",
 *   "contents": [
 *     { "kind": "text", "text": "What's the weather today?" }
 *   ],
 *   "userId": "user_789",
 *   "createdAt": "2026-02-07T10:00:00Z"
 * }
 * ```
 *
 * @example Agent response with tool call
 * ```json
 * {
 *   "messageId": "msg_124",
 *   "role": "assistant",
 *   "contents": [
 *     {
 *       "kind": "functionCall",
 *       "callId": "call_001",
 *       "name": "get_weather",
 *       "arguments": "{\"location\": \"San Francisco\"}"
 *     }
 *   ],
 *   "agentId": "agent_001",
 *   "completionId": "run_789",
 *   "createdAt": "2026-02-07T10:00:01Z"
 * }
 * ```
 *
 * @example Multi-modal message with image
 * ```json
 * {
 *   "messageId": "msg_125",
 *   "role": "user",
 *   "contents": [
 *     { "kind": "text", "text": "What's in this image?" },
 *     {
 *       "kind": "image",
 *       "uri": "https://example.com/photo.jpg",
 *       "mimeType": "image/jpeg"
 *     }
 *   ],
 *   "userId": "user_789",
 *   "createdAt": "2026-02-07T10:00:05Z"
 * }
 * ```
 */
model ChatMessage {
  /**
   * Unique message identifier.
   * BASE: MAF ChatMessage.MessageId (optional)
   * FROM: Azure Agent API (required, server-generated)
   *
   * MODIFIED: Made required for M365 tracking
   *
   * ID ASSIGNMENT:
   * - Client-provided: Channels can provide their own messageId (e.g., Teams message ID, Slack ts)
   * - Server-generated: If omitted, server generates GUID
   * - Uniqueness: Must be unique within conversation store (recommend: {channelId}:{originalId})
   *
   * RATIONALE: Channels are source of truth for conversation store
   * - Preserves original message IDs from external systems
   * - Enables idempotent message creation (retry with same ID)
   * - Supports message deduplication and correlation
   */
  @key
  @visibility("create", "read")
  @xmlAttribute("message-id")
  messageId: string;

  /**
 * Parent message ID for conversation branching.
 *
 * @usage
 *
 * Use Cases:
 * - User wants to edit message-5 and rerun from that point
 * - A/B testing different conversation paths
 * - Undo/redo by branching to previous states
 * - Time travel debugging
 *
 */
  @xmlAttribute("parent-message-id")
  parentMessageId?: string;

  /**
   * Thread this message belongs to.
   * FROM: Azure Agent API
   * NOT SERIALIZED: Excluded from XML (use @xmlIgnore)
   *
   * RATIONALE: Thread ID is useful for API/database queries but not
   * needed in XML message serialization. Messages can be grouped by
   * thread at the API layer without including thread ID in each message.
   */
  @xmlIgnore
  threadId?: string;

  /**
   * Message role.
   * BASE: MAF ChatMessage.Role (ChatRole struct with static instances)
   *
   * SIMPLIFIED: Changed from struct to enum for TypeSpec
   *
   * ROLES:
   * - system: System instructions (MAF + Azure)
   * - developer: Developer-provided context (Anthropic/OpenAI)
   * - user: User messages (MAF + Azure)
   * - agent: Agent responses (MAF + Azure)
   * - tool: Tool results (MAF + Azure)
   * - channel: Platform/infrastructure events (Activity Protocol)
   *
   * NOT SERIALIZED: Role is implicit in XML element name (e.g., <system>, <user>)
   */
  @xmlIgnore
  role: ChatRole;

  /**
   * Content items in this message.
   * BASE: MAF ChatMessage.Contents (IList<AIContent>)
   *
   * RATIONALE: List pattern supports multi-modal content
   * (vs Azure's string | AIContent[] which requires union types)
   *
   * M365: Enables multi-modal future scenarios
   *
   * NOT SERIALIZED HERE: Role-specific message classes handle contents serialization
   */
  @xmlIgnore
  contents: AIContent[];

  /**
   * Concatenated text from all TextContent items.
   * BASE: MAF ChatMessage.Text (computed property)
   *
   * RATIONALE: Convenience for text-only messages
   * NOT SERIALIZED: Computed from contents
   */
  @visibility("read")
  @xmlIgnore
  text?: string;

  /**
   * Author name for display.
   * BASE: MAF ChatMessage.AuthorName
   */
  @xmlAttribute("author-name")
  authorName?: string;

  /**
   * User who created this message.
   * FROM: Azure Agent API
   * ADDITION: Not in MAF ChatMessage
   *
   * M365: Entra User ID (Object ID from Microsoft Entra ID)
   * - For end users: User's Object ID (e.g., "12345678-1234-1234-1234-123456789012")
   * - Retrieved via Microsoft Graph API /me or /users/{id}
   *
   * MESSAGING APP PATTERN:
   * - Like userId in Slack, Teams, WhatsApp
   * - Identifies who sent the message
   *
   * XML: Only on UserMessage (role-specific)
   */
  @xmlIgnore
  userId?: string;

  /**
   * Agent that generated this message.
   * FROM: Azure Agent API
   * ADDITION: Not in MAF ChatMessage
   *
   * M365: Entra Agent ID (Object ID from Microsoft Entra ID)
   * - For bot/agent principals: Service Principal Object ID
   * - For user-acting-as-agent: User Object ID
   * - Retrieved via Microsoft Graph API /servicePrincipals or /users
   *
   * MESSAGING APP PATTERN:
   * - Like bot_id in Slack, Teams
   * - Identifies which agent/bot generated the message
   *
   * XML: Only on AgentMessage (role-specific)
   */
  @xmlIgnore
  agentId?: string;

  /**
   * Run that generated this message.
   * FROM: Azure Agent API (completion_id)
   * ADDITION: Not in MAF ChatMessage
   *
   * M365: Links message to Run for audit trail
   *
   * XML: Only on AgentMessage (role-specific)
   */
  @xmlIgnore
  completionId?: string;

  /**
   * Timestamp when message was created.
   * BASE: MAF ChatMessage.CreatedAt (DateTimeOffset?)
   */
  @xmlAttribute("created-at")
  createdAt?: utcDateTime;

  /**
   * Timestamp when message generation completed.
   * FROM: Azure Agent API
   * ADDITION: Not in MAF ChatMessage
   *
   * RATIONALE: Tracks latency for agent responses
   *
   * XML: Only on AgentMessage (role-specific)
   */
  @xmlIgnore
  completedAt?: utcDateTime;

  /**
   * Custom metadata.
   * BASE: MAF ChatMessage.AdditionalProperties (AdditionalPropertiesDictionary)
   *
   * M365: Can store conversation metadata (e.g., injected by orchestration pipeline)
   * NOT SERIALIZED: Excluded from XML
   */
  @xmlIgnore
  metadata?: Record<unknown>;

  /**
   * Underlying provider representation.
   * BASE: MAF ChatMessage.RawRepresentation
   *
   * RATIONALE: Preserves original response for debugging
   * NOT SERIALIZED: Excluded from XML
   */
  @xmlIgnore
  rawRepresentation?: unknown;
}


/**
 * Chat Role Enum
 *
 * BASE: MAF ChatRole (readonly struct)
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/ChatCompletion/ChatRole.cs
 *
 * SIMPLIFIED: Enum instead of struct for TypeSpec
 *
 * ADDITIONS:
 * - developer role (from Anthropic/OpenAI)
 *   - Used for system-level context that's distinct from system instructions
 *   - Anthropic: "developer" role for instructions from app developer
 *   - OpenAI: Plans to deprecate system role in favor of developer role
 * - channel role (from Activity Protocol)
 *   - Used for platform/infrastructure events (EventContent, TraceContent, etc.)
 *   - Not sent to LLM, handled by orchestrator
 *   - KEY FOR PROACTIVE MESSAGING: External triggers create messages with role="channel"
 *
 * PROACTIVE MESSAGING:
 * The "channel" role is ESSENTIAL for agent-initiated (proactive) messages:
 * - External event triggers → Message with role="channel" + EventContent
 * - Orchestrator can optionally respond to these events
 * - LLM does NOT see channel messages (filtered out during context building)
 *
 * EXAMPLES:
 * - role="user": User-initiated conversation ("Hello, how are you?")
 * - role="channel": External trigger (scheduled_trigger, webhook_received, participant_added)
 * - role="assistant": Agent response to either user or channel events
 *
 * FILTERING:
 * When building LLM context, filter by role:
 * - Include: system, developer, user, assistant, tool
 * - Exclude: channel (unless orchestrator explicitly includes for context)
 */
enum ChatRole {
  /** System instructions */
  system,

  /** Developer-provided context/instructions (supersedes system in some models) */
  developer,

  /**
   * Agent responses
   *
   * CRITICAL WARNING: DO NOT CHANGE THIS TO "assistant"
   * =====================================================
   * Agent Protocol uses "agent" as the role name for agent responses.
   * This is NOT "assistant" - that is a different protocol (OpenAI, etc.)
   *
   * When implementing in any language:
   * - Python: role must be "agent"
   * - C#/.NET: role must be "agent"
   * - TypeScript: role must be "agent"
   *
   * DO NOT map this to "assistant" in any server implementation.
   * DO NOT convert "assistant" to "agent" or vice versa.
   * The role value in Agent Protocol is ALWAYS "agent" for agent responses.
   * =====================================================
   */
  agent,

  /** User messages */
  user,

  /** Tool execution results */
  tool,

  /**
   * Platform/infrastructure events (Activity Protocol channel messages)
   * USED FOR: Proactive messaging triggers, system events, lifecycle notifications
   * FILTERED: Not sent to LLM (orchestrator-only)
   */
  channel,
}

/**
 * AI Content - Base Class for Message Content
 *
 * BASE: Microsoft.Extensions.AI.AIContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/AIContent.cs
 *
 * POLYMORPHIC: Uses JSON discriminator "$type" (MAF pattern)
 *
 * DERIVED TYPES (from MAF):
 * - TextContent
 * - FunctionCallContent
 * - FunctionResultContent
 * - ErrorContent
 * - TextReasoningContent
 * - DataContent
 * - UriContent
 *
 * ADDITIONS (from other frameworks):
 * - ImageContent (Azure Agent API)
 * - AudioContent (Azure Agent API)
 * - VideoContent (Azure Agent API)
 * - FileContent (Azure Agent API)
 * - SearchResultContent (LLMProxy - citable)
 * - DocumentContent (LLMProxy - citable)
 * - AdaptiveCardContent (Activity Protocol)
 * - RefusalContent (Azure Agent API)
 * - ContentFilterResultContent (Azure Agent API)
 */

/**
 * Base model for all AI content types.
 * Provides common properties for audience filtering, encryption, and extensibility.
 *
 * RATIONALE: DRY principle - common properties inherited by all 29+ content types
 *
 * PROPERTIES:
 * - audience: Content-level audience filtering (e.g., reasoning visible to assistant only)
 * - encryption: Content-level encryption metadata
 * - additionalProperties: Client-side extensibility (not serialized to XML)
 */
model AIContentBase {
  /**
   * Target audience filter (comma-separated roles).
   * Controls which roles should see this content:
   * - Omitted/null: Visible to all roles (default)
   * - "user": Human-only content (UI hints, summaries)
   * - "agent": Agent-only content (reasoning, internal context)
   * - "user,agent": Explicitly visible to both
   *
   * EXAMPLES:
   * - <thinking audience="agent">reasoning here</thinking>
   * - <text audience="user">User-facing summary</text>
   * - <adaptive-card audience="user" />
   */
  @xmlAttribute
  audience?: string;

  /**
   * Encryption information (simplified as string for XML).
   * Contains encryption key reference and metadata.
   *
   * RATIONALE: Simplified from complex EncryptionInfo object for XML compatibility
   * FORMAT: JSON string or key reference
   */
  @xmlAttribute
  encryption?: string;

  /**
   * Additional properties for extensibility.
   * NOT SERIALIZED: Client-side metadata, transient state.
   *
   * EXAMPLES:
   * - Tracking IDs, correlation data
   * - Client-specific rendering hints
   * - Temporary computation results
   */
  @xmlIgnore
  additionalProperties?: Record<unknown>;
}

@discriminator("kind")
union AIContent {
  // Core LLM Content (6 types)
  TextContent,
  FunctionCallContent,
  FunctionResultContent,
  ErrorContent,
  TextReasoningContent,
  DataContent,

  // Multimedia Content (8 types)
  UriContent,
  ImageContent,
  AudioContent,
  TranscriptContent,
  VideoContent,
  FileContent,
  HostedFileContent,
  HostedVectorStoreContent,

  // Document Content (3 types)
  SearchResultContent,
  DocumentContent,
  AdaptiveCardContent,

  // UI Interaction Content (7 types)
  TypingIndicatorContent,
  MessageReactionContent,
  MessageDeleteContent,
  MessageUpdateContent,
  SuggestedActionsContent,
  ActionContent,
  UserInputRequestContent,

  // System Content (4 types)
  EventContent,
  TraceContent,
  RefusalContent,
  ContentFilterResultContent,
}

// ============================================
// SECTION 2: CORE LLM CONTENT (6 types)
//
// Content types for core language model interactions:
// - Text input/output
// - Function calling (tool use)
// - Error reporting
// - Chain-of-thought reasoning
// - Raw data
// ============================================

/**
 * Text Content
 *
 * BASE: Microsoft.Extensions.AI.TextContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextContent.cs
 *
 * XML: <text>Hello world</text>
 */
@xmlRoot("text")
model TextContent extends AIContentBase {
  kind: "text";

  /** The text string */
  @xmlText
  @contentType("text")
  text: string;
}

/**
 * Function Call Content
 *
 * BASE: Microsoft.Extensions.AI.FunctionCallContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionCallContent.cs
 *
 * REPRESENTS: Agent's request to execute a tool
 *
 * XML: <function-call call-id="..." name="...">{"arg": "value"}</function-call>
 */
@xmlRoot("function-call")
model FunctionCallContent extends AIContentBase {
  kind: "functionCall";

  /** Unique identifier for this tool call */
  @xmlAttribute("call-id")
  callId: string;

  /** Name of the function to call */
  @xmlAttribute("name")
  name: string;

  /** Arguments as JSON string (XML serialization uses string only) */
  @xmlText
  @contentType("json")
  arguments: string;
}

/**
 * Function Result Content
 *
 * BASE: Microsoft.Extensions.AI.FunctionResultContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionResultContent.cs
 *
 * REPRESENTS: Result of tool execution
 *
 * XML: <function-result call-id="..." name="...">{"result": "value"}</function-result>
 */
@xmlRoot("function-result")
model FunctionResultContent extends AIContentBase {
  kind: "functionResult";

  /** Tool call ID this result corresponds to */
  @xmlAttribute("call-id")
  callId?: string;

  /** Name of the function that was called */
  @xmlAttribute("name")
  name?: string;

  /** Result data as JSON string (XML serialization uses string only) */
  @xmlText
  @contentType("json")
  result: string;
}

/**
 * Error Content
 *
 * BASE: Microsoft.Extensions.AI.ErrorContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/ErrorContent.cs
 *
 * XML: <error code="..."><message>...</message><stack-trace>...</stack-trace></error>
 */
@xmlRoot("error")
model ErrorContent extends AIContentBase {
  kind: "error";

  /** Error code */
  @xmlAttribute("code")
  code?: string;

  /** Error message */
  @xmlElement("message")
  message: string;

  /** Stack trace */
  @xmlElement("stack-trace")
  stackTrace?: string;
}

/**
 * Text Reasoning Content
 *
 * BASE: Microsoft.Extensions.AI.TextReasoningContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextReasoningContent.cs
 *
 * FROM: Extended thinking support (Anthropic, OpenAI o1/o3)
 *
 * USAGE: Use inherited 'audience' property to control visibility
 * - audience="agent": Reasoning visible to agent only (internal reasoning)
 * - audience="user": Reasoning visible to user (exposed reasoning)
 * - audience omitted: Visible to all (default)
 *
 * XML: <thinking audience="agent">Internal reasoning...</thinking>
 */
@xmlRoot("thinking")
model TextReasoningContent extends AIContentBase {
  kind: "reasoning";

  /** Reasoning text */
  @xmlText
  @contentType("text")
  text: string;
}

/**
 * Data Content
 *
 * BASE: Microsoft.Extensions.AI.DataContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/DataContent.cs
 *
 * REPRESENTS: Arbitrary structured data
 *
 * XML: <data uri="..." mime-type="...">base64data</data>
 */
@xmlRoot("data")
model DataContent extends AIContentBase {
  kind: "data";

  /** URI identifying the data */
  @xmlAttribute("uri")
  uri?: string;

  /** MIME type */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** Data value (base64 or text) */
  @xmlText
  value?: string;
}

// ============================================
// SECTION 3: MULTIMEDIA CONTENT (8 types)
//
// Content types for rich media:
// - Images, audio, video
// - File attachments
// - Transcripts
// - Hosted resources (files, vector stores)
// ============================================

/**
 * URI Content
 *
 * BASE: Microsoft.Extensions.AI.UriContent
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/UriContent.cs
 *
 * REPRESENTS: Reference to external content via URI
 *
 * XML: <uri>https://example.com</uri>
 */
@xmlRoot("uri")
model UriContent extends AIContentBase {
  kind: "uri";

  /** The URI */
  @xmlText
  uri: string;
}

/**
 * Image Content
 *
 * FROM: Azure Agent API (ImageContent)
 * ADDITION: Not in MAF
 *
 * Provides three delivery methods: uri, dataUri, or raw data bytes.
 *
 * M365: Future multi-modal scenarios
 *
 * XML: <image uri="..." mime-type="..." width="1920" height="1080" />
 */
@xmlRoot("image")
model ImageContent extends AIContentBase {
  kind: "image";

  /** External image URL */
  @xmlAttribute("uri")
  uri?: string;

  /** Alt text for accessibility */
  @xmlAttribute("alt")
  alt?: string;

  /** MIME type (e.g., "image/png") */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** Image width in pixels */
  @xmlAttribute("width")
  width?: int32;

  /** Image height in pixels */
  @xmlAttribute("height")
  height?: int32;
}

/**
 * Audio Content
 *
 * FROM: Azure Agent API (AudioContent)
 * ADDITION: Not in MAF
 *
 * Represents audio data that can be included in messages. Supports voice notes,
 * audio responses, and other audio scenarios. Audio can be provided as raw bytes,
 * data URI, or external URL reference.
 *
 * M365: Multi-modal scenarios (voice input, audio responses, voice notes)
 */
/**
 * XML: <audio uri="..." mime-type="..." duration="15" />
 */
@xmlRoot("audio")
model AudioContent extends AIContentBase {
  kind: "audio";

  /** External audio URL */
  @xmlAttribute("uri")
  uri?: string;

  /** MIME type */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** Duration in seconds */
  @xmlAttribute("duration")
  duration?: int32;
}

/**
 * Transcript Content
 *
 * @usage
 *
 * Use Cases:
 * 1. **Audio Message Transcripts**: User sends voice message, transcript shown in UI
 * 2. **Video Captions**: Video content with transcript for accessibility
 * 3. **Meeting Transcripts**: Audio recording with human-readable transcript
 * 4. **Accessibility**: Screen reader support for audio/video content
 *
 */
/**
 * XML: <transcript text="..." language="en" confidence="0.98" speaker="..." />
 */
@xmlRoot("transcript")
model TranscriptContent extends AIContentBase {
  kind: "transcript";

  /** Transcript text */
  @xmlAttribute("text")
  text: string;

  /** Language code (ISO 639-1 or BCP 47) */
  @xmlAttribute("language")
  language?: string;

  /** Confidence score (0.0 - 1.0) */
  @xmlAttribute("confidence")
  confidence?: float32;

  /** Speaker identification */
  @xmlAttribute("speaker")
  speaker?: string;
}

/**
 * Word Timing
 *
 * ADDITION: For synchronized transcript playback
 * PURPOSE: Word-level timestamps for highlighting during audio/video playback
 */
model WordTiming {
  /** Word text */
  word: string;

  /** Start time in seconds */
  start: float32;

  /** End time in seconds */
  end: float32;

  /** Optional confidence score for this word */
  confidence?: float32;
}

/**
 * Video Content
 *
 * FROM: Azure Agent API (VideoContent)
 * ADDITION: Not in MAF
 *
 * Represents video data that can be included in messages.
 *
 * M365: Multi-modal scenarios (video input, video responses, screen recordings)
 *
 * XML: <video uri="..." mime-type="..." width="1920" height="1080" duration="120" frame-rate="30" />
 */
@xmlRoot("video")
model VideoContent extends AIContentBase {
  kind: "video";

  /** External video URL */
  @xmlAttribute("uri")
  uri?: string;

  /** MIME type */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** Video width in pixels */
  @xmlAttribute("width")
  width?: int32;

  /** Video height in pixels */
  @xmlAttribute("height")
  height?: int32;

  /** Duration in seconds */
  @xmlAttribute("duration")
  duration?: int32;

  /** Frame rate (frames per second) */
  @xmlAttribute("frame-rate")
  frameRate?: int32;
}

/**
 * File Content
 *
 * FROM: Azure Agent API (FileContent)
 * ADDITION: Not in MAF
 *
 * REPRESENTS: Generic file attachment
 */
/**
 * XML: <file uri="..." filename="..." mime-type="..." size-bytes="1024" />
 */
@xmlRoot("file")
model FileContent extends AIContentBase {
  kind: "file";

  /** External file URL */
  @xmlAttribute("uri")
  uri?: string;

  /** File name */
  @xmlAttribute("filename")
  filename?: string;

  /** MIME type */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** File size in bytes */
  @xmlAttribute("size-bytes")
  sizeBytes?: int64;
}

/**
 * Search Result Content
 *
 * FROM: LLMProxy (SearchResultContent - citable)
 * ADDITION: Not in MAF or Azure Agent API
 *
 * RATIONALE: RAG scenarios require citable search results
 *
 * M365: Supports grounding and citation requirements
 */

// ============================================
// SECTION 4: DOCUMENT CONTENT (3 types)
//
// Content types for document/search integration:
// - Search results
// - Document chunks
// - Adaptive cards
// - Citations
// ============================================

/**
 * XML: <search-result title="..." url="..." score="0.94"><snippet>...</snippet></search-result>
 */
@xmlRoot("search-result")
model SearchResultContent extends AIContentBase {
  kind: "searchResult";

  /** Search result title */
  @xmlAttribute("title")
  title: string;

  /** Source URL */
  @xmlAttribute("url")
  url: string;

  /** Relevance score (0.0-1.0) */
  @xmlAttribute("score")
  score?: float32;

  /** Snippet/summary */
  @xmlElement("snippet")
  snippet: string;
}

/**
 * Document Content
 *
 * FROM: LLMProxy (DocumentContent - citable)
 * ADDITION: Not in MAF or Azure Agent API
 *
 * RATIONALE: Document references for RAG
 *
 * M365: Supports document context tools and citations
 */
/**
 * XML: <document title="..." document-id="..." source="..." mime-type="..."><content>...</content></document>
 */
@xmlRoot("document")
model DocumentContent extends AIContentBase {
  kind: "document";

  /** Document title */
  @xmlAttribute("title")
  title: string;

  /** Document ID */
  @xmlAttribute("document-id")
  documentId: string;

  /** Source URL or path */
  @xmlAttribute("source")
  source: string;

  /** MIME type of document */
  @xmlAttribute("mime-type")
  mimeType?: string;

  /** Document content or excerpt */
  @xmlElement("content")
  content?: string;
}

/**
 * Citation
 *
 * FROM: LLMProxy + Anthropic (search_result_location pattern)
 * ADDITION: Not in MAF or Azure Agent API
 *
 * M365: Critical for compliance and attribution
 */
model Citation {
  /** Source reference (URL, document ID, etc.) */
  source: string;

  /** Quoted text */
  text?: string;

  /** Location in source (from Anthropic) */
  location?: {
    /** Start character index */
    start: int32;

    /** End character index */
    end: int32;
  };

  /** Relevance score */
  score?: float32;
}

/**
 * Adaptive Card Content
 *
 * FROM: Activity Protocol (rich cards)
 * ADDITION: Not in MAF or Azure Agent API
 *
 * RATIONALE: Rich UI for human-in-the-loop scenarios
 *
 * M365: Future Teams integration scenarios
 */
/**
 * XML: <adaptive-card version="1.5" fallback-text="...">{"type":"AdaptiveCard",...}</adaptive-card>
 */
@xmlRoot("adaptive-card")
model AdaptiveCardContent extends AIContentBase {
  kind: "adaptiveCard";

  /** Card version */
  @xmlAttribute("version")
  version?: string;

  /** Fallback text if card not supported */
  @xmlAttribute("fallback-text")
  fallbackText?: string;

  /** Adaptive Card JSON */
  @xmlText
  @contentType("json")
  card: string;
}

/**
 * Refusal Content
 *
 * FROM: Azure Agent API (RefusalContent)
 * ADDITION: Not in MAF
 *
 * RATIONALE: Model refuses to complete request (safety/policy)
 *
 * M365: Compliance and content policy tracking
 *
 * XML: <refusal reason="...">Detailed refusal message</refusal>
 */
@xmlRoot("refusal")
model RefusalContent extends AIContentBase {
  kind: "refusal";

  /** Reason for refusal */
  @xmlAttribute("reason")
  reason: string;
}

/**
 * Content Filter Result Content
 *
 * FROM: Azure Agent API (ContentFilterResultContent)
 * ADDITION: Not in MAF
 *
 * RATIONALE: Azure content moderation results
 *
 * M365: Compliance and audit requirements
 *
 * XML: <content-filter-result filtered="true" category="hate" severity="medium" />
 */
@xmlRoot("content-filter-result")
model ContentFilterResultContent extends AIContentBase {
  kind: "contentFilterResult";

  /** Whether content was filtered */
  @xmlAttribute("filtered")
  filtered: boolean;

  /** Filter category (violence, hate, sexual, self_harm) */
  @xmlAttribute("category")
  category: string;

  /** Severity level (low, medium, high) */
  @xmlAttribute("severity")
  severity: string;
}

/**
 * User Input Request Content
 *
 * BASE: Concept exists in MAF (AgentResponse.UserInputRequests)
 * SOURCE: /agent-framework/dotnet/src/Microsoft.Agents.AI.Abstractions/AgentResponse.cs
 *
 * REPRESENTS: Agent requesting input from user (HITL)
 *
 * M365: Critical for human-in-the-loop workflows
 */
/**
 * XML: <user-input-request request-id="..." prompt="..." input-type="choice" required="true" />
 */
@xmlRoot("user-input-request")
model UserInputRequestContent extends AIContentBase {
  kind: "userInputRequest";

  /** Unique identifier for this input request */
  @xmlAttribute("request-id")
  requestId: string;

  /** Prompt for user */
  @xmlAttribute("prompt")
  prompt: string;

  /** Input type */
  @xmlAttribute("input-type")
  inputType?: string;

  /** Whether input is required */
  @xmlAttribute("required")
  required?: boolean;
}

/**
 * Suggested Actions Content (Quick Reply Buttons)
 *
 * @usage
 *
 * Use Cases:
 * - Quick reply options ("Yes", "No", "Maybe")
 * - Menu selections ("Check Status", "Contact Support")
 * - Call-to-action buttons ("View Details", "Learn More")
 *
 */
/**
 * XML: <suggested-actions><action title="Yes" type="message" value="yes" /></suggested-actions>
 */
@xmlRoot("suggested-actions")
model SuggestedActionsContent extends AIContentBase {
  kind: "suggestedActions";

  /** Array of suggested action buttons */
  @xmlElement("action")
  actions: SuggestedAction[];
}

/**
 * Suggested Action
 *
 * Represents a single quick reply button/action
 */
model SuggestedAction {
  /** Display text on the button */
  @xmlAttribute("title")
  title: string;

  /** Type of action */
  @xmlAttribute("type")
  actionType: string;

  /** Action payload */
  @xmlAttribute("value")
  value?: string;

  /** Text to send when clicked */
  @xmlAttribute("text")
  text?: string;
}

/**
 * Event Content (Programmatic Events)
 *
 * @usage
 *
 * Use Cases:
 * - Programmatic notifications: token_refresh, payment_received, workflow_completed
 * - Thread lifecycle: participant_added, participant_removed, topic_changed
 * - System notifications: session_started, session_ended
 * - External triggers: scheduled_trigger, webhook_received, threshold_alert
 *
 */

// ============================================
// SECTION 5: SYSTEM CONTENT (4 types)
//
// Content types for system events and metadata:
// - Events, traces
// - Content filtering
// - Refusals
// - Content annotations and encryption
// ============================================

/**
 * XML: <event name="..." timestamp="...">{value}</event>
 */
@xmlRoot("event")
model EventContent extends AIContentBase {
  kind: "event";

  /** Event name */
  @xmlAttribute("name")
  name: string;

  /** Event timestamp */
  @xmlAttribute("timestamp")
  timestamp?: utcDateTime;

  /** Event payload (as text/JSON) */
  @xmlText
  value?: string;
}

/**
 * Trace Content (Debugging/Telemetry)
 *
 * @usage
 *
 * Use Cases:
 * - Observability: luis_recognizer, qna_maker, dialog_state
 * - Debug traces: turn_context, middleware_executed
 * - Performance metrics: latency_measured, tokens_consumed
 *
 */
/**
 * XML: <trace name="..." label="..." severity="information" timestamp="...">{value}</trace>
 */
@xmlRoot("trace")
model TraceContent extends AIContentBase {
  kind: "trace";

  /** Trace name (identifies the component/operation) */
  @xmlAttribute("name")
  name: string;

  /** Human-readable label */
  @xmlAttribute("label")
  label?: string;

  /** Severity level */
  @xmlAttribute("severity")
  severity?: string;

  /** Trace timestamp */
  @xmlAttribute("timestamp")
  timestamp?: utcDateTime;

  /** Trace data/payload (as text/JSON) */
  @xmlText
  value?: string;
}

/**
 * Action Content (Interactive Actions Requiring Response)
 *
 * @usage
 *
 * Use Cases:
 * - Card button clicks: card_action_submit, adaptive_card_action
 * - Interactive elements: button_clicked, menu_selected
 * - Form submissions: form_submitted, input_provided
 *
 */
/**
 * XML: <action name="button_clicked" text="Refresh" timestamp="...">{value}</action>
 */
@xmlRoot("action")
model ActionContent extends AIContentBase {
  kind: "action";

  /** Action name/type */
  @xmlAttribute("name")
  name: string;

  /** Display text for the action */
  @xmlAttribute("text")
  text?: string;

  /** Action timestamp */
  @xmlAttribute("timestamp")
  timestamp?: utcDateTime;

  /** Action payload/data (as text/JSON) */
  @xmlText
  value?: string;
}

/**
 * Typing Indicator Content (Bidirectional Presence)
 *
 * FROM: Activity Protocol Typing activity
 * ADDITION: Not in MAF or Azure Agent API
 *
 * REPRESENTS: Typing/thinking indicator from USER OR AGENT
 *
 * BIDIRECTIONAL: Can be sent by either party
 * - User sends: "I'm typing a message"
 * - Agent sends: "I'm generating a response"
 *
 * EPHEMERAL: Not persisted in message history
 * - Temporary presence indicator
 * - Cleared when actual content arrives
 *
 * MESSAGING APP PATTERN:
 * - Like "..." typing indicator in iMessage, WhatsApp
 * - Like "Alice is typing..." in Teams
 * - Like "Thinking..." in ChatGPT
 */

// ============================================
// SECTION 6: UI INTERACTION CONTENT (7 types)
//
// Content types for user interactions:
// - Typing indicators
// - Reactions
// - Message operations (delete, update)
// - Suggested actions
// ============================================

/**
 * XML: <typing-indicator from="user_123" status="typing" timestamp="..." />
 */
@xmlRoot("typing-indicator")
model TypingIndicatorContent extends AIContentBase {
  kind: "typingIndicator";

  /** Who is typing (user ID or agent ID) */
  @xmlAttribute("from")
  from: string;

  /** Indicator status */
  @xmlAttribute("status")
  status: "typing" | "thinking" | "processing";

  /** Optional timestamp */
  @xmlAttribute("timestamp")
  timestamp?: utcDateTime;
}

/**
 * Message Reaction Content (Social Interactions)
 *
 * FROM: Activity Protocol messageReaction activity
 * ADDITION: Not in MAF or Azure Agent API
 *
 * REPRESENTS: Social reactions to messages (like, love, thumbs up, etc.)
 *
 * LIGHTWEIGHT: Doesn't interrupt conversation flow
 * - Simple social acknowledgment
 * - Multiple reactions can exist on one message
 *
 * MESSAGING APP PATTERN:
 * - Like emoji reactions in Slack, Teams, iMessage
 * - Like "reactions" in Facebook Messenger
 * - Non-intrusive way to acknowledge messages
 *
 * XML: <message-reaction referenced-message-id="msg_123"><added type="like" /></message-reaction>
 */
@xmlRoot("message-reaction")
model MessageReactionContent extends AIContentBase {
  kind: "messageReaction";

  /** Message ID being reacted to */
  @xmlAttribute("referenced-message-id")
  referencedMessageId: string;

  /** Reactions added */
  @xmlElement("added")
  reactionsAdded?: MessageReaction[];

  /** Reactions removed */
  @xmlElement("removed")
  reactionsRemoved?: MessageReaction[];
}

/**
 * Message Reaction (Individual Reaction)
 */
model MessageReaction {
  /** Reaction type (e.g., "like", "love", "thumbsUp", "+1") */
  type: string;

  /** User who reacted (optional) */
  userId?: string;

  /** Timestamp of reaction */
  timestamp?: utcDateTime;
}

/**
 * Message Delete Content (Message Removal)
 *
 * FROM: Activity Protocol messageDelete activity
 * ADDITION: Not in MAF or Azure Agent API
 *
 * REPRESENTS: Request to delete an existing message
 *
 * MESSAGING APP PATTERN:
 * - Like deleting a message in Slack or Teams
 * - Message ID references the message to delete
 *
 * XML: <message-delete message-id="msg_123" reason="user_requested" />
 */
@xmlRoot("message-delete")
model MessageDeleteContent extends AIContentBase {
  kind: "messageDelete";

  /** Message ID to delete */
  @xmlAttribute("message-id")
  messageId: string;

  /** Reason for deletion (optional) */
  @xmlAttribute("reason")
  reason?: string;
}

/**
 * Message Update Content (Message Edit)
 *
 * FROM: Activity Protocol messageUpdate activity
 * ADDITION: Not in MAF or Azure Agent API
 *
 * REPRESENTS: Update to an existing message
 *
 * MESSAGING APP PATTERN:
 * - Like editing a message in Slack or Teams
 * - Message ID references the message to update
 * - Updated content provided in separate ChatMessage
 *
 * XML: <message-update message-id="msg_123" reason="typo_fix" />
 */
@xmlRoot("message-update")
model MessageUpdateContent extends AIContentBase {
  kind: "messageUpdate";

  /** Message ID to update */
  @xmlAttribute("message-id")
  messageId: string;

  /** Update reason/description (optional) */
  @xmlAttribute("reason")
  reason?: string;
}

/**
 * Hosted File Content
 *
 * @usage
 *
 * Rationale:
 * - Provider-hosted files (e.g., OpenAI file uploads, Azure blob storage)
 * - File processing by provider (embeddings, image analysis, transcription)
 * - Efficient reference without transferring file content in messages
 *
 * EXAMPLES:
 * - OpenAI: file-abc123 (uploaded via files API)
 * - Azure: azure://storage.blob.core.windows.net/container/file.pdf
 *
 * XML: <hosted-file file-id="file-abc123" filename="doc.pdf" media-type="application/pdf" size-bytes="1024" />
 */
@xmlRoot("hosted-file")
model HostedFileContent extends AIContentBase {
  kind: "hostedFile";

  /**
   * Provider's file identifier.
   * EXAMPLES:
   * - OpenAI: "file-abc123"
   * - Azure: "https://storage.blob.core.windows.net/container/file.pdf"
   */
  @xmlAttribute("file-id")
  fileId: string;

  /**
   * Original filename (optional).
   */
  @xmlAttribute("filename")
  filename?: string;

  /**
   * Media type (MIME type).
   */
  @xmlAttribute("media-type")
  mediaType?: string;

  /**
   * File size in bytes (optional).
   */
  @xmlAttribute("size-bytes")
  sizeBytes?: int64;
}

/**
 * Hosted Vector Store Content
 *
 * @usage
 *
 * Rationale:
 * - Provider-hosted vector stores (e.g., OpenAI Assistants vector stores)
 * - RAG (Retrieval-Augmented Generation) with provider-managed embeddings
 * - Efficient reference without transferring embeddings in messages
 *
 * EXAMPLES:
 * - OpenAI: vs_abc123 (created via vector stores API)
 * - Azure: Reference to Azure AI Search index
 *
 * M365: Supports BYOM (Bring Your Own Memory) pattern via vector store references
 *
 * XML: <hosted-vector-store vector-store-id="vs_abc123" name="my-vectors" document-count="1000" />
 */
@xmlRoot("hosted-vector-store")
model HostedVectorStoreContent extends AIContentBase {
  kind: "hostedVectorStore";

  /**
   * Provider's vector store identifier.
   * EXAMPLES:
   * - OpenAI: "vs_abc123"
   * - Azure: "https://search.azure.com/indexes/my-index"
   */
  @xmlAttribute("vector-store-id")
  vectorStoreId: string;

  /**
   * Vector store name (optional).
   */
  @xmlAttribute("name")
  name?: string;

  /**
   * Number of vectors/documents in store (optional).
   */
  @xmlAttribute("document-count")
  documentCount?: int32;
}

/**
 * AI Annotation
 *
 * BASE: Microsoft.Extensions.AI.AIAnnotation (base class for annotations)
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/AIAnnotation.cs
 *
 * REPRESENTS: Metadata attached to content (e.g., citations)
 */
model AIAnnotation {
  /** Annotation type */
  type: string;

  /** Annotation data */
  data?: Record<unknown>;
}

