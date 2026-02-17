import type { DeveloperMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for DeveloperMessage.
 */
export class DeveloperMessageValidator extends MessageValidatorBase<DeveloperMessage> {
  protected validateSpecificFields(message: DeveloperMessage, context?: ValidationContext): ValidationError[] {
    // MSG-009: Developer messages have no special fields beyond common ones
    return [];
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-002: Developer messages can only contain text, document
    return ['text', 'document'];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_002;
  }

  protected getMessageTypeName(): string {
    return 'DeveloperMessage';
  }

  protected requiresContent(): boolean {
    return false; // Developer messages can be empty
  }
}
