using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for UserMessage.
/// </summary>
public class UserMessageValidator : MessageValidatorBase<UserMessage>
{
    protected override List<ValidationError> ValidateSpecificFields(UserMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-010: UserMessage must have at least one content item
        if (message.Contents == null || message.Contents.Count == 0)
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_010,
                "UserMessage must have at least one content item",
                "Contents"));
        }
        else
        {
            // ROLE-005: UserMessage cannot contain FunctionCallContent
            var hasFunctionCall = message.Contents.Any(c => c is FunctionCallContent);
            if (hasFunctionCall)
            {
                errors.Add(CreateError(
                    ValidationErrorCode.ROLE_005,
                    "UserMessage cannot contain FunctionCallContent",
                    "Contents"));
            }

            // Validate content items
            errors.AddRange(ValidateContentItems(message.Contents, context));
        }

        // REL-011: UserMessage user-id must be non-empty when present
        if (message.UserId != null && string.IsNullOrWhiteSpace(message.UserId))
        {
            errors.Add(CreateError(
                ValidationErrorCode.REL_011,
                "UserMessage user-id must be non-empty when present",
                "UserId"));
        }

        return errors;
    }
}
