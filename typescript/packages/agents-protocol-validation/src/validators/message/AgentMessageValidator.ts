import type { AgentMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for AgentMessage.
 */
export class AgentMessageValidator extends MessageValidatorBase<AgentMessage> {
  protected validateSpecificFields(message: AgentMessage, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // MSG-011: Agent messages must have contents (checked in base class)

    // ROLE-007: At most one text-reasoning content
    if (message.contents) {
      const reasoningCount = message.contents.filter((c) => c.kind === 'textReasoning').length;
      if (reasoningCount > 1) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.ROLE_007,
            'AgentMessage can have at most one text-reasoning content',
            'contents'
          )
        );
      }

      // BIZ-001: If text-reasoning exists, it must come before other content
      const reasoningIndex = message.contents.findIndex((c) => c.kind === 'textReasoning');
      if (reasoningIndex > 0) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.BIZ_001,
            'text-reasoning content must come before other content types',
            'contents'
          )
        );
      }
    }

    // REL-009, REL-010: Validate function calls (if context available)
    // These are validated at content level and by relationship validator

    return errors;
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-003: Agent messages can contain text, functionCall, textReasoning, refusal, error
    return ['text', 'functionCall', 'textReasoning', 'refusal', 'error'];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_003;
  }

  protected getMessageTypeName(): string {
    return 'AgentMessage';
  }

  protected requiresContent(): boolean {
    return true;
  }
}
