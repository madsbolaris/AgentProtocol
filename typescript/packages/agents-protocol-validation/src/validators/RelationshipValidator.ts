import type { Thread, ChatMessage } from '@microsoft/agents-protocol-abstractions';
import type { IValidator } from '../core/IValidator';
import { ValidationContext } from '../core/ValidationContext';
import { ValidationResult } from '../core/ValidationResult';
import { ValidationError, ValidationSeverity } from '../core/ValidationError';
import { ValidationErrorCode } from '../core/ValidationErrorCode';

/**
 * Validator for cross-message relationships.
 * Validates call-id matching, parent-message-id references, and other relationships.
 */
export class RelationshipValidator implements IValidator<Thread> {
  public validate(thread: Thread, context?: ValidationContext): ValidationResult {
    const ctx = context || new ValidationContext();
    ctx.thread = thread;

    const errors: ValidationError[] = [];

    // Build registries first
    if (thread.messages) {
      for (const message of thread.messages) {
        // Register message
        if (message.messageId && !ctx.registerMessage(message)) {
          errors.push(
            new ValidationError(
              ValidationErrorCode.MSG_002,
              `Duplicate message-id: ${message.messageId}`,
              'messageId'
            )
          );
        }

        // Register function calls and results from contents
        if (message.contents) {
          for (const content of message.contents) {
            if (content.kind === 'functionCall') {
              const functionCall = content as any;
              if (functionCall.callId && !ctx.registerFunctionCall(functionCall)) {
                errors.push(
                  new ValidationError(
                    ValidationErrorCode.REL_003,
                    `Duplicate call-id: ${functionCall.callId}`,
                    'callId'
                  )
                );
              }
            } else if (content.kind === 'functionResult') {
              const functionResult = content as any;
              if (functionResult.callId) {
                if (!ctx.hasFunctionCall(functionResult.callId)) {
                  errors.push(
                    new ValidationError(
                      ValidationErrorCode.REL_004,
                      `FunctionResultContent call-id does not match any FunctionCall: ${functionResult.callId}`,
                      'callId'
                    )
                  );
                }
                if (!ctx.registerFunctionResult(functionResult)) {
                  errors.push(
                    new ValidationError(
                      ValidationErrorCode.REL_006,
                      `Duplicate FunctionResultContent for call-id: ${functionResult.callId}`,
                      'callId'
                    )
                  );
                }
              }
            }
          }
        }
      }
    }

    // REL-007: Every FunctionCall should have a corresponding FunctionResult (warning)
    for (const [callId, functionCall] of ctx.functionCallRegistry) {
      if (!ctx.hasFunctionResult(callId)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.REL_007,
            `FunctionCall with call-id "${callId}" has no corresponding FunctionResult`,
            'callId',
            ValidationSeverity.Warning
          )
        );
      }
    }

    // REL-011: Validate message ordering (tool results should follow agent messages with calls)
    errors.push(...this.validateMessageOrdering(thread));

    // REL-012: Validate parent-message-id forms valid DAG (no cycles)
    // This is handled by ThreadValidator

    // REL-013: Validate all parent-message-id references exist
    if (thread.messages) {
      for (const message of thread.messages) {
        if (message.parentMessageId && !ctx.hasMessage(message.parentMessageId)) {
          errors.push(
            new ValidationError(
              ValidationErrorCode.REL_013,
              `parent-message-id references non-existent message: ${message.parentMessageId}`,
              'parentMessageId'
            )
          );
        }
      }
    }

    return new ValidationResult(errors);
  }

  private validateMessageOrdering(thread: Thread): ValidationError[] {
    const errors: ValidationError[] = [];

    if (!thread.messages || thread.messages.length === 0) {
      return errors;
    }

    // REL-011: Tool messages should follow agent messages that contain the referenced function call
    for (let i = 0; i < thread.messages.length; i++) {
      const message = thread.messages[i];
      if (this.isToolMessage(message)) {
        const toolMessage = message as any;
        if (toolMessage.callId) {
          // Find the agent message with this call-id
          let foundPrecedingCall = false;
          for (let j = i - 1; j >= 0; j--) {
            const prevMessage = thread.messages[j];
            if (this.isAgentMessage(prevMessage) && prevMessage.contents) {
              for (const content of prevMessage.contents) {
                if (content.kind === 'functionCall') {
                  const functionCall = content as any;
                  if (functionCall.callId === toolMessage.callId) {
                    foundPrecedingCall = true;
                    break;
                  }
                }
              }
            }
            if (foundPrecedingCall) break;
          }

          if (!foundPrecedingCall) {
            errors.push(
              new ValidationError(
                ValidationErrorCode.REL_011,
                `ToolMessage with call-id "${toolMessage.callId}" does not follow an AgentMessage with matching FunctionCall`,
                'callId',
                ValidationSeverity.Warning
              )
            );
          }
        }
      }
    }

    return errors;
  }

  private isToolMessage(message: ChatMessage): boolean {
    return (message as any).role === 'tool' || message.constructor?.name?.includes('Tool');
  }

  private isAgentMessage(message: ChatMessage): boolean {
    const role = (message as any).role;
    return (
      role === 'agent' ||
      role === 'assistant' ||
      message.constructor?.name?.includes('Agent') ||
      message.constructor?.name?.includes('Assistant')
    );
  }
}
