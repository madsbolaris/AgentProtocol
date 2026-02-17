/**
 * Base HTTP client for API requests
 * Uses native fetch with type-safe error handling
 */

/**
 * API Error class for structured error handling
 */
export class ApiError extends Error {
  status: number
  data?: unknown

  constructor(message: string, status: number, data?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

/**
 * Base API client configuration
 */
export interface ClientConfig {
  baseUrl?: string
  timeout?: number
  headers?: Record<string, string>
}

/**
 * Default configuration
 */
const DEFAULT_CONFIG: Required<ClientConfig> = {
  baseUrl: '/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
}

/**
 * HTTP client class
 */
export class HttpClient {
  private config: Required<ClientConfig>

  constructor(config: ClientConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * Make a GET request
   */
  async get<T>(path: string, options?: RequestInit): Promise<T> {
    return this.request<T>('GET', path, undefined, options)
  }

  /**
   * Make a POST request
   */
  async post<T>(path: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>('POST', path, data, options)
  }

  /**
   * Make a PUT request
   */
  async put<T>(path: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>('PUT', path, data, options)
  }

  /**
   * Make a DELETE request
   */
  async delete<T>(path: string, options?: RequestInit): Promise<T> {
    return this.request<T>('DELETE', path, undefined, options)
  }

  /**
   * Core request method with timeout and error handling
   */
  private async request<T>(
    method: string,
    path: string,
    data?: unknown,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`

    // Create AbortController for timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout)

    try {
      const response = await fetch(url, {
        method,
        headers: {
          ...this.config.headers,
          ...options?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
        ...options,
      })

      clearTimeout(timeoutId)

      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiError(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      // Parse JSON response
      const result = await response.json()
      return result as T
    } catch (error) {
      clearTimeout(timeoutId)

      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408)
      }

      // Re-throw ApiError
      if (error instanceof ApiError) {
        throw error
      }

      // Handle other errors
      throw new ApiError(error instanceof Error ? error.message : 'Unknown error', 0, error)
    }
  }
}

/**
 * Default HTTP client instance
 */
export const httpClient = new HttpClient()

/**
 * Create a new HTTP client with custom configuration
 */
export const createHttpClient = (config: ClientConfig): HttpClient => {
  return new HttpClient(config)
}
