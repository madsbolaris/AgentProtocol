/**
 * High-level simplified client API for Agent Protocol
 * Provides easy-to-use methods for chat completion and streaming
 */

import type { ChatMessage, ChatRole } from '@microsoft/agents-protocol-abstractions';
import { AgentProtocolClient } from './client';
import type { AgentProtocolClientConfig } from './types';
import type { ChatOptions } from './chat-options';
import type { StreamEvent } from './stream-event';
import { createStreamEvent } from './stream-event';
import { Conversation, type IConversation } from './conversation';

/**
 * Request for creating a run
 */
export interface RunRequest {
  agentId?: string;
  threadId?: string;
  journalId?: string;
  input: ChatMessage[];
  metadata?: Record<string, unknown>;
  webhook?: string;
}

/**
 * Response from a run operation
 */
export interface RunResponse {
  runId: string;
  threadId: string;
  status: string;
  output?: ChatMessage[];
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * High-level client for Agent Protocol with simplified API
 */
export class SimplifiedClient {
  private readonly lowLevelClient: AgentProtocolClient;
  private readonly config: AgentProtocolClientConfig;

  /**
   * Creates a new simplified client
   * @param config Client configuration (baseUrl, authToken, etc.)
   */
  constructor(config: AgentProtocolClientConfig) {
    this.config = config;
    this.lowLevelClient = new AgentProtocolClient(config);
  }

