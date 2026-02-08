using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for FunctionResultContent.
/// </summary>
public class FunctionResultContentValidator : ContentValidatorBase<FunctionResultContent>
{
    public override ValidationResult Validate(FunctionResultContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // REL-004: One FunctionResultContent per call-id (no duplicates)
        if (context != null && !string.IsNullOrEmpty(content.CallId))
        {
            if (context.FunctionResultExists(content.CallId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_004,
                    $"Duplicate function result for call-id '{content.CallId}'. Each call-id can only have one function result.",
                    "CallId"));
            }
            else
            {
                context.RegisterFunctionResult(content);
            }

            // REL-002 & REL-006: FunctionResultContent call-id must match a FunctionCallContent call-id
            if (!context.FunctionCallExists(content.CallId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_002,
                    $"Function result has call-id '{content.CallId}' but no matching function call was found",
                    "CallId"));
            }
            else
            {
                // REL-007: FunctionResultContent name must match FunctionCallContent name
                var functionCall = context.GetFunctionCall(content.CallId);
                if (functionCall != null &&
                    !string.IsNullOrEmpty(content.Name) &&
                    !string.IsNullOrEmpty(functionCall.Name) &&
                    content.Name != functionCall.Name)
                {
                    errors.Add(CreateError(
                        ValidationErrorCode.REL_007,
                        $"Function result name '{content.Name}' does not match function call name '{functionCall.Name}' for call-id '{content.CallId}'",
                        "Name"));
                }
            }
        }

        // CNT-005: FunctionResultContent result must be valid JSON
        var jsonError = ValidateJson(content.Result, "Result",
            ValidationErrorCode.CNT_005,
            "FunctionResultContent result must be valid JSON");
        if (jsonError != null)
            errors.Add(jsonError);

        return new ValidationResult(errors);
    }
}
