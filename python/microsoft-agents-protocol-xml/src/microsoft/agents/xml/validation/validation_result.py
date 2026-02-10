"""
Validation result classes.

Provides structured validation results with error details.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationError:
    """Represents a single validation error."""

    message: str
    """Error message describing what went wrong"""

    field: Optional[str] = None
    """Field name that caused the error, if applicable"""

    code: Optional[str] = None
    """Error code for programmatic handling"""

    context: Optional[dict] = None
    """Additional context about the error"""

    def __str__(self) -> str:
        """String representation of the error."""
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    """Whether validation passed"""

    errors: List[ValidationError] = field(default_factory=list)
    """List of validation errors, empty if is_valid=True"""

    warnings: List[str] = field(default_factory=list)
    """Non-fatal warnings"""

    def __str__(self) -> str:
        """String representation of the validation result."""
        if self.is_valid:
            return "Validation passed"
        error_messages = "\n".join(str(e) for e in self.errors)
        return f"Validation failed with {len(self.errors)} error(s):\n{error_messages}"

    def add_error(self, message: str, field: Optional[str] = None,
                  code: Optional[str] = None, context: Optional[dict] = None) -> None:
        """
        Add a validation error.

        Args:
            message: Error message
            field: Field name that caused the error
            code: Error code
            context: Additional context
        """
        self.errors.append(ValidationError(
            message=message,
            field=field,
            code=code,
            context=context
        ))
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """
        Add a validation warning.

        Args:
            message: Warning message
        """
        self.warnings.append(message)

    @staticmethod
    def success() -> "ValidationResult":
        """Create a successful validation result."""
        return ValidationResult(is_valid=True)

    @staticmethod
    def failure(error_message: str, field: Optional[str] = None,
                code: Optional[str] = None) -> "ValidationResult":
        """
        Create a failed validation result.

        Args:
            error_message: Error message
            field: Field name that caused the error
            code: Error code

        Returns:
            ValidationResult with the error
        """
        result = ValidationResult(is_valid=False)
        result.add_error(error_message, field=field, code=code)
        return result
