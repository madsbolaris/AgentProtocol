import type { TextReasoningContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for TextReasoningContent.
 */
export class TextReasoningContentValidator extends ContentValidatorBase<TextReasoningContent> {
  public validate(content: TextReasoningContent, context?: ValidationContext): ValidationResult {
    // TextReasoningContent has no strict validation requirements
    return ValidationResult.success();
  }
}
