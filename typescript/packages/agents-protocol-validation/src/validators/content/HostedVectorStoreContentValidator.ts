import type { HostedVectorStoreContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for HostedVectorStoreContent.
 */
export class HostedVectorStoreContentValidator extends ContentValidatorBase<HostedVectorStoreContent> {
  public validate(content: HostedVectorStoreContent, context?: ValidationContext): ValidationResult {
    // HostedVectorStoreContent has no strict validation requirements
    return ValidationResult.success();
  }
}
