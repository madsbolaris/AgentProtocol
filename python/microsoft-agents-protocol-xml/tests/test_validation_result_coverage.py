"""Comprehensive tests for ValidationResult to improve code coverage."""

import pytest
from microsoft.agents.xml.validation.validation_result import ValidationResult, ValidationError


class TestValidationErrorCoverage:
    """Test all methods and branches of ValidationError."""

    def test_create_error_with_message_only(self):
        """Test creating error with just a message."""
        error = ValidationError(message="Test error")
        assert error.message == "Test error"
        assert error.field is None
        assert error.code is None
        assert error.context is None

    def test_create_error_with_all_fields(self):
        """Test creating error with all fields."""
        context = {"key": "value", "index": 0}
        error = ValidationError(
            message="Test error",
            field="test_field",
            code="TEST_001",
            context=context
        )
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.code == "TEST_001"
        assert error.context == context

    def test_error_str_without_field(self):
        """Test string representation without field."""
        error = ValidationError(message="Test error")
        assert str(error) == "Test error"

    def test_error_str_with_field(self):
        """Test string representation with field."""
        error = ValidationError(message="Test error", field="test_field")
        assert str(error) == "test_field: Test error"

    def test_error_representation(self):
        """Test error representation."""
        error = ValidationError(
            message="Test error",
            field="test_field",
            code="TEST_001"
        )
        # Just check that the error has the expected attributes
        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.code == "TEST_001"

    def test_error_with_context(self):
        """Test error with context."""
        context = {"key": "value"}
        error = ValidationError(
            message="Test error",
            context=context
        )
        assert error.context == context


