import type { TraceContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for TraceContent.
 */
export class TraceContentValidator extends ContentValidatorBase<TraceContent> {
  public validate(content: TraceContent, context?: ValidationContext): ValidationResult {
    // TraceContent has no strict validation requirements
    return ValidationResult.success();
  }
}
