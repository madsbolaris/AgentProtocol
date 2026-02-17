/**
 * Severity levels for validation errors.
 */
export enum ValidationSeverity {
  Info = 'info',
  Warning = 'warning',
  Error = 'error'
}

/**
 * Represents a validation error with structured information.
 */
export class ValidationError {
  /**
   * The error code (e.g., "MSG-001", "REL-002").
   */
  public readonly code: string;

  /**
   * The human-readable error message.
   */
  public readonly message: string;

  /**
   * The field or property name that failed validation.
   */
  public readonly field?: string;

  /**
   * The severity of the validation error.
   */
  public readonly severity: ValidationSeverity;

  /**
   * Additional context information for the error.
   */
  public readonly context?: Record<string, unknown>;

  constructor(
    code: string,
    message: string,
    field?: string,
    severity: ValidationSeverity = ValidationSeverity.Error,
    context?: Record<string, unknown>
  ) {
    this.code = code;
    this.message = message;
    this.field = field;
    this.severity = severity;
    this.context = context;
  }

  /**
   * Returns a string representation of this validation error.
   */
  toString(): string {
    const fieldPart = this.field ? ` [${this.field}]` : '';
    return `${this.code}${fieldPart}: ${this.message}`;
  }
}
