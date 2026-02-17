import type { VideoContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for VideoContent.
 */
export class VideoContentValidator extends ContentValidatorBase<VideoContent> {
  public validate(content: VideoContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // Must have uri
    const uriError = this.validateNotEmpty(
      content.uri,
      'uri',
      ValidationErrorCode.CNT_006,
      'VideoContent must have uri'
    );
    if (uriError) {
      errors.push(uriError);
    }

    // Validate URI format
    if (content.uri) {
      const uriFormatError = this.validateUri(
        content.uri,
        'uri',
        ValidationErrorCode.CNT_006,
        'VideoContent uri must be a valid URI'
      );
      if (uriFormatError) {
        errors.push(uriFormatError);
      }
    }

    // mime-type should be video/* (if present)
    if (content.mimeType && !content.mimeType.toLowerCase().startsWith('video/')) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.CNT_008,
          'VideoContent mime-type should start with "video/"',
          'mimeType'
        )
      );
    }

    // Width and height must be positive (if present)
    const widthError = this.validatePositive(
      content.width,
      'width',
      ValidationErrorCode.CNT_007,
      'VideoContent width must be positive'
    );
    if (widthError) {
      errors.push(widthError);
    }

    const heightError = this.validatePositive(
      content.height,
      'height',
      ValidationErrorCode.CNT_007,
      'VideoContent height must be positive'
    );
    if (heightError) {
      errors.push(heightError);
    }

    return new ValidationResult(errors);
  }
}
