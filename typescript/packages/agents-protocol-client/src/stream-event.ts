/**
 * Enhanced streaming event types for high-level API
 */

/**
 * Generic stream event wrapper with typed data extraction
 */
export interface StreamEvent<T = unknown> {
  /**
   * Event type (e.g., "message.created", "run.completed")
   */
  eventType: string;

  /**
   * Raw event data
   */
  data: T;

  /**
   * Extracts and deserializes data as a specific type
   * @param type Constructor function for the target type
   * @returns Typed data instance
   */
  getDataAs<TData>(type: new () => TData): TData;
}

/**
 * Implementation of StreamEvent with data extraction
 */
export class StreamEventImpl<T = unknown> implements StreamEvent<T> {
  constructor(
    public readonly eventType: string,
    public readonly data: T
  ) {}

  /**
   * Extracts and deserializes data as a specific type
   * @param _type Constructor function (not used in JS, kept for API compatibility)
   * @returns Typed data instance
   */
  getDataAs<TData>(_type: new () => TData): TData {
    // In TypeScript, we can't instantiate generic types at runtime
    // This method exists for API compatibility with .NET
    // The data is already parsed, so we just cast it
    return this.data as unknown as TData;
  }

  /**
   * Convenience method to get data directly
   * @returns The event data
   */
  getData<TData>(): TData {
    return this.data as unknown as TData;
  }
}

/**
 * Creates a StreamEvent from raw event data
 * @param eventType Event type string
 * @param data Event data
 * @returns StreamEvent instance
 */
export function createStreamEvent<T = unknown>(
  eventType: string,
  data: T
): StreamEvent<T> {
  return new StreamEventImpl(eventType, data);
}
