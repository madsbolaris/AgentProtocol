import type { TextContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for TextContent.
 */
export class TextContentValidator extends ContentValidatorBase<TextContent> {
  public validate(content: TextContent, context?: ValidationContext): ValidationResult {
    const errors = this.collectErrors(
      // CNT-001: text must be non-empty
      this.validateNotEmpty(
        content.text,
        'text',
        ValidationErrorCode.CNT_001,
        'TextContent text must be non-empty'
      ),

      // CNT-002: text must not exceed 100,000 characters
      this.validateMaxLength(
        content.text,
        100000,
        'text',
        ValidationErrorCode.CNT_002,
        'TextContent text must not exceed 100,000 characters'
      )
    );

    return new ValidationResult(errors);
  }
}
