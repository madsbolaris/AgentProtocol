// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import type { JSONSchema } from '@microsoft/agents-protocol-abstractions';

/**
 * Executes tools/functions with JSON arguments.
 * Shared utility across Client and Hosting SDKs for consistent tool execution.
 *
 * @example
 * ```typescript
 * const handler = async (params: { name: string; age: number }) => {
 *   return `${params.name} is ${params.age}`;
 * };
 *
 * const schema = {
 *   type: 'object',
 *   properties: {
 *     name: { type: 'string' },
 *     age: { type: 'number' }
 *   },
 *   required: ['name', 'age']
 * };
 *
 * const result = await ToolExecutor.execute(
 *   handler,
 *   schema,
 *   '{"name": "Alice", "age": 30}'
 * );
 * // result === "Alice is 30"
 * ```
 */
export class ToolExecutor {
  /**
   * Executes a tool with JSON arguments.
   *
   * @param handler - The function to execute
   * @param schema - JSON schema for validation
   * @param argumentsJson - JSON-encoded arguments
   * @returns Tool execution result as string
   * @throws Error if validation fails or execution errors
   *
   * @example
   * ```typescript
   * const handler = ({ a, b }: { a: number; b: number }) => a + b;
   * const schema = {
   *   type: 'object',
   *   properties: {
   *     a: { type: 'number' },
   *     b: { type: 'number' }
   *   },
   *   required: ['a', 'b']
   * };
   *
   * const result = await ToolExecutor.execute(
   *   handler,
   *   schema,
   *   '{"a": 5, "b": 3}'
   * );
   * // result === "8"
   * ```
   */
  static async execute<TParams = Record<string, unknown>>(
    handler: (params: TParams) => string | Promise<string>,
    schema: JSONSchema,
    argumentsJson: string
  ): Promise<string> {
    // Parse JSON arguments
    let args: unknown;
    try {
      args = JSON.parse(argumentsJson);
    } catch (error) {
      throw new Error(
        `Invalid JSON arguments: ${(error as Error).message}`
      );
    }

    // Validate arguments against schema
    ToolExecutor.validateArguments(args, schema);

    // Execute handler
    try {
      const result = await handler(args as TParams);
      return result;
    } catch (error) {
      // Preserve original error
      throw error;
    }
  }

  /**
   * Validates arguments against a JSON schema.
   *
   * @param args - The arguments to validate
   * @param schema - The schema to validate against
   * @throws Error if validation fails
   *
   * @example
   * ```typescript
   * const schema = {
   *   type: 'object',
   *   properties: { name: { type: 'string' } },
   *   required: ['name']
   * };
   *
   * ToolExecutor.validateArguments({ name: 'Alice' }, schema); // OK
   * ToolExecutor.validateArguments({}, schema); // Throws (missing 'name')
   * ```
   */
  static validateArguments(args: unknown, schema: JSONSchema): void {
    // Type validation
    if (schema.type === 'object' && typeof args !== 'object') {
      throw new Error(`Expected object, got ${typeof args}`);
    }

    if (schema.type === 'array' && !Array.isArray(args)) {
      throw new Error(`Expected array, got ${typeof args}`);
    }

    if (schema.type === 'string' && typeof args !== 'string') {
      throw new Error(`Expected string, got ${typeof args}`);
    }

    if (schema.type === 'number' && typeof args !== 'number') {
      throw new Error(`Expected number, got ${typeof args}`);
    }

    if (schema.type === 'boolean' && typeof args !== 'boolean') {
      throw new Error(`Expected boolean, got ${typeof args}`);
    }

    // Required properties validation
    if (schema.type === 'object' && schema.required) {
      const obj = args as Record<string, unknown>;
      for (const requiredProp of schema.required) {
        if (!(requiredProp in obj)) {
          throw new Error(`Missing required parameter: ${requiredProp}`);
        }
      }
    }

    // Property type validation
    if (schema.type === 'object' && schema.properties) {
      const obj = args as Record<string, unknown>;
      for (const [key, propSchema] of Object.entries(schema.properties)) {
        if (key in obj) {
          const value = obj[key];
          ToolExecutor.validateValue(value, propSchema, key);
        }
      }
    }

    // Array items validation
    if (schema.type === 'array' && schema.items) {
      const arr = args as unknown[];
      for (let i = 0; i < arr.length; i++) {
        ToolExecutor.validateValue(arr[i], schema.items, `[${i}]`);
      }
    }

    // Enum validation
    if (schema.enum && !schema.enum.includes(args)) {
      throw new Error(
        `Value must be one of: ${schema.enum.join(', ')}`
      );
    }

    // Number range validation
    if (schema.type === 'number' || schema.type === 'integer') {
      const num = args as number;
      if (schema.minimum !== undefined && num < schema.minimum) {
        throw new Error(`Value ${num} is less than minimum ${schema.minimum}`);
      }
      if (schema.maximum !== undefined && num > schema.maximum) {
        throw new Error(`Value ${num} is greater than maximum ${schema.maximum}`);
      }
    }

    // String length validation
    if (schema.type === 'string') {
      const str = args as string;
      if (schema.minLength !== undefined && str.length < schema.minLength) {
        throw new Error(
          `String length ${str.length} is less than minimum ${schema.minLength}`
        );
      }
      if (schema.maxLength !== undefined && str.length > schema.maxLength) {
        throw new Error(
          `String length ${str.length} is greater than maximum ${schema.maxLength}`
        );
      }
      if (schema.pattern) {
        const regex = new RegExp(schema.pattern);
        if (!regex.test(str)) {
          throw new Error(`String does not match pattern: ${schema.pattern}`);
        }
      }
    }

    // Array length validation
    if (schema.type === 'array') {
      const arr = args as unknown[];
      if (schema.minItems !== undefined && arr.length < schema.minItems) {
        throw new Error(
          `Array length ${arr.length} is less than minimum ${schema.minItems}`
        );
      }
      if (schema.maxItems !== undefined && arr.length > schema.maxItems) {
        throw new Error(
          `Array length ${arr.length} is greater than maximum ${schema.maxItems}`
        );
      }
    }
  }

  /**
   * Validates a single value against a schema.
   *
   * @param value - The value to validate
   * @param schema - The schema to validate against
   * @param path - Property path (for error messages)
   * @throws Error if validation fails
   */
  private static validateValue(
    value: unknown,
    schema: JSONSchema,
    path: string
  ): void {
    try {
      ToolExecutor.validateArguments(value, schema);
    } catch (error) {
      throw new Error(
        `Validation error for property '${path}': ${(error as Error).message}`
      );
    }
  }

  /**
   * Executes a tool without schema validation (use with caution).
   *
   * @param handler - The function to execute
   * @param argumentsJson - JSON-encoded arguments
   * @returns Tool execution result as string
   *
   * @example
   * ```typescript
   * const handler = (params: any) => `Got: ${params.value}`;
   * const result = await ToolExecutor.executeUnsafe(
   *   handler,
   *   '{"value": 42}'
   * );
   * ```
   */
  static async executeUnsafe<TParams = Record<string, unknown>>(
    handler: (params: TParams) => string | Promise<string>,
    argumentsJson: string
  ): Promise<string> {
    let args: unknown;
    try {
      args = JSON.parse(argumentsJson);
    } catch (error) {
      throw new Error(
        `Invalid JSON arguments: ${(error as Error).message}`
      );
    }

    try {
      const result = await handler(args as TParams);
      return result;
    } catch (error) {
      throw error;
    }
  }
}
