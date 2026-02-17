/**
 * Client for Agent operations
 * Handles agent discovery, registration, and inspection
 */

import type { AgentCard, AgentDefinition } from '@microsoft/agents-protocol-abstractions';
import { BaseClient } from './base-client';
import { RequestOptions, PaginationParams, ListResponse } from '../types';

/**
 * Validation result for agent configurations
 */
export interface ValidationResult {
  /** Whether the agent configuration is valid */
  valid: boolean;

  /** Array of validation errors */
  errors: Array<{
    field: string;
    message: string;
  }>;
}

/**
 * Client for managing agents
 */
export class AgentsClient extends BaseClient {
  /**
   * Gets agent card (discovery/registration metadata)
   * @param agentId Agent identifier
   * @param options Request options (signal, timeout, headers)
   * @returns The agent card with capabilities and tools
   */
  async getCard(agentId: string, options?: RequestOptions): Promise<AgentCard> {
    if (!agentId || agentId.trim() === '') {
      throw new Error('Agent ID cannot be null or empty');
    }

    return this.get<AgentCard>(`/agents/${agentId}/card`, options);
  }

  /**
   * Inspects ephemeral agent (capability discovery without persisting)
   * Useful for validating agent configuration before running
   * @param agent Agent definition to inspect
   * @param options Request options (signal, timeout, headers)
   * @returns Agent card with capabilities (agentId will be empty - not persisted)
   */
  async inspect(
    agent: AgentDefinition,
    options?: RequestOptions
  ): Promise<AgentCard> {
    if (!agent) {
      throw new Error('Agent definition cannot be null');
    }

    return this.post<AgentCard>('/agents/inspect', { agent }, options);
  }

  /**
   * Registers a new agent
   * @param agent Agent definition to register
   * @param options Request options (signal, timeout, headers)
   * @returns The registered agent card with generated agentId
   */
  async register(
    agent: AgentDefinition,
    options?: RequestOptions
  ): Promise<AgentCard> {
    if (!agent) {
      throw new Error('Agent definition cannot be null');
    }

    return this.post<AgentCard>('/agents', { agent }, options);
  }

  /**
   * Updates an existing agent configuration
   * @param agentId Agent identifier
   * @param updates Partial agent definition with fields to update
   * @param options Request options (signal, timeout, headers)
   * @returns The updated agent card
   */
  async update(
    agentId: string,
    updates: Partial<AgentDefinition>,
    options?: RequestOptions
  ): Promise<AgentCard> {
    if (!agentId || agentId.trim() === '') {
      throw new Error('Agent ID cannot be null or empty');
    }

    if (!updates) {
      throw new Error('Updates cannot be null');
    }

    return this.patch<AgentCard>(`/agents/${agentId}`, updates, options);
  }

  /**
   * Deletes an agent
   * @param agentId Agent identifier
   * @param options Request options (signal, timeout, headers)
   */
  async remove(agentId: string, options?: RequestOptions): Promise<void> {
    if (!agentId || agentId.trim() === '') {
      throw new Error('Agent ID cannot be null or empty');
    }

    return super.delete<void>(`/agents/${agentId}`, options);
  }

  /**
   * Lists all agents with pagination
   * @param params Pagination parameters (limit, after, before)
   * @param options Request options (signal, timeout, headers)
   * @returns Paginated list of agent cards
   */
  async list(
    params?: PaginationParams,
    options?: RequestOptions
  ): Promise<ListResponse<AgentCard>> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.after) query.set('after', params.after);
    if (params?.before) query.set('before', params.before);

    const queryString = query.toString();
    return this.get<ListResponse<AgentCard>>(
      `/agents${queryString ? `?${queryString}` : ''}`,
      options
    );
  }

  /**
   * Validates an agent configuration without registering it
   * @param agent Agent definition to validate
   * @param options Request options (signal, timeout, headers)
   * @returns Validation result with any errors found
   */
  async validate(
    agent: AgentDefinition,
    options?: RequestOptions
  ): Promise<ValidationResult> {
    if (!agent) {
      throw new Error('Agent definition cannot be null');
    }

    return this.post<ValidationResult>('/agents/validate', { agent }, options);
  }
}
