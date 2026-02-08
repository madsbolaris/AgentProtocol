using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for DataContent.
/// </summary>
public class DataContentValidator : ContentValidatorBase<DataContent>
{
    public override ValidationResult Validate(DataContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for DataContent
        return ValidationResult.Success();
    }
}
