using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators;

/// <summary>
/// Validator for cross-message relationships within a thread.
/// </summary>
public class RelationshipValidator
{
    /// <summary>
    /// Validates relationships between messages in the context.
    /// </summary>
    public static ValidationResult ValidateRelationships(ValidationContext context)
    {
        var errors = new List<ValidationError>();

        // Validate function call/result matching
        errors.AddRange(ValidateFunctionCallResults(context));

        // Validate message reactions
        errors.AddRange(ValidateMessageReferences(context));

        return new ValidationResult(errors);
    }

    /// <summary>
    /// Validates that all function calls have matching results and vice versa.
    /// </summary>
    private static List<ValidationError> ValidateFunctionCallResults(ValidationContext context)
    {
        var errors = new List<ValidationError>();

        // Check for function calls without results (warning, not error - result may be pending)
        foreach (var (callId, functionCall) in context.FunctionCallRegistry)
        {
            if (!context.FunctionResultExists(callId))
            {
                // This is actually valid - the result might not have arrived yet
                // So this is informational, not an error
            }
        }

        // Check for function results without calls (this IS an error)
        foreach (var (callId, functionResult) in context.FunctionResultRegistry)
        {
            if (!context.FunctionCallExists(callId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_002,
                    $"Function result has call-id '{callId}' but no matching function call was found",
                    "CallId"));
            }
        }

        return errors;
    }

    /// <summary>
    /// Validates message references (reactions, deletes, updates).
    /// </summary>
    private static List<ValidationError> ValidateMessageReferences(ValidationContext context)
    {
        var errors = new List<ValidationError>();

        // Check MessageReactionContent, MessageDeleteContent, MessageUpdateContent references
        foreach (var (messageId, message) in context.MessageRegistry)
        {
            if (message.Contents == null)
                continue;

            foreach (var content in message.Contents)
            {
                // REL-013: MessageReactionContent referenced-message-id must exist
                if (content is MessageReactionContent reaction &&
                    !string.IsNullOrWhiteSpace(reaction.ReferencedMessageId))
                {
                    if (!context.MessageExists(reaction.ReferencedMessageId))
                    {
                        errors.Add(CreateError(
                            ValidationErrorCode.REL_013,
                            $"MessageReactionContent references message '{reaction.ReferencedMessageId}' which does not exist",
                            "ReferencedMessageId"));
                    }
                }

                // REL-014: MessageDeleteContent message-id must exist
                if (content is MessageDeleteContent delete &&
                    !string.IsNullOrWhiteSpace(delete.MessageId))
                {
                    if (!context.MessageExists(delete.MessageId))
                    {
                        errors.Add(CreateError(
                            ValidationErrorCode.REL_014,
                            $"MessageDeleteContent references message '{delete.MessageId}' which does not exist",
                            "MessageId"));
                    }
                }

                // REL-014: MessageUpdateContent message-id must exist
                if (content is MessageUpdateContent update &&
                    !string.IsNullOrWhiteSpace(update.MessageId))
                {
                    if (!context.MessageExists(update.MessageId))
                    {
                        errors.Add(CreateError(
                            ValidationErrorCode.REL_014,
                            $"MessageUpdateContent references message '{update.MessageId}' which does not exist",
                            "MessageId"));
                    }
                }
            }
        }

        return errors;
    }

    private static ValidationError CreateError(string code, string message, string? field = null)
    {
        return new ValidationError(code, message, field);
    }
}
