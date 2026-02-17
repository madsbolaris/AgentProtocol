/**
 * Interface for streaming LLM responses.
 */
export interface IStreamHandler {
  /**
   * Called when streaming starts.
   */
  onStart(): Promise<void>;

  /**
   * Called for each token.
   *
   * @param token - The token text
   */
  onToken(token: string): Promise<void>;

  /**
   * Called when streaming completes.
   */
  onComplete(): Promise<void>;

  /**
   * Called if streaming fails.
   *
   * @param error - The error that occurred
   */
  onError(error: Error): Promise<void>;
}
