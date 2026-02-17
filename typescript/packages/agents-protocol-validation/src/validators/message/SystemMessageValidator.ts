import type { SystemMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for SystemMessage.
 */
export class SystemMessageValidator extends MessageValidatorBase<SystemMessage> {
  protected validateSpecificFields(message: SystemMessage, context?: ValidationContext): ValidationError[] {
    // MSG-008: System messages have no special fields beyond common ones
    return [];
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-001: System messages can only contain text, document, adaptive-card
    return ['text', 'document', 'adaptive-card'];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_001;
  }

  protected getMessageTypeName(): string {
    return 'SystemMessage';
  }

  protected requiresContent(): boolean {
    return false; // System messages can be empty
  }
}
