import type { ChatMessage, Thread, FunctionCallContent, FunctionResultContent } from '@microsoft/agents-protocol-abstractions';

/**
 * Context for validation that tracks cross-message relationships and thread-level state.
 * Used to validate relationships like call-id matching, message-id uniqueness, and parent references.
 */
export class ValidationContext {
  /**
   * Registry of all messages in the thread, indexed by message-id.
   * Used to validate parent-message-id references and detect duplicate message-ids.
   */
  public readonly messageRegistry: Map<string, ChatMessage> = new Map();

  /**
   * Registry of all function calls, indexed by call-id.
   * Used to validate that tool results reference valid function calls.
   */
  public readonly functionCallRegistry: Map<string, FunctionCallContent> = new Map();

  /**
   * Registry of all function results, indexed by call-id.
   * Used to validate that each call-id has at most one result.
   */
  public readonly functionResultRegistry: Map<string, FunctionResultContent> = new Map();

  /**
   * The thread being validated (if validating at thread level).
   */
  public thread?: Thread;

  /**
   * Registers a message in the context.
   * @param message The message to register
   * @returns true if registered successfully, false if message-id already exists
   */
  public registerMessage(message: ChatMessage): boolean {
    if (!message.messageId) {
      return true; // Will be caught by message validator
    }

    if (this.messageRegistry.has(message.messageId)) {
      return false; // Duplicate message-id
    }

    this.messageRegistry.set(message.messageId, message);
    return true;
  }

  /**
   * Registers a function call in the context.
   * @param functionCall The function call to register
   * @returns true if registered successfully, false if call-id already exists
   */
  public registerFunctionCall(functionCall: FunctionCallContent): boolean {
    if (!functionCall.callId) {
      return true; // Will be caught by content validator
    }

    if (this.functionCallRegistry.has(functionCall.callId)) {
      return false; // Duplicate call-id
    }

    this.functionCallRegistry.set(functionCall.callId, functionCall);
    return true;
  }

  /**
   * Registers a function result in the context.
   * @param functionResult The function result to register
   * @returns true if registered successfully, false if call-id already exists
   */
  public registerFunctionResult(functionResult: FunctionResultContent): boolean {
    if (!functionResult.callId) {
      return true; // Will be caught by content validator
    }

    if (this.functionResultRegistry.has(functionResult.callId)) {
      return false; // Duplicate result for same call-id
    }

    this.functionResultRegistry.set(functionResult.callId, functionResult);
    return true;
  }

  /**
   * Checks if a message with the given message-id exists.
   */
  public hasMessage(messageId: string): boolean {
    return this.messageRegistry.has(messageId);
  }

  /**
   * Gets a message by message-id.
   */
  public getMessage(messageId: string): ChatMessage | undefined {
    return this.messageRegistry.get(messageId);
  }

  /**
   * Checks if a function call with the given call-id exists.
   */
  public hasFunctionCall(callId: string): boolean {
    return this.functionCallRegistry.has(callId);
  }

  /**
   * Gets a function call by call-id.
   */
  public getFunctionCall(callId: string): FunctionCallContent | undefined {
    return this.functionCallRegistry.get(callId);
  }

  /**
   * Checks if a function result with the given call-id exists.
   */
  public hasFunctionResult(callId: string): boolean {
    return this.functionResultRegistry.has(callId);
  }

  /**
   * Gets a function result by call-id.
   */
  public getFunctionResult(callId: string): FunctionResultContent | undefined {
    return this.functionResultRegistry.get(callId);
  }
}
