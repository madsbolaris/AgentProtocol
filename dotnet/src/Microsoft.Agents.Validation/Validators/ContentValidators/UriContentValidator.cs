using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for UriContent.
/// </summary>
public class UriContentValidator : ContentValidatorBase<UriContent>
{
    public override ValidationResult Validate(UriContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for UriContent
        return ValidationResult.Success();
    }
}
