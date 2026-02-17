/**
 * Testing wrapper for SimplifiedClient that supports HTTP recording and playback.
 * Enables deterministic testing by recording/replaying HTTP interactions.
 */

import * as path from 'path';
import { SimplifiedClient } from '../simplified-client';
import type { ChatMessage, ChatRole } from '@microsoft/agents-protocol-abstractions';
import type { ChatOptions } from '../chat-options';
import type { IConversation } from '../conversation';
import { HttpRecorder } from './HttpRecorder';
import { HttpPlayer } from './HttpPlayer';

/**
 * Wrapper around SimplifiedClient with HTTP recording/playback support.
 * Uses shared test-data/llm-recordings/docs/ for cross-language compatibility.
 */
export class RecordingAgentProtocolClient {
  private realClient?: SimplifiedClient;
  private recorder?: HttpRecorder;
  private player?: HttpPlayer;
  private recordMode: boolean;
  private recordingsDir: string;
  private originalFetch?: typeof global.fetch;

  constructor(
    baseUrl: string = 'http://localhost:5000',
    recordingsDir?: string,
    scenarioName: string = 'default'
  ) {
    // Determine recording mode from environment
    const recordEnv = process.env.RECORD_HTTP?.toLowerCase();
    this.recordMode = recordEnv === 'true' || recordEnv === '1';

    // Use shared recordings directory by default (repository root /test-data/llm-recordings/docs/)
    if (!recordingsDir) {
      // Navigate from src/testing/ up to repo root
      const repoRoot = path.join(__dirname, '../../../../..');
      recordingsDir = path.join(
        repoRoot,
        'test-data',
        'llm-recordings',
        'docs',
        scenarioName
      );
    }

    this.recordingsDir = recordingsDir;

    if (this.recordMode) {
      // Record mode: use real client + recorder
      this.realClient = new SimplifiedClient({ baseUrl });
      this.recorder = new HttpRecorder(recordingsDir);
      console.log(`📹 HTTP Recording enabled: ${recordingsDir}`);
    } else {
      // Playback mode: use player only, create mock client
      this.player = new HttpPlayer(recordingsDir);
      this.realClient = new SimplifiedClient({ baseUrl });
      console.log(`▶️  HTTP Playback enabled: ${recordingsDir}`);
    }

    // Intercept fetch calls
    this.interceptFetch();
  }

  /**
   * Intercept fetch to record or replay HTTP calls
   */
  private interceptFetch(): void {
    this.originalFetch = global.fetch;

    global.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      const method = init?.method?.toUpperCase() ?? 'GET';
      const body = init?.body?.toString();

      // Parse URL to get path
      const urlObj = new URL(url);
      const path = urlObj.pathname + urlObj.search;

      if (this.recordMode && this.recorder && this.originalFetch) {
        // Record mode: make real request and save response
        const response = await this.originalFetch(input, init);
        const responseBody = await response.text();

        await this.recorder.recordAsync(
          method,
          path,
          body,
          response.status,
          responseBody
        );

        // Return response with cloned body
        return new Response(responseBody, {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
        });
      } else if (this.player) {
        // Playback mode: load from recording
        const recordedResponse = await this.player.replayAsync(method, path, body);

        return new Response(recordedResponse.body, {
          status: recordedResponse.statusCode,
          statusText: 'OK',
          headers: { 'Content-Type': 'application/json' },
        });
      }

      throw new Error('Invalid state: neither record nor playback mode');
    };
  }

  /**
   * Restore original fetch implementation
   */
  dispose(): void {
    if (this.originalFetch) {
      global.fetch = this.originalFetch;
    }
  }

  /**
   * Send a chat completion request with recording/playback.
   */
  async completeChat(
    message: string,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<string> {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return await this.realClient.completeChat(message, options, signal);
  }

  /**
   * Send a structured message with recording/playback.
   */
  async completeChatStructured(
    message: ChatMessage,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<ChatMessage> {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return await this.realClient.completeChatStructured(message, options, signal);
  }

  /**
   * Stream chat with recording/playback.
   */
  async streamChat(
    message: string,
    onTextChunk: (text: string) => void,
    options?: ChatOptions,
    signal?: AbortSignal
  ): Promise<void> {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return await this.realClient.streamChat(message, onTextChunk, options, signal);
  }

  /**
   * Create a conversation.
   */
  createConversation(): IConversation {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return this.realClient.createConversation();
  }

  /**
   * Resume an existing conversation.
   */
  resumeConversation(threadId: string): IConversation {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return this.realClient.resumeConversation(threadId);
  }

  /**
   * Get the underlying client (for advanced operations)
   */
  get client(): SimplifiedClient {
    if (!this.realClient) {
      throw new Error('Client not initialized');
    }
    return this.realClient;
  }
}
