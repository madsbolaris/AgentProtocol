import { ValidationError, ValidationSeverity } from './ValidationError';

/**
 * Represents the result of a validation operation.
 */
export class ValidationResult {
  /**
   * Gets the list of validation errors.
   */
  public readonly errors: ReadonlyArray<ValidationError>;

  constructor(errors: ValidationError[] = []) {
    this.errors = errors;
  }

  /**
   * Gets a value indicating whether the validation passed (no errors).
   */
  get isValid(): boolean {
    return !this.errors.some(e => e.severity === ValidationSeverity.Error);
  }

  /**
   * Gets a value indicating whether there are any warnings.
   */
  get hasWarnings(): boolean {
    return this.errors.some(e => e.severity === ValidationSeverity.Warning);
  }

  /**
   * Combines this validation result with another validation result.
   */
  combine(other: ValidationResult): ValidationResult {
    if (!other) {
      return this;
    }
    return new ValidationResult([...this.errors, ...other.errors]);
  }

  /**
   * Throws a ValidationException if this result is not valid.
   */
  throwIfInvalid(): void {
    if (!this.isValid) {
      throw new ValidationException(this);
    }
  }

  /**
   * Gets all errors of the specified severity.
   */
  getErrorsBySeverity(severity: ValidationSeverity): ValidationError[] {
    return this.errors.filter(e => e.severity === severity);
  }

  /**
   * Gets all errors with the specified code.
   */
  getErrorsByCode(code: string): ValidationError[] {
    return this.errors.filter(e => e.code === code);
  }

  /**
   * Creates a successful validation result.
   */
  static success(): ValidationResult {
    return new ValidationResult();
  }

  /**
   * Creates a validation result with a single error.
   */
  static failure(code: string, message: string, field?: string): ValidationResult {
    return new ValidationResult([new ValidationError(code, message, field)]);
  }

  /**
   * Returns a string representation of this validation result.
   */
  toString(): string {
    if (this.isValid) {
      return 'Validation passed';
    }

    const errorCount = this.getErrorsBySeverity(ValidationSeverity.Error).length;
    const warningCount = this.getErrorsBySeverity(ValidationSeverity.Warning).length;

    return `Validation failed: ${errorCount} error(s), ${warningCount} warning(s)`;
  }
}

/**
 * Exception thrown when validation fails.
 */
export class ValidationException extends Error {
  public readonly validationResult: ValidationResult;

  constructor(validationResult: ValidationResult) {
    super(ValidationException.formatMessage(validationResult));
    this.name = 'ValidationException';
    this.validationResult = validationResult;
    Object.setPrototypeOf(this, ValidationException.prototype);
  }

  private static formatMessage(result: ValidationResult): string {
    const errors = result.getErrorsBySeverity(ValidationSeverity.Error);
    if (errors.length === 0) {
      return 'Validation failed';
    }

    if (errors.length === 1) {
      return `Validation failed: ${errors[0]}`;
    }

    const errorList = errors.map((e, i) => `  ${i + 1}. ${e}`).join('\n');
    return `Validation failed with ${errors.length} error(s):\n${errorList}`;
  }
}
