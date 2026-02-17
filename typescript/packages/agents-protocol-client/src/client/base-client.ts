/**
 * Base HTTP client with retry logic and error handling
 */

import {
  AgentProtocolClientConfig,
  RequestOptions,
} from '../types';
import {
  AgentProtocolError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
} from '../errors';

export class BaseClient {
  protected readonly baseUrl: string;
  protected readonly authToken?: string;
  protected readonly defaultTimeout: number;
  protected readonly maxRetries: number;
  protected readonly headers: Record<string, string>;
  protected readonly debug: boolean;

  constructor(config: AgentProtocolClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.authToken = config.authToken;
    this.defaultTimeout = config.timeout || 30000;
    this.maxRetries = config.maxRetries || 3;
    this.debug = config.debug || false;
    this.headers = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    if (this.authToken) {
      this.headers['Authorization'] = `Bearer ${this.authToken}`;
    }
  }

  /**
   * Make an HTTP request with retry logic
   */
  protected async request<T>(
    method: string,
    path: string,
    body?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const timeout = options?.timeout || this.defaultTimeout;
    const maxRetries = options?.maxRetries ?? this.maxRetries;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (this.debug) {
          console.log(`[AgentProtocolClient] ${method} ${url} (attempt ${attempt + 1})`);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        // Combine signals if provided
        const signal = options?.signal
          ? this.combineSignals(controller.signal, options.signal)
          : controller.signal;

        const response = await fetch(url, {
          method,
          headers: {
            ...this.headers,
            ...options?.headers,
          },
          body: body ? JSON.stringify(body) : undefined,
          signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw await this.handleErrorResponse(response);
        }

        // Handle 204 No Content
        if (response.status === 204) {
          return undefined as T;
        }

        const data = await response.json();
        return data as T;
      } catch (error) {
        lastError = error as Error;

        // Don't retry for certain errors
        if (
          error instanceof AuthenticationError ||
          error instanceof NotFoundError ||
          error instanceof ValidationError ||
          options?.signal?.aborted
        ) {
          throw error;
        }

        // Don't retry if this was the last attempt
        if (attempt === maxRetries) {
          break;
        }

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
        if (this.debug) {
          console.log(`[AgentProtocolClient] Retrying after ${delay}ms...`);
        }
        await this.sleep(delay);
      }
    }

    // All retries exhausted
    if (lastError instanceof Error) {
      throw lastError;
    }
    throw new AgentProtocolError('Request failed after all retries');
  }

  /**
   * Handle error responses from the API
   */
  private async handleErrorResponse(response: Response): Promise<Error> {
    let errorData: any;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: response.statusText };
    }

    const message = errorData.message || errorData.error || 'Unknown error';

    switch (response.status) {
      case 401:
        return new AuthenticationError(message);
      case 404:
        return new NotFoundError(errorData.resource || message);
      case 400:
        return new ValidationError(message, errorData.errors);
      case 429:
        return new RateLimitError(
          message,
          response.headers.get('Retry-After')
            ? parseInt(response.headers.get('Retry-After')!, 10)
            : undefined
        );
      default:
        return new AgentProtocolError(message, response.status, errorData);
    }
  }

  /**
   * Combine multiple AbortSignals
   */
  private combineSignals(...signals: AbortSignal[]): AbortSignal {
    const controller = new AbortController();

    for (const signal of signals) {
      if (signal.aborted) {
        controller.abort();
        break;
      }
      signal.addEventListener('abort', () => controller.abort());
    }

    return controller.signal;
  }

  /**
   * Sleep for a given duration
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * GET request
   */
  protected get<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('GET', path, undefined, options);
  }

  /**
   * POST request
   */
  protected post<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('POST', path, body, options);
  }

  /**
   * PUT request
   */
  protected put<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('PUT', path, body, options);
  }

  /**
   * PATCH request
   */
  protected patch<T>(path: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>('PATCH', path, body, options);
  }

  /**
   * DELETE request
   */
  protected delete<T>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>('DELETE', path, undefined, options);
  }
}
