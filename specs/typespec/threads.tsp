/**
 * Thread Models
 *
 * This file defines the core thread (conversation) primitives.
 *
 * MOVED FROM: execution.tsp
 * RATIONALE: Separate concerns - threads are conversation-centric, not execution-centric
 *
 * BASE: Microsoft Agent Framework (MAF) AgentSession
 * FROM: Azure Agent API (Thread resource)
 *
 * REPRESENTS: Single conversation thread with participants, messages, and lifecycle
 *
 * M365 REQUIREMENTS:
 * - Maps to Conversation in Conversation Store
 * - Supports multi-turn conversations, group chats, and channel-based routing
 * - Tracks conversation lifecycle (active, closed, archived)
 * - Enables proactive messaging (webhooks, polling, SSE)
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./messages.tsp";
import "./xml-decorators.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using AgentXml.Decorators;

namespace Microsoft.Agents.AI;

/**
 * Thread Status Enum
 *
 * RATIONALE: Type-safe status values for thread lifecycle
 *
 * ALIGNED WITH: Messaging app conversation states
 * - active: Thread is ongoing (like WhatsApp/Teams active chat)
 * - closed: Thread is completed but archived (like closed ticket)
 * - archived: Thread is hidden from active view (like archived email)
 */
enum ThreadStatus {
  /** Thread is active and ongoing */
  active,

  /** Thread is closed but accessible */
  closed,

  /** Thread is archived and hidden from default views */
  archived,
}

/**
 * Thread Cleanup Strategy
 *
 * @usage
 *
 * Use Cases:
 * - keep: Chat conversations, multi-turn interactions
 * - delete: Extraction tasks, one-shot queries, stateless APIs
 *
 */
enum ThreadCleanup {
  /** Preserve thread after run completes (default for stateful runs) */
  keep,

  /** Auto-delete thread after run completes (for ephemeral runs) */
  delete,
}

/**
 * Thread - Conversation
 *
 * BASE: MAF AgentSession (represents single conversation)
 * FROM: Azure Agent API (Thread resource)
 *
 * REPRESENTS: Single conversation thread
 *
 * M365 REQUIREMENT: Maps to Conversation in Conversation Store
 *
 * MESSAGING APP PATTERN:
 * - Thread = single conversation (like SMS thread, Slack channel, Teams chat)
 * - Has participants, messages, metadata
 *
 * @usage
 * Core conversation model representing a persistent message thread.
 * Manages conversation lifecycle, participants, messages, and metadata.
 * Supports multi-turn conversations, group chats, and channel-based routing.
 *
 * Key Capabilities:
 * - Persistent message history with participants
 * - Lifecycle management (active, closed, archived)
 * - Multi-channel support via channelInfo
 * - Unread count tracking for notifications
 * - Proactive messaging support (webhooks, polling, SSE)
 *
 * Conversation Patterns:
 * - 1:1 conversations (2 participants)
 * - Group chats (multiple participants)
 * - Channel-based routing (Teams, Slack, etc.)
 * - Cross-channel conversations (same thread, multiple channels)
 *
 * M365 Integration:
 * - Maps to Conversation in Conversation Store
 * - Links to Agent Journal for cross-conversation memory
 * - Supports Teams/Outlook participant mapping
 *
 * @example 1:1 conversation thread
 * ```json
 * {
 *   "threadId": "thread_123",
 *   "status": "active",
 *   "participants": [
 *     { "userId": "user_001", "role": "user" },
 *     { "agentId": "agent_001", "role": "assistant" }
 *   ],
 *   "messages": [
 *     {
 *       "messageId": "msg_001",
 *       "role": "user",
 *       "contents": [{ "kind": "text", "text": "Hello!" }],
 *       "createdAt": "2026-02-07T10:00:00Z"
 *     }
 *   ],
 *   "createdAt": "2026-02-07T10:00:00Z",
 *   "lastActivityAt": "2026-02-07T10:00:00Z",
 *   "unreadCount": 0
 * }
 * ```
 *
 * @example Group chat thread
 * ```json
 * {
 *   "threadId": "thread_456",
 *   "status": "active",
 *   "participants": [
 *     { "userId": "user_001", "role": "user" },
 *     { "userId": "user_002", "role": "user" },
 *     { "agentId": "agent_001", "role": "assistant" }
 *   ],
 *   "messages": [],
 *   "metadata": {
 *     "topic": "Project Planning",
 *     "department": "Engineering"
 *   },
 *   "createdAt": "2026-02-07T10:00:00Z"
 * }
 * ```
 *
 * @example Multi-channel thread
 * ```json
 * {
 *   "threadId": "thread_789",
 *   "status": "active",
 *   "channelInfo": {
 *     "channelId": "teams",
 *     "channelConversationId": "19:abc123@thread.skype"
 *   },
 *   "participants": [
 *     { "userId": "user_001", "role": "user" },
 *     { "agentId": "agent_001", "role": "assistant" }
 *   ],
 *   "messages": [],
 *   "createdAt": "2026-02-07T10:00:00Z"
 * }
 * ```
 *
 * @example XML Output with thread wrapper
 * ```xml
 * <thread thread-id="thread_123" status="active" created-at="2026-02-07T10:00:00Z">
 *   <user message-id="msg_001" user-id="user_001" created-at="2026-02-07T10:00:00Z">
 *     <text>Hello!</text>
 *   </user>
 *   <agent message-id="msg_002" agent-id="agent_001" created-at="2026-02-07T10:00:01Z">
 *     <text>Hi there!</text>
 *   </agent>
 * </thread>
 * ```
 */
