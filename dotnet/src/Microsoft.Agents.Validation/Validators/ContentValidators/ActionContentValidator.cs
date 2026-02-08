using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for ActionContent.
/// </summary>
public class ActionContentValidator : ContentValidatorBase<ActionContent>
{
    public override ValidationResult Validate(ActionContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for ActionContent
        return ValidationResult.Success();
    }
}
