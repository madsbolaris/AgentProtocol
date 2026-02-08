using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for TextReasoningContent.
/// </summary>
public class TextReasoningContentValidator : ContentValidatorBase<TextReasoningContent>
{
    public override ValidationResult Validate(TextReasoningContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for TextReasoningContent
        return ValidationResult.Success();
    }
}
