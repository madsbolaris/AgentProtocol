// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import type { JSONSchema } from '@microsoft/agents-protocol-abstractions';

/**
 * Generates JSON schemas from TypeScript functions.
 * Shared utility across Client and Hosting SDKs for consistent schema generation.
 *
 * NOTE: TypeScript has limited runtime reflection, so schemas must be provided
 * explicitly. This class validates and normalizes the provided schemas.
 *
 * @example
 * ```typescript
 * const schema = ToolSchemaGenerator.createObjectSchema({
 *   name: { type: 'string', description: 'The person name' },
 *   age: { type: 'number', description: 'The person age' }
 * }, ['name', 'age']);
 *
 * // schema.type === 'object'
 * // schema.required === ['name', 'age']
 * ```
 */
export class ToolSchemaGenerator {
  /**
   * Creates a simple object schema with typed properties.
   *
   * @param properties - Object properties with their schemas
   * @param required - Optional array of required property names
   * @returns Validated JSONSchema
   *
   * @example
   * ```typescript
   * const schema = ToolSchemaGenerator.createObjectSchema({
   *   query: { type: 'string', description: 'Search query' },
   *   limit: { type: 'number', description: 'Max results', default: 10 }
   * }, ['query']);
   * ```
   */
  static createObjectSchema(
    properties: Record<string, JSONSchema>,
    required?: string[]
  ): JSONSchema {
    return {
      type: 'object',
      properties,
      required: required || []
    };
  }

  /**
   * Creates a schema for a string parameter.
   *
   * @param description - Parameter description
   * @param options - Optional string constraints
   * @returns JSONSchema for string
   *
   * @example
   * ```typescript
   * const schema = ToolSchemaGenerator.createStringSchema(
   *   'User email address',
   *   { pattern: '^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$' }
   * );
   * ```
   */
  static createStringSchema(
    description: string,
    options?: {
      minLength?: number;
      maxLength?: number;
      pattern?: string;
      enum?: string[];
    }
  ): JSONSchema {
    return {
      type: 'string',
      description,
      ...options
    };
  }

  /**
   * Creates a schema for a number parameter.
   *
   * @param description - Parameter description
   * @param options - Optional number constraints
   * @returns JSONSchema for number
   *
   * @example
   * ```typescript
   * const schema = ToolSchemaGenerator.createNumberSchema(
   *   'User age',
   *   { minimum: 0, maximum: 120 }
   * );
   * ```
   */
  static createNumberSchema(
    description: string,
    options?: {
      minimum?: number;
      maximum?: number;
      type?: 'integer' | 'number';
    }
  ): JSONSchema {
    return {
      type: options?.type || 'number',
      description,
      minimum: options?.minimum,
      maximum: options?.maximum
    };
  }

  /**
   * Creates a schema for a boolean parameter.
   *
   * @param description - Parameter description
   * @returns JSONSchema for boolean
   *
   * @example
   * ```typescript
   * const schema = ToolSchemaGenerator.createBooleanSchema('Enable notifications');
   * ```
   */
  static createBooleanSchema(description: string): JSONSchema {
    return {
      type: 'boolean',
      description
    };
  }

  /**
   * Creates a schema for an array parameter.
   *
   * @param description - Parameter description
   * @param items - Schema for array items
   * @param options - Optional array constraints
   * @returns JSONSchema for array
   *
   * @example
   * ```typescript
   * const schema = ToolSchemaGenerator.createArraySchema(
   *   'List of tags',
   *   { type: 'string' },
   *   { minItems: 1, maxItems: 10 }
   * );
   * ```
   */
  static createArraySchema(
    description: string,
    items: JSONSchema,
    options?: {
      minItems?: number;
      maxItems?: number;
    }
  ): JSONSchema {
    return {
      type: 'array',
      description,
      items,
      minItems: options?.minItems,
      maxItems: options?.maxItems
    };
  }

  /**
   * Validates a JSON schema.
   *
   * @param schema - The schema to validate
   * @throws Error if schema is invalid
   *
   * @example
   * ```typescript
   * const schema = { type: 'object', properties: {} };
   * ToolSchemaGenerator.validateSchema(schema); // OK
   *
   * const invalid = { properties: {} }; // Missing type
   * ToolSchemaGenerator.validateSchema(invalid); // Throws
   * ```
   */
  static validateSchema(schema: JSONSchema): void {
    if (!schema.type) {
      throw new Error('Schema must have a type field');
    }

    if (schema.type === 'object' && !schema.properties) {
      throw new Error('Object schema must have properties');
    }

    if (schema.type === 'array' && !schema.items) {
      throw new Error('Array schema must have items');
    }

    // Validate nested schemas
    if (schema.properties) {
      for (const [key, value] of Object.entries(schema.properties)) {
        try {
          ToolSchemaGenerator.validateSchema(value);
        } catch (error) {
          throw new Error(`Invalid schema for property '${key}': ${(error as Error).message}`);
        }
      }
    }

    if (schema.items && typeof schema.items === 'object' && !Array.isArray(schema.items)) {
      ToolSchemaGenerator.validateSchema(schema.items);
    }
  }

  /**
   * Merges two schemas (useful for extending base schemas).
   *
   * @param base - Base schema
   * @param extension - Schema to merge in
   * @returns Merged schema
   *
   * @example
   * ```typescript
   * const base = {
   *   type: 'object',
   *   properties: { name: { type: 'string' } },
   *   required: ['name']
   * };
   *
   * const extension = {
   *   properties: { age: { type: 'number' } },
   *   required: ['age']
   * };
   *
   * const merged = ToolSchemaGenerator.mergeSchemas(base, extension);
   * // merged.properties has both name and age
   * // merged.required includes both name and age
   * ```
   */
  static mergeSchemas(base: JSONSchema, extension: Partial<JSONSchema>): JSONSchema {
    return {
      ...base,
      ...extension,
      properties: {
        ...base.properties,
        ...extension.properties
      },
      required: [
        ...(base.required || []),
        ...(extension.required || [])
      ]
    };
  }
}
