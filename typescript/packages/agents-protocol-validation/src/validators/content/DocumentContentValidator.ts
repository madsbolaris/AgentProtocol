import type { DocumentContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for DocumentContent.
 */
export class DocumentContentValidator extends ContentValidatorBase<DocumentContent> {
  public validate(content: DocumentContent, context?: ValidationContext): ValidationResult {
    // DocumentContent has no strict validation requirements
    return ValidationResult.success();
  }
}
