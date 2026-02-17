import type { ChannelMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for ChannelMessage.
 */
export class ChannelMessageValidator extends MessageValidatorBase<ChannelMessage> {
  protected validateSpecificFields(message: ChannelMessage, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // Channel-specific validation can be added here

    return errors;
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-006: Channel messages can contain UI and system content types
    return [
      'text',
      'typing-indicator',
      'message-reaction',
      'message-delete',
      'message-update',
      'suggested-actions',
      'action',
      'user-input-request',
      'event',
      'trace',
      'content-filter-result',
    ];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_006;
  }

  protected getMessageTypeName(): string {
    return 'ChannelMessage';
  }

  protected requiresContent(): boolean {
    return true;
  }
}
