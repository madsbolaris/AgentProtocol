import type { RefusalContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for RefusalContent.
 */
export class RefusalContentValidator extends ContentValidatorBase<RefusalContent> {
  public validate(content: RefusalContent, context?: ValidationContext): ValidationResult {
    // RefusalContent has no strict validation requirements
    return ValidationResult.success();
  }
}
