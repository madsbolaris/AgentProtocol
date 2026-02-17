/**
 * Client configuration and types
 */

export interface AgentProtocolClientConfig {
  /** Base URL of the Agent Protocol API */
  baseUrl: string;

  /** Authentication token (Bearer) */
  authToken?: string;

  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;

  /** Maximum retry attempts for failed requests (default: 3) */
  maxRetries?: number;

  /** Custom headers to include in all requests */
  headers?: Record<string, string>;

  /** Enable debug logging */
  debug?: boolean;

  /** Enable automatic logging of conversations to XML files (default: false) */
  enableLogging?: boolean;

  /** Directory path for saving conversation logs (default: logs/conversations) */
  logDirectory?: string;
}

export interface RequestOptions {
  /** Override timeout for this request */
  timeout?: number;

  /** Override retry attempts for this request */
  maxRetries?: number;

  /** Additional headers for this request */
  headers?: Record<string, string>;

  /** AbortController signal for request cancellation */
  signal?: AbortSignal;
}

export interface PaginationParams {
  /** Maximum number of items to return */
  limit?: number;

  /** Cursor for pagination */
  after?: string;

  /** Cursor for pagination (backwards) */
  before?: string;
}

export interface ListResponse<T> {
  /** Array of items */
  data: T[];

  /** Pagination information */
  hasMore: boolean;

  /** First item ID in the list */
  firstId?: string;

  /** Last item ID in the list */
  lastId?: string;
}
