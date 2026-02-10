using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for UserInputRequestContent.
/// </summary>
public class UserInputRequestContentValidator : ContentValidatorBase<UserInputRequestContent>
{
    public override ValidationResult Validate(UserInputRequestContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for UserInputRequestContent
        return ValidationResult.Success();
    }
}
