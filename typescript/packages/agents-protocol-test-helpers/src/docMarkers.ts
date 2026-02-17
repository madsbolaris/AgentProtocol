/**
 * Decorators for marking tests as documentation examples.
 *
 * Tests marked with @docExample can be extracted for use in documentation.
 * The actual code to extract should be wrapped with // doc-example-start/end comments.
 */

/**
 * Metadata for a documentation example
 */
export interface DocExampleMetadata {
  /** Unique identifier for this example (e.g., "basic-serialization") */
  testId: string;
  /** Human-readable title for the example */
  title: string;
  /** Optional longer description of what the example demonstrates */
  description?: string;
  /** Category for organization (e.g., "serialization", "deserialization") */
  category?: string;
  /** Additional tags for filtering and search */
  tags?: string[];
}

/** Registry for all doc examples */
const _docExamples: Map<string, DocExampleMetadata> = new Map();

/**
 * Decorator to mark a test method as a documentation example.
 *
 * @param metadata - Metadata describing the example
 * @returns Method decorator
 *
 * @example
 * ```typescript
 * class TestExamples {
 *   @docExample({
 *     testId: 'basic-message',
 *     title: 'Create a Basic Message',
 *     description: 'Demonstrates creating a simple message',
 *     category: 'serialization',
 *     tags: ['basic', 'message']
 *   })
 *   testBasicMessage() {
 *     // doc-example-start
 *     const message = createMessage();
 *     // doc-example-end
 *
 *     expect(message).toBeDefined();
 *   }
 * }
 * ```
 */
export function docExample(metadata: DocExampleMetadata) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    // Store metadata in registry
    _docExamples.set(metadata.testId, {
      ...metadata,
    });

    // Attach metadata to the descriptor for introspection
    if (!descriptor.value._docExampleMetadata) {
      descriptor.value._docExampleMetadata = metadata;
    }

    return descriptor;
  };
}

/**
 * Get all registered documentation examples.
 *
 * @returns Map of test IDs to their metadata
 */
export function getAllDocExamples(): Map<string, DocExampleMetadata> {
  return new Map(_docExamples);
}

/**
 * Get metadata for a specific documentation example.
 *
 * @param testId - The unique test identifier
 * @returns The metadata for the example, or undefined if not found
 */
export function getDocExample(testId: string): DocExampleMetadata | undefined {
  return _docExamples.get(testId);
}
