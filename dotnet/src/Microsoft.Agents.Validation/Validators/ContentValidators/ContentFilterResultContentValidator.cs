using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for ContentFilterResultContent.
/// </summary>
public class ContentFilterResultContentValidator : ContentValidatorBase<ContentFilterResultContent>
{
    public override ValidationResult Validate(ContentFilterResultContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for ContentFilterResultContent
        return ValidationResult.Success();
    }
}
