/**
 * Main Agent Protocol Client
 */

import { AgentProtocolClientConfig } from '../types';
import { BaseClient } from './base-client';
import { RunsClient } from './runs-client';
import { ThreadsClient } from './threads-client';
import { MessagesClient } from './messages-client';
import { AgentsClient } from './agents-client';

export class AgentProtocolClient extends BaseClient {
  /** Agents operations */
  public readonly agents: AgentsClient;

  /** Runs (executions) operations */
  public readonly runs: RunsClient;

  /** Threads (conversations) operations */
  public readonly threads: ThreadsClient;

  /** Messages operations */
  public readonly messages: MessagesClient;

  constructor(config: AgentProtocolClientConfig) {
    super(config);

    // Initialize resource clients
    this.agents = new AgentsClient(config);
    this.runs = new RunsClient(config);
    this.threads = new ThreadsClient(config);
    this.messages = new MessagesClient(config);
  }
}

export * from './base-client';
export * from './agents-client';
export * from './runs-client';
export * from './threads-client';
export * from './messages-client';
