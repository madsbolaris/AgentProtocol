using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.MessageValidators;

/// <summary>
/// Validator for ToolMessage.
/// </summary>
public class ToolMessageValidator : MessageValidatorBase<ToolMessage>
{
    protected override List<ValidationError> ValidateSpecificFields(ToolMessage message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-012: ToolMessage must have call-id and name
        if (string.IsNullOrWhiteSpace(message.CallId))
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_012,
                "ToolMessage must have a call-id",
                "CallId"));
        }

        if (string.IsNullOrWhiteSpace(message.Name))
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_012,
                "ToolMessage must have a name",
                "Name"));
        }

        // REL-005, REL-007, REL-008: Cross-validate with function calls if context available
        // This should happen regardless of whether there are contents
        if (context != null && !string.IsNullOrWhiteSpace(message.CallId))
        {
            var functionCall = context.GetFunctionCall(message.CallId);
            if (functionCall == null)
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_005,
                    $"ToolMessage call-id '{message.CallId}' does not match any FunctionCallContent in preceding AgentMessage",
                    "CallId"));
            }
            else if (!string.IsNullOrWhiteSpace(message.Name) &&
                     !string.IsNullOrWhiteSpace(functionCall.Name) &&
                     message.Name != functionCall.Name)
            {
                errors.Add(CreateError(
                    ValidationErrorCode.REL_008,
                    $"ToolMessage name '{message.Name}' does not match FunctionCallContent name '{functionCall.Name}' for call-id '{message.CallId}'",
                    "Name"));
            }
        }

        // ROLE-004: ToolMessage can only contain FunctionResultContent, ErrorContent
        // ROLE-008: FunctionResultContent can only appear in ToolMessage
        if (message.Contents != null && message.Contents.Count > 0)
        {
            var invalidContent = message.Contents
                .Where(c => c is not FunctionResultContent && c is not ErrorContent)
                .ToList();

            if (invalidContent.Any())
            {
                var contentTypes = string.Join(", ", invalidContent.Select(c => c.GetType().Name));
                errors.Add(CreateError(
                    ValidationErrorCode.ROLE_004,
                    $"ToolMessage can only contain FunctionResultContent or ErrorContent, found: {contentTypes}",
                    "Contents"));
            }

            // Validate content items
            errors.AddRange(ValidateContentItems(message.Contents, context));
        }

        return errors;
    }
}
