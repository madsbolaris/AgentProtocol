using Microsoft.Agents;
using Microsoft.Agents.Protocol.Validation.Validators.MessageValidators;
using AgentThread = Microsoft.Agents.Thread;

namespace Microsoft.Agents.Protocol.Validation.Validators;

/// <summary>
/// Validator for Thread, which orchestrates validation across all messages.
/// </summary>
public class ThreadValidator : IValidator<AgentThread>
{
    public ValidationResult Validate(AgentThread thread, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // Create context if not provided
        context ??= new ValidationContext { Thread = thread };

        // THR-001: Thread must have unique message-ids (validated during message validation)
        // THR-002: Thread status must be valid enum
        // (Status is enum type, so this is enforced by type system)

        // THR-003: Thread created-at must be before or equal to last-message-at
        if (thread.LastMessageAt.HasValue &&
            thread.CreatedAt > thread.LastMessageAt.Value)
        {
            errors.Add(CreateError(
                ValidationErrorCode.THR_003,
                $"Thread created-at '{thread.CreatedAt:O}' must be before or equal to last-message-at '{thread.LastMessageAt:O}'",
                "CreatedAt"));
        }

        // THR-004: Thread unread-count must be non-negative
        if (thread.UnreadCount.HasValue && thread.UnreadCount.Value < 0)
        {
            errors.Add(CreateError(
                ValidationErrorCode.THR_004,
                $"Thread unread-count must be non-negative (actual: {thread.UnreadCount})",
                "UnreadCount"));
        }

        // Validate all messages in the thread
        if (thread.Messages != null)
        {
            foreach (var message in thread.Messages)
            {
                // Use pattern matching to call the validator with the correct concrete type
                // This ensures the generic type parameter T is properly resolved
                var result = message switch
                {
                    SystemMessage sysMsg => new SystemMessageValidator().Validate(sysMsg, context),
                    DeveloperMessage devMsg => new DeveloperMessageValidator().Validate(devMsg, context),
                    UserMessage userMsg => new UserMessageValidator().Validate(userMsg, context),
                    AgentMessage agentMsg => new AgentMessageValidator().Validate(agentMsg, context),
                    ToolMessage toolMsg => new ToolMessageValidator().Validate(toolMsg, context),
                    ChannelMessage chanMsg => new ChannelMessageValidator().Validate(chanMsg, context),
                    _ => ValidationResult.Success()
                };
                errors.AddRange(result.Errors);
            }
        }

        // THR-005: All parent-message-id references must exist in thread
        // THR-006: Thread must not have circular parent-message-id references
        var dagErrors = ValidateParentMessageDAG(thread.Messages, context);
        errors.AddRange(dagErrors);

        return new ValidationResult(errors);
    }

    /// <summary>
    /// Validates that parent-message-id references form a valid DAG (no cycles).
    /// </summary>
    private List<ValidationError> ValidateParentMessageDAG(List<ChatMessage>? messages, ValidationContext context)
    {
        var errors = new List<ValidationError>();

        if (messages == null || messages.Count == 0)
            return errors;

        foreach (var message in messages)
        {
            if (string.IsNullOrWhiteSpace(message.ParentMessageId))
                continue;

            // Check for cycles by following parent chain
            var visited = new HashSet<string>();
            var current = message.ParentMessageId;

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (visited.Contains(current))
                {
                    errors.Add(CreateError(
                        ValidationErrorCode.THR_006,
                        $"Circular parent-message-id reference detected involving message '{current}'",
                        "ParentMessageId"));
                    break;
                }

                visited.Add(current);

                var parentMessage = context.GetMessage(current);
                if (parentMessage == null)
                {
                    // THR-005: Parent message not found
                    errors.Add(CreateError(
                        ValidationErrorCode.THR_005,
                        $"Parent message ID '{current}' referenced by message '{message.MessageId}' not found in thread",
                        "ParentMessageId"));
                    break;
                }

                current = parentMessage.ParentMessageId;
            }
        }

        return errors;
    }

    /// <summary>
    /// Gets the appropriate message validator for the given message type.
    /// </summary>
    private IValidator<ChatMessage>? GetMessageValidator(ChatMessage message)
    {
        return message switch
        {
            SystemMessage => new SystemMessageValidator() as IValidator<ChatMessage>,
            DeveloperMessage => new DeveloperMessageValidator() as IValidator<ChatMessage>,
            UserMessage => new UserMessageValidator() as IValidator<ChatMessage>,
            AgentMessage => new AgentMessageValidator() as IValidator<ChatMessage>,
            ToolMessage => new ToolMessageValidator() as IValidator<ChatMessage>,
            ChannelMessage => new ChannelMessageValidator() as IValidator<ChatMessage>,
            _ => null
        };
    }

    private ValidationError CreateError(string code, string message, string? field = null)
    {
        return new ValidationError(code, message, field);
    }
}
