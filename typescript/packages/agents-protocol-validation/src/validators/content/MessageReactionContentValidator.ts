import type { MessageReactionContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for MessageReactionContent.
 */
export class MessageReactionContentValidator extends ContentValidatorBase<MessageReactionContent> {
  public validate(content: MessageReactionContent, context?: ValidationContext): ValidationResult {
    // MessageReactionContent has no strict validation requirements
    return ValidationResult.success();
  }
}
