/**
 * Client for Run (execution) operations
 */

import type {
  Run,
  ChatMessage,
  AITool,
} from '@microsoft/agents-protocol-abstractions';
import { BaseClient } from './base-client';
import { RequestOptions, PaginationParams, ListResponse } from '../types';

export interface CreateRunRequest {
  /** Agent ID to execute */
  agentId: string;

  /** Thread ID (optional for stateless) */
  threadId?: string;

  /** Input messages */
  input?: ChatMessage[];

  /** Additional instructions */
  instructions?: string;

  /** Tools to make available */
  tools?: AITool[];

  /** Metadata */
  metadata?: Record<string, unknown>;

  /** Thread cleanup strategy */
  threadCleanup?: 'keep' | 'delete';
}

export interface SubmitToolOutputsRequest {
  /** Tool call outputs */
  toolOutputs: Array<{
    toolCallId: string;
    output: string;
  }>;
}

export class RunsClient extends BaseClient {
  /**
   * Create a new run
   */
  async create(request: CreateRunRequest, options?: RequestOptions): Promise<Run> {
    return this.post<Run>('/runs', request, options);
  }

  /**
   * Create a run and wait for completion (blocking)
   */
  async createAndWait(
    request: CreateRunRequest,
    options?: RequestOptions
  ): Promise<Run> {
    return this.post<Run>('/runs/wait', request, {
      ...options,
      timeout: options?.timeout || 120000, // 2 minutes default
    });
  }

  /**
   * Get a run by ID
   */
  async retrieve(runId: string, options?: RequestOptions): Promise<Run> {
    return super.get<Run>(`/runs/${runId}`, options);
  }

  /**
   * List runs
   */
  async list(
    params?: PaginationParams & { threadId?: string; agentId?: string },
    options?: RequestOptions
  ): Promise<ListResponse<Run>> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.after) query.set('after', params.after);
    if (params?.before) query.set('before', params.before);
    if (params?.threadId) query.set('thread_id', params.threadId);
    if (params?.agentId) query.set('agent_id', params.agentId);

    const queryString = query.toString();
    return super.get<ListResponse<Run>>(
      `/runs${queryString ? `?${queryString}` : ''}`,
      options
    );
  }

  /**
   * Cancel a run
   */
  async cancel(runId: string, options?: RequestOptions): Promise<Run> {
    return this.post<Run>(`/runs/${runId}/cancel`, undefined, options);
  }

  /**
   * Submit tool outputs for a run
   */
  async submitToolOutputs(
    runId: string,
    request: SubmitToolOutputsRequest,
    options?: RequestOptions
  ): Promise<Run> {
    return this.post<Run>(`/runs/${runId}/submit_tool_outputs`, request, options);
  }
}
