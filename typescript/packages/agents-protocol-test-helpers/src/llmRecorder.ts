/**
 * LLM Recording and Replay functionality.
 *
 * Handles deterministic hash generation and loading of recorded LLM responses.
 * Based on Python's LLMRecorder implementation.
 */

import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Normalized message for hashing
 */
interface NormalizedMessage {
  role: string;
  content: string | null;
  tool_calls?: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      arguments: string;
    };
  }>;
  tool_call_id?: string;
  name?: string;
}

/**
 * Normalized tool for hashing
 */
interface NormalizedTool {
  type: string;
  function: {
    name: string;
    description?: string;
    parameters?: any;
  };
}

/**
 * Raw message structure (flexible input)
 */
export interface RawMessage {
  role: string;
  content?: string | null;
  tool_calls?: Array<{
    id?: string;
    type?: string;
    function?: {
      name?: string;
      arguments?: string;
    };
  }>;
  tool_call_id?: string;
  name?: string;
}

/**
 * Raw tool definition (flexible input)
 */
export interface RawTool {
  type?: string;
  function?: {
    name?: string;
    description?: string;
    parameters?: any;
  };
}

/**
 * LLM response data structure
 */
export interface LLMResponseData {
  callId: number;
  timestamp: string;
  hash: string;
  response: any;
}

/**
 * Records and replays LLM API interactions for deterministic testing.
 * Uses content-based hashing to match requests to recorded responses.
 */
export class LLMRecorder {
  private recordingsDir: string;

  /**
   * Initialize recorder.
   *
   * @param recordingsDir - Directory containing recorded interactions
   */
  constructor(recordingsDir: string) {
    this.recordingsDir = recordingsDir;

    // Ensure directory exists
    if (!fs.existsSync(this.recordingsDir)) {
      fs.mkdirSync(this.recordingsDir, { recursive: true });
    }
  }

  /**
   * Generate deterministic hash for LLM request.
   *
   * The hash is based on:
   * - Model name
   * - Message content (roles and content)
   * - Tool definitions (names and parameters)
   * - Temperature
   * - Seed
   *
   * @param model - Model name
   * @param messages - Conversation messages
   * @param tools - Function tool definitions
   * @param temperature - Temperature setting
   * @param seed - Random seed
   * @returns Hex-encoded SHA256 hash of request (first 16 chars)
   */
  hashRequest(
    model: string,
    messages: RawMessage[],
    tools?: RawTool[] | null,
    temperature: number = 0.0,
    seed?: number | null
  ): string {
    // Normalize request for hashing
    const normalized = {
      model,
      messages: this.normalizeMessages(messages),
      tools: tools ? this.normalizeTools(tools) : null,
      temperature,
      seed: seed ?? null,
    };

    // Convert to JSON string with sorted keys
    const jsonStr = JSON.stringify(normalized, this.sortKeys);

    // Generate SHA256 hash
    const hash = crypto.createHash('sha256');
    hash.update(jsonStr, 'utf8');

    // Return first 16 chars for readability
    return hash.digest('hex').substring(0, 16);
  }

  /**
   * Normalize messages for consistent hashing.
   *
   * @param messages - Raw message list
   * @returns Normalized message list
   */
  private normalizeMessages(messages: RawMessage[]): NormalizedMessage[] {
    return messages.map(msg => {
      const normalized: NormalizedMessage = {
        role: msg.role,
        content: msg.content ?? null,
      };

      // Include tool calls if present
      if (msg.tool_calls && msg.tool_calls.length > 0) {
        normalized.tool_calls = msg.tool_calls.map(tc => ({
          id: tc.id || '',
          type: tc.type || 'function',
          function: {
            name: tc.function?.name || '',
            arguments: tc.function?.arguments || '{}',
          },
        }));
      }

      // Include tool_call_id if present (for tool responses)
      if (msg.tool_call_id) {
        normalized.tool_call_id = msg.tool_call_id;
      }

      // Include name if present
      if (msg.name) {
        normalized.name = msg.name;
      }

      return normalized;
    });
  }

  /**
   * Normalize tool definitions for consistent hashing.
   *
   * @param tools - Raw tool list
   * @returns Normalized tool list
   */
  private normalizeTools(tools: RawTool[]): NormalizedTool[] {
    return tools
      .filter(tool => tool.type === 'function' || !tool.type)
      .map(tool => ({
        type: 'function',
        function: {
          name: tool.function?.name || '',
          description: tool.function?.description,
          parameters: tool.function?.parameters,
        },
      }));
  }

  /**
   * JSON replacer function for sorted keys
   */
  private sortKeys(key: string, value: any): any {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return Object.keys(value)
        .sort()
        .reduce((sorted: any, k) => {
          sorted[k] = value[k];
          return sorted;
        }, {});
    }
    return value;
  }

  /**
   * Load recorded response for hash key.
   *
   * @param hashKey - Request hash from hashRequest()
   * @returns Recorded response data
   * @throws Error if no recording exists
   */
  loadResponse(hashKey: string): LLMResponseData {
    const responsePath = path.join(this.recordingsDir, `${hashKey}.response.json`);

    if (!fs.existsSync(responsePath)) {
      throw new Error(`No recording found: ${responsePath}`);
    }

    const content = fs.readFileSync(responsePath, 'utf8');
    return JSON.parse(content) as LLMResponseData;
  }

  /**
   * Save LLM response for future replay.
   *
   * @param hashKey - Request hash from hashRequest()
   * @param responseData - Response data to save
   */
  saveResponse(hashKey: string, responseData: LLMResponseData): void {
    const responsePath = path.join(this.recordingsDir, `${hashKey}.response.json`);

    fs.writeFileSync(
      responsePath,
      JSON.stringify(responseData, null, 2),
      'utf8'
    );

    console.log(`  💾 Saved recording: ${hashKey}.response.json`);
  }

  /**
   * Save request data for debugging.
   *
   * @param hashKey - Request hash from hashRequest()
   * @param requestData - Request data to save
   */
  saveRequest(hashKey: string, requestData: any): void {
    const requestPath = path.join(this.recordingsDir, `${hashKey}.request.json`);

    fs.writeFileSync(
      requestPath,
      JSON.stringify(requestData, null, 2),
      'utf8'
    );
  }
}