@resource("threads")
@xmlRoot("thread")
model Thread {
  /**
   * Unique thread identifier.
   * FROM: Azure Agent API
   * GENERATED: Server-generated GUID
   *
   * M365: Maps to Conversation Key in Conversation Store
   */
  @key
  @xmlAttribute("thread-id")
  threadId: string;

  /**
   * Thread lifecycle status.
   * FROM: Activity Protocol (EndOfConversation, ConversationUpdate patterns)
   * ADDITION: Not in Azure Agent API
   *
   * RATIONALE: Track conversation lifecycle (active, closed, archived)
   *
   * STATES:
   * - active: Thread is active and accepting messages (default)
   * - closed: Conversation ended but retained for history
   * - archived: Thread archived and not accepting new messages
   *
   * MESSAGING APP PATTERN:
   * - Like Teams marking a chat as "closed" or "archived"
   * - Like Slack archiving a channel
   * - Like email conversation being "closed"
   *
   * ACTIVITY PROTOCOL MAPPING:
   * - EndOfConversation activity → Thread.status = "closed"
   * - ConversationUpdate with end reason → Thread.status = "closed"
   */
  @xmlAttribute
  status?: ThreadStatus = ThreadStatus.active;

  /**
 * Channel information for multi-channel routing.
 *
 * @usage
 *
 * Use Cases:
 * - Route responses to correct channel
 * - Store channel-specific conversation IDs for correlation
 * - Enable channel-specific features (Teams adaptive cards, Slack blocks, etc.)
 * - Track which platform the conversation originated from
 *
 * NOT SERIALIZED: Used for API routing only
 */
  @xmlIgnore
  channelInfo?: ChannelInfo;

  /**
   * Participants in this thread.
   * ADDITION: Not in Azure Agent API
   *
   * RATIONALE: Critical for group conversations
   *
   * MESSAGING APP REQUIREMENT:
   * - Every conversation has participants
   * - Enables: 1:1, group chats, channels
   * - Supports adding/removing participants
   *
   * M365: Maps to conversation participants in Teams/Outlook
   *
   * NOT SERIALIZED: Participant info included in individual messages
   */
  @xmlIgnore
  participants: Participant[];

  /**
   * Messages in this thread.
   * FROM: Azure Agent API (Thread.messages)
   *
   * M365: Stored in Conversation Store as Canonical Events
   *
   * XML: Direct children of <thread>, serialized as role-specific elements
   */
  messages: ChatMessage[];

  /**
   * Custom metadata for the thread.
   * FROM: Azure Agent API
   *
   * M365: Can store conversation metadata (topic, participants, etc.)
   *
   * NOT SERIALIZED: Used for API metadata only
   */
  @xmlIgnore
  metadata?: Record<unknown>;

  /**
   * Timestamp when thread was created.
   */
  @xmlAttribute("created-at")
  createdAt: utcDateTime;

  /**
   * Timestamp of last message.
   */
  @xmlAttribute("last-message-at")
  lastMessageAt?: utcDateTime;

  /**
   * Timestamp of last activity (message, event, or status change).
   * ADDITION: For proactive messaging Phase 2 (polling support)
   *
   * RATIONALE: Enables polling pattern for clients without webhook capability
   * - Updated when: new message, new event, status change, participant change
   * - Allows: GET /threads?updatedSince={timestamp} for polling
   *
   * PROACTIVE MESSAGING SUPPORT:
   * - Phase 1 (Webhooks): POST notification to subscriber webhook URL
   * - Phase 2 (Polling): Client polls GET /threads?updatedSince={lastActivityAt}
   * - Phase 3 (SSE): Real-time push via GET /threads/{threadId}/events (SSE stream)
   *
   * PATTERN: Like GitHub's "updated_at" field for issue polling
   */
  @xmlAttribute("last-activity-at")
  lastActivityAt?: utcDateTime;

  /**
   * Number of unread messages/events for subscribed clients.
   * ADDITION: For proactive messaging Phase 2 (polling support)
   *
   * RATIONALE: Enables notification badge counts
   * - Incremented on: new message, new event (role="channel" excluded by client preference)
   * - Reset by: Client marks thread as read via POST /threads/{threadId}/read
   *
   * PATTERN: Like messaging app unread counts (Teams, Slack, WhatsApp)
   */
  @xmlAttribute("unread-count")
  unreadCount?: int32 = 0;
}

