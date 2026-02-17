import type { DataContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for DataContent.
 */
export class DataContentValidator extends ContentValidatorBase<DataContent> {
  public validate(content: DataContent, context?: ValidationContext): ValidationResult {
    // DataContent has no strict validation requirements
    return ValidationResult.success();
  }
}
