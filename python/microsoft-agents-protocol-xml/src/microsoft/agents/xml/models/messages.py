"""
Generated from TypeSpec definitions.

This file is auto-generated. Do not edit manually.
"""

# ruff: noqa: E501  # Allow long lines in generated code
# type: ignore  # Skip type checking for generated code

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union, Literal

from xsdata.models.datatype import XmlDateTime
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

class ChatRole(str, Enum):
    SYSTEM = "system"
    DEVELOPER = "developer"
    AGENT = "agent"
    USER = "user"
    TOOL = "tool"
    CHANNEL = "channel"


@dataclass(kw_only=True)
class ChatMessage:
    """
    Unique message identifier.
    BASE: MAF ChatMessage.MessageId (optional)
    FROM: Azure Agent API (required, server-generated)
    
    MODIFIED: Made required for M365 tracking
    
    ID ASSIGNMENT:
    - Client-provided: Channels can provide their own messageId (e.g., Teams message ID, Slack ts)
    - Server-generated: If omitted, server generates GUID
    - Uniqueness: Must be unique within conversation store (recommend: {channelId}:{originalId})
    
    RATIONALE: Channels are source of truth for conversation store
    - Preserves original message IDs from external systems
    - Enables idempotent message creation (retry with same ID)
    - Supports message deduplication and correlation
    """
    message_id: str = field(metadata={"name": "message-id", "type": "Attribute"})
    """
    Message role.
    BASE: MAF ChatMessage.Role (ChatRole struct with static instances)

    SIMPLIFIED: Changed from struct to enum for TypeSpec

    ROLES:
    - system: System instructions (MAF + Azure)
    - developer: Developer-provided context (Anthropic/OpenAI)
    - user: User messages (MAF + Azure)
    - agent: Agent responses (MAF + Azure)
    - tool: Tool results (MAF + Azure)
    - channel: Platform/infrastructure events (Activity Protocol)

    NOT SERIALIZED: Role is implicit in XML element name (e.g., <system>, <user>)
    """
    role: ChatRole
    """
    Parent message ID for conversation branching.

    @usage

    Use Cases:
    - User wants to edit message-5 and rerun from that point
    - A/B testing different conversation paths
    - Undo/redo by branching to previous states
    - Time travel debugging

    """
    parent_message_id: Optional[str] = field(default=None, metadata={"name": "parent-message-id", "type": "Attribute"})
    """
    Thread this message belongs to.
    FROM: Azure Agent API
    NOT SERIALIZED: Excluded from XML (use @xmlIgnore)

    RATIONALE: Thread ID is useful for API/database queries but not
    needed in XML message serialization. Messages can be grouped by
    thread at the API layer without including thread ID in each message.
    """
    thread_id: Optional[str] = None
    """
    Content items in this message.
    BASE: MAF ChatMessage.Contents (IList<AIContent>)
    
    RATIONALE: List pattern supports multi-modal content
    (vs Azure's string | AIContent[] which requires union types)
    
    M365: Enables multi-modal future scenarios
    
    NOT SERIALIZED HERE: Role-specific message classes handle contents serialization
    """
    contents: list[AIContent] = field(default_factory=list)
    """
    Concatenated text from all TextContent items.
    BASE: MAF ChatMessage.Text (computed property)
    
    RATIONALE: Convenience for text-only messages
    NOT SERIALIZED: Computed from contents
    """
    text: Optional[str] = None
    """
    Author name for display.
    BASE: MAF ChatMessage.AuthorName
    """
    author_name: Optional[str] = field(default=None, metadata={"name": "author-name", "type": "Attribute"})
    """
    User who created this message.
    FROM: Azure Agent API
    ADDITION: Not in MAF ChatMessage
    
    M365: Entra User ID (Object ID from Microsoft Entra ID)
    - For end users: User's Object ID (e.g., "12345678-1234-1234-1234-123456789012")
    - Retrieved via Microsoft Graph API /me or /users/{id}
    
    MESSAGING APP PATTERN:
    - Like userId in Slack, Teams, WhatsApp
    - Identifies who sent the message
    
    XML: Only on UserMessage (role-specific)
    """
    user_id: Optional[str] = None
    """
    Agent that generated this message.
    FROM: Azure Agent API
    ADDITION: Not in MAF ChatMessage
    
    M365: Entra Agent ID (Object ID from Microsoft Entra ID)
    - For bot/agent principals: Service Principal Object ID
    - For user-acting-as-agent: User Object ID
    - Retrieved via Microsoft Graph API /servicePrincipals or /users
    
    MESSAGING APP PATTERN:
    - Like bot_id in Slack, Teams
    - Identifies which agent/bot generated the message
    
    XML: Only on AgentMessage (role-specific)
    """
    agent_id: Optional[str] = None
    """
    Run that generated this message.
    FROM: Azure Agent API (completion_id)
    ADDITION: Not in MAF ChatMessage
    
    M365: Links message to Run for audit trail
    
    XML: Only on AgentMessage (role-specific)
    """
    completion_id: Optional[str] = None
    """
    Timestamp when message was created.
    BASE: MAF ChatMessage.CreatedAt (DateTimeOffset?)
    """
    created_at: Optional[datetime] = field(default=None, metadata={"name": "created-at", "type": "Attribute"})
    """
    Timestamp when message generation completed.
    FROM: Azure Agent API
    ADDITION: Not in MAF ChatMessage
    
    RATIONALE: Tracks latency for agent responses
    
    XML: Only on AgentMessage (role-specific)
    """
    completed_at: Optional[datetime] = None
    """
    Custom metadata.
    BASE: MAF ChatMessage.AdditionalProperties (AdditionalPropertiesDictionary)
    
    M365: Can store conversation metadata (e.g., injected by orchestration pipeline)
    NOT SERIALIZED: Excluded from XML
    """
    metadata: Optional[dict[str, Any]] = None
    """
    Underlying provider representation.
    BASE: MAF ChatMessage.RawRepresentation
    
    RATIONALE: Preserves original response for debugging
    NOT SERIALIZED: Excluded from XML
    """
    raw_representation: Optional[Any] = None


