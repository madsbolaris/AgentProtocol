using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for HostedVectorStoreContent.
/// </summary>
public class HostedVectorStoreContentValidator : ContentValidatorBase<HostedVectorStoreContent>
{
    public override ValidationResult Validate(HostedVectorStoreContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for HostedVectorStoreContent
        return ValidationResult.Success();
    }
}
