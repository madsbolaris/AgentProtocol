import type { AdaptiveCardContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for AdaptiveCardContent.
 */
export class AdaptiveCardContentValidator extends ContentValidatorBase<AdaptiveCardContent> {
  public validate(content: AdaptiveCardContent, context?: ValidationContext): ValidationResult {
    // AdaptiveCardContent has no strict validation requirements
    return ValidationResult.success();
  }
}
