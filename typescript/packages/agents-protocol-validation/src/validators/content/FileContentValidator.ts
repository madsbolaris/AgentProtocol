import type { FileContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for FileContent.
 */
export class FileContentValidator extends ContentValidatorBase<FileContent> {
  public validate(content: FileContent, context?: ValidationContext): ValidationResult {
    // FileContent has optional fields, no strict validation needed
    return ValidationResult.success();
  }
}
