/**
 * Represents the result of processing a turn in an agent conversation.
 * Provides explicit control flow for message handling.
 *
 * Handlers execute in registration order. The first handler to return
 * Consumed or Replied stops the chain.
 */
export enum TurnResult {
  /**
   * Continue processing - pass to next handler or LLM.
   * Use this when you want preprocessing but don't want to consume the message.
   *
   * @example
   * ```typescript
   * async function logMessages(
   *   msg: ChatMessage,
   *   ctx: IAgentContext
   * ): Promise<TurnResult> {
   *   await ctx.logAsync(`Received: ${msg.text}`);
   *   return TurnResult.Continue;  // Let LLM handle it
   * }
   * ```
   */
  Continue = 'continue',

  /**
   * Message has been consumed - stop processing, no response needed.
   * Use this for reactions, typing indicators, or other events that don't need a response.
   *
   * @example
   * ```typescript
   * async function handleTyping(
   *   msg: ChatMessage,
   *   ctx: IAgentContext
   * ): Promise<TurnResult> {
   *   if (msg.type === 'typing') {
   *     // Just acknowledge, no response needed
   *     return TurnResult.Consumed;
   *   }
   *   return TurnResult.Continue;
   * }
   * ```
   */
  Consumed = 'consumed',

  /**
   * A response has already been sent - stop processing.
   * Use this when your handler has sent a response via ctx.respondAsync().
   *
   * @example
   * ```typescript
   * async function handleCommands(
   *   msg: ChatMessage,
   *   ctx: IAgentContext
   * ): Promise<TurnResult> {
   *   if (msg.text === '/help') {
   *     await ctx.respondAsync('Available commands: /help, /about');
   *     return TurnResult.Replied;  // We handled it
   *   }
   *   return TurnResult.Continue;
   * }
   * ```
   */
  Replied = 'replied'
}
