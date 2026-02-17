import type { MessageUpdateContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for MessageUpdateContent.
 */
export class MessageUpdateContentValidator extends ContentValidatorBase<MessageUpdateContent> {
  public validate(content: MessageUpdateContent, context?: ValidationContext): ValidationResult {
    // MessageUpdateContent has no strict validation requirements
    return ValidationResult.success();
  }
}
