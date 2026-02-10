namespace Microsoft.Agents.Protocol.Validation;

/// <summary>
/// Exception thrown when validation fails.
/// </summary>
public class ValidationException : Exception
{
    /// <summary>
    /// Gets the validation result that caused this exception.
    /// </summary>
    public ValidationResult ValidationResult { get; }

    /// <summary>
    /// Creates a new validation exception with the specified validation result.
    /// </summary>
    public ValidationException(ValidationResult validationResult)
        : base(FormatMessage(validationResult))
    {
        ValidationResult = validationResult;
    }

    /// <summary>
    /// Creates a new validation exception with the specified message and validation result.
    /// </summary>
    public ValidationException(string message, ValidationResult validationResult)
        : base(message)
    {
        ValidationResult = validationResult;
    }

    private static string FormatMessage(ValidationResult result)
    {
        var errors = result.GetErrorsBySeverity(ValidationSeverity.Error).ToList();
        if (errors.Count == 0)
            return "Validation failed";

        if (errors.Count == 1)
            return $"Validation failed: {errors[0]}";

        var errorList = string.Join(Environment.NewLine, errors.Select((e, i) => $"  {i + 1}. {e}"));
        return $"Validation failed with {errors.Count} error(s):{Environment.NewLine}{errorList}";
    }
}
