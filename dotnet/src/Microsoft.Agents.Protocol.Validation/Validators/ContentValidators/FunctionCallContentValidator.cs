using Microsoft.Agents;
using System.Text.RegularExpressions;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for FunctionCallContent.
/// </summary>
public partial class FunctionCallContentValidator : ContentValidatorBase<FunctionCallContent>
{
    [GeneratedRegex(@"^[a-zA-Z0-9_-]+$")]
    private static partial Regex ValidIdentifierRegex();

    public override ValidationResult Validate(FunctionCallContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // REL-001: FunctionCallContent call-id must be unique within message
        // Note: This is checked at the message level, but we validate format here
        var callIdError = ValidateNotEmpty(content.CallId, "CallId",
            ValidationErrorCode.REL_001,
            "FunctionCallContent call-id must be non-empty");
        if (callIdError != null)
            errors.Add(callIdError);

        // REL-003: Register function call in context for cross-validation
        if (context != null && !string.IsNullOrEmpty(content.CallId))
        {
            if (context.FunctionCallExists(content.CallId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_003,
                    $"Duplicate call-id '{content.CallId}' found. Each function call must have a unique call-id.",
                    "CallId"));
            }
            else
            {
                context.RegisterFunctionCall(content);
            }
        }

        // CNT-003: FunctionCallContent name must be valid identifier ([a-zA-Z0-9_-]+)
        if (string.IsNullOrWhiteSpace(content.Name))
        {
            errors.Add(CreateError(
                ValidationErrorCode.CNT_003,
                "FunctionCallContent name must be non-empty",
                "Name"));
        }
        else if (!ValidIdentifierRegex().IsMatch(content.Name))
        {
            errors.Add(CreateError(
                ValidationErrorCode.CNT_003,
                $"FunctionCallContent name '{content.Name}' must be a valid identifier (letters, numbers, underscore, hyphen only)",
                "Name"));
        }

        // CNT-004: FunctionCallContent arguments must be valid JSON
        var jsonError = ValidateJson(content.Arguments, "Arguments",
            ValidationErrorCode.CNT_004,
            "FunctionCallContent arguments must be valid JSON");
        if (jsonError != null)
            errors.Add(jsonError);

        return new ValidationResult(errors);
    }
}
