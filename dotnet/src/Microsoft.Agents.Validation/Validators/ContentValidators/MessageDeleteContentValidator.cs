using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for MessageDeleteContent.
/// </summary>
public class MessageDeleteContentValidator : ContentValidatorBase<MessageDeleteContent>
{
    public override ValidationResult Validate(MessageDeleteContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for MessageDeleteContent
        return ValidationResult.Success();
    }
}