"""
Base model for all AI content types.
Provides common properties for audience filtering, encryption, and extensibility.
RATIONALE: DRY principle - common properties inherited by all 29+ content types
PROPERTIES:
- audience: Content-level audience filtering (e.g., reasoning visible to assistant only)
- encryption: Content-level encryption metadata
- additionalProperties: Client-side extensibility (not serialized to XML)
"""
@dataclass(kw_only=True)
class AIContentBase:
    """
    Target audience filter (comma-separated roles).
    Controls which roles should see this content:
    - Omitted/null: Visible to all roles (default)
    - "user": Human-only content (UI hints, summaries)
    - "agent": Agent-only content (reasoning, internal context)
    - "user,agent": Explicitly visible to both
    
    EXAMPLES:
    - <thinking audience="agent">reasoning here</thinking>
    - <text audience="user">User-facing summary</text>
    - <adaptive-card audience="user" />
    """
    audience: Optional[str] = field(default=None, metadata={"name": "audience", "type": "Attribute"})
    """
    Encryption information (simplified as string for XML).
    Contains encryption key reference and metadata.
    
    RATIONALE: Simplified from complex EncryptionInfo object for XML compatibility
    FORMAT: JSON string or key reference
    """
    encryption: Optional[str] = field(default=None, metadata={"name": "encryption", "type": "Attribute"})
    """
    Additional properties for extensibility.
    NOT SERIALIZED: Client-side metadata, transient state.
    
    EXAMPLES:
    - Tracking IDs, correlation data
    - Client-specific rendering hints
    - Temporary computation results
    """
    additional_properties: Optional[dict[str, Any]] = None


"""
Text Content
BASE: Microsoft.Extensions.AI.TextContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextContent.cs
XML: <text>Hello world</text>
"""
@dataclass(kw_only=True)
class TextContent(AIContentBase):
    kind: str = field(default="text", metadata={"name": "kind", "type": "Element"})
    text: str = field(metadata={"type": "Text"})


"""
The text string
"""
@dataclass(kw_only=True)
class FunctionCallContent(AIContentBase):
    kind: str = field(default="functionCall", metadata={"name": "kind", "type": "Element"})
    call_id: str = field(metadata={"name": "call-id", "type": "Attribute"})
    name: str = field(metadata={"name": "name", "type": "Attribute"})
    arguments: str = field(metadata={"type": "Text"})


