using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Microsoft.Agents.Protocol.Xml.Validation;

/// <summary>
/// Represents a single validation error.
/// </summary>
public class ValidationError
{
    /// <summary>
    /// Error message describing what went wrong.
    /// </summary>
    public string Message { get; set; }

    /// <summary>
    /// Field name that caused the error, if applicable.
    /// </summary>
    public string? Field { get; set; }

    /// <summary>
    /// Error code for programmatic handling.
    /// </summary>
    public string? Code { get; set; }

    /// <summary>
    /// Additional context about the error.
    /// </summary>
    public Dictionary<string, object>? Context { get; set; }

    public ValidationError(string message, string? field = null, string? code = null, Dictionary<string, object>? context = null)
    {
        Message = message;
        Field = field;
        Code = code;
        Context = context;
    }

    public override string ToString()
    {
        return Field != null ? $"{Field}: {Message}" : Message;
    }
}

/// <summary>
/// Result of a validation operation.
/// </summary>
public class ValidationResult
{
    /// <summary>
    /// Whether validation passed.
    /// </summary>
    public bool IsValid { get; set; }

    /// <summary>
    /// List of validation errors, empty if IsValid=true.
    /// </summary>
    public List<ValidationError> Errors { get; set; }

    /// <summary>
    /// Non-fatal warnings.
    /// </summary>
    public List<string> Warnings { get; set; }

    public ValidationResult(bool isValid = true)
    {
        IsValid = isValid;
        Errors = new List<ValidationError>();
        Warnings = new List<string>();
    }

    /// <summary>
    /// Add a validation error.
    /// </summary>
    public void AddError(string message, string? field = null, string? code = null, Dictionary<string, object>? context = null)
    {
        Errors.Add(new ValidationError(message, field, code, context));
        IsValid = false;
    }

    /// <summary>
    /// Add a validation warning.
    /// </summary>
    public void AddWarning(string message)
    {
        Warnings.Add(message);
    }

    /// <summary>
    /// Create a successful validation result.
    /// </summary>
    public static ValidationResult Success()
    {
        return new ValidationResult(true);
    }

    /// <summary>
    /// Create a failed validation result.
    /// </summary>
    public static ValidationResult Failure(string errorMessage, string? field = null, string? code = null)
    {
        var result = new ValidationResult(false);
        result.AddError(errorMessage, field, code);
        return result;
    }

    public override string ToString()
    {
        if (IsValid)
        {
            return "Validation passed";
        }

        var sb = new StringBuilder();
        sb.AppendLine($"Validation failed with {Errors.Count} error(s):");
        foreach (var error in Errors)
        {
            sb.AppendLine(error.ToString());
        }
        return sb.ToString();
    }
}