/**
 * Thread Copy Request
 *
 * @usage
 *
 * Use Cases:
 * - "Try this approach instead" → Copy thread, continue with different strategy
 * - Testing agents: Same input conversation, multiple agent configurations
 * - Template threads: Copy starter thread for new conversations
 * - Conversation variations: Explore what-if scenarios
 *
 */
model ThreadCopyRequest {
  /**
 * Whether to include full message history in copied thread.
 *
 * @usage
 *
 * Use Cases:
 * - true: Branch from specific conversation point (A/B testing, variations)
 * - false: Reuse thread template/structure without history
 *
 */
  includeHistory?: boolean = true;

  /**
   * Metadata for the new copied thread.
   * OPTIONAL: Override or add metadata to distinguish copy from original
   *
   * COMMON FIELDS:
   * - original_thread_id: Reference to source thread
   * - copy_reason: Why this thread was copied
   * - variant_name: For A/B testing variants
   *
   * MERGE BEHAVIOR:
   * - Merges with original thread metadata
   * - New values override original values for same keys
   */
  metadata?: Record<unknown>;
}

/**
 * Channel Information
 *
 * @usage
 *
 * Use Cases:
 * - Teams Integration: channelId="msteams", externalConversationId="19:meeting@thread.v2"
 * - Slack Integration: channelId="slack", externalConversationId="C123456", workspaceId="T123456"
 * - Discord Integration: channelId="discord", externalConversationId="123456789012345678"
 * - Web Chat: channelId="webchat" (no external ID needed)
 *
 */
