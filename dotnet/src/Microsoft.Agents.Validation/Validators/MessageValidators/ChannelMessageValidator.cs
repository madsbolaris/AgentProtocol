using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for ChannelMessage.
/// </summary>
public class ChannelMessageValidator : MessageValidatorBase<ChannelMessage>
{
    protected override List<ValidationError> ValidateSpecificFields(ChannelMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // ROLE-006: ChannelMessage can contain EventContent, TraceContent, ActionContent
        if (message.Contents != null && message.Contents.Count > 0)
        {
            var invalidContent = message.Contents
                .Where(c => c is not EventContent && c is not TraceContent && c is not ActionContent)
                .ToList();

            if (invalidContent.Any())
            {
                var contentTypes = string.Join(", ", invalidContent.Select(c => c.GetType().Name));
                errors.Add(CreateError(
                    ValidationErrorCode.ROLE_006,
                    $"ChannelMessage can only contain EventContent, TraceContent, or ActionContent, found: {contentTypes}",
                    "Contents"));
            }

            // Validate content items
            errors.AddRange(ValidateContentItems(message.Contents, context));
        }

        return errors;
    }
}
