import type { TypingIndicatorContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for TypingIndicatorContent.
 */
export class TypingIndicatorContentValidator extends ContentValidatorBase<TypingIndicatorContent> {
  public validate(content: TypingIndicatorContent, context?: ValidationContext): ValidationResult {
    // TypingIndicatorContent has no strict validation requirements
    return ValidationResult.success();
  }
}
