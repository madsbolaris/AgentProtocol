/**
 * Conversation interface and implementation for stateful multi-turn chats
 */

import type { ChatMessage, ChatRole } from '@microsoft/agents-protocol-abstractions';
import type { SimplifiedClient } from './simplified-client';
import type { StreamEvent } from './stream-event';
import { MessageSerializer } from '@microsoft/agents-xml';

/**
 * Represents a conversation with state maintained across multiple messages
 */
export interface IConversation {
  /**
   * Gets the thread ID for this conversation (null until first message sent)
   */
  readonly threadId?: string;

  /**
   * Gets all messages in this conversation (cached locally).
   * Messages are automatically added as the conversation progresses.
   */
  readonly messages: ChatMessage[];

  /**
   * Sends a message and returns the complete response as text
   * @param message The message to send
   * @param signal Optional abort signal for cancellation
   * @returns The agent's text response
   */
  send(message: string, signal?: AbortSignal): Promise<string>;

  /**
   * Sends a structured message and returns the complete response
   * @param message The message to send
   * @param signal Optional abort signal for cancellation
   * @returns The agent's response message
   */
  sendStructured(message: ChatMessage, signal?: AbortSignal): Promise<ChatMessage>;

  /**
   * Streams message responses as structured messages
   * @param message The message to send
   * @param signal Optional abort signal for cancellation
   * @returns Async generator of messages
   */
  streamMessages(
    message: string,
    signal?: AbortSignal
  ): AsyncGenerator<ChatMessage, void, undefined>;

  /**
   * Streams raw events from the conversation
   * @param message The message to send
   * @param signal Optional abort signal for cancellation
   * @returns Async generator of stream events
   */
  streamEvents(
    message: string,
    signal?: AbortSignal
  ): AsyncGenerator<StreamEvent, void, undefined>;

  /**
   * Gets all messages from this conversation's thread.
   *
   * This is a convenience method that retrieves the full message history
   * for this conversation's thread. It delegates to the client's threads API.
   *
   * @param options - Optional parameters for message retrieval
   * @param options.limit - Maximum number of messages to return
   * @param options.after - Return messages after this message ID
   * @returns Promise resolving to array of ChatMessage objects in chronological order
   * @throws {Error} If thread ID is not available. Send a message first to create a thread.
   *
   * @example
   * ```typescript
   * const conversation = client.createConversation();
   * await conversation.send("Hello");
   * const messages = await conversation.getMessages();
   * console.log(`Found ${messages.length} messages`);
   * ```
   *
   * @remarks
   * This method requires an active thread. If you haven't sent any messages yet,
   * call send() first to create the thread.
   */
  getMessages(options?: {
    limit?: number;
    after?: string;
  }): Promise<ChatMessage[]>;
}

/**
 * Internal implementation of IConversation
 */
export class Conversation implements IConversation {
  private _threadId?: string;
  private _messages: ChatMessage[] = [];
  private readonly _enableLogging: boolean;
  private readonly _logDirectory: string;

  constructor(
    private readonly client: SimplifiedClient,
    threadId?: string,
    enableLogging: boolean = false,
    logDirectory: string = 'logs/conversations'
  ) {
    this._threadId = threadId;
    this._enableLogging = enableLogging;
    this._logDirectory = logDirectory;
  }

  get threadId(): string | undefined {
    return this._threadId;
  }

  get messages(): ChatMessage[] {
    return [...this._messages];
  }

  /**
   * Sends a text message and returns the agent's text response
   */
  async send(message: string, signal?: AbortSignal): Promise<string> {
    const userMessage: ChatMessage = {
      role: 'user' as ChatRole,
      messageId: this.generateMessageId(),
      contents: [
        {
          kind: 'text',
          type: 'text',
          text: message,
        } as any,
      ],
    };

    const request = {
      threadId: this._threadId,
      input: [userMessage],
    };

    // Use internal client method to create run
    const response = await this.client.createRunAndWait(request, signal);

    // Update thread ID if this was the first message
    if (!this._threadId && response.threadId) {
      this._threadId = response.threadId;
    }

    // Add user message to cache
    this._messages.push(userMessage);

    // Add agent response to cache
    if (response.output && response.output.length > 0) {
      for (const msg of response.output) {
        this._messages.push(msg);
      }
    }

    // Auto-save if logging is enabled
    this.autoSaveConversation();

    // Extract text from agent response
    if (!response.output || response.output.length === 0) {
      return '';
    }

    const agentMessage = response.output.find((m) => m.role === 'agent');
    if (!agentMessage) {
      return '';
    }

    return this.extractText(agentMessage);
  }

