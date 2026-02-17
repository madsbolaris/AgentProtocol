import type { UriContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for UriContent.
 */
export class UriContentValidator extends ContentValidatorBase<UriContent> {
  public validate(content: UriContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // Must have uri
    const uriError = this.validateNotEmpty(
      content.uri,
      'uri',
      ValidationErrorCode.CNT_006,
      'UriContent must have uri'
    );
    if (uriError) {
      errors.push(uriError);
    }

    // Validate URI format
    if (content.uri) {
      const uriFormatError = this.validateUri(
        content.uri,
        'uri',
        ValidationErrorCode.CNT_012,
        'UriContent uri must be a valid URI'
      );
      if (uriFormatError) {
        errors.push(uriFormatError);
      }
    }

    return new ValidationResult(errors);
  }
}
