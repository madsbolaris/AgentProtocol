using Microsoft.Agents.Abstractions.Models;
using System.Text.RegularExpressions;

namespace Microsoft.Agents.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for AgentMessage.
/// </summary>
public partial class AgentMessageValidator : MessageValidatorBase<AgentMessage>
{
    [GeneratedRegex(@"^run_[a-zA-Z0-9_-]+$")]
    private static partial Regex CompletionIdRegex();

    protected override List<ValidationError> ValidateSpecificFields(AgentMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-011: AgentMessage must have at least one content item
        if (message.Contents == null || message.Contents.Count == 0)
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_011,
                "AgentMessage must have at least one content item",
                "Contents"));
        }
        else
        {
            // ROLE-003: AgentMessage can contain FunctionCallContent, TextContent, TextReasoningContent
            // ROLE-007: FunctionCallContent can only appear in AgentMessage
            // These are validated at content level

            // Validate content items
            errors.AddRange(ValidateContentItems(message.Contents, context));
        }

        // REL-009: AgentMessage completion-id must be valid format (run_*)
        if (!string.IsNullOrWhiteSpace(message.CompletionId) &&
            !CompletionIdRegex().IsMatch(message.CompletionId))
        {
            errors.Add(CreateError(
                ValidationErrorCode.REL_009,
                $"AgentMessage completion-id '{message.CompletionId}' must match format 'run_*'",
                "CompletionId"));
        }

        // REL-010: AgentMessage agent-id must be non-empty when present
        if (message.AgentId != null && string.IsNullOrWhiteSpace(message.AgentId))
        {
            errors.Add(CreateError(
                ValidationErrorCode.REL_010,
                "AgentMessage agent-id must be non-empty when present",
                "AgentId"));
        }

        return errors;
    }
}
