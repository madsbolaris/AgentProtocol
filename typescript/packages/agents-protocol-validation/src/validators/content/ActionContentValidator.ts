import type { ActionContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for ActionContent.
 */
export class ActionContentValidator extends ContentValidatorBase<ActionContent> {
  public validate(content: ActionContent, context?: ValidationContext): ValidationResult {
    // ActionContent has no strict validation requirements
    return ValidationResult.success();
  }
}
