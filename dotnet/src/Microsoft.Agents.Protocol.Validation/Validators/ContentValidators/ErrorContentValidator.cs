using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for ErrorContent.
/// </summary>
public class ErrorContentValidator : ContentValidatorBase<ErrorContent>
{
    public override ValidationResult Validate(ErrorContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-011: ErrorContent message must be non-empty
        var messageError = ValidateNotEmpty(content.Message, "Message",
            ValidationErrorCode.CNT_011,
            "ErrorContent message must be non-empty");
        if (messageError != null)
            errors.Add(messageError);

        return new ValidationResult(errors);
    }
}
