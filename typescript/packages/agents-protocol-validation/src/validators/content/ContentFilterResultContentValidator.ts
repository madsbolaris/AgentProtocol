import type { ContentFilterResultContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for ContentFilterResultContent.
 */
export class ContentFilterResultContentValidator extends ContentValidatorBase<ContentFilterResultContent> {
  public validate(content: ContentFilterResultContent, context?: ValidationContext): ValidationResult {
    // ContentFilterResultContent has no strict validation requirements
    return ValidationResult.success();
  }
}
