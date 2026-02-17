import { AgentBuilder } from '../src/builder/AgentBuilder.js';
import { TurnResult } from '../src/core/TurnResult.js';

describe('AgentBuilder', () => {
  describe('constructor', () => {
    it('should create a new AgentBuilder instance', () => {
      const builder = new AgentBuilder();
      expect(builder).toBeInstanceOf(AgentBuilder);
    });

    it('should accept optional services', () => {
      const services = new Map<symbol, unknown>();
      const builder = new AgentBuilder(services);
      expect(builder).toBeInstanceOf(AgentBuilder);
    });
  });

  describe('useLLM', () => {
    it('should configure LLM with model and instructions', () => {
      const builder = new AgentBuilder()
        .useLLM('gpt-4', 'You are a helpful assistant.');

      const config = (builder as any).build();
      expect(config.llmModel).toBe('gpt-4');
      expect(config.llmInstructions).toBe('You are a helpful assistant.');
    });

    it('should accept LLM options', () => {
      const options = { streaming: true, temperature: 0.7, maxTokens: 2000 };
      const builder = new AgentBuilder()
        .useLLM('gpt-4', 'Instructions', options);

      const config = (builder as any).build();
      expect(config.llmOptions).toEqual(options);
    });

    it('should throw TypeError for null model', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM(null as any, 'Instructions');
      }).toThrow(TypeError);
    });

    it('should throw TypeError for undefined model', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM(undefined as any, 'Instructions');
      }).toThrow(TypeError);
    });

    it('should throw TypeError for null instructions', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('gpt-4', null as any);
      }).toThrow(TypeError);
    });

    it('should throw TypeError for undefined instructions', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('gpt-4', undefined as any);
      }).toThrow(TypeError);
    });

    it('should throw Error for empty model', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('', 'Instructions');
      }).toThrow(Error);
      expect(() => {
        builder.useLLM('', 'Instructions');
      }).toThrow('model cannot be empty');
    });

    it('should throw Error for whitespace-only model', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('   ', 'Instructions');
      }).toThrow(Error);
    });

    it('should throw Error for empty instructions', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('gpt-4', '');
      }).toThrow(Error);
      expect(() => {
        builder.useLLM('gpt-4', '');
      }).toThrow('instructions cannot be empty');
    });

    it('should throw Error for whitespace-only instructions', () => {
      const builder = new AgentBuilder();
      expect(() => {
        builder.useLLM('gpt-4', '   ');
      }).toThrow(Error);
    });

    it('should return new builder instance (immutability)', () => {
      const builder1 = new AgentBuilder();
      const builder2 = builder1.useLLM('gpt-4', 'Instructions');

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('addFunctions', () => {
    it('should add functions using FunctionBuilder', () => {
      const builder = new AgentBuilder()
        .addFunctions(f => f
          .add('getTime@v1', 'Gets time', { type: 'object' }, () => new Date().toISOString(), { trustLevel: 'trusted' })
        );

      const config = (builder as any).build();
      expect(config.functions).toHaveLength(1);
      expect(config.functions[0].name).toBe('getTime@v1');
    });

    it('should add multiple functions', () => {
      const builder = new AgentBuilder()
        .addFunctions(f => f
          .add('func1@v1', 'First', { type: 'object' }, () => '1', { trustLevel: 'trusted' })
          .add('func2@v1', 'Second', { type: 'object' }, () => '2', { trustLevel: 'trusted' })
        );

      const config = (builder as any).build();
      expect(config.functions).toHaveLength(2);
    });

    it('should accumulate functions across multiple calls', () => {
      const builder = new AgentBuilder()
        .addFunctions(f => f.add('func1@v1', 'First', { type: 'object' }, () => '1', { trustLevel: 'trusted' }))
        .addFunctions(f => f.add('func2@v1', 'Second', { type: 'object' }, () => '2', { trustLevel: 'trusted' }));

      const config = (builder as any).build();
      expect(config.functions).toHaveLength(2);
    });

    it('should return new builder instance (immutability)', () => {
      const builder1 = new AgentBuilder();
      const builder2 = builder1.addFunctions(f => f
        .add('func@v1', 'Function', { type: 'object' }, () => 'result', { trustLevel: 'trusted' })
      );

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('onUserMessage', () => {
    it('should add a user message handler', () => {
      const handler = async () => TurnResult.Continue;
      const builder = new AgentBuilder()
        .onUserMessage(handler);

      const config = (builder as any).build();
      expect(config.userMessageHandlers).toHaveLength(1);
      expect(config.userMessageHandlers[0].handler).toBe(handler);
    });

    it('should add multiple handlers', () => {
      const handler1 = async () => TurnResult.Continue;
      const handler2 = async () => TurnResult.Consumed;

      const builder = new AgentBuilder()
        .onUserMessage(handler1)
        .onUserMessage(handler2);

      const config = (builder as any).build();
      expect(config.userMessageHandlers).toHaveLength(2);
    });

    it('should accept error handling config', () => {
      const handler = async () => TurnResult.Continue;
      const builder = new AgentBuilder()
        .onUserMessage(handler, { onError: 'stop' });

      const config = (builder as any).build();
      expect(config.userMessageHandlers[0].config.onError).toBe('stop');
    });

    it('should use default error handling config when not provided', () => {
      const handler = async () => TurnResult.Continue;
      const builder = new AgentBuilder()
        .onUserMessage(handler);

      const config = (builder as any).build();
      expect(config.userMessageHandlers[0].config.onError).toBe('continue');
    });

    it('should return new builder instance (immutability)', () => {
      const handler = async () => TurnResult.Continue;
      const builder1 = new AgentBuilder();
      const builder2 = builder1.onUserMessage(handler);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('onReaction', () => {
    it('should add a reaction handler', () => {
      const handler = async () => TurnResult.Consumed;
      const builder = new AgentBuilder()
        .onReaction(handler);

      const config = (builder as any).build();
      expect(config.reactionHandlers).toHaveLength(1);
      expect(config.reactionHandlers[0].handler).toBe(handler);
    });

    it('should add multiple reaction handlers', () => {
      const handler1 = async () => TurnResult.Consumed;
      const handler2 = async () => TurnResult.Continue;

      const builder = new AgentBuilder()
        .onReaction(handler1)
        .onReaction(handler2);

      const config = (builder as any).build();
      expect(config.reactionHandlers).toHaveLength(2);
    });

    it('should accept error handling config', () => {
      const handler = async () => TurnResult.Consumed;
      const builder = new AgentBuilder()
        .onReaction(handler, { onError: 'stop' });

      const config = (builder as any).build();
      expect(config.reactionHandlers[0].config.onError).toBe('stop');
    });

    it('should return new builder instance (immutability)', () => {
      const handler = async () => TurnResult.Consumed;
      const builder1 = new AgentBuilder();
      const builder2 = builder1.onReaction(handler);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('integration', () => {
    it('should chain all configuration methods', () => {
      const handler = async () => TurnResult.Continue;

      const builder = new AgentBuilder()
        .useLLM('gpt-4', 'You are helpful.', { streaming: true })
        .addFunctions(f => f
          .add('getTime@v1', 'Gets time', { type: 'object' }, () => new Date().toISOString(), { trustLevel: 'trusted' })
        )
        .onUserMessage(handler)
        .onReaction(handler);

      expect(builder).toBeInstanceOf(AgentBuilder);

      const config = (builder as any).build();
      expect(config.llmModel).toBe('gpt-4');
      expect(config.functions).toHaveLength(1);
      expect(config.userMessageHandlers).toHaveLength(1);
      expect(config.reactionHandlers).toHaveLength(1);
    });
  });
});
