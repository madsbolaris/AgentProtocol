import type { FunctionResultContent } from '@microsoft/agents-protocol-abstractions';
import type { ValidationContext } from '../../core/ValidationContext';
import { ContentValidatorBase } from '../base/ContentValidatorBase';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';
import { ValidationErrorCode } from '../../core/ValidationErrorCode';

/**
 * Validator for FunctionResultContent.
 */
export class FunctionResultContentValidator extends ContentValidatorBase<FunctionResultContent> {
  public validate(content: FunctionResultContent, context?: ValidationContext): ValidationResult {
    const errors: ValidationError[] = [];

    // REL-002: call-id must be non-empty
    const callIdError = this.validateNotEmpty(
      content.callId,
      'callId',
      ValidationErrorCode.REL_002,
      'FunctionResultContent call-id must be non-empty'
    );
    if (callIdError) {
      errors.push(callIdError);
    }

    // REL-004: call-id must match a FunctionCall (if context available)
    if (context && content.callId) {
      if (!context.hasFunctionCall(content.callId)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.REL_004,
            `FunctionResultContent call-id does not match any FunctionCall: ${content.callId}`,
            'callId'
          )
        );
      }
    }

    // REL-006: call-id must be unique among results (if context available)
    if (context && content.callId) {
      if (!context.registerFunctionResult(content)) {
        errors.push(
          new ValidationError(
            ValidationErrorCode.REL_006,
            `Duplicate FunctionResultContent for call-id: ${content.callId}`,
            'callId'
          )
        );
      }
    }

    // CNT-005: result must be valid JSON (if present)
    if (content.result) {
      const resultError = this.validateJson(
        content.result,
        'result',
        ValidationErrorCode.CNT_005,
        'FunctionResultContent result must be valid JSON'
      );
      if (resultError) {
        errors.push(resultError);
      }
    }

    return new ValidationResult(errors);
  }
}
