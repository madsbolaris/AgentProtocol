using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators;

/// <summary>
/// Base class for content validators.
/// </summary>
/// <typeparam name="T">The type of content to validate.</typeparam>
public abstract class ContentValidatorBase<T> : IValidator<T> where T : AIContent
{
    /// <summary>
    /// Validates the content and returns a validation result.
    /// </summary>
    public abstract ValidationResult Validate(T content, ValidationContext? context = null);

    /// <summary>
    /// Helper method to create a validation error.
    /// </summary>
    protected ValidationError CreateError(string code, string message, string? field = null)
    {
        return new ValidationError(code, message, field);
    }

    /// <summary>
    /// Helper method to validate that a string is not empty.
    /// </summary>
    protected ValidationError? ValidateNotEmpty(string? value, string fieldName, string errorCode, string errorMessage)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
        return null;
    }

    /// <summary>
    /// Helper method to validate that a number is positive.
    /// </summary>
    protected ValidationError? ValidatePositive(int? value, string fieldName, string errorCode, string errorMessage)
    {
        if (value.HasValue && value.Value <= 0)
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
        return null;
    }

    /// <summary>
    /// Helper method to validate that a number is positive.
    /// </summary>
    protected ValidationError? ValidatePositive(long? value, string fieldName, string errorCode, string errorMessage)
    {
        if (value.HasValue && value.Value <= 0)
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
        return null;
    }

    /// <summary>
    /// Helper method to validate that a number is positive.
    /// </summary>
    protected ValidationError? ValidatePositive(float? value, string fieldName, string errorCode, string errorMessage)
    {
        if (value.HasValue && value.Value <= 0)
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
        return null;
    }

    /// <summary>
    /// Helper method to validate JSON format.
    /// </summary>
    protected ValidationError? ValidateJson(string? json, string fieldName, string errorCode, string errorMessage)
    {
        if (string.IsNullOrWhiteSpace(json))
            return null;

        try
        {
            System.Text.Json.JsonDocument.Parse(json);
            return null;
        }
        catch (System.Text.Json.JsonException)
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
    }

    /// <summary>
    /// Helper method to validate URI format.
    /// </summary>
    protected ValidationError? ValidateUri(string? uri, string fieldName, string errorCode, string errorMessage)
    {
        if (string.IsNullOrWhiteSpace(uri))
            return null;

        if (!Uri.TryCreate(uri, UriKind.Absolute, out _))
        {
            return CreateError(errorCode, errorMessage, fieldName);
        }
        return null;
    }
}
