/**
 * Testing utilities for the Agents Hosting SDK
 */

// TODO: Implement MockLLM and MockAgentContext for testing
// These would be used in unit tests to avoid real API calls

/**
 * Mock LLM for testing without making real API calls.
 *
 * @example
 * ```typescript
 * const mockLLM = new MockLLM()
 *   .on('Hello!', 'Hi there!')
 *   .on('What time is it?', (functions) => {
 *     const result = functions.call('getTime@v1');
 *     return `The current time is ${result}`;
 *   });
 * ```
 */
export class MockLLM {
  private responses: Map<string, string | ((functions: any) => string)> = new Map();

  on(input: string, response: string | ((functions: any) => string)): MockLLM {
    this.responses.set(input, response);
    return this;
  }

  async generate(input: string, functions?: any): Promise<string> {
    const response = this.responses.get(input);
    if (!response) {
      return 'I don\'t understand that question.';
    }

    if (typeof response === 'function') {
      return response(functions);
    }

    return response;
  }
}

/**
 * Mock agent context for testing handlers.
 *
 * @example
 * ```typescript
 * const ctx = new MockAgentContext('run-123', 'thread-456');
 * await handler(message, ctx);
 * expect(ctx.responses).toEqual(['Expected response']);
 * ```
 */
export class MockAgentContext {
  public responses: string[] = [];
  public logs: string[] = [];
  public state: Map<string, unknown> = new Map();

  constructor(
    public readonly runId: string,
    public readonly threadId: string
  ) {}

  async respondAsync(content: string): Promise<void> {
    this.responses.push(content);
  }

  async logAsync(message: string): Promise<void> {
    this.logs.push(message);
  }

  async getStateAsync<T>(key: string): Promise<T | null> {
    return (this.state.get(key) as T) || null;
  }

  async setStateAsync<T>(key: string, value: T): Promise<void> {
    this.state.set(key, value);
  }
}
