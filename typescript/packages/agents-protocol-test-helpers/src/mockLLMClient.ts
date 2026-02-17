/**
 * Mock LLM Client for test mode.
 *
 * Replays recorded LLM responses instead of making real API calls.
 * Based on Python's MockLLMClient implementation.
 */

import * as fs from 'fs';
import * as path from 'path';
import { LLMRecorder, RawMessage, RawTool, LLMResponseData } from './llmRecorder.js';

/**
 * Mock content part
 */
export interface MockContentPart {
  text: string;
}

/**
 * Mock function call
 */
export interface MockFunction {
  name: string;
  arguments: string;
}

/**
 * Mock tool call
 */
export interface MockToolCall {
  id: string;
  type: string;
  function: MockFunction;
}

/**
 * Mock chat completion response
 */
export interface MockChatCompletion {
  id: string;
  model: string;
  finishReason: string;
  content: MockContentPart[];
  toolCalls: MockToolCall[];
}

/**
 * Mock chat message for request
 */
export interface MockChatMessage {
  role: string;
  content?: string | null;
  toolCalls?: MockToolCall[];
  toolCallId?: string;
  name?: string;
}

/**
 * Mock tool definition
 */
export interface MockTool {
  type: string;
  function: {
    name: string;
    description?: string;
    parameters?: any;
  };
}

/**
 * Mock OpenAI client that replays recorded responses.
 *
 * Uses recorded request/response pairs from generation mode to provide
 * deterministic, fast, free LLM responses for testing.
 *
 * Example:
 * ```typescript
 * const mockClient = new MockLLMClient('/path/to/test-data/llm-recordings/evals');
 * const completion = await mockClient.chat.completions.create({
 *   model: 'gpt-4',
 *   messages: [{ role: 'user', content: 'Hello' }]
 * });
 * // Returns recorded response, no API call
 * ```
 */
export class MockLLMClient {
  private recorder: LLMRecorder;
  private callCount: number = 0;

  /**
   * Chat namespace (for compatibility with OpenAI client)
   */
  public readonly chat: {
    completions: {
      create: (params: {
        model: string;
        messages: MockChatMessage[];
        tools?: MockTool[];
        temperature?: number;
        seed?: number;
        [key: string]: any;
      }) => Promise<MockChatCompletion>;
    };
  };

  /**
   * Initialize mock client.
   *
   * @param recordingsDir - Directory containing recorded interactions
   */
  constructor(recordingsDir: string) {
    if (!fs.existsSync(recordingsDir)) {
      throw new Error(
        `Recordings directory not found: ${recordingsDir}\n\n` +
        `Please ensure LLM recordings exist for eval tests.\n` +
        `Run generation mode first to create recordings.`
      );
    }

    this.recorder = new LLMRecorder(recordingsDir);

    // Provide chat.completions namespace
    this.chat = {
      completions: {
        create: this.replayResponse.bind(this),
      },
    };
  }

  /**
   * Get the current call count
   */
  get CallCount(): number {
    return this.callCount;
  }

  /**
   * Replay recorded response for this request.
   *
   * @param params - Request parameters
   * @returns MockChatCompletion with recorded response
   */
  private async replayResponse(params: {
    model: string;
    messages: MockChatMessage[];
    tools?: MockTool[];
    temperature?: number;
    seed?: number;
    [key: string]: any;
  }): Promise<MockChatCompletion> {
    this.callCount++;

    const {
      model,
      messages,
      tools,
      temperature = 0.0,
      seed,
      ...otherParams
    } = params;

    // Convert MockChatMessage to RawMessage for hashing
    const rawMessages: RawMessage[] = messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      tool_calls: msg.toolCalls?.map(tc => ({
        id: tc.id,
        type: tc.type,
        function: {
          name: tc.function.name,
          arguments: tc.function.arguments,
        },
      })),
      tool_call_id: msg.toolCallId,
      name: msg.name,
    }));

    // Convert MockTool to RawTool for hashing
    const rawTools: RawTool[] | undefined = tools?.map(t => ({
      type: t.type,
      function: {
        name: t.function.name,
        description: t.function.description,
        parameters: t.function.parameters,
      },
    }));

    // Generate hash to find recording
    const hashKey = this.recorder.hashRequest(
      model,
      rawMessages,
      rawTools,
      temperature,
      seed
    );

    // Load recorded response
    let responseData: LLMResponseData;
    try {
      responseData = this.recorder.loadResponse(hashKey);
    } catch (error: any) {
      // Provide helpful error message
      throw new Error(
        `No recorded LLM response found for request hash: ${hashKey}\n` +
        `Expected file: ${path.join(this.recorder['recordingsDir'], hashKey)}.response.json\n\n` +
        `This usually means:\n` +
        `1. Tests need to be run in generation mode first: TEST_MODE=generate\n` +
        `2. The request parameters have changed (different hash)\n` +
        `3. The recording file was deleted\n\n` +
        `Request details:\n` +
        `  Model: ${model}\n` +
        `  Messages: ${messages.length} messages\n` +
        `  Tools: ${tools?.length ?? 0} tools\n` +
        `  Temperature: ${temperature}\n` +
        `  Seed: ${seed}\n`
      );
    }

    // Log replay
    console.log(`  ▶️  Replaying LLM call #${this.callCount}: ${hashKey}`);

    // Convert recorded data to mock response object
    return this.parseMockCompletion(responseData);
  }

  /**
   * Parse LLM response data into MockChatCompletion
   *
   * @param responseData - Recorded response data
   * @returns MockChatCompletion object
   */
  private parseMockCompletion(responseData: LLMResponseData): MockChatCompletion {
    const response = responseData.response;

    const completion: MockChatCompletion = {
      id: response.id || 'mock-completion',
      model: response.model || 'unknown',
      finishReason: response.finishReason || 'stop',
      content: [],
      toolCalls: [],
    };

    // Parse content
    if (response.content && Array.isArray(response.content)) {
      for (const contentItem of response.content) {
        if (contentItem.text) {
          completion.content.push({
            text: contentItem.text,
          });
        }
      }
    }

    // Parse tool calls
    if (response.toolCalls && Array.isArray(response.toolCalls)) {
      for (const toolCallItem of response.toolCalls) {
        completion.toolCalls.push({
          id: toolCallItem.id || 'mock-tool-call',
          type: toolCallItem.type || 'function',
          function: {
            name: toolCallItem.function?.name || 'unknown',
            arguments: toolCallItem.function?.arguments || '{}',
          },
        });
      }
    }

    return completion;
  }
}
