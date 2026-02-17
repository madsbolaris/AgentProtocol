import { AgentBuilder } from '../src/builder/AgentBuilder.js';
import { TurnResult } from '../src/core/TurnResult.js';
import { FunctionBuilder } from '../src/builder/FunctionBuilder.js';

describe('Error Handling', () => {
  describe('AgentBuilder validation', () => {
    it('should throw on null model', () => {
      const builder = new AgentBuilder();
      expect(() => builder.useLLM(null as any, 'Instructions')).toThrow(TypeError);
    });

    it('should throw on empty model', () => {
      const builder = new AgentBuilder();
      expect(() => builder.useLLM('', 'Instructions')).toThrow('model cannot be empty');
    });

    it('should throw on null instructions', () => {
      const builder = new AgentBuilder();
      expect(() => builder.useLLM('gpt-4', null as any)).toThrow(TypeError);
    });

    it('should throw on empty instructions', () => {
      const builder = new AgentBuilder();
      expect(() => builder.useLLM('gpt-4', '')).toThrow('instructions cannot be empty');
    });
  });

  describe('FunctionBuilder validation', () => {
    it('should throw on empty function name', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('', 'Description', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw on empty description', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', '', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw on invalid schema', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', 'Description', null as any, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw on missing execution options', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', 'Description', { type: 'object' }, () => 'result', null as any);
      }).toThrow();
    });
  });

  describe('Handler error behavior', () => {
    it('should handle handler that returns Continue', async () => {
      const handler = async () => TurnResult.Continue;
      const builder = new AgentBuilder().onUserMessage(handler);
      expect(builder).toBeInstanceOf(AgentBuilder);
    });

    it('should handle handler that returns Consumed', async () => {
      const handler = async () => TurnResult.Consumed;
      const builder = new AgentBuilder().onUserMessage(handler);
      expect(builder).toBeInstanceOf(AgentBuilder);
    });

    it('should handle handler that returns Replied', async () => {
      const handler = async () => TurnResult.Replied;
      const builder = new AgentBuilder().onUserMessage(handler);
      expect(builder).toBeInstanceOf(AgentBuilder);
    });

    it('should support onError config', () => {
      const handler = async () => TurnResult.Continue;
      const builder = new AgentBuilder()
        .onUserMessage(handler, { onError: 'continue' });

      const config = (builder as any).build();
      expect(config.userMessageHandlers[0].config.onError).toBe('continue');
    });
  });

  describe('Function execution options', () => {
    it('should require trustLevel', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('func@v1', 'Description', { type: 'object' }, () => 'result', {} as any);
      }).toThrow();
    });

    it('should accept trusted functions', () => {
      const builder = new FunctionBuilder()
        .add('func@v1', 'Description', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });

      const functions = builder.build();
      expect(functions[0].executionOptions.trustLevel).toBe('trusted');
    });

    it('should accept untrusted functions', () => {
      const builder = new FunctionBuilder()
        .add('func@v1', 'Description', { type: 'object' }, () => 'result', { trustLevel: 'untrusted' });

      const functions = builder.build();
      expect(functions[0].executionOptions.trustLevel).toBe('untrusted');
    });

    it('should accept timeout option', () => {
      const builder = new FunctionBuilder()
        .add('func@v1', 'Description', { type: 'object' }, () => 'result', {
          trustLevel: 'trusted',
          timeoutMs: 5000
        });

      const functions = builder.build();
      expect(functions[0].executionOptions.timeoutMs).toBe(5000);
    });
  });

  describe('Cancellation handling', () => {
    it('should handle pre-cancelled operations', () => {
      const controller = new AbortController();
      controller.abort();

      expect(controller.signal.aborted).toBe(true);
    });

    it('should handle cancellation during operation', () => {
      const controller = new AbortController();

      setTimeout(() => controller.abort(), 10);

      expect(controller.signal.aborted).toBe(false);
    });
  });

  describe('Type safety', () => {
    it('should enforce correct TurnResult types', () => {
      const validResults: TurnResult[] = [
        TurnResult.Continue,
        TurnResult.Consumed,
        TurnResult.Replied
      ];

      validResults.forEach(result => {
        expect(['continue', 'consumed', 'replied']).toContain(result);
      });
    });

    it('should support typed state management', async () => {
      interface UserPrefs {
        theme: string;
        language: string;
      }

      const prefs: UserPrefs = {
        theme: 'dark',
        language: 'en'
      };

      expect(prefs.theme).toBe('dark');
      expect(prefs.language).toBe('en');
    });
  });
});
