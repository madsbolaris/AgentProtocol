/**
 * Type definitions for React UI components
 */

import type { ReactNode } from 'react';
import type { AIContent, ChatMessage } from '@microsoft/agents-protocol-abstractions';

export interface ThemeConfig {
  // Colors
  primaryColor?: string;
  secondaryColor?: string;
  userMessageBg?: string;
  agentMessageBg?: string;
  systemMessageBg?: string;
  backgroundColor?: string;
  textColor?: string;

  // Typography
  fontFamily?: string;
  fontSize?: {
    small?: string;
    medium?: string;
    large?: string;
  };

  // Spacing
  bubbleRadius?: string;
  bubblePadding?: string;
  messageSpacing?: string;

  // Avatars
  avatarSize?: string;
  avatarRadius?: string;

  // Animations
  streamingSpeed?: number;
  fadeInDuration?: number;

  // Dark mode
  darkMode?: boolean;
}

export interface ContentRendererProps<T extends AIContent = AIContent> {
  content: T;
  message: ChatMessage;
  isStreaming?: boolean;
  onAction?: (action: string, data: any) => void;
}

export type ContentRenderer = (props: ContentRendererProps) => ReactNode;

export interface ContentRenderers {
  [key: string]: ContentRenderer;
}

export interface MessageComponentProps {
  message: ChatMessage;
  showAvatar?: boolean;
  showTimestamp?: boolean;
  showReactions?: boolean;
  compactMode?: boolean;
  onReact?: (reaction: string) => void;
  onCopy?: () => void;
  onDelete?: () => void;
  renderAvatar?: (message: ChatMessage) => ReactNode;
  renderTimestamp?: (message: ChatMessage) => ReactNode;
}
