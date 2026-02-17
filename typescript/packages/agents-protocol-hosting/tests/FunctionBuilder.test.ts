import { FunctionBuilder } from '../src/builder/FunctionBuilder.js';

describe('FunctionBuilder', () => {
  describe('constructor', () => {
    it('should create a new FunctionBuilder instance', () => {
      const builder = new FunctionBuilder();
      expect(builder).toBeInstanceOf(FunctionBuilder);
    });

    it('should start with empty function list', () => {
      const builder = new FunctionBuilder();
      const functions = builder.build();
      expect(functions).toEqual([]);
    });
  });

  describe('add', () => {
    it('should add a function with no parameters', () => {
      const builder = new FunctionBuilder()
        .add(
          'getTime@v1',
          'Gets current time',
          { type: 'object' },
          (): string => new Date().toISOString(),
          { trustLevel: 'trusted' }
        );

      const functions = builder.build();
      expect(functions).toHaveLength(1);
      expect(functions[0].name).toBe('getTime@v1');
      expect(functions[0].description).toBe('Gets current time');
    });

    it('should add a function with parameters', () => {
      const builder = new FunctionBuilder()
        .add(
          'greet@v1',
          'Greets a person',
          {
            type: 'object',
            properties: {
              name: { type: 'string' }
            },
            required: ['name']
          },
          ({ name }: { name: string }): string => `Hello, ${name}!`,
          { trustLevel: 'trusted' }
        );

      const functions = builder.build();
      expect(functions).toHaveLength(1);
      expect(functions[0].name).toBe('greet@v1');
      expect(functions[0].parametersSchema).toHaveProperty('properties');
    });

    it('should add multiple functions', () => {
      const builder = new FunctionBuilder()
        .add('func1@v1', 'First function', { type: 'object' }, () => 'one', { trustLevel: 'trusted' })
        .add('func2@v1', 'Second function', { type: 'object' }, () => 'two', { trustLevel: 'trusted' })
        .add('func3@v1', 'Third function', { type: 'object' }, () => 'three', { trustLevel: 'trusted' });

      const functions = builder.build();
      expect(functions).toHaveLength(3);
      expect(functions[0].name).toBe('func1@v1');
      expect(functions[1].name).toBe('func2@v1');
      expect(functions[2].name).toBe('func3@v1');
    });

    it('should preserve function implementation', () => {
      const implementation = ({ a, b }: { a: number; b: number }): string => (a + b).toString();
      const builder = new FunctionBuilder()
        .add(
          'sum@v1',
          'Adds numbers',
          {
            type: 'object',
            properties: {
              a: { type: 'number' },
              b: { type: 'number' }
            },
            required: ['a', 'b']
          },
          implementation,
          { trustLevel: 'trusted' }
        );

      const functions = builder.build();
      expect(functions[0].implementation).toBe(implementation);
      expect(functions[0].implementation({ a: 2, b: 3 })).toBe('5');
    });

    it('should handle different trust levels', () => {
      const builder = new FunctionBuilder()
        .add('trusted@v1', 'Trusted function', { type: 'object' }, () => 'trusted', { trustLevel: 'trusted' })
        .add('untrusted@v1', 'Untrusted function', { type: 'object' }, () => 'untrusted', { trustLevel: 'untrusted' });

      const functions = builder.build();
      expect(functions[0].executionOptions.trustLevel).toBe('trusted');
      expect(functions[1].executionOptions.trustLevel).toBe('untrusted');
    });

    it('should support timeout option', () => {
      const builder = new FunctionBuilder()
        .add(
          'longRunning@v1',
          'Long running function',
          { type: 'object' },
          () => 'result',
          { trustLevel: 'trusted', timeoutMs: 5000 }
        );

      const functions = builder.build();
      expect(functions[0].executionOptions.timeoutMs).toBe(5000);
    });

    it('should throw error for invalid empty name', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('', 'Description', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw error for invalid empty description', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', '', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw error for invalid schema', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', 'Description', null as any, () => 'result', { trustLevel: 'trusted' });
      }).toThrow();
    });

    it('should throw error for missing execution options', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add('name@v1', 'Description', { type: 'object' }, () => 'result', null as any);
      }).toThrow();
    });

    it('should accept empty schema (no parameters)', () => {
      const builder = new FunctionBuilder()
        .add('noParams@v1', 'Function with no parameters', {} as any, () => 'result', { trustLevel: 'trusted' });

      const functions = builder.build();
      expect(functions).toHaveLength(1);
      expect(functions[0].parametersSchema).toEqual({});
    });

    it('should throw error for schema with properties but no type', () => {
      const builder = new FunctionBuilder();
      expect(() => {
        builder.add(
          'invalid@v1',
          'Invalid schema',
          { properties: { name: { type: 'string' } } } as any,
          () => 'result',
          { trustLevel: 'trusted' }
        );
      }).toThrow('Invalid JSON schema');
    });

    it('should accept schema with type and properties', () => {
      const builder = new FunctionBuilder()
        .add(
          'valid@v1',
          'Valid schema',
          {
            type: 'object',
            properties: { name: { type: 'string' } }
          },
          () => 'result',
          { trustLevel: 'trusted' }
        );

      const functions = builder.build();
      expect(functions).toHaveLength(1);
    });
  });

  describe('immutability', () => {
    it('should return a new builder instance on add', () => {
      const builder1 = new FunctionBuilder();
      const builder2 = builder1.add('func@v1', 'Description', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });

      expect(builder1).not.toBe(builder2);
      expect(builder1.build()).toHaveLength(0);
      expect(builder2.build()).toHaveLength(1);
    });

    it('should not modify original builder when adding to new builder', () => {
      const builder1 = new FunctionBuilder()
        .add('func1@v1', 'First', { type: 'object' }, () => 'one', { trustLevel: 'trusted' });

      const builder2 = builder1.add('func2@v1', 'Second', { type: 'object' }, () => 'two', { trustLevel: 'trusted' });

      expect(builder1.build()).toHaveLength(1);
      expect(builder2.build()).toHaveLength(2);
    });
  });

  describe('build', () => {
    it('should return array of function definitions', () => {
      const builder = new FunctionBuilder()
        .add('func1@v1', 'First', { type: 'object' }, () => 'one', { trustLevel: 'trusted' })
        .add('func2@v1', 'Second', { type: 'object' }, () => 'two', { trustLevel: 'trusted' });

      const functions = builder.build();
      expect(Array.isArray(functions)).toBe(true);
      expect(functions).toHaveLength(2);
    });

    it('should return a new array on each call', () => {
      const builder = new FunctionBuilder()
        .add('func@v1', 'Function', { type: 'object' }, () => 'result', { trustLevel: 'trusted' });

      const functions1 = builder.build();
      const functions2 = builder.build();

      expect(functions1).not.toBe(functions2);
      expect(functions1).toEqual(functions2);
    });
  });
});
