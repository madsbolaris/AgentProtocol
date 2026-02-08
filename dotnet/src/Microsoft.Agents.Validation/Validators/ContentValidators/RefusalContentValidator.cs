using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for RefusalContent.
/// </summary>
public class RefusalContentValidator : ContentValidatorBase<RefusalContent>
{
    public override ValidationResult Validate(RefusalContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for RefusalContent
        return ValidationResult.Success();
    }
}
