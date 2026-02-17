/**
 * Client for Thread (conversation) operations
 */

import type { Thread, ChatMessage } from '@microsoft/agents-protocol-abstractions';
import { BaseClient } from './base-client';
import { RequestOptions, PaginationParams, ListResponse } from '../types';

export interface CreateThreadRequest {
  /** Initial messages */
  messages?: ChatMessage[];

  /** Metadata */
  metadata?: Record<string, unknown>;
}

export interface UpdateThreadRequest {
  /** Updated metadata */
  metadata?: Record<string, unknown>;
}

export class ThreadsClient extends BaseClient {
  /**
   * Create a new thread
   */
  async create(request?: CreateThreadRequest, options?: RequestOptions): Promise<Thread> {
    return this.post<Thread>('/threads', request || {}, options);
  }

  /**
   * Get a thread by ID
   */
  async retrieve(threadId: string, options?: RequestOptions): Promise<Thread> {
    return super.get<Thread>(`/threads/${threadId}`, options);
  }

  /**
   * List threads
   */
  async list(
    params?: PaginationParams,
    options?: RequestOptions
  ): Promise<ListResponse<Thread>> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.after) query.set('after', params.after);
    if (params?.before) query.set('before', params.before);

    const queryString = query.toString();
    return super.get<ListResponse<Thread>>(
      `/threads${queryString ? `?${queryString}` : ''}`,
      options
    );
  }

  /**
   * Update a thread
   */
  async update(
    threadId: string,
    request: UpdateThreadRequest,
    options?: RequestOptions
  ): Promise<Thread> {
    return this.patch<Thread>(`/threads/${threadId}`, request, options);
  }

  /**
   * Delete a thread
   */
  async remove(threadId: string, options?: RequestOptions): Promise<void> {
    return super.delete<void>(`/threads/${threadId}`, options);
  }
}
