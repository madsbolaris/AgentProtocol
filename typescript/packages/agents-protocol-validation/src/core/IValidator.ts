import { ValidationResult } from './ValidationResult';
import { ValidationContext } from './ValidationContext';

/**
 * Interface for validators that can validate objects of type T.
 */
export interface IValidator<T> {
  /**
   * Validates the given object and returns a validation result.
   */
  validate(obj: T, context?: ValidationContext): ValidationResult;
}
