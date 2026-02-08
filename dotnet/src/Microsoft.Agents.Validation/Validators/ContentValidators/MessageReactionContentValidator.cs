using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for MessageReactionContent.
/// </summary>
public class MessageReactionContentValidator : ContentValidatorBase<MessageReactionContent>
{
    public override ValidationResult Validate(MessageReactionContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for MessageReactionContent
        return ValidationResult.Success();
    }
}
