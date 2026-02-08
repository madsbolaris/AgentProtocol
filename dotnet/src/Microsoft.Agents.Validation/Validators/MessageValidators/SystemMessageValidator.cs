using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for SystemMessage.
/// </summary>
public class SystemMessageValidator : MessageValidatorBase<SystemMessage>
{
    protected override List<ValidationError> ValidateSpecificFields(SystemMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-008: SystemMessage content must be non-empty
        if (string.IsNullOrWhiteSpace(message.Content))
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_008,
                "SystemMessage content must be non-empty",
                "Content"));
        }

        // ROLE-001: SystemMessage can only contain TextContent
        // Note: SystemMessage uses Content property, not Contents list
        // This rule applies when SystemMessage is extended to support Contents

        return errors;
    }
}
