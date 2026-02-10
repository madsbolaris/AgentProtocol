using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for MessageUpdateContent.
/// </summary>
public class MessageUpdateContentValidator : ContentValidatorBase<MessageUpdateContent>
{
    public override ValidationResult Validate(MessageUpdateContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for MessageUpdateContent
        return ValidationResult.Success();
    }
}
