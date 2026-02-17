/**
 * Thread validator for conversation threads.
 *
 * Validates that:
 * - Messages are in chronological order
 * - Message IDs are unique
 * - Tool results have matching function calls (call-id validation)
 * - Function names match between calls and results
 * - Call-ids are unique within a message
 * - Call-ids are only fulfilled once
 * - Messages have non-empty contents
 * - Messages have valid roles
 * - Required fields are present
 */

import { ValidationResult } from './ValidationResult';

/**
 * Validates conversation threads
 */
export class ThreadValidator {
  /** Valid message roles per spec */
  private static readonly VALID_ROLES = new Set(['user', 'agent', 'system', 'tool', 'developer', 'channel']);

  /**
   * Validate a conversation thread
   */
  validate(thread: any): ValidationResult {
    const result = ValidationResult.success();

    // Track state during validation
    const messageIds = new Set<string>();
    const functionCalls = new Map<string, string>(); // call_id -> function_name
    const fulfilledCallIds = new Set<string>(); // Track which calls have been fulfilled
    let lastTimestamp: Date | null = null;

    // Validate thread ID
    if (!thread.threadId && !thread.thread_id) {
      result.addError('Thread ID is required', { field: 'threadId', code: 'THREAD_001' });
    }

    // Validate messages
    if (!thread.messages) {
      result.addError('Thread must have messages attribute', { field: 'messages', code: 'THREAD_002' });
      return result;
    }

    if (!Array.isArray(thread.messages)) {
      result.addError('Thread messages must be an array', { field: 'messages', code: 'THREAD_002' });
      return result;
    }

    for (let idx = 0; idx < thread.messages.length; idx++) {
      const message = thread.messages[idx];

      // Validate message role
      this.validateMessageRole(message, idx, result);

      // Validate message ID uniqueness
      const messageId = message.messageId || message.message_id;
      if (messageId) {
        if (messageIds.has(messageId)) {
          result.addError(
            `Duplicate message ID: ${messageId}`,
            { field: `messages[${idx}].messageId`, code: 'THREAD_003' }
          );
        }
        messageIds.add(messageId);
      }

      // Validate chronological order
      const createdAt = message.createdAt || message.created_at;
      if (createdAt) {
        const timestamp = typeof createdAt === 'string' ? new Date(createdAt) : createdAt;
        if (lastTimestamp && timestamp < lastTimestamp) {
          result.addError(
            `Messages not in chronological order at index ${idx}`,
            { field: `messages[${idx}].createdAt`, code: 'THREAD_004' }
          );
        }
        lastTimestamp = timestamp;
      }

      // Validate message contents and track function calls
      this.validateMessageContents(
        message,
        idx,
        functionCalls,
        fulfilledCallIds,
        result
      );
    }

    // Check for unfulfilled function calls
    const unfulfilledCalls = Array.from(functionCalls.keys()).filter(
      callId => !fulfilledCallIds.has(callId)
    );
    if (unfulfilledCalls.length > 0) {
      result.addWarning(
        `${unfulfilledCalls.length} function call(s) without matching result: ${unfulfilledCalls.join(', ')}`
      );
    }

    return result;
  }

  /**
   * Validate message has a valid role
   */
  private validateMessageRole(message: any, messageIdx: number, result: ValidationResult): void {
    const role = message.role;
    if (!role) {
      return; // Role might be inferred from message type
    }

    if (!ThreadValidator.VALID_ROLES.has(role)) {
      result.addError(
        `Invalid message role: ${role}. Must be one of: ${Array.from(ThreadValidator.VALID_ROLES).join(', ')}`,
        { field: `messages[${messageIdx}].role`, code: 'THREAD_005' }
      );
    }
  }

  /**
   * Validate message contents and track function calls
   */
  private validateMessageContents(
    message: any,
    messageIdx: number,
    functionCalls: Map<string, string>,
    fulfilledCallIds: Set<string>,
    result: ValidationResult
  ): void {
    const contents = message.contents || message.content || [];

    if (!Array.isArray(contents)) {
      result.addError(
        'Message contents must be an array',
        { field: `messages[${messageIdx}].contents`, code: 'THREAD_006' }
      );
      return;
    }

    if (contents.length === 0) {
      result.addWarning(`Message at index ${messageIdx} has empty contents`);
    }

    // Track call IDs within this message for uniqueness check
    const callIdsInMessage = new Set<string>();

    for (let contentIdx = 0; contentIdx < contents.length; contentIdx++) {
      const content = contents[contentIdx];
      const kind = content.kind || content.type;

      // Validate function calls
      if (kind === 'functionCall' || kind === 'function_call') {
        const callId = content.callId || content.call_id;
        const name = content.name;

        if (!callId) {
          result.addError(
            'Function call missing call-id',
            { field: `messages[${messageIdx}].contents[${contentIdx}].callId`, code: 'THREAD_007' }
          );
        } else {
          // Check for duplicate call-id within message
          if (callIdsInMessage.has(callId)) {
            result.addError(
              `Duplicate call-id in message: ${callId}`,
              { field: `messages[${messageIdx}].contents[${contentIdx}].callId`, code: 'THREAD_008' }
            );
          }
          callIdsInMessage.add(callId);

          // Track function call for later validation
          functionCalls.set(callId, name || '');
        }

        if (!name) {
          result.addError(
            'Function call missing name',
            { field: `messages[${messageIdx}].contents[${contentIdx}].name`, code: 'THREAD_009' }
          );
        }
      }

      // Validate function results
      if (kind === 'functionResult' || kind === 'function_result') {
        const callId = content.callId || content.call_id;
        const name = content.name;

        if (!callId) {
          result.addError(
            'Function result missing call-id',
            { field: `messages[${messageIdx}].contents[${contentIdx}].callId`, code: 'THREAD_010' }
          );
        } else {
          // Check if call-id has matching function call
          if (!functionCalls.has(callId)) {
            result.addError(
              `Function result has call-id ${callId} but no matching function call`,
              { field: `messages[${messageIdx}].contents[${contentIdx}].callId`, code: 'THREAD_011' }
            );
          } else {
            // Check if function names match
            const expectedName = functionCalls.get(callId);
            if (name && expectedName && name !== expectedName) {
              result.addError(
                `Function result name '${name}' does not match function call name '${expectedName}' for call-id ${callId}`,
                { field: `messages[${messageIdx}].contents[${contentIdx}].name`, code: 'THREAD_012' }
              );
            }

            // Check if call-id already fulfilled
            if (fulfilledCallIds.has(callId)) {
              result.addError(
                `Function result has call-id ${callId} which was already fulfilled`,
                { field: `messages[${messageIdx}].contents[${contentIdx}].callId`, code: 'THREAD_013' }
              );
            }
            fulfilledCallIds.add(callId);
          }
        }
      }

      // Validate text content
      if (kind === 'text') {
        const text = content.text || content.content;
        if (!text || text.trim().length === 0) {
          result.addWarning(`Text content at messages[${messageIdx}].contents[${contentIdx}] is empty`);
        }
      }
    }
  }
}
