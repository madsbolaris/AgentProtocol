using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for HostedFileContent.
/// </summary>
public class HostedFileContentValidator : ContentValidatorBase<HostedFileContent>
{
    public override ValidationResult Validate(HostedFileContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for HostedFileContent
        return ValidationResult.Success();
    }
}
