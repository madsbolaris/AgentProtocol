import type { AIContent } from '@microsoft/agents-protocol-abstractions';
import type { IValidator } from '../../core/IValidator';
import type { ValidationContext } from '../../core/ValidationContext';
import { ValidationResult } from '../../core/ValidationResult';
import { ValidationError } from '../../core/ValidationError';

/**
 * Base class for all content validators.
 * Provides common validation helper methods.
 */
export abstract class ContentValidatorBase<T extends AIContent> implements IValidator<T> {
  /**
   * Validates the content object.
   */
  public abstract validate(obj: T, context?: ValidationContext): ValidationResult;

  /**
   * Validates that a string value is non-empty.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateNotEmpty(
    value: string | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (!value || value.trim().length === 0) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Validates that a numeric value is positive (> 0).
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validatePositive(
    value: number | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (value !== null && value !== undefined && value <= 0) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Validates that a numeric value is non-negative (>= 0).
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateNonNegative(
    value: number | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (value !== null && value !== undefined && value < 0) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Validates that a string is valid JSON.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateJson(
    json: string | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (!json) {
      return undefined; // Empty is OK unless checked separately
    }

    try {
      JSON.parse(json);
      return undefined;
    } catch {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
  }

  /**
   * Validates that a string is a valid URI.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateUri(
    uri: string | null | undefined,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (!uri) {
      return undefined; // Empty is OK unless checked separately
    }

    try {
      new URL(uri);
      return undefined;
    } catch {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
  }

  /**
   * Validates that a string matches a regex pattern.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validatePattern(
    value: string | null | undefined,
    pattern: RegExp,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (!value) {
      return undefined; // Empty is OK unless checked separately
    }

    if (!pattern.test(value)) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }

    return undefined;
  }

  /**
   * Validates that a string does not exceed a maximum length.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateMaxLength(
    value: string | null | undefined,
    maxLength: number,
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (value && value.length > maxLength) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Validates that a value is within a set of allowed values.
   * @returns ValidationError if validation fails, undefined otherwise
   */
  protected validateAllowedValues<V>(
    value: V | null | undefined,
    allowedValues: V[],
    fieldName: string,
    errorCode: string,
    errorMessage: string
  ): ValidationError | undefined {
    if (value !== null && value !== undefined && !allowedValues.includes(value)) {
      return new ValidationError(errorCode, errorMessage, fieldName);
    }
    return undefined;
  }

  /**
   * Helper to collect non-null validation errors.
   */
  protected collectErrors(...errors: (ValidationError | undefined)[]): ValidationError[] {
    return errors.filter((e): e is ValidationError => e !== undefined);
  }
}
