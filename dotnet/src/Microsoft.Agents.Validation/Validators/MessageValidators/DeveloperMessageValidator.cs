using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for DeveloperMessage.
/// </summary>
public class DeveloperMessageValidator : MessageValidatorBase<DeveloperMessage>
{
    protected override List<ValidationError> ValidateSpecificFields(DeveloperMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-009: DeveloperMessage content must be non-empty
        if (string.IsNullOrWhiteSpace(message.Content))
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_009,
                "DeveloperMessage content must be non-empty",
                "Content"));
        }

        // ROLE-002: DeveloperMessage can only contain TextContent
        // Note: DeveloperMessage uses Content property, not Contents list

        return errors;
    }
}
