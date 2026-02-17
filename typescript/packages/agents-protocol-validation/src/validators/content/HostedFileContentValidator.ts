import type { HostedFileContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for HostedFileContent.
 */
export class HostedFileContentValidator extends ContentValidatorBase<HostedFileContent> {
  public validate(content: HostedFileContent, context?: ValidationContext): ValidationResult {
    // HostedFileContent has no strict validation requirements
    return ValidationResult.success();
  }
}
