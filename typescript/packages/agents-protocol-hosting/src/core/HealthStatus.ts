/**
 * Health status for agent host and dependencies.
 */
export interface HealthStatus {
  /**
   * Overall health status.
   *
   * - 'healthy': All systems operational
   * - 'degraded': Some non-critical systems failing
   * - 'unhealthy': Critical systems failing
   */
  status: 'healthy' | 'degraded' | 'unhealthy';

  /**
   * Individual component health checks.
   */
  checks: {
    /** Is LLM API reachable? */
    llmConnection: boolean;
    /** Is storage accessible? */
    storage: boolean;
    /** Is queue accessible? */
    queue: boolean;
    /** Is server accepting requests? */
    server: boolean;
  };

  /**
   * Uptime in milliseconds.
   */
  uptimeMs: number;

  /**
   * Optional details about failures.
   */
  details?: string;
}
