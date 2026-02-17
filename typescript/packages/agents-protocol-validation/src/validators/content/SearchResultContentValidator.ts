import type { SearchResultContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';

/**
 * Validator for SearchResultContent.
 */
export class SearchResultContentValidator extends ContentValidatorBase<SearchResultContent> {
  public validate(content: SearchResultContent, context?: ValidationContext): ValidationResult {
    return ValidationResult.success();
  }
}
