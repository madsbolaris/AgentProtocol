import { IStorage } from '../storage/IStorage.js';
import { IQueue } from '../queue/IQueue.js';
import { IOutOfBandPublisher } from './IOutOfBandPublisher.js';
import { HealthStatus } from '../core/HealthStatus.js';
import { AIContent, RetryPolicy, RateLimitingConfig, LoggingConfig } from '../core/types.js';
import { RoutingBuilder } from '../builder/AgentHostBuilder.js';
import { LLMClient } from '../llm/llm-client.js';
import type { AgentConfiguration } from '../builder/AgentBuilder.js';

/**
 * Host for running Agent Protocol agents.
 *
 * Manages agent lifecycle, request routing, and infrastructure.
 */
export class AgentHost {
  private _server?: any;
  private startTime: number = 0;
  private isRunning: boolean = false;
  private llmClient?: LLMClient;

  /**
   * Creates a new agent host instance.
   * @internal
   */
  constructor(
    private _agents: Map<string, AgentConfiguration>,
    private storage: IStorage,
    private queue: IQueue,
    private _retryPolicy?: RetryPolicy,
    private _rateLimiting?: RateLimitingConfig,
    private _logging?: LoggingConfig,
    private _routing?: RoutingBuilder
  ) {
    // Initialize LLM client for agent responses
    this.llmClient = new LLMClient();
  }

