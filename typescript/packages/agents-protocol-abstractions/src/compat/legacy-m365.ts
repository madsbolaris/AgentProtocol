/**
 * Legacy M365 Agents SDK Compatibility Layer
 *
 * This module provides backwards-compatible exports for legacy M365 SDK samples.
 */

// Activity Types enum (legacy)
export enum ActivityTypes {
  Message = 'message',
  ConversationUpdate = 'conversationUpdate',
  ContactRelationUpdate = 'contactRelationUpdate',
  Typing = 'typing',
  EndOfConversation = 'endOfConversation',
  Event = 'event',
  Invoke = 'invoke',
  DeleteUserData = 'deleteUserData',
  MessageUpdate = 'messageUpdate',
  MessageDelete = 'messageDelete',
  InstallationUpdate = 'installationUpdate',
  MessageReaction = 'messageReaction',
  Suggestion = 'suggestion',
  Trace = 'trace',
  Handoff = 'handoff'
}