model ChannelInfo {
  /**
   * Channel identifier (platform type).
   *
   * STANDARD VALUES:
   * - "msteams": Microsoft Teams
   * - "slack": Slack
   * - "discord": Discord
   * - "webchat": Web chat widget
   * - "sms": SMS/text messaging
   * - "email": Email
   * - "whatsapp": WhatsApp
   * - "directline": Bot Framework Direct Line
   * - "custom": Custom channel integration
   *
   * PATTERN: Like Bot Framework Activity.channelId
   */
  channelId: string;

  /**
   * External conversation ID from the channel.
   * OPTIONAL: Channel's native conversation/thread identifier
   *
   * EXAMPLES:
   * - Teams: "19:meeting_abc@thread.v2" (conversation ID)
   * - Slack: "C123456" (channel ID)
   * - Discord: "123456789012345678" (channel ID)
   *
   * PURPOSE: Correlation and bidirectional sync
   */
  externalConversationId?: string;

  /**
   * External tenant/workspace/server ID.
   * OPTIONAL: Multi-tenant or workspace-scoped channels
   *
   * EXAMPLES:
   * - Teams: Tenant ID (Entra tenant)
   * - Slack: "T123456" (workspace ID)
   * - Discord: Server ID
   *
   * PURPOSE: Isolate conversations by tenant/workspace
   */
  externalTenantId?: string;

  /**
   * Channel-specific service URL.
   * OPTIONAL: Base URL for channel-specific APIs
   *
   * EXAMPLES:
   * - Teams: "https://smba.trafficmanager.net/amer/" (Bot Framework service URL)
   * - Slack: "https://slack.com/api" (Slack API URL)
   *
   * PURPOSE: Dynamic routing for different channel regions/deployments
   */
  serviceUrl?: string;

  /**
   * Channel-specific metadata.
   * FLEXIBLE: Additional channel-specific context
   *
   * EXAMPLES:
   * - Teams: { "meetingId": "...", "channelId": "..." }
   * - Slack: { "teamName": "...", "channelName": "..." }
   * - Discord: { "guildName": "...", "channelName": "..." }
   */
  metadata?: Record<unknown>;
}

/**
 * Thread Watch - Agent Participation Tracking
 *
 * @usage
 *
 * Use Cases:
 * - Support agents: Watch support threads for user messages
 * - Monitoring agents: Watch threads for specific content types
 * - Multi-agent: Multiple agents watching same thread with different conditions
 *
 */
model ThreadWatch {
  /**
   * Unique watch identifier.
   * GENERATED: Server-generated GUID
   */
  @key
  watchId: string;

  /**
   * Thread being watched.
   * REQUIRED: Must be valid threadId
   */
  threadId: string;

  /**
   * Agent watching the thread.
   * REQUIRED: Must be valid agentId with autoResponse configuration
   *
   * VALIDATION:
   * - Agent must exist
   * - Agent must have AutoResponseConfig defined
   * - AutoResponseConfig.runCondition determines when agent participates
   */
  agentId: string;

  /**
   * Whether watch is currently active.
   * DEFAULT: true
   *
   * RATIONALE: Allows temporary disable without deletion
   * - false: Watch exists but agent doesn't evaluate for participation
   * - true: Agent actively watching and evaluating conditions
   */
  active?: boolean = true;

  /**
   * Timestamp when watch was created.
   */
  @visibility("read")
  createdAt: utcDateTime;

  /**
   * Timestamp of last activation (last time agent created run for this thread).
   * UPDATED: By server after each automatic run creation
   */
  @visibility("read")
  lastActivatedAt?: utcDateTime;

  /**
   * Number of runs created by this watch.
   * INCREMENTED: Each time agent automatically creates run
   *
   * RATIONALE: Analytics and monitoring
   */
  @visibility("read")
  activationCount?: int32 = 0;

  /**
   * Custom metadata for watch.
   * FLEXIBLE: Client can store correlation IDs, user info, etc.
   */
  metadata?: Record<unknown>;
}
