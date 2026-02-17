import OpenAI from 'openai';
import * as path from 'path';
import { LLMRecorder, LLMRequest, LLMResponse } from './llm-recorder.js';
import { LLMPlayer } from './llm-player.js';

export interface LLMClientOptions {
  model?: string;
  endpoint?: string;
  apiKey?: string;
  useRecordings?: boolean;
  recordLLM?: boolean;
  recordingsDir?: string;
}

/**
 * LLM client that supports recording and playback for deterministic testing.
 */
export class LLMClient {
  private openAIClient?: OpenAI;
  private recorder?: LLMRecorder;
  private player?: LLMPlayer;
  private model: string;
  private useRecordings: boolean;

  constructor(options: LLMClientOptions = {}) {
    this.model = options.model || process.env.FOUNDRY_MODEL_DEPLOYMENT || 'gpt-4';
    this.useRecordings = options.useRecordings ??
      (process.env.USE_LLM_RECORDINGS?.toLowerCase() === 'true');

    // Determine recordings directory
    const recordingsDir = options.recordingsDir ||
      path.join(process.cwd(), '..', '..', '..', '..', 'test-data', 'llm-recordings', 'sample', 'emoji-chat');

    if (this.useRecordings) {
      // Playback mode: use recorded responses
      this.player = new LLMPlayer(recordingsDir);
      console.log(`▶️  LLM Playback enabled: ${recordingsDir}`);
      console.log('   Using recorded LLM responses (test mode)');
    } else {
      // Generation mode: use real LLM
      const endpoint = options.endpoint || process.env.FOUNDRY_ENDPOINT;
      const apiKey = options.apiKey || process.env.FOUNDRY_API_KEY;

      if (endpoint && apiKey) {
        this.openAIClient = new OpenAI({
          apiKey,
          baseURL: `${endpoint}/openai/v1/`
        });

        // Check if recording is enabled
        const recordLLM = options.recordLLM ??
          (process.env.RECORD_LLM?.toLowerCase() === 'true');

        if (recordLLM) {
          this.recorder = new LLMRecorder(recordingsDir);
          console.log(`🔴 LLM Recording enabled: ${recordingsDir}`);
          console.log(`   Model: ${this.model}`);
        } else {
          console.log(`🤖 Using LLM: ${this.model} (recording disabled)`);
        }
      } else {
        console.warn('⚠️  No LLM credentials found!');
        console.warn('   Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables to use LLM.');
        console.warn('   Or set USE_LLM_RECORDINGS=true to use recorded responses.');
      }
    }
  }

  /**
   * Complete a chat conversation.
   */
  async chatComplete(
    messages: Array<{
      role: 'system' | 'user' | 'assistant' | 'tool';
      content: string;
      tool_calls?: any[];
      tool_call_id?: string;
    }>,
    tools?: Array<{
      type: 'function';
      function: {
        name: string;
        description?: string;
        parameters?: any;
      };
    }>
  ): Promise<LLMResponse> {
    const request: LLMRequest = {
      model: this.model,
      messages,
      tools
      // temperature removed - use model default
    };

    // If using recordings, replay
    if (this.useRecordings && this.player) {
      return await this.player.replayAsync(request);
    }

    // Otherwise, call real LLM
    if (!this.openAIClient) {
      throw new Error('No LLM client configured. Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY or USE_LLM_RECORDINGS=true');
    }

    const completion = await this.openAIClient.chat.completions.create({
      model: this.model,
      messages: messages as any,
      tools: tools as any
      // Note: temperature removed - some models (like gpt-5-nano) only support default temperature
    });

    // Convert OpenAI response to our format
    const response: LLMResponse = {
      id: completion.id,
      model: completion.model,
      created: completion.created,
      choices: completion.choices.map(choice => ({
        finish_reason: choice.finish_reason || 'stop',
        message: {
          role: choice.message.role,
          content: choice.message.content,
          tool_calls: choice.message.tool_calls?.map(tc => {
            // Handle function tool calls
            const toolCall: any = tc;
            if (toolCall.function) {
              return {
                id: tc.id,
                type: tc.type,
                function: {
                  name: toolCall.function.name,
                  arguments: toolCall.function.arguments
                }
              };
            }
            // Fallback for unknown tool types
            return {
              id: tc.id,
              type: tc.type,
              function: {
                name: 'unknown',
                arguments: '{}'
              }
            };
          })
        }
      })),
      usage: completion.usage ? {
        prompt_tokens: completion.usage.prompt_tokens,
        completion_tokens: completion.usage.completion_tokens,
        total_tokens: completion.usage.total_tokens
      } : undefined
    };

    // If recording is enabled, record the interaction
    if (this.recorder) {
      await this.recorder.recordAsync(request, response);
    }

    return response;
  }

  /**
   * Check if LLM is available (either real or recorded).
   */
  isAvailable(): boolean {
    return !!(this.openAIClient || this.player);
  }
}
