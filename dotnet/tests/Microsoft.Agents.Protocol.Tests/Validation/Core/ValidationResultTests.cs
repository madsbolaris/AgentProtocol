using FluentAssertions;
using Microsoft.Agents.Protocol.Validation;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests.Validation.Core;

public class ValidationResultTests
{
    [Fact]
    public void Success_ReturnsValidResult()
    {
        // Act
        var result = ValidationResult.Success();

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
    }

    [Fact]
    public void Failure_ReturnsInvalidResult()
    {
        // Act
        var result = ValidationResult.Failure("TEST-001", "Test error");

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().HaveCount(1);
        result.Errors[0].Code.Should().Be("TEST-001");
        result.Errors[0].Message.Should().Be("Test error");
    }

    [Fact]
    public void Combine_MergesErrors()
    {
        // Arrange
        var result1 = ValidationResult.Failure("TEST-001", "Error 1");
        var result2 = ValidationResult.Failure("TEST-002", "Error 2");

        // Act
        var combined = result1.Combine(result2);

        // Assert
        combined.IsValid.Should().BeFalse();
        combined.Errors.Should().HaveCount(2);
        combined.Errors.Should().Contain(e => e.Code == "TEST-001");
        combined.Errors.Should().Contain(e => e.Code == "TEST-002");
    }

    [Fact]
    public void ThrowIfInvalid_ThrowsWhenInvalid()
    {
        // Arrange
        var result = ValidationResult.Failure("TEST-001", "Test error");

        // Act & Assert
        var action = () => result.ThrowIfInvalid();
        action.Should().Throw<ValidationException>()
            .Which.ValidationResult.Should().Be(result);
    }

    [Fact]
    public void ThrowIfInvalid_DoesNotThrowWhenValid()
    {
        // Arrange
        var result = ValidationResult.Success();

        // Act & Assert
        var action = () => result.ThrowIfInvalid();
        action.Should().NotThrow();
    }

    [Fact]
    public void GetErrorsByCode_FiltersCorrectly()
    {
        // Arrange
        var errors = new List<ValidationError>
        {
            new("TEST-001", "Error 1"),
            new("TEST-002", "Error 2"),
            new("TEST-001", "Error 3")
        };
        var result = new ValidationResult(errors);

        // Act
        var filtered = result.GetErrorsByCode("TEST-001");

        // Assert
        filtered.Should().HaveCount(2);
        filtered.Should().AllSatisfy(e => e.Code.Should().Be("TEST-001"));
    }

    [Fact]
    public void GetErrorsBySeverity_FiltersCorrectly()
    {
        // Arrange
        var errors = new List<ValidationError>
        {
            new("TEST-001", "Error 1") { Severity = ValidationSeverity.Error },
            new("TEST-002", "Warning 1") { Severity = ValidationSeverity.Warning },
            new("TEST-003", "Error 2") { Severity = ValidationSeverity.Error }
        };
        var result = new ValidationResult(errors);

        // Act
        var filtered = result.GetErrorsBySeverity(ValidationSeverity.Error);

        // Assert
        filtered.Should().HaveCount(2);
        filtered.Should().AllSatisfy(e => e.Severity.Should().Be(ValidationSeverity.Error));
    }
}
