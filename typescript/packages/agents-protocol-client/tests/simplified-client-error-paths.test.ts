/**
 * Tests for error paths and edge cases in SimplifiedClient to achieve 100% coverage
 * Focus: Line coverage for simplified-client.ts uncovered lines: 292-293, 298-299, 309, 321, 351-360, 395
 */

import { SimplifiedClient } from '../src/simplified-client';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('SimplifiedClient - Error Paths and Edge Cases', () => {
  let client: SimplifiedClient;

  beforeEach(() => {
    client = new SimplifiedClient({
      baseUrl: 'http://localhost:5000',
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('client getter (line 395)', () => {
    it('should return the low-level client instance', () => {
      const lowLevelClient = client.client;

      expect(lowLevelClient).toBeDefined();
      expect(lowLevelClient).toBe((client as any).lowLevelClient);
    });
  });

  describe('completeChat with tools option', () => {
    it('should handle tools being provided', async () => {
      const { ToolCollection } = await import('../src/tool-collection');
      const tools = new ToolCollection();
      tools.add('test_tool', () => 'result');

      // Mock streamRun to return a simple message
      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.updated',
          data: {
            role: 'agent',
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: 'Response from agent' }],
          },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const result = await client.completeChat('Hello', { tools });

      expect(result).toBe('Response from agent');
      expect(mockStreamRun).toHaveBeenCalled();
    });
  });
});
