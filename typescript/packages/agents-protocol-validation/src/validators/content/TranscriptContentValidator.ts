import type { TranscriptContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for TranscriptContent.
 */
export class TranscriptContentValidator extends ContentValidatorBase<TranscriptContent> {
  public validate(content: TranscriptContent, context?: ValidationContext): ValidationResult {
    // TranscriptContent has no strict validation requirements
    return ValidationResult.success();
  }
}
