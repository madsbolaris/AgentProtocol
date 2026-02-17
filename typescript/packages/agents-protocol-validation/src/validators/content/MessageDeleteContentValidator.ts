import type { MessageDeleteContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for MessageDeleteContent.
 */
export class MessageDeleteContentValidator extends ContentValidatorBase<MessageDeleteContent> {
  public validate(content: MessageDeleteContent, context?: ValidationContext): ValidationResult {
    // MessageDeleteContent has no strict validation requirements
    return ValidationResult.success();
  }
}
