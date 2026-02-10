namespace Microsoft.Agents.Protocol.Validation;

/// <summary>
/// Represents the result of a validation operation.
/// </summary>
public class ValidationResult
{
    /// <summary>
    /// Gets a value indicating whether the validation passed (no errors).
    /// </summary>
    public bool IsValid => !Errors.Any(e => e.Severity == ValidationSeverity.Error);

    /// <summary>
    /// Gets the list of validation errors.
    /// </summary>
    public IReadOnlyList<ValidationError> Errors { get; }

    /// <summary>
    /// Gets a value indicating whether there are any warnings.
    /// </summary>
    public bool HasWarnings => Errors.Any(e => e.Severity == ValidationSeverity.Warning);

    /// <summary>
    /// Creates a new successful validation result with no errors.
    /// </summary>
    public ValidationResult()
    {
        Errors = Array.Empty<ValidationError>();
    }

    /// <summary>
    /// Creates a new validation result with the specified errors.
    /// </summary>
    public ValidationResult(IEnumerable<ValidationError> errors)
    {
        Errors = errors.ToList().AsReadOnly();
    }

    /// <summary>
    /// Creates a new validation result with a single error.
    /// </summary>
    public ValidationResult(ValidationError error)
    {
        Errors = new[] { error }.ToList().AsReadOnly();
    }

    /// <summary>
    /// Combines this validation result with another validation result.
    /// </summary>
    /// <param name="other">The other validation result to combine with.</param>
    /// <returns>A new validation result containing errors from both results.</returns>
    public ValidationResult Combine(ValidationResult other)
    {
        if (other == null)
            return this;

        var combinedErrors = Errors.Concat(other.Errors).ToList();
        return new ValidationResult(combinedErrors);
    }

    /// <summary>
    /// Throws a ValidationException if this result is not valid.
    /// </summary>
    public void ThrowIfInvalid()
    {
        if (!IsValid)
        {
            throw new ValidationException(this);
        }
    }

    /// <summary>
    /// Gets all errors of the specified severity.
    /// </summary>
    public IEnumerable<ValidationError> GetErrorsBySeverity(ValidationSeverity severity)
    {
        return Errors.Where(e => e.Severity == severity);
    }

    /// <summary>
    /// Gets all errors with the specified code.
    /// </summary>
    public IEnumerable<ValidationError> GetErrorsByCode(string code)
    {
        return Errors.Where(e => e.Code == code);
    }

    /// <summary>
    /// Creates a successful validation result.
    /// </summary>
    public static ValidationResult Success()
    {
        return new ValidationResult();
    }

    /// <summary>
    /// Creates a validation result with a single error.
    /// </summary>
    public static ValidationResult Failure(string code, string message, string? field = null)
    {
        return new ValidationResult(new ValidationError(code, message, field));
    }

    /// <summary>
    /// Returns a string representation of this validation result.
    /// </summary>
    public override string ToString()
    {
        if (IsValid)
            return "Validation passed";

        var errorCount = GetErrorsBySeverity(ValidationSeverity.Error).Count();
        var warningCount = GetErrorsBySeverity(ValidationSeverity.Warning).Count();

        return $"Validation failed: {errorCount} error(s), {warningCount} warning(s)";
    }
}
