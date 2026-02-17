import type { SuggestedActionsContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for SuggestedActionsContent.
 */
export class SuggestedActionsContentValidator extends ContentValidatorBase<SuggestedActionsContent> {
  public validate(content: SuggestedActionsContent, context?: ValidationContext): ValidationResult {
    // SuggestedActionsContent has no strict validation requirements
    return ValidationResult.success();
  }
}
