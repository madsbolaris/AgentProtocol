/**
 * Type guard functions for Agent Protocol types
 */

import type {
  AIContent,
  TextContent,
  ImageContent,
  AudioContent,
  VideoContent,
  FileContent,
  FunctionCallContent,
  FunctionResultContent,
} from '../generated/content';

import type {
  ChatMessage,
  UserMessage,
  AgentMessage,
  ToolMessage,
  SystemMessage,
} from '../generated/messages';

/**
 * Type guard for TextContent
 */
export function isTextContent(content: AIContent): content is TextContent {
  return content.kind === 'text';
}

/**
 * Type guard for ImageContent
 */
export function isImageContent(content: AIContent): content is ImageContent {
  return content.kind === 'image';
}

/**
 * Type guard for AudioContent
 */
export function isAudioContent(content: AIContent): content is AudioContent {
  return content.kind === 'audio';
}

/**
 * Type guard for VideoContent
 */
export function isVideoContent(content: AIContent): content is VideoContent {
  return content.kind === 'video';
}

/**
 * Type guard for FileContent
 */
export function isFileContent(content: AIContent): content is FileContent {
  return content.kind === 'file';
}

/**
 * Type guard for FunctionCallContent
 */
export function isFunctionCallContent(content: AIContent): content is FunctionCallContent {
  return content.kind === 'functionCall';
}

/**
 * Type guard for FunctionResultContent
 */
export function isFunctionResultContent(content: AIContent): content is FunctionResultContent {
  return content.kind === 'functionResult';
}

/**
 * Type guard for UserMessage
 */
export function isUserMessage(message: ChatMessage): message is UserMessage {
  return message.role === 'user';
}

/**
 * Type guard for AgentMessage
 */
export function isAgentMessage(message: ChatMessage): message is AgentMessage {
  return message.role === 'agent';
}

/**
 * Type guard for ToolMessage
 */
export function isToolMessage(message: ChatMessage): message is ToolMessage {
  return message.role === 'tool';
}

/**
 * Type guard for SystemMessage
 */
export function isSystemMessage(message: ChatMessage): message is SystemMessage {
  return message.role === 'system';
}
