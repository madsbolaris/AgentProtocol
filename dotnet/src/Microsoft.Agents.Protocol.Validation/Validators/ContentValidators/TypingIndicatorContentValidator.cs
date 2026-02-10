using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for TypingIndicatorContent.
/// </summary>
public class TypingIndicatorContentValidator : ContentValidatorBase<TypingIndicatorContent>
{
    public override ValidationResult Validate(TypingIndicatorContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for TypingIndicatorContent
        return ValidationResult.Success();
    }
}
