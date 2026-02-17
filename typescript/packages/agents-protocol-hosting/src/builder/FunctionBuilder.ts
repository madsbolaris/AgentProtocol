import { FunctionDefinition, FunctionExecutionOptions, JSONSchema } from '../core/types.js';

/**
 * Builder for adding functions/tools to an agent.
 *
 * Functions require explicit schema definitions for parameter types.
 * This ensures type information survives minification and provides
 * runtime validation.
 *
 * SECURITY: All functions must specify a trust level. Use 'trusted'
 * only for functions you control. Use 'untrusted' for any function
 * that processes user input or comes from external sources.
 *
 * @example
 * ```typescript
 * const functions = new FunctionBuilder()
 *   .add('getTime@v1', 'Gets current time',
 *     {},  // No parameters
 *     (): string => new Date().toISOString(),
 *     { trustLevel: 'trusted' })
 *   .add('sum@v1', 'Adds numbers',
 *     {
 *       type: 'object',
 *       properties: {
 *         a: { type: 'number', description: 'First number' },
 *         b: { type: 'number', description: 'Second number' }
 *       },
 *       required: ['a', 'b']
 *     },
 *     ({ a, b }: { a: number; b: number }): string => (a + b).toString(),
 *     { trustLevel: 'trusted' });
 * ```
 */
export class FunctionBuilder {
  private functions: FunctionDefinition<Record<string, unknown>>[] = [];

  /**
   * Creates a new function builder.
   */
  constructor() {}

  /**
   * Adds a function with explicit parameter schema.
   *
   * The schema defines the parameter types and validation rules.
   * This approach ensures type information is available at runtime,
   * even after code minification.
   *
   * @param name - Function name (include @v1 suffix for versioning)
   * @param description - Human-readable description for the LLM
   * @param parametersSchema - JSON Schema defining parameters
   * @param implementation - The function implementation
   * @param executionOptions - Security and execution options (REQUIRED)
   * @returns A new FunctionBuilder with the function added
   *
   * @example No parameters
   * ```typescript
   * f.add('getTime@v1', 'Gets current UTC time',
   *   {},
   *   (): string => new Date().toISOString(),
   *   { trustLevel: 'trusted' }
   * );
   * ```
   *
   * @example Simple parameters
   * ```typescript
   * f.add('greet@v1', 'Greets a person',
   *   {
   *     type: 'object',
   *     properties: {
   *       name: { type: 'string', minLength: 1, maxLength: 100 }
   *     },
   *     required: ['name']
   *   },
   *   ({ name }: { name: string }): string => `Hello, ${name}!`,
   *   { trustLevel: 'trusted' }
   * );
   * ```
   */
  add<TParams = Record<string, unknown>>(
    name: string,
    description: string,
    parametersSchema: JSONSchema,
    implementation: (params: TParams) => string | Promise<string>,
    executionOptions: FunctionExecutionOptions
  ): FunctionBuilder {
    // Validate inputs
    if (!name || name.trim().length === 0) {
      throw new Error('Function name is required');
    }

    if (!description || description.trim().length === 0) {
      throw new Error('Function description is required');
    }

    if (!executionOptions || !executionOptions.trustLevel) {
      throw new Error(
        'executionOptions.trustLevel is required. Specify "trusted" or "untrusted".'
      );
    }

    // Validate schema
    if (!this.isValidSchema(parametersSchema)) {
      throw new Error('Invalid JSON schema');
    }

    const definition: FunctionDefinition<TParams> = {
      name,
      description,
      implementation,
      parametersSchema,
      executionOptions
    };

    // Return new builder (immutable pattern)
    const newBuilder = new FunctionBuilder();
    newBuilder.functions = [...this.functions, definition as FunctionDefinition<Record<string, unknown>>];
    return newBuilder;
  }

  /**
   * Builds the function list (internal use).
   *
   * @internal
   */
  build(): FunctionDefinition[] {
    return [...this.functions];
  }

  private isValidSchema(schema: JSONSchema): boolean {
    // Basic validation - could use ajv for more comprehensive validation
    if (typeof schema !== 'object' || schema === null) {
      return false;
    }

    // Empty schema is valid (no parameters)
    if (Object.keys(schema).length === 0) {
      return true;
    }

    // Must have a type if not empty
    if (!schema.type) {
      return false;
    }

    return true;
  }
}
