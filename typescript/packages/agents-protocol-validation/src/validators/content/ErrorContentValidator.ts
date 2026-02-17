import type { ErrorContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for ErrorContent.
 */
export class ErrorContentValidator extends ContentValidatorBase<ErrorContent> {
  public validate(content: ErrorContent, context?: ValidationContext): ValidationResult {
    const errors = this.collectErrors(
      // CNT-011: error message must be non-empty
      this.validateNotEmpty(
        content.message,
        'message',
        ValidationErrorCode.CNT_011,
        'ErrorContent message must be non-empty'
      )
    );

    return new ValidationResult(errors);
  }
}
