import type { EventContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for EventContent.
 */
export class EventContentValidator extends ContentValidatorBase<EventContent> {
  public validate(content: EventContent, context?: ValidationContext): ValidationResult {
    const errors = this.collectErrors(
      // CNT-015: event name must be non-empty
      this.validateNotEmpty(
        content.name,
        'name',
        ValidationErrorCode.CNT_015,
        'EventContent name must be non-empty'
      )
    );

    return new ValidationResult(errors);
  }
}