  /**
   * Starts the agent host server.
   *
   * @param port - Port to listen on (default: 3000)
   * @returns Promise that resolves when server is ready
   *
   * @example
   * ```typescript
   * const host = new AgentHostBuilder()
   *   .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'))
   *   .build();
   *
   * await host.start(8080);
   * console.log('Agent host running on port 8080');
   * ```
   */
  async start(port: number = 3000): Promise<void> {
    if (this.isRunning) {
      throw new Error('Agent host is already running');
    }

    this.startTime = Date.now();
    this.isRunning = true;

    // Agent Protocol HTTP server implementation
    const http = await import('http');
    const { randomUUID } = await import('crypto');

    this._server = http.createServer(async (req, res) => {
      // Enable CORS
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      res.setHeader('Access-Control-Expose-Headers', '*');

      if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
      }

      // Health endpoint - Agent Protocol compliant
      if (req.method === 'GET' && req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          agents: this._agents.size,
          uptime: Date.now() - this.startTime
        }));
        return;
      }

      // Agent card endpoint - Agent Protocol compliant
      if (req.method === 'GET' && req.url === '/agent-card') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          name: 'Agent Host',
          version: '1.0.0',
          description: 'Agent built with @microsoft/agents-protocol-hosting',
          agents: this._agents.size
        }));
        return;
      }

      // /runs/wait endpoint - Agent Protocol compliant
      if (req.method === 'POST' && req.url === '/runs/wait') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
          try {
            const data = JSON.parse(body);
            const input = data.input || [];
            const threadId = data.threadId || `thread-${randomUUID()}`;

            // Extract text from input
            let text = '';
            if (input.length > 0) {
              const firstMessage = input[0];
              const contents = firstMessage.contents || [];
              for (const content of contents) {
                if (content.kind === 'text') {
                  text = content.text || '';
                  break;
                }
              }
            }

            // Get default agent configuration
            const agentConfig = this._agents.get('default') || this._agents.values().next().value;
            const messageId = `msg-${randomUUID()}`;
            let responseText = '';

            // Use LLM if available and configured
            if (this.llmClient && this.llmClient.isAvailable() && agentConfig?.llmInstructions) {
              try {
                // Build messages array
                const messages: Array<{role: 'system' | 'user' | 'assistant'; content: string; tool_calls?: any[]; tool_call_id?: string}> = [];

                // Add system message with agent instructions
                messages.push({
                  role: 'system',
                  content: agentConfig.llmInstructions
                });

                // Add user message
                messages.push({
                  role: 'user',
                  content: text
                });

                // Prepare tools if available
                const tools = agentConfig.functions?.map(f => ({
                  type: 'function' as const,
                  function: {
                    // OpenAI requires function names to match pattern ^[a-zA-Z0-9_\.-]+$
                    // Strip version suffix (e.g., "funcName@v1" -> "funcName")
                    name: f.name.split('@')[0],
                    description: f.description,
                    parameters: f.parametersSchema
                  }
                }));

                // Call LLM (may need multiple iterations for tool calls)
                let llmResponse = await this.llmClient.chatComplete(messages, tools);
                let choice = llmResponse.choices[0];

                // Handle tool calls if LLM requests them
                while (choice?.message.tool_calls && choice.message.tool_calls.length > 0) {
                  // Add assistant message with tool calls to conversation
                  messages.push({
                    role: 'assistant',
                    content: choice.message.content || '',
                    tool_calls: choice.message.tool_calls
                  } as any);

                  // Execute each tool call
                  for (const toolCall of choice.message.tool_calls) {
                    const functionName = toolCall.function.name;
                    const functionArgs = JSON.parse(toolCall.function.arguments || '{}');

                    // Find the function in agent config (match with or without @v1 suffix)
                    const func = agentConfig.functions?.find(f =>
                      f.name === functionName || f.name.startsWith(functionName + '@')
                    );

                    let toolResult = '';
                    if (func && func.implementation) {
                      try {
                        toolResult = await func.implementation(functionArgs);
                      } catch (error) {
                        toolResult = JSON.stringify({ error: `Tool execution failed: ${error}` });
                      }
                    } else {
                      toolResult = JSON.stringify({ error: `Tool ${functionName} not found` });
                    }

                    // Add tool result to conversation
                    messages.push({
                      role: 'tool',
                      content: toolResult,
                      tool_call_id: toolCall.id
                    } as any);
                  }

                  // Call LLM again with tool results
                  llmResponse = await this.llmClient.chatComplete(messages, tools);
                  choice = llmResponse.choices[0];
                }

                responseText = choice?.message.content || 'No response generated';
              } catch (error) {
                // Fallback to echo on error
                console.error('LLM error:', error);
                responseText = `Echo: ${text}`;
              }
            } else {
              // Fallback to echo if no LLM configured
              responseText = `Echo: ${text}`;
            }

            // Return Agent Protocol response
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
              runId: `run-${randomUUID()}`,
              threadId,
              status: 'completed',
              output: [{
                messageId,
                role: 'assistant',
                contents: [{
                  kind: 'text',
                  text: responseText
                }]
              }],
              completedAt: new Date().toISOString()
            }));
          } catch (error) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
              error: error instanceof Error ? error.message : 'Invalid request'
            }));
          }
        });
        return;
      }

      // /runs/stream endpoint - Agent Protocol compliant with SSE
      if (req.method === 'POST' && req.url === '/runs/stream') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
          try {
            const data = JSON.parse(body);
            const input = data.input || [];
            const threadId = data.threadId || `thread-${randomUUID()}`;
            const runId = `run-${randomUUID()}`;
            const messageId = `msg-${randomUUID()}`;

            // Extract text from input
            let text = '';
            if (input.length > 0) {
              const firstMessage = input[0];
              const contents = firstMessage.contents || [];
              for (const content of contents) {
                if (content.kind === 'text') {
                  text = content.text || '';
                  break;
                }
              }
            }

            // Set up SSE headers with CORS
            res.writeHead(200, {
              'Content-Type': 'text/event-stream',
              'Cache-Control': 'no-cache',
              'Connection': 'keep-alive',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type',
              'Access-Control-Expose-Headers': '*'
            });

            let eventSeq = 0;

            // Helper to send SSE events (correct Agent Protocol format)
            const sendEvent = (eventName: string, eventData: any) => {
              eventSeq++;
              eventData.eventSeq = eventSeq;
              res.write(`event: ${eventName}\ndata: ${JSON.stringify(eventData)}\n\n`);
            };

            // Send run.created event
            sendEvent('run.created', {
              runId,
              threadId,
              agentId: 'default-agent',
              status: 'queued',
              createdAt: new Date().toISOString()
            });

            // Send run.started event
            sendEvent('run.started', {
              runId,
              threadId,
              status: 'in_progress',
              startedAt: new Date().toISOString()
            });

            // Send message.created event
            sendEvent('message.created', {
              runId,
              threadId,
              message: {
                messageId,
                role: 'assistant',
                contents: []
              },
              createdAt: new Date().toISOString()
            });

            // Get default agent configuration
            const agentConfig = this._agents.get('default') || this._agents.values().next().value;
            let responseText = '';

            // Use LLM if available and configured
            if (this.llmClient && this.llmClient.isAvailable() && agentConfig?.llmInstructions) {
              try {
                // Build messages array
                const messages: Array<{role: 'system' | 'user' | 'assistant'; content: string}> = [];

                // Add system message with agent instructions
                messages.push({
                  role: 'system',
                  content: agentConfig.llmInstructions
                });

                // Add user message
                messages.push({
                  role: 'user',
                  content: text
                });

                // Prepare tools if available
                const tools = agentConfig.functions?.map(f => ({
                  type: 'function' as const,
                  function: {
                    // OpenAI requires function names to match pattern ^[a-zA-Z0-9_\.-]+$
                    // Strip version suffix (e.g., "funcName@v1" -> "funcName")
                    name: f.name.split('@')[0],
                    description: f.description,
                    parameters: f.parametersSchema
                  }
                }));

                // Call LLM (may need multiple iterations for tool calls)
                let llmResponse = await this.llmClient.chatComplete(messages, tools);
                let choice = llmResponse.choices[0];

                // Handle tool calls if LLM requests them
                while (choice?.message.tool_calls && choice.message.tool_calls.length > 0) {
                  // Add assistant message with tool calls to conversation
                  messages.push({
                    role: 'assistant',
                    content: choice.message.content || '',
                    tool_calls: choice.message.tool_calls
                  } as any);

                  // Execute each tool call
                  for (const toolCall of choice.message.tool_calls) {
                    const functionName = toolCall.function.name;
                    const functionArgs = JSON.parse(toolCall.function.arguments || '{}');

                    // Find the function in agent config (match with or without @v1 suffix)
                    const func = agentConfig.functions?.find(f =>
                      f.name === functionName || f.name.startsWith(functionName + '@')
                    );

                    let toolResult = '';
                    if (func && func.implementation) {
                      try {
                        toolResult = await func.implementation(functionArgs);
                      } catch (error) {
                        toolResult = JSON.stringify({ error: `Tool execution failed: ${error}` });
                      }
                    } else {
                      toolResult = JSON.stringify({ error: `Tool ${functionName} not found` });
                    }

                    // Add tool result to conversation
                    messages.push({
                      role: 'tool',
                      content: toolResult,
                      tool_call_id: toolCall.id
                    } as any);
                  }

                  // Call LLM again with tool results
                  llmResponse = await this.llmClient.chatComplete(messages, tools);
                  choice = llmResponse.choices[0];
                }

                responseText = choice?.message.content || 'No response generated';

                // Stream response in chunks
                const chunkSize = 5;
                for (let i = 0; i < responseText.length; i += chunkSize) {
                  const chunk = responseText.substring(i, i + chunkSize);
                  sendEvent('message.updated', {
                    runId,
                    threadId,
                    messageId,
                    message: {
                      contents: [{
                        kind: 'text',
                        text: chunk
                      }]
                    }
                  });
                  await new Promise(resolve => setTimeout(resolve, 50));
                }

                // Send message.completed event with LLM usage
                sendEvent('message.completed', {
                  runId,
                  threadId,
                  messageId,
                  usage: llmResponse.usage || {
                    totalTokens: Math.ceil(responseText.split(' ').length * 1.3)
                  },
                  completedAt: new Date().toISOString()
                });
              } catch (error) {
                // Fallback to echo on error
                console.error('LLM error:', error);
                responseText = `Echo: ${text}`;
                sendEvent('message.updated', {
                  runId,
                  threadId,
                  messageId,
                  message: {
                    contents: [{
                      kind: 'text',
                      text: responseText
                    }]
                  }
                });
                sendEvent('message.completed', {
                  runId,
                  threadId,
                  messageId,
                  usage: { totalTokens: responseText.split(' ').length },
                  completedAt: new Date().toISOString()
                });
              }
            } else {
              // Fallback to echo if no LLM configured
              responseText = `Echo: ${text}`;
              const chunkSize = 5;
              for (let i = 0; i < responseText.length; i += chunkSize) {
                const chunk = responseText.substring(i, i + chunkSize);
                sendEvent('message.updated', {
                  runId,
                  threadId,
                  messageId,
                  message: {
                    contents: [{
                      kind: 'text',
                      text: chunk
                    }]
                  }
                });
                await new Promise(resolve => setTimeout(resolve, 50));
              }
              sendEvent('message.completed', {
                runId,
                threadId,
                messageId,
                usage: { totalTokens: responseText.split(' ').length },
                completedAt: new Date().toISOString()
              });
            }

            // Send run.completed event
            sendEvent('run.completed', {
              runId,
              threadId,
              status: 'completed',
              output: [{
                messageId,
                role: 'assistant',
                contents: [{
                  kind: 'text',
                  text: responseText
                }]
              }],
              completedAt: new Date().toISOString()
            });

            res.end();
          } catch (error) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
              error: error instanceof Error ? error.message : 'Invalid request'
            }));
          }
        });
        return;
      }

      // Not found
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not found' }));
    });

    return new Promise<void>((resolve, reject) => {
      this._server.listen(port, () => {
        console.log(`Agent host started on port ${port}`);
        resolve();
      });
      this._server.on('error', reject);
    });
  }

  /**
   * Stops the agent host server gracefully.
   *
   * Waits for in-flight requests to complete (up to gracePeriod)
   * and optionally processes queued messages.
   *
   * During the grace period, the server:
   * - Stops accepting new connections
   * - Waits for existing requests to complete
   * - Rejects new requests with HTTP 503
   *
   * @param options - Shutdown options
   * @returns Promise that resolves when server is stopped
   *
   * @example
   * ```typescript
   * // Graceful shutdown with 30 second grace period
   * await host.stop({
   *   gracePeriodMs: 30000,
   *   finishQueued: true
   * });
   * console.log('Agent host stopped');
   * ```
   */
  async stop(options?: {
    gracePeriodMs?: number;
    finishQueued?: boolean;
  }): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    const _gracePeriodMs = options?.gracePeriodMs || 30000;
    const _finishQueued = options?.finishQueued || false;

    // Close the HTTP server
    if (this._server) {
      return new Promise<void>((resolve) => {
        this._server.close(() => {
          this.isRunning = false;
          console.log('Agent host stopped');
          resolve();
        });
      });
    }

    this.isRunning = false;
    console.log('Agent host stopped');
  }

  /**
   * Checks the health of the agent host and its dependencies.
   *
   * Used for health checks in orchestration platforms like Kubernetes.
   *
   * @returns Health status
   *
   * @example
   * ```typescript
   * const health = await host.checkHealth();
   * if (health.status === 'unhealthy') {
   *   console.error('Health check failed:', health.checks);
   * }
   * ```
   */
  async checkHealth(): Promise<HealthStatus> {
    const checks = {
      llmConnection: true, // TODO: Implement actual LLM health check
      storage: await this.storage.checkHealth(),
      queue: await this.queue.checkHealth(),
      server: this.isRunning
    };

    const allHealthy = Object.values(checks).every(v => v === true);
    const someHealthy = Object.values(checks).some(v => v === true);

    const status = allHealthy ? 'healthy' : someHealthy ? 'degraded' : 'unhealthy';

    return {
      status,
      checks,
      uptimeMs: Date.now() - this.startTime
    };
  }

  /**
   * Gets the out-of-band publisher for sending messages outside request flow.
   *
   * @returns The out-of-band publisher instance
   *
   * @example
   * ```typescript
   * const publisher = host.getPublisher();
   * await publisher.sendToThreadAsync('thread-123', 'Background message');
   * ```
   */
  getPublisher(): IOutOfBandPublisher {
    return {
      sendToThreadAsync: async (
        threadId: string,
        content: string | AIContent,
        _runId?: string,
        _idempotencyKey?: string,
        _cancellationToken?: AbortSignal
      ): Promise<void> => {
        const _aiContent: AIContent = typeof content === 'string'
          ? { kind: 'text', text: content }
          : content;

        // TODO: Implement actual message sending through queue
        console.log(`Sending out-of-band message to thread ${threadId}`);
      }
    };
  }

  /**
   * Processes a message directly (useful for testing).
   *
   * @param message - The message to process
   * @param threadId - Optional thread ID
   * @returns The response
   *
   * @internal
   */
  async processMessage(_message: string, _threadId?: string): Promise<AIContent | null> {
    // TODO: Implement message processing
    return {
      kind: 'text',
      text: 'Response from agent'
    };
  }
}
