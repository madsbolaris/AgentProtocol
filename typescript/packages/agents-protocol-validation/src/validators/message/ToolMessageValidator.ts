import type { ToolMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for ToolMessage.
 */
export class ToolMessageValidator extends MessageValidatorBase<ToolMessage> {
  protected validateSpecificFields(message: ToolMessage, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // MSG-012: Tool messages must have toolCallId
    const callIdError = this.validateNotEmpty(
      message.toolCallId,
      'toolCallId',
      ValidationErrorCode.MSG_012,
      'ToolMessage must have toolCallId'
    );
    if (callIdError) {
      errors.push(callIdError);
    }

    // REL-005: toolCallId must match a FunctionCall in preceding AgentMessage
    if (context && message.toolCallId) {
      if (!context.hasFunctionCall(message.toolCallId)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.REL_005,
            `ToolMessage toolCallId does not match any FunctionCall: ${message.toolCallId}`,
            'toolCallId'
          )
        );
      }
    }

    // ROLE-008: ToolMessage should have exactly one function-result or error content
    if (message.contents) {
      const resultCount = message.contents.filter(
        (c) => c.kind === 'functionResult' || c.kind === 'error'
      ).length;
      if (resultCount === 0) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.ROLE_008,
            'ToolMessage should have at least one function-result or error content',
            'contents'
          )
        );
      }
    }

    return errors;
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-004: Tool messages can only contain function-result and error
    return ['functionResult', 'error'];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_004;
  }

  protected getMessageTypeName(): string {
    return 'ToolMessage';
  }

  protected requiresContent(): boolean {
    return true;
  }
}
