namespace Microsoft.Agents.Protocol.Validation;

/// <summary>
/// Represents a validation error with structured information.
/// </summary>
public class ValidationError
{
    /// <summary>
    /// Gets or sets the error code (e.g., "MSG-001", "REL-002").
    /// </summary>
    public string Code { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the human-readable error message.
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the field or property name that failed validation.
    /// </summary>
    public string? Field { get; set; }

    /// <summary>
    /// Gets or sets the severity of the validation error.
    /// </summary>
    public ValidationSeverity Severity { get; set; } = ValidationSeverity.Error;

    /// <summary>
    /// Gets or sets additional context information for the error.
    /// </summary>
    public Dictionary<string, object>? Context { get; set; }

    /// <summary>
    /// Creates a new validation error.
    /// </summary>
    public ValidationError()
    {
    }

    /// <summary>
    /// Creates a new validation error with the specified code and message.
    /// </summary>
    public ValidationError(string code, string message, string? field = null, ValidationSeverity severity = ValidationSeverity.Error)
    {
        Code = code;
        Message = message;
        Field = field;
        Severity = severity;
    }

    /// <summary>
    /// Returns a string representation of this validation error.
    /// </summary>
    public override string ToString()
    {
        var fieldPart = !string.IsNullOrEmpty(Field) ? $" [{Field}]" : "";
        return $"{Code}{fieldPart}: {Message}";
    }
}

/// <summary>
/// Severity levels for validation errors.
/// </summary>
public enum ValidationSeverity
{
    /// <summary>
    /// Informational message.
    /// </summary>
    Info,

    /// <summary>
    /// Warning that should be addressed.
    /// </summary>
    Warning,

    /// <summary>
    /// Error that must be fixed.
    /// </summary>
    Error
}
