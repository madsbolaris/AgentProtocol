using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for FileContent.
/// </summary>
public class FileContentValidator : ContentValidatorBase<FileContent>
{
    public override ValidationResult Validate(FileContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for FileContent
        return ValidationResult.Success();
    }
}
