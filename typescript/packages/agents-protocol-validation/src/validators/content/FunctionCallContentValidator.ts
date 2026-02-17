import type { FunctionCallContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for FunctionCallContent.
 */
export class FunctionCallContentValidator extends ContentValidatorBase<FunctionCallContent> {
  private static readonly VALID_IDENTIFIER_PATTERN = /^[a-zA-Z0-9_-]+$/;

  public validate(content: FunctionCallContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // REL-001: call-id must be non-empty
    const callIdError = this.validateNotEmpty(
      content.callId,
      'callId',
      ValidationErrorCode.REL_001,
      'FunctionCallContent call-id must be non-empty'
    );
    if (callIdError) {
      errors.push(callIdError);
    }

    // REL-003: call-id must be unique (if context available)
    if (context && content.callId) {
      if (!context.registerFunctionCall(content)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.REL_003,
            `Duplicate call-id: ${content.callId}`,
            'callId'
          )
        );
      }
    }

    // CNT-003: name must be a valid identifier (alphanumeric, underscore, hyphen)
    const nameError = this.validatePattern(
      content.name,
      FunctionCallContentValidator.VALID_IDENTIFIER_PATTERN,
      'name',
      ValidationErrorCode.CNT_003,
      'FunctionCallContent name must be a valid identifier (alphanumeric, underscore, hyphen)'
    );
    if (nameError) {
      errors.push(nameError);
    }

    // Name must also be non-empty
    const nameEmptyError = this.validateNotEmpty(
      content.name,
      'name',
      ValidationErrorCode.CNT_003,
      'FunctionCallContent name must be non-empty'
    );
    if (nameEmptyError) {
      errors.push(nameEmptyError);
    }

    // CNT-004: arguments must be valid JSON (if present)
    if (content.arguments) {
      const argsError = this.validateJson(
        content.arguments,
        'arguments',
        ValidationErrorCode.CNT_004,
        'FunctionCallContent arguments must be valid JSON'
      );
      if (argsError) {
        errors.push(argsError);
      }
    }

    return new ValidationResult(errors);
  }
}