  /**
   * Sends a structured message and returns the agent's structured response
   */
  async sendStructured(
    message: ChatMessage,
    signal?: AbortSignal
  ): Promise<ChatMessage> {
    const request = {
      threadId: this._threadId,
      input: [message],
    };

    const response = await this.client.createRunAndWait(request, signal);

    // Update thread ID if this was the first message
    if (!this._threadId && response.threadId) {
      this._threadId = response.threadId;
    }

    // Add user message to cache
    this._messages.push(message);

    // Add agent response to cache
    if (response.output && response.output.length > 0) {
      for (const msg of response.output) {
        this._messages.push(msg);
      }
    }

    // Auto-save if logging is enabled
    this.autoSaveConversation();

    // Return first agent message
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
   * Streams messages from the agent
   */
  async *streamMessages(
    message: string,
    signal?: AbortSignal
  ): AsyncGenerator<ChatMessage, void, undefined> {
    const userMessage: ChatMessage = {
      role: 'user' as ChatRole,
      messageId: this.generateMessageId(),
      contents: [
        {
          kind: 'text',
          type: 'text',
          text: message,
        } as any,
      ],
    };

    const request = {
      threadId: this._threadId,
      input: [userMessage],
    };

    // Track messages by ID
    const messageMap = new Map<string, ChatMessage>();

    // Stream events from client
    for await (const event of this.client.streamRun(request, signal)) {
      // Update thread ID from first event
      if (!this._threadId && event.eventType === 'run.started') {
        const runData = event.data as any;
        if (runData?.threadId) {
          this._threadId = runData.threadId;
        }
      }

      // Handle message events
      if (event.eventType === 'message.created') {
        const messageData = event.data as ChatMessage;
        if (messageData?.messageId) {
          messageMap.set(messageData.messageId, messageData);
          yield messageData;
        }
      } else if (
        event.eventType === 'message.updated' ||
        event.eventType === 'message.delta'
      ) {
        const messageData = event.data as ChatMessage;
        if (messageData?.messageId) {
          messageMap.set(messageData.messageId, messageData);
          yield messageData;
        }
      }
    }
  }

  /**
   * Streams raw events from the agent
   */
  async *streamEvents(
    message: string,
    signal?: AbortSignal
  ): AsyncGenerator<StreamEvent, void, undefined> {
    const userMessage: ChatMessage = {
      role: 'user' as ChatRole,
      messageId: this.generateMessageId(),
      contents: [
        {
          kind: 'text',
          type: 'text',
          text: message,
        } as any,
      ],
    };

    const request = {
      threadId: this._threadId,
      input: [userMessage],
    };

    // Stream all events from client
    for await (const event of this.client.streamRun(request, signal)) {
      // Update thread ID from first event
      if (!this._threadId && event.eventType === 'run.started') {
        const runData = event.data as any;
        if (runData?.threadId) {
          this._threadId = runData.threadId;
        }
      }

      yield event;
    }
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
   * Gets all messages from this conversation's thread
   */
  async getMessages(options?: {
    limit?: number;
    after?: string;
  }): Promise<ChatMessage[]> {
    if (!this._threadId) {
      throw new Error(
        'No thread ID available. Send a message to this conversation first to create a thread.'
      );
    }

    return await this.client.threads.getMessages(this._threadId, options);
  }

  /**
   * Generates a unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Automatically saves the conversation to XML if logging is enabled
   */
  private autoSaveConversation(): void {
    if (!this._enableLogging || !this._threadId) {
      return;
    }

    try {
      const fs = require('fs');
      const path = require('path');

      // Ensure log directory exists
      if (!fs.existsSync(this._logDirectory)) {
        fs.mkdirSync(this._logDirectory, { recursive: true });
      }

      // Save conversation to file
      const filePath = path.join(this._logDirectory, `${this._threadId}.xml`);
      fs.writeFileSync(filePath, this.toString(), 'utf-8');
    } catch {
      // Silently ignore logging errors to avoid breaking the main flow
    }
  }

  /**
   * Returns the XML representation of all messages in this conversation
   * @returns XML string with all messages wrapped in a thread element
   */
  toString(): string {
    if (this._messages.length === 0) {
      return '<?xml version="1.0" encoding="utf-8"?>\n<thread />';
    }

    const serializer = new MessageSerializer();
    const messagesXml = serializer.serializeMany(this._messages);

    return `<?xml version="1.0" encoding="utf-8"?>\n<thread>\n${messagesXml}\n</thread>`;
  }
}
