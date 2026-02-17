import type { ImageContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for ImageContent.
 */
export class ImageContentValidator extends ContentValidatorBase<ImageContent> {
  public validate(content: ImageContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // CNT-006: must have uri
    const uriError = this.validateNotEmpty(
      content.uri,
      'uri',
      ValidationErrorCode.CNT_006,
      'ImageContent must have uri'
    );
    if (uriError) {
      errors.push(uriError);
    }

    // Validate URI format (if present)
    if (content.uri) {
      const uriFormatError = this.validateUri(
        content.uri,
        'uri',
        ValidationErrorCode.CNT_006,
        'ImageContent uri must be a valid URI'
      );
      if (uriFormatError) {
        errors.push(uriFormatError);
      }
    }

    // CNT-007: width and height must be positive (if present)
    const widthError = this.validatePositive(
      content.width,
      'width',
      ValidationErrorCode.CNT_007,
      'ImageContent width must be positive'
    );
    if (widthError) {
      errors.push(widthError);
    }

    const heightError = this.validatePositive(
      content.height,
      'height',
      ValidationErrorCode.CNT_007,
      'ImageContent height must be positive'
    );
    if (heightError) {
      errors.push(heightError);
    }

    // CNT-008: mime-type must be image/* (if present)
    if (content.mimeType && !content.mimeType.toLowerCase().startsWith('image/')) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.CNT_008,
          'ImageContent mime-type must start with "image/"',
          'mimeType'
        )
      );
    }

    return new ValidationResult(errors);
  }
}
