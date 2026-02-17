/**
 * Validation result classes for XML message validation.
 *
 * Provides structured validation results with error details.
 */

/**
 * Represents a single validation error
 */
export interface ValidationError {
  /** Error message describing what went wrong */
  message: string;
  /** Field name that caused the error, if applicable */
  field?: string;
  /** Error code for programmatic handling */
  code?: string;
  /** Additional context about the error */
  context?: Record<string, unknown>;
}

/**
 * Result of a validation operation
 */
export class ValidationResult {
  /** Whether validation passed */
  isValid: boolean;
  /** List of validation errors, empty if isValid=true */
  errors: ValidationError[];
  /** Non-fatal warnings */
  warnings: string[];

  constructor(isValid: boolean = true, errors: ValidationError[] = [], warnings: string[] = []) {
    this.isValid = isValid;
    this.errors = errors;
    this.warnings = warnings;
  }

  /**
   * Add a validation error
   */
  addError(message: string, options?: {
    field?: string;
    code?: string;
    context?: Record<string, unknown>;
  }): void {
    this.errors.push({
      message,
      field: options?.field,
      code: options?.code,
      context: options?.context,
    });
    this.isValid = false;
  }

  /**
   * Add a validation warning
   */
  addWarning(message: string): void {
    this.warnings.push(message);
  }

  /**
   * String representation of the validation result
   */
  toString(): string {
    if (this.isValid) {
      return 'Validation passed';
    }
    const errorMessages = this.errors
      .map(e => (e.field ? `${e.field}: ${e.message}` : e.message))
      .join('\n');
    return `Validation failed with ${this.errors.length} error(s):\n${errorMessages}`;
  }

  /**
   * Create a successful validation result
   */
  static success(): ValidationResult {
    return new ValidationResult(true);
  }

  /**
   * Create a failed validation result
   */
  static failure(
    errorMessage: string,
    options?: { field?: string; code?: string }
  ): ValidationResult {
    const result = new ValidationResult(false);
    result.addError(errorMessage, options);
    return result;
  }
}
