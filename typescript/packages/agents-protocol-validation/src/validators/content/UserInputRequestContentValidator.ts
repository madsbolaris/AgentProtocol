import type { UserInputRequestContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for UserInputRequestContent.
 */
export class UserInputRequestContentValidator extends ContentValidatorBase<UserInputRequestContent> {
  public validate(content: UserInputRequestContent, context?: ValidationContext): ValidationResult {
    // UserInputRequestContent has no strict validation requirements
    return ValidationResult.success();
  }
}