"""
Arguments as JSON string (XML serialization uses string only)
"""
@dataclass(kw_only=True)
class FunctionResultContent(AIContentBase):
    kind: str = field(default="functionResult", metadata={"name": "kind", "type": "Element"})
    call_id: Optional[str] = field(default=None, metadata={"name": "call-id", "type": "Attribute"})
    name: Optional[str] = field(default=None, metadata={"name": "name", "type": "Attribute"})
    result: str = field(metadata={"type": "Text"})


"""
Name of the function that was called
"""
@dataclass(kw_only=True)
class ErrorContent(AIContentBase):
    kind: str = field(default="error", metadata={"name": "kind", "type": "Element"})
    code: Optional[str] = field(default=None, metadata={"name": "code", "type": "Attribute"})
    message: str = field(metadata={"name": "message", "type": "Element"})
    stack_trace: Optional[str] = field(default=None, metadata={"name": "stack-trace", "type": "Element"})


"""
Text Reasoning Content
BASE: Microsoft.Extensions.AI.TextReasoningContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextReasoningContent.cs
FROM: Extended thinking support (Anthropic, OpenAI o1/o3)
ADDITION: Added 'exposed' flag from Anthropic
- exposed = true: Reasoning visible to user
- exposed = false: Internal reasoning trace
XML: <thinking exposed="false">Internal reasoning...</thinking>
"""
@dataclass(kw_only=True)
class TextReasoningContent(AIContentBase):
    kind: str = field(default="reasoning", metadata={"name": "kind", "type": "Element"})
    text: str = field(metadata={"type": "Text"})
    exposed: Optional[bool] = field(default=None, metadata={"name": "exposed", "type": "Attribute"})


