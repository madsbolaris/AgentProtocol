import type { AudioContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for AudioContent.
 */
export class AudioContentValidator extends ContentValidatorBase<AudioContent> {
  public validate(content: AudioContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // Must have uri
    const uriError = this.validateNotEmpty(
      content.uri,
      'uri',
      ValidationErrorCode.CNT_006,
      'AudioContent must have uri'
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
        'AudioContent uri must be a valid URI'
      );
      if (uriFormatError) {
        errors.push(uriFormatError);
      }
    }

    // mime-type should be audio/* (if present)
    if (content.mimeType && !content.mimeType.toLowerCase().startsWith('audio/')) {
      errors.push(
        new ValidationError(
          ValidationErrorCode.CNT_008,
          'AudioContent mime-type should start with "audio/"',
          'mimeType'
        )
      );
    }

    return new ValidationResult(errors);
  }
}
