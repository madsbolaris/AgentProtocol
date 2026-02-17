import type { Thread } from '@microsoft/agents-protocol-abstractions';
import type { IValidator } from '../core/IValidator';
import { ValidationContext } from '../core/ValidationContext';
import { ValidationResult } from '../core/ValidationResult';
import { ValidationError } from '../core/ValidationError';
import { ValidationErrorCode } from '../core/ValidationErrorCode';
import { SystemMessageValidator } from './message/SystemMessageValidator';
import { DeveloperMessageValidator } from './message/DeveloperMessageValidator';
import { UserMessageValidator } from './message/UserMessageValidator';
import { AgentMessageValidator } from './message/AgentMessageValidator';
import { ToolMessageValidator } from './message/ToolMessageValidator';
import { ChannelMessageValidator } from './message/ChannelMessageValidator';

/**
 * Validator for Thread.
 * Orchestrates validation across the entire thread, validates relationships between messages,
 * and enforces thread-level constraints.
 */
export class ThreadValidator implements IValidator<Thread> {
  private readonly systemMessageValidator = new SystemMessageValidator();
  private readonly developerMessageValidator = new DeveloperMessageValidator();
  private readonly userMessageValidator = new UserMessageValidator();
  private readonly agentMessageValidator = new AgentMessageValidator();
  private readonly toolMessageValidator = new ToolMessageValidator();
  private readonly channelMessageValidator = new ChannelMessageValidator();

  public validate(thread: Thread, context?: ValidationContext): ValidationResult {
    const ctx = context || new ValidationContext();
    ctx.thread = thread;

    const errors: ValidationError[] = [];

    // THR-001: thread-id must be non-empty
    if (!thread.threadId || thread.threadId.trim().length === 0) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.THR_001,
          'thread-id must be non-empty',
          'threadId'
        )
      );
    }

    // THR-002: status must be valid (if present)
    if (thread.status) {
      const validStatuses = ['active', 'closed', 'archived'];
      if (!validStatuses.includes(thread.status)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.THR_002,
            `status must be one of: ${validStatuses.join(', ')}`,
            'status'
          )
        );
      }
    }

    // THR-003: created-at must be before last-message-at (if both present)
    if (thread.createdAt && thread.lastMessageAt) {
      const createdAt = new Date(thread.createdAt);
      const lastMessageAt = new Date(thread.lastMessageAt);
      if (createdAt > lastMessageAt) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.THR_003,
            'created-at must be before last-message-at',
            'createdAt'
          )
        );
      }
    }

    // THR-004: unread-count must be non-negative (if present)
    if (thread.unreadCount !== null && thread.unreadCount !== undefined && thread.unreadCount < 0) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.THR_004,
          'unread-count must be non-negative',
          'unreadCount'
        )
      );
    }

    // THR-005: Validate all messages
    if (!thread.messages || thread.messages.length === 0) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.THR_005,
          'Thread must have at least one message',
          'messages'
        )
      );
    } else {
      for (const message of thread.messages) {
        const validator = this.getValidatorForMessage(message);
        if (validator) {
          const result = validator.validate(message, ctx);
          errors.push(...result.errors);
        }
      }
    }

    // THR-006: Validate parent-message-id DAG (no cycles)
    const dagErrors = this.validateParentMessageIdDag(thread, ctx);
    errors.push(...dagErrors);

    // THR-007: All messages must have unique message-ids (checked by context registration)

    return new ValidationResult(errors);
  }

  private getValidatorForMessage(message: any): IValidator<any> | null {
    // Determine message type and return appropriate validator
    // This assumes messages have a discriminator or we can check their type
    if ('role' in message) {
      switch (message.role) {
        case 'system':
          return this.systemMessageValidator;
        case 'developer':
          return this.developerMessageValidator;
        case 'user':
          return this.userMessageValidator;
        case 'agent':
        case 'assistant':
          return this.agentMessageValidator;
        case 'tool':
          return this.toolMessageValidator;
        case 'channel':
          return this.channelMessageValidator;
      }
    }

    // Fallback: check constructor name or kind
    const typeName = message.constructor?.name;
    if (typeName) {
      if (typeName.includes('System')) return this.systemMessageValidator;
      if (typeName.includes('Developer')) return this.developerMessageValidator;
      if (typeName.includes('User')) return this.userMessageValidator;
      if (typeName.includes('Agent') || typeName.includes('Assistant'))
        return this.agentMessageValidator;
      if (typeName.includes('Tool')) return this.toolMessageValidator;
      if (typeName.includes('Channel')) return this.channelMessageValidator;
    }

    return null;
  }

  private validateParentMessageIdDag(thread: Thread, context: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    // Check for cycles in parent-message-id references
    for (const message of thread.messages) {
      if (!message.messageId) continue;

      if (!visited.has(message.messageId)) {
        const cycleError = this.detectCycle(message.messageId, context, visited, recursionStack);
        if (cycleError) {
          errors.push(cycleError);
        }
      }
    }

    return errors;
  }

  private detectCycle(
    messageId: string,
    context: ValidationContext,
    visited: Set<string>,
    recursionStack: Set<string>
  ): ValidationError | null {
    visited.add(messageId);
    recursionStack.add(messageId);

    const message = context.getMessage(messageId);
    if (message?.parentMessageId) {
      if (!visited.has(message.parentMessageId)) {
        const cycleError = this.detectCycle(
          message.parentMessageId,
          context,
          visited,
          recursionStack
        );
        if (cycleError) return cycleError;
      } else if (recursionStack.has(message.parentMessageId)) {
        return new ValidationError(
          ValidationErrorCode.THR_006,
          `Cycle detected in parent-message-id references: ${messageId} -> ${message.parentMessageId}`,
          'parentMessageId'
        );
      }
    }

    recursionStack.delete(messageId);
    return null;
  }
}