"""
Whether reasoning is exposed to user (from Anthropic)
"""
@dataclass(kw_only=True)
class DataContent(AIContentBase):
    kind: str = field(default="data", metadata={"name": "kind", "type": "Element"})
    uri: Optional[str] = field(default=None, metadata={"name": "uri", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    value: Optional[str] = field(default=None, metadata={"type": "Text"})


"""
URI Content
BASE: Microsoft.Extensions.AI.UriContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/UriContent.cs
REPRESENTS: Reference to external content via URI
XML: <uri>https://example.com</uri>
"""
@dataclass(kw_only=True)
class UriContent(AIContentBase):
    kind: str = field(default="uri", metadata={"name": "kind", "type": "Element"})
    uri: str = field(metadata={"type": "Text"})


"""
The URI
"""
@dataclass(kw_only=True)
class ImageContent(AIContentBase):
    kind: str = field(default="image", metadata={"name": "kind", "type": "Element"})
    uri: Optional[str] = field(default=None, metadata={"name": "uri", "type": "Attribute"})
    alt: Optional[str] = field(default=None, metadata={"name": "alt", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    width: Optional[int] = field(default=None, metadata={"name": "width", "type": "Attribute"})
    height: Optional[int] = field(default=None, metadata={"name": "height", "type": "Attribute"})


"""
Audio Content
FROM: Azure Agent API (AudioContent)
ADDITION: Not in MAF
Represents audio data that can be included in messages. Supports voice notes,
audio responses, and other audio scenarios. Audio can be provided as raw bytes,
data URI, or external URL reference.
M365: Multi-modal scenarios (voice input, audio responses, voice notes)
"""
@dataclass(kw_only=True)
class AudioContent(AIContentBase):
    kind: str = field(default="audio", metadata={"name": "kind", "type": "Element"})
    uri: Optional[str] = field(default=None, metadata={"name": "uri", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    duration: Optional[int] = field(default=None, metadata={"name": "duration", "type": "Attribute"})


"""
Transcript Content
@usage
Use Cases:
1. **Audio Message Transcripts**: User sends voice message, transcript shown in UI
2. **Video Captions**: Video content with transcript for accessibility
3. **Meeting Transcripts**: Audio recording with human-readable transcript
4. **Accessibility**: Screen reader support for audio/video content
"""
@dataclass(kw_only=True)
class TranscriptContent(AIContentBase):
    kind: str = field(default="transcript", metadata={"name": "kind", "type": "Element"})
    text: str = field(metadata={"name": "text", "type": "Attribute"})
    language: Optional[str] = field(default=None, metadata={"name": "language", "type": "Attribute"})
    confidence: Optional[float] = field(default=None, metadata={"name": "confidence", "type": "Attribute"})
    speaker: Optional[str] = field(default=None, metadata={"name": "speaker", "type": "Attribute"})


"""
Transcript text
"""
@dataclass(kw_only=True)
class WordTiming:
    word: str = field(metadata={"name": "word", "type": "Element"})
    start: float = field(metadata={"name": "start", "type": "Element"})
    end: float = field(metadata={"name": "end", "type": "Element"})
    confidence: Optional[float] = field(default=None, metadata={"name": "confidence", "type": "Element"})


"""
End time in seconds
"""
@dataclass(kw_only=True)
class VideoContent(AIContentBase):
    kind: str = field(default="video", metadata={"name": "kind", "type": "Element"})
    uri: Optional[str] = field(default=None, metadata={"name": "uri", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    width: Optional[int] = field(default=None, metadata={"name": "width", "type": "Attribute"})
    height: Optional[int] = field(default=None, metadata={"name": "height", "type": "Attribute"})
    duration: Optional[int] = field(default=None, metadata={"name": "duration", "type": "Attribute"})
    frame_rate: Optional[int] = field(default=None, metadata={"name": "frame-rate", "type": "Attribute"})


"""
Video height in pixels
"""
@dataclass(kw_only=True)
class FileContent(AIContentBase):
    kind: str = field(default="file", metadata={"name": "kind", "type": "Element"})
    uri: Optional[str] = field(default=None, metadata={"name": "uri", "type": "Attribute"})
    filename: Optional[str] = field(default=None, metadata={"name": "filename", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    size_bytes: Optional[int] = field(default=None, metadata={"name": "size-bytes", "type": "Attribute"})


"""
XML: <search-result title="..." url="..." score="0.94"><snippet>...</snippet></search-result>
"""
@dataclass(kw_only=True)
class SearchResultContent(AIContentBase):
    kind: str = field(default="searchResult", metadata={"name": "kind", "type": "Element"})
    title: str = field(metadata={"name": "title", "type": "Attribute"})
    url: str = field(metadata={"name": "url", "type": "Attribute"})
    score: Optional[float] = field(default=None, metadata={"name": "score", "type": "Attribute"})
    snippet: str = field(metadata={"name": "snippet", "type": "Element"})


"""
Snippet/summary
"""
@dataclass(kw_only=True)
class DocumentContent(AIContentBase):
    kind: str = field(default="document", metadata={"name": "kind", "type": "Element"})
    title: str = field(metadata={"name": "title", "type": "Attribute"})
    document_id: str = field(metadata={"name": "document-id", "type": "Attribute"})
    source: str = field(metadata={"name": "source", "type": "Attribute"})
    mime_type: Optional[str] = field(default=None, metadata={"name": "mime-type", "type": "Attribute"})
    content: Optional[str] = field(default=None, metadata={"name": "content", "type": "Element"})


"""
Document ID
"""
@dataclass(kw_only=True)
class Citation:
    source: str = field(metadata={"name": "source", "type": "Element"})
    text: Optional[str] = field(default=None, metadata={"name": "text", "type": "Element"})
    start: int = field(metadata={"name": "start", "type": "Element"})
    end: int = field(metadata={"name": "end", "type": "Element"})
    score: Optional[float] = field(default=None, metadata={"name": "score", "type": "Element"})


"""
End character index
"""
@dataclass(kw_only=True)
class AdaptiveCardContent(AIContentBase):
    kind: str = field(default="adaptiveCard", metadata={"name": "kind", "type": "Element"})
    version: Optional[str] = field(default=None, metadata={"name": "version", "type": "Attribute"})
    fallback_text: Optional[str] = field(default=None, metadata={"name": "fallback-text", "type": "Attribute"})
    card: str = field(metadata={"type": "Text"})


"""
Card version
"""
@dataclass(kw_only=True)
class RefusalContent(AIContentBase):
    kind: str = field(default="refusal", metadata={"name": "kind", "type": "Element"})
    reason: str = field(metadata={"name": "reason", "type": "Element"})


"""
Reason for refusal
"""
@dataclass(kw_only=True)
class ContentFilterResultContent(AIContentBase):
    kind: str = field(default="contentFilterResult", metadata={"name": "kind", "type": "Element"})
    filtered: bool = field(metadata={"name": "filtered", "type": "Element"})
    category: str = field(metadata={"name": "category", "type": "Element"})
    severity: str = field(metadata={"name": "severity", "type": "Element"})


"""
User Input Request Content
BASE: Concept exists in MAF (AgentResponse.UserInputRequests)
SOURCE: /agent-framework/dotnet/src/Microsoft.Agents.AI.Abstractions/AgentResponse.cs
REPRESENTS: Agent requesting input from user (HITL)
M365: Critical for human-in-the-loop workflows
"""
@dataclass(kw_only=True)
class UserInputRequestContent(AIContentBase):
    kind: str = field(default="userInputRequest", metadata={"name": "kind", "type": "Element"})
    request_id: str = field(metadata={"name": "request-id", "type": "Attribute"})
    prompt: str = field(metadata={"name": "prompt", "type": "Attribute"})
    input_type: Optional[str] = field(default=None, metadata={"name": "input-type", "type": "Attribute"})
    required: Optional[bool] = field(default=None, metadata={"name": "required", "type": "Attribute"})


"""
Whether input is required
"""
@dataclass(kw_only=True)
class SuggestedActionsContent(AIContentBase):
    kind: str = field(default="suggestedActions", metadata={"name": "kind", "type": "Element"})
    actions: list[SuggestedAction] = field(default_factory=list, metadata={"name": "action", "type": "Element"})


"""
XML: <suggested-actions><action title="Yes" type="message" value="yes" /></suggested-actions>
"""
@dataclass(kw_only=True)
class SuggestedAction:
    title: str = field(metadata={"name": "title", "type": "Attribute"})
    action_type: str = field(metadata={"name": "type", "type": "Attribute"})
    value: Optional[str] = field(default=None, metadata={"name": "value", "type": "Attribute"})
    text: Optional[str] = field(default=None, metadata={"name": "text", "type": "Attribute"})


"""
XML: <event name="..." timestamp="...">{value}</event>
"""
@dataclass(kw_only=True)
class EventContent(AIContentBase):
    kind: str = field(default="event", metadata={"name": "kind", "type": "Element"})
    name: str = field(metadata={"name": "name", "type": "Attribute"})
    timestamp: Optional[datetime] = field(default=None, metadata={"name": "timestamp", "type": "Attribute"})
    value: Optional[str] = field(default=None, metadata={"type": "Text"})


"""
Event payload (as text/JSON)
"""
@dataclass(kw_only=True)
class TraceContent(AIContentBase):
    kind: str = field(default="trace", metadata={"name": "kind", "type": "Element"})
    name: str = field(metadata={"name": "name", "type": "Attribute"})
    label: Optional[str] = field(default=None, metadata={"name": "label", "type": "Attribute"})
    severity: Optional[str] = field(default=None, metadata={"name": "severity", "type": "Attribute"})
    timestamp: Optional[datetime] = field(default=None, metadata={"name": "timestamp", "type": "Attribute"})
    value: Optional[str] = field(default=None, metadata={"type": "Text"})


"""
Trace data/payload (as text/JSON)
"""
@dataclass(kw_only=True)
class ActionContent(AIContentBase):
    kind: str = field(default="action", metadata={"name": "kind", "type": "Element"})
    name: str = field(metadata={"name": "name", "type": "Attribute"})
    text: Optional[str] = field(default=None, metadata={"name": "text", "type": "Attribute"})
    timestamp: Optional[datetime] = field(default=None, metadata={"name": "timestamp", "type": "Attribute"})
    value: Optional[str] = field(default=None, metadata={"type": "Text"})


@dataclass(kw_only=True)
class TypingIndicatorContent(AIContentBase):
    kind: str = field(default="typingIndicator", metadata={"name": "kind", "type": "Element"})
    from_: str = field(metadata={"name": "from", "type": "Element"})
    status: Literal["typing", "thinking", "processing"] = field(metadata={"name": "status", "type": "Element"})
    timestamp: Optional[datetime] = field(default=None, metadata={"name": "timestamp", "type": "Element"})


@dataclass(kw_only=True)
class MessageReactionContent(AIContentBase):
    kind: str = field(default="messageReaction", metadata={"name": "kind", "type": "Element"})
    referenced_message_id: str = field(metadata={"name": "referenced-message-id", "type": "Element"})
    reactions_added: Optional[list[MessageReaction]] = field(default=None, metadata={"name": "reactions-added", "type": "Element"})
    reactions_removed: Optional[list[MessageReaction]] = field(default=None, metadata={"name": "reactions-removed", "type": "Element"})


"""
Message ID being reacted to
"""
@dataclass(kw_only=True)
class MessageReaction:
    type: str = field(metadata={"name": "type", "type": "Element"})
    user_id: Optional[str] = field(default=None, metadata={"name": "user-id", "type": "Element"})
    timestamp: Optional[datetime] = field(default=None, metadata={"name": "timestamp", "type": "Element"})


"""
User who reacted (optional)
"""
@dataclass(kw_only=True)
class MessageDeleteContent(AIContentBase):
    kind: str = field(default="messageDelete", metadata={"name": "kind", "type": "Element"})
    message_id: str = field(metadata={"name": "message-id", "type": "Element"})
    reason: Optional[str] = field(default=None, metadata={"name": "reason", "type": "Element"})


"""
Message ID to delete
"""
@dataclass(kw_only=True)
class MessageUpdateContent(AIContentBase):
    kind: str = field(default="messageUpdate", metadata={"name": "kind", "type": "Element"})
    message_id: str = field(metadata={"name": "message-id", "type": "Element"})
    reason: Optional[str] = field(default=None, metadata={"name": "reason", "type": "Element"})


"""
Update reason/description (optional)
"""
@dataclass(kw_only=True)
class HostedFileContent(AIContentBase):
    kind: str = field(default="hostedFile", metadata={"name": "kind", "type": "Element"})
    """
    Provider's file identifier.
    EXAMPLES:
    - OpenAI: "file-abc123"
    - Azure: "https://storage.blob.core.windows.net/container/file.pdf"
    """
    file_id: str = field(metadata={"name": "file-id", "type": "Element"})
    """Original filename (optional)."""
    filename: Optional[str] = field(default=None, metadata={"name": "filename", "type": "Element"})
    """Media type (MIME type)."""
    media_type: Optional[str] = field(default=None, metadata={"name": "media-type", "type": "Element"})
    """File size in bytes (optional)."""
    size_bytes: Optional[int] = field(default=None, metadata={"name": "size-bytes", "type": "Element"})


"""
Hosted Vector Store Content
@usage
Rationale:
- Provider-hosted vector stores (e.g., OpenAI Assistants vector stores)
- RAG (Retrieval-Augmented Generation) with provider-managed embeddings
- Efficient reference without transferring embeddings in messages
EXAMPLES:
- OpenAI: vs_abc123 (created via vector stores API)
- Azure: Reference to Azure AI Search index
M365: Supports BYOM (Bring Your Own Memory) pattern via vector store references
"""
@dataclass(kw_only=True)
class HostedVectorStoreContent(AIContentBase):
    kind: str = field(default="hostedVectorStore", metadata={"name": "kind", "type": "Element"})
    """
    Provider's vector store identifier.
    EXAMPLES:
    - OpenAI: "vs_abc123"
    - Azure: "https://search.azure.com/indexes/my-index"
    """
    vector_store_id: str = field(metadata={"name": "vector-store-id", "type": "Element"})
    """Vector store name (optional)."""
    name: Optional[str] = field(default=None, metadata={"name": "name", "type": "Element"})
    """Number of vectors/documents in store (optional)."""
    document_count: Optional[int] = field(default=None, metadata={"name": "document-count", "type": "Element"})


"""
Vector store name (optional).
"""
@dataclass(kw_only=True)
class AIAnnotation:
    type: str = field(metadata={"name": "type", "type": "Element"})
    data: Optional[dict[str, Any]] = field(default=None, metadata={"name": "data", "type": "Element"})


"""
Additional properties for extensibility.
NOT SERIALIZED: Client-side metadata, transient state.
EXAMPLES:
- Tracking IDs, correlation data
- Client-specific rendering hints
- Temporary computation results
"""
# Union of all content types that inherit from AIContentBase
AIContent = Union[
    TextContent,
    FunctionCallContent,
    FunctionResultContent,
    ErrorContent,
    TextReasoningContent,
    DataContent,
    UriContent,
    ImageContent,
    AudioContent,
    TranscriptContent,
    VideoContent,
    FileContent,
    HostedFileContent,
    HostedVectorStoreContent,
    SearchResultContent,
    DocumentContent,
    AdaptiveCardContent,
    TypingIndicatorContent,
    MessageReactionContent,
    MessageDeleteContent,
    MessageUpdateContent,
    SuggestedActionsContent,
    ActionContent,
    UserInputRequestContent,
    EventContent,
    TraceContent,
    RefusalContent,
    ContentFilterResultContent,
]

