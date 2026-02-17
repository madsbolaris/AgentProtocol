import * as fs from 'fs/promises';
import * as crypto from 'crypto';
import * as path from 'path';

export interface LLMRequest {
  model: string;
  messages: Array<{
    role: string;
    content: string;
    tool_calls?: any[];
    tool_call_id?: string;
  }>;
  tools?: Array<{
    type: string;
    function: {
      name: string;
      description?: string;
      parameters?: any;
    };
  }>;
  temperature?: number;
}

export interface LLMResponse {
  id: string;
  model: string;
  created: number;
  choices: Array<{
    finish_reason: string;
    message: {
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
    };
  }>;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
}

/**
 * Records LLM request/response pairs for deterministic testing.
 * Based on the .NET LLMRecorder implementation.
 */
export class LLMRecorder {
  private callCount = 0;

  constructor(private recordingsDir: string) {}

  /**
   * Generate deterministic hash from request parameters.
   */
  hashRequest(request: LLMRequest): string {
    // Build canonical request representation
    const requestDict: Record<string, any> = {
      model: request.model,
      messages: this.normalizeMessages(request.messages),
      temperature: request.temperature || 0.0
    };

    if (request.tools && request.tools.length > 0) {
      requestDict.tools = request.tools.map(t => ({
        type: t.type,
        function: {
          name: t.function.name,
          description: t.function.description,
          parameters: t.function.parameters
        }
      }));
    }

    // Serialize to stable JSON (sorted keys)
    const json = this.sortedStringify(requestDict);

    // Hash and truncate
    const hash = crypto.createHash('sha256').update(json).digest('hex');
    return hash.substring(0, 16);
  }

  /**
   * Record an LLM request/response pair.
   */
  async recordAsync(request: LLMRequest, response: LLMResponse): Promise<void> {
    const callId = ++this.callCount;
    const timestamp = new Date().toISOString();
    const hashKey = this.hashRequest(request);

    // Ensure directory exists
    await fs.mkdir(this.recordingsDir, { recursive: true });

    // Record request
    const requestData = {
      callId,
      timestamp,
      hash: hashKey,
      model: request.model,
      messages: this.normalizeMessages(request.messages),
      tools: request.tools
    };

    const requestFile = path.join(this.recordingsDir, `${hashKey}.request.json`);
    await fs.writeFile(requestFile, JSON.stringify(requestData, null, 2));

    // Record response
    const responseData = {
      callId,
      timestamp: new Date().toISOString(),
      hash: hashKey,
      response: {
        id: response.id,
        model: response.model,
        created: response.created,
        finishReason: response.choices[0]?.finish_reason || 'stop',
        content: response.choices[0]?.message.content
          ? [{ text: response.choices[0].message.content }]
          : [],
        toolCalls: response.choices[0]?.message.tool_calls?.map(tc => ({
          id: tc.id,
          type: tc.type,
          function: {
            name: tc.function.name,
            arguments: tc.function.arguments
          }
        })) || []
      }
    };

    const responseFile = path.join(this.recordingsDir, `${hashKey}.response.json`);
    await fs.writeFile(responseFile, JSON.stringify(responseData, null, 2));

    console.log(`  🔴 Recorded LLM call #${callId}: ${hashKey}`);
  }

  private normalizeMessages(messages: Array<any>): Array<any> {
    return messages.map(msg => {
      const normalized: any = {
        role: msg.role
      };

      if (msg.content) {
        normalized.content = msg.content;
      }

      if (msg.tool_calls) {
        normalized.tool_calls = msg.tool_calls.map((tc: any) => ({
          id: tc.id,
          type: tc.type,
          function: {
            name: tc.function.name,
            arguments: tc.function.arguments
          }
        }));
      }

      if (msg.tool_call_id) {
        normalized.tool_call_id = msg.tool_call_id;
      }

      return normalized;
    });
  }

  private sortedStringify(obj: any): string {
    if (Array.isArray(obj)) {
      return '[' + obj.map(item => this.sortedStringify(item)).join(',') + ']';
    } else if (obj !== null && typeof obj === 'object') {
      const keys = Object.keys(obj).sort();
      const pairs = keys.map(key => `"${key}":${this.sortedStringify(obj[key])}`);
      return '{' + pairs.join(',') + '}';
    } else {
      return JSON.stringify(obj);
    }
  }
}
