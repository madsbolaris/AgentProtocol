import type { UserMessage } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { MessageValidatorBase } from '../base/MessageValidatorBase';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for UserMessage.
 */
export class UserMessageValidator extends MessageValidatorBase<UserMessage> {
  protected validateSpecificFields(message: UserMessage, context?: ValidationContext): ValidationError[] {
    const errors: ValidationError[] = [];

    // MSG-010: User messages must have contents (checked in base class)

    return errors;
  }

  protected getAllowedContentTypes(): string[] {
    // ROLE-005: User messages can contain text, image, audio, video, file, uri, document, transcript, hosted-file
    return [
      'text',
      'image',
      'audio',
      'video',
      'file',
      'uri',
      'document',
      'transcript',
      'hosted-file',
      'data',
    ];
  }

  protected getRoleSpecificErrorCode(): string {
    return ValidationErrorCode.ROLE_005;
  }

  protected getMessageTypeName(): string {
    return 'UserMessage';
  }

  protected requiresContent(): boolean {
    return true;
  }
}