class TestValidationResultCoverage:
    """Test all methods and branches of ValidationResult."""

    def test_create_success_result(self):
        """Test creating a successful validation result."""
        result = ValidationResult.success()
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_create_failure_result(self):
        """Test creating a failed validation result."""
        result = ValidationResult.failure(
            "Test error",
            field="test_field",
            code="TEST_001"
        )
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
        assert result.errors[0].field == "test_field"
        assert result.errors[0].code == "TEST_001"

    def test_create_empty_result(self):
        """Test creating empty validation result."""
        result = ValidationResult()
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_create_result_invalid(self):
        """Test creating invalid result explicitly."""
        result = ValidationResult(is_valid=False)
        assert not result.is_valid
        assert len(result.errors) == 0

    def test_add_error(self):
        """Test adding an error to result."""
        result = ValidationResult()
        assert result.is_valid

        result.add_error("Test error")
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"

    def test_add_error_with_all_fields(self):
        """Test adding error with all fields."""
        result = ValidationResult()
        context = {"key": "value"}
        result.add_error(
            "Test error",
            field="test_field",
            code="TEST_001",
            context=context
        )
        assert not result.is_valid
        assert result.errors[0].field == "test_field"
        assert result.errors[0].code == "TEST_001"
        assert result.errors[0].context == context

    def test_add_multiple_errors(self):
        """Test adding multiple errors."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        result.add_error("Error 3")

        assert not result.is_valid
        assert len(result.errors) == 3
        assert result.errors[0].message == "Error 1"
        assert result.errors[1].message == "Error 2"
        assert result.errors[2].message == "Error 3"

    def test_add_warning(self):
        """Test adding a warning to result."""
        result = ValidationResult()
        result.add_warning("Test warning")

        assert result.is_valid  # Warnings don't affect validity
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"

    def test_add_multiple_warnings(self):
        """Test adding multiple warnings."""
        result = ValidationResult()
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")

        assert result.is_valid
        assert len(result.warnings) == 2

    def test_errors_and_warnings_together(self):
        """Test result with both errors and warnings."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")

        assert not result.is_valid
        assert len(result.errors) == 1
        assert len(result.warnings) == 1

    def test_to_string_success(self):
        """Test string representation of successful result."""
        result = ValidationResult.success()
        string_repr = str(result)
        assert "passed" in string_repr.lower() or "valid" in string_repr.lower()

    def test_to_string_failure(self):
        """Test string representation of failed result."""
        result = ValidationResult.failure("Test error", field="test_field")
        string_repr = str(result)
        assert "failed" in string_repr.lower() or "error" in string_repr.lower()
        assert "Test error" in string_repr

    def test_to_string_multiple_errors(self):
        """Test string representation with multiple errors."""
        result = ValidationResult()
        result.add_error("Error 1", field="field1")
        result.add_error("Error 2", field="field2")

        string_repr = str(result)
        assert "2" in string_repr  # Should mention number of errors
        assert "Error 1" in string_repr or "field1" in string_repr

    def test_result_attributes(self):
        """Test result has expected attributes."""
        result = ValidationResult.success()
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert result.is_valid is True

    def test_result_with_errors_attributes(self):
        """Test result with errors has correct attributes."""
        result = ValidationResult()
        result.add_error("Test error", field="test_field", code="TEST_001")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].message == "Test error"
        assert result.errors[0].field == "test_field"
        assert result.errors[0].code == "TEST_001"

    def test_result_with_warnings_attributes(self):
        """Test result with warnings has correct attributes."""
        result = ValidationResult()
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")

        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "Warning 1" in result.warnings
        assert "Warning 2" in result.warnings

    def test_result_state(self):
        """Test result state consistency."""
        result1 = ValidationResult.success()
        result2 = ValidationResult.success()
        # They should have same validity state
        assert result1.is_valid == result2.is_valid
        assert len(result1.errors) == len(result2.errors)

    def test_error_count(self):
        """Test getting error count."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        result.add_error("Error 3")

        assert len(result.errors) == 3

    def test_warning_count(self):
        """Test getting warning count."""
        result = ValidationResult()
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")

        assert len(result.warnings) == 2

    def test_has_errors(self):
        """Test checking if result has errors."""
        result1 = ValidationResult.success()
        assert len(result1.errors) == 0

        result2 = ValidationResult.failure("Error")
        assert len(result2.errors) > 0

    def test_has_warnings(self):
        """Test checking if result has warnings."""
        result = ValidationResult()
        assert len(result.warnings) == 0

        result.add_warning("Warning")
        assert len(result.warnings) > 0

    def test_immutability_of_success(self):
        """Test that success() creates independent instances."""
        result1 = ValidationResult.success()
        result2 = ValidationResult.success()

        result1.add_error("Error")

        assert not result1.is_valid
        assert result2.is_valid  # Should not be affected

    def test_failure_with_context(self):
        """Test failure result with context."""
        context = {"line": 42, "column": 10}
        result = ValidationResult.failure(
            "Syntax error",
            field="code",
            code="SYNTAX_001",
            context=context
        )
        assert not result.is_valid
        assert result.errors[0].context == context

    def test_error_codes_collection(self):
        """Test collecting all error codes."""
        result = ValidationResult()
        result.add_error("Error 1", code="ERR_001")
        result.add_error("Error 2", code="ERR_002")
        result.add_error("Error 3", code="ERR_003")

        codes = [error.code for error in result.errors]
        assert "ERR_001" in codes
        assert "ERR_002" in codes
        assert "ERR_003" in codes

    def test_filter_errors_by_code(self):
        """Test filtering errors by code."""
        result = ValidationResult()
        result.add_error("Error 1", code="ERR_001")
        result.add_error("Error 2", code="ERR_002")
        result.add_error("Error 3", code="ERR_001")

        err_001_errors = [e for e in result.errors if e.code == "ERR_001"]
        assert len(err_001_errors) == 2

    def test_filter_errors_by_field(self):
        """Test filtering errors by field."""
        result = ValidationResult()
        result.add_error("Error 1", field="field_a")
        result.add_error("Error 2", field="field_b")
        result.add_error("Error 3", field="field_a")

        field_a_errors = [e for e in result.errors if e.field == "field_a"]
        assert len(field_a_errors) == 2
