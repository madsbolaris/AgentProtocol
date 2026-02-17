/**
 * Client for Message operations
 */

import type { ChatMessage } from '@microsoft/agents-protocol-abstractions';
import { BaseClient } from './base-client';
import { RequestOptions, PaginationParams, ListResponse } from '../types';

export interface CreateMessageRequest {
  /** Message role */
  role: 'user' | 'system';

  /** Message content */
  content: string | Array<{ type: string; [key: string]: unknown }>;

  /** Metadata */
  metadata?: Record<string, unknown>;
}

export class MessagesClient extends BaseClient {
  /**
   * Create a message in a thread
   */
  async create(
    threadId: string,
    request: CreateMessageRequest,
    options?: RequestOptions
  ): Promise<ChatMessage> {
    return this.post<ChatMessage>(`/threads/${threadId}/messages`, request, options);
  }

  /**
   * Get a message by ID
   */
  async retrieve(
    threadId: string,
    messageId: string,
    options?: RequestOptions
  ): Promise<ChatMessage> {
    return super.get<ChatMessage>(`/threads/${threadId}/messages/${messageId}`, options);
  }

  /**
   * List messages in a thread
   */
  async list(
    threadId: string,
    params?: PaginationParams,
    options?: RequestOptions
  ): Promise<ListResponse<ChatMessage>> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.after) query.set('after', params.after);
    if (params?.before) query.set('before', params.before);

    const queryString = query.toString();
    return super.get<ListResponse<ChatMessage>>(
      `/threads/${threadId}/messages${queryString ? `?${queryString}` : ''}`,
      options
    );
  }

  /**
   * Update a message
   */
  async update(
    threadId: string,
    messageId: string,
    metadata: Record<string, unknown>,
    options?: RequestOptions
  ): Promise<ChatMessage> {
    return this.patch<ChatMessage>(
      `/threads/${threadId}/messages/${messageId}`,
      { metadata },
      options
    );
  }

  /**
   * Delete a message
   */
  async remove(
    threadId: string,
    messageId: string,
    options?: RequestOptions
  ): Promise<void> {
    return super.delete<void>(`/threads/${threadId}/messages/${messageId}`, options);
  }
}
