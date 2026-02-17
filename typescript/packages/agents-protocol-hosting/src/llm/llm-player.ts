import * as fs from 'fs/promises';
import * as path from 'path';
import { LLMRequest, LLMResponse, LLMRecorder } from './llm-recorder.js';

/**
 * Replays recorded LLM responses for deterministic testing.
 * Based on the .NET LLMPlayer implementation.
 */
export class LLMPlayer {
  private callCount = 0;
  private recorder: LLMRecorder;

  constructor(private recordingsDir: string) {
    this.recorder = new LLMRecorder(recordingsDir);
  }

  /**
   * Replay a recorded LLM response.
   */
  async replayAsync(request: LLMRequest): Promise<LLMResponse> {
    const callId = ++this.callCount;

    // Generate hash to find recording
    const hashKey = this.recorder.hashRequest(request);

    // Load recorded response
    const responseFile = path.join(this.recordingsDir, `${hashKey}.response.json`);

    try {
      const responseJson = await fs.readFile(responseFile, 'utf-8');
      const responseData = JSON.parse(responseJson);

      console.log(`  ▶️  Replaying LLM call #${callId}: ${hashKey}`);

      // Convert recorded response to LLMResponse format
      return this.convertToLLMResponse(responseData);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new Error(
          `No recorded LLM response found for request hash: ${hashKey}\n` +
          `Expected file: ${responseFile}\n\n` +
          `This usually means:\n` +
          `1. Tests need to be run in generation mode first: RECORD_LLM=true\n` +
          `2. The request parameters have changed (different hash)\n` +
          `3. The recording file was deleted\n\n` +
          `Request details:\n` +
          `  Model: ${request.model}\n` +
          `  Messages: ${request.messages.length} messages\n` +
          `  Tools: ${request.tools?.length || 0} tools\n`
        );
      }
      throw error;
    }
  }

  private convertToLLMResponse(responseData: any): LLMResponse {
    const response = responseData.response;

    // Extract content
    const content = response.content && response.content.length > 0
      ? response.content.map((c: any) => c.text).join('')
      : null;

    // Extract tool calls
    const toolCalls = response.toolCalls || [];

    return {
      id: response.id || 'mock-completion',
      model: response.model || 'unknown',
      created: response.created || Math.floor(Date.now() / 1000),
      choices: [{
        finish_reason: response.finishReason || 'stop',
        message: {
          role: 'assistant',
          content,
          tool_calls: toolCalls.length > 0 ? toolCalls.map((tc: any) => ({
            id: tc.id,
            type: tc.type,
            function: {
              name: tc.function.name,
              arguments: tc.function.arguments
            }
          })) : undefined
        }
      }],
      usage: response.usage
    };
  }
}
