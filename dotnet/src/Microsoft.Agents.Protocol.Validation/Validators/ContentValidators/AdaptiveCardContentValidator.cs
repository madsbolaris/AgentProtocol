using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for AdaptiveCardContent.
/// </summary>
public class AdaptiveCardContentValidator : ContentValidatorBase<AdaptiveCardContent>
{
    public override ValidationResult Validate(AdaptiveCardContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-014: AdaptiveCardContent card must be valid JSON
        var jsonError = ValidateJson(content.Card, "Card",
            ValidationErrorCode.CNT_014,
            "AdaptiveCardContent card must be valid JSON");
        if (jsonError != null)
            errors.Add(jsonError);

        return new ValidationResult(errors);
    }
}
