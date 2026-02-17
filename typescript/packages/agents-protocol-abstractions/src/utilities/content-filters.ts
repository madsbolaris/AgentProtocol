/**
 * Content filtering utilities for Agent Protocol types
 */

import type { AIContent } from '../generated/content';

/**
 * Filter content by audience visibility
 *
 * @param contents - Array of content items to filter
 * @param audience - Target audience ('user', 'agent', 'channel', 'all')
 * @returns Filtered content array
 *
 * @example
 * ```typescript
 * const userContent = filterContentByAudience(message.contents, 'user');
 * const agentContent = filterContentByAudience(message.contents, 'agent');
 * ```
 */
export function filterContentByAudience(
  contents: AIContent[],
  audience: 'user' | 'agent' | 'channel' | 'all'
): AIContent[] {
  return contents.filter(content => {
    // Content without audience is visible to all
    if (!('audience' in content) || !content.audience) {
      return true;
    }

    // Check if content is visible to the specified audience
    const contentAudience = content.audience as string | string[];

    if (Array.isArray(contentAudience)) {
      return contentAudience.includes(audience) || contentAudience.includes('all');
    }

    return contentAudience === audience || contentAudience === 'all';
  });
}

/**
 * Check if content has audience restrictions
 *
 * @param content - Content item to check
 * @returns True if content has audience restrictions
 */
export function hasAudienceRestriction(content: AIContent): boolean {
  return 'audience' in content && content.audience !== undefined && content.audience !== null;
}

/**
 * Get visible audiences for content
 *
 * @param content - Content item
 * @returns Array of audiences that can see this content
 */
export function getVisibleAudiences(content: AIContent): string[] {
  if (!hasAudienceRestriction(content)) {
    return ['all'];
  }

  const audience = (content as any).audience;

  if (Array.isArray(audience)) {
    return audience;
  }

  return [audience];
}