  /**
   * Sends a message and returns the complete response as text (simple API)
   * @param message The message to send
   * @param options Optional chat options (agent ID, tools, metadata)
   * @param signal Optional abort signal for cancellation
   * @returns The agent's text response
   */
  async completeChat(
    message: string,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<string> {
    const request: RunRequest = {
      agentId: options?.agentId,
      input: [
        {
          role: 'user' as ChatRole,
          messageId: this.generateMessageId(),
          contents: [
            {
              kind: 'text',
              type: 'text',
              text: message,
            } as any,
          ],
        },
      ],
      metadata: options?.metadata,
    };

    // If tools are provided, handle tool execution
    if (options?.tools) {
      return await this.completeChatWithTools(request, options, signal);
    }

    const response = await this.createRunAndWait(request, signal);

    if (!response.output || response.output.length === 0) {
      return '';
    }

    // Extract text from first agent message
    const agentMessage = response.output.find((m) => m.role === 'agent');
    if (!agentMessage) {
      return '';
    }

    return this.extractText(agentMessage);
  }

  /**
   * Sends a structured message and returns the complete response
   * @param message The message to send (can include images, audio, etc.)
   * @param options Optional chat options
   * @param signal Optional abort signal for cancellation
   * @returns The agent's response message
   */
  async completeChatStructured(
    message: ChatMessage,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<ChatMessage> {
    const request: RunRequest = {
      agentId: options?.agentId,
      input: [message],
      metadata: options?.metadata,
    };

    const response = await this.createRunAndWait(request, signal);

    if (!response.output || response.output.length === 0) {
      return {
        role: 'agent' as ChatRole,
        messageId: this.generateMessageId(),
        contents: [],
      };
    }

    return (
      response.output.find((m) => m.role === 'agent') ?? {
        role: 'agent' as ChatRole,
        messageId: this.generateMessageId(),
        contents: [],
      }
    );
  }

  /**
   * Streams a message response with text chunks delivered via callback
   * @param message The message to send
   * @param onTextChunk Callback fired for each text chunk
   * @param options Optional chat options
   * @param signal Optional abort signal for cancellation
   */
  async streamChat(
    message: string,
    onTextChunk: (text: string) => void,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<void> {
    const request: RunRequest = {
      agentId: options?.agentId,
      input: [
        {
          role: 'user' as ChatRole,
          messageId: this.generateMessageId(),
          contents: [
            {
              kind: 'text',
              type: 'text',
              text: message,
            } as any,
          ],
        },
      ],
      metadata: options?.metadata,
    };

    let accumulatedText = '';

    for await (const event of this.streamRun(request, signal)) {
      // Handle different event types for text streaming
      if (event.eventType === 'message.delta' || event.eventType === 'message.updated') {
        const messageData = event.data as ChatMessage;
        if (messageData?.contents) {
          const textContent = messageData.contents.find(
            (c: any) => c.type === 'text'
          ) as any;

          if (textContent?.text) {
            // Calculate new text since last update
            const currentText = textContent.text;
            if (currentText.length > accumulatedText.length) {
              const newText = currentText.substring(accumulatedText.length);
              onTextChunk(newText);
              accumulatedText = currentText;
            }
          }
        }
      }
    }
  }

  /**
   * Creates a new conversation for maintaining state across multiple messages
   * @returns A conversation instance
   */
  createConversation(): IConversation {
    return new Conversation(
      this,
      undefined,
      this.config.enableLogging ?? false,
      this.config.logDirectory ?? 'logs/conversations'
    );
  }

  /**
   * Resumes an existing conversation using a thread ID
   * @param threadId The thread ID to resume
   * @returns A conversation instance
   */
  resumeConversation(threadId: string): IConversation {
    return new Conversation(
      this,
      threadId,
      this.config.enableLogging ?? false,
      this.config.logDirectory ?? 'logs/conversations'
    );
  }

  /**
   * Creates a run and waits for completion (internal method used by Conversation)
   * @internal
   */
  async createRunAndWait(request: RunRequest, signal?: AbortSignal): Promise<RunResponse> {
    const response = await this.lowLevelClient.runs.createAndWait(
      {
        agentId: request.agentId!,
        threadId: request.threadId,
        input: request.input,
        metadata: request.metadata,
      },
      {
        signal,
        timeout: 120000, // 2 minutes default
      }
    );

    return {
      runId: response.runId,
      threadId: response.threadId ?? '',
      status: response.status,
      output: response.output,
      error: response.error
        ? {
            code: response.error.code,
            message: response.error.message,
            details: response.error.details,
          }
        : undefined,
    };
  }

  /**
   * Streams a run and yields events (internal method used by Conversation)
   * @internal
   */
  async *streamRun(
    request: RunRequest,
    signal?: AbortSignal
  ): AsyncGenerator<StreamEvent, void, undefined> {
    // Create run via POST /runs
    const run = await this.lowLevelClient.runs.create(
      {
        agentId: request.agentId!,
        threadId: request.threadId,
        input: request.input,
        metadata: request.metadata,
      },
      { signal }
    );

    // Stream events via SSE
    const { SSEStream } = await import('./streaming');
    const baseUrl = (this.lowLevelClient as any).baseUrl;
    const authToken = (this.lowLevelClient as any).authToken;

    const stream = new SSEStream(`${baseUrl}/runs/${run.runId}/stream`, {
      authToken,
      autoReconnect: false,
    });

    // Convert SSE events to StreamEvent
    const eventQueue: StreamEvent[] = [];
    let streamComplete = false;
    let streamError: Error | null = null;

    stream.on('*', (event: any) => {
      const streamEvent = createStreamEvent(event.event, event);
      eventQueue.push(streamEvent);
    });

    stream.on('done', () => {
      streamComplete = true;
    });

    stream.on('error', (error: any) => {
      streamError = error;
      streamComplete = true;
    });

    // Handle abort signal
    const abortHandler = () => {
      stream.close();
      streamComplete = true;
    };
    signal?.addEventListener('abort', abortHandler);

    try {
      stream.connect();

      // Yield events as they arrive
      while (!streamComplete || eventQueue.length > 0) {
        if (signal?.aborted) {
          throw new Error('Stream aborted');
        }

        if (eventQueue.length > 0) {
          yield eventQueue.shift()!;
        } else if (!streamComplete) {
          // Wait a bit before checking again
          await new Promise((resolve) => setTimeout(resolve, 10));
        }
      }

      if (streamError) {
        throw streamError;
      }
    } finally {
      signal?.removeEventListener('abort', abortHandler);
      stream.close();
    }
  }

  /**
   * Handles tool execution automatically during streaming
   */
  private async completeChatWithTools(
    request: RunRequest,
    options: ChatOptions,
    signal?: AbortSignal
  ): Promise<string> {
    let resultText = '';

    for await (const event of this.streamRun(request, signal)) {
      if (event.eventType === 'message.delta' || event.eventType === 'message.updated') {
        const messageData = event.data as ChatMessage;
        if (messageData?.contents) {
          const textContent = messageData.contents.find(
            (c: any) => c.kind === 'text'
          ) as any;

          if (textContent?.text) {
            resultText = textContent.text;
          }
        }
      } else if (event.eventType === 'run.requires_action') {
        // TODO: Handle tool execution
        // Extract tool calls from the event
        // Execute tools using options.tools
        // Submit tool outputs back to the run
        const runData = event.data as any;
        if (runData && options.tools) {
          // This requires protocol-level support for submitting tool outputs
          // For now, tools need to be handled at a lower level
          console.warn('Tool execution during streaming not yet fully implemented');
        }
      }
    }

    return resultText;
  }

  /**
   * Extracts text content from a message
   */
  private extractText(message: ChatMessage): string {
    if (!message.contents || message.contents.length === 0) {
      return '';
    }

    const textContent = message.contents.find(
      (c: any) => c.kind === 'text'
    ) as any;

    return textContent?.text ?? '';
  }

  /**
   * Generates a unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Gets the underlying low-level client for advanced operations
   * @returns The low-level AgentProtocolClient instance
   */
  get client(): AgentProtocolClient {
    return this.lowLevelClient;
  }
}
