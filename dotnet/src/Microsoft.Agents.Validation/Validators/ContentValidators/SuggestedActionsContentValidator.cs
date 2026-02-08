using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for SuggestedActionsContent.
/// </summary>
public class SuggestedActionsContentValidator : ContentValidatorBase<SuggestedActionsContent>
{
    public override ValidationResult Validate(SuggestedActionsContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for SuggestedActionsContent
        return ValidationResult.Success();
    }
}
