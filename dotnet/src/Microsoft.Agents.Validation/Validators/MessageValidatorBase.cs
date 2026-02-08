using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators;

/// <summary>
/// Base class for message validators.
/// </summary>
/// <typeparam name="T">The type of message to validate.</typeparam>
public abstract class MessageValidatorBase<T> : IValidator<T> where T : ChatMessage
{
    /// <summary>
    /// Validates the message and returns a validation result.
    /// </summary>
    public ValidationResult Validate(T message, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // Check for duplicate message-id BEFORE registering
        // MSG-002: message-id must be unique within a thread
        if (context != null && !string.IsNullOrWhiteSpace(message.MessageId))
        {
            if (context.MessageExists(message.MessageId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.MSG_002,
                    $"Duplicate message ID '{message.MessageId}' found. Each message must have a unique ID within the thread.",
                    "MessageId"));
            }

            // Register message in context so it's available for subsequent validations
            context.RegisterMessage(message);
        }

        // Validate common message fields (excluding MSG-002 which we already checked)
        var commonErrors = ValidateCommonFields(message, context);
        errors.AddRange(commonErrors);

        // Validate message-specific fields
        var specificErrors = ValidateSpecificFields(message, context);
        errors.AddRange(specificErrors);

        return new ValidationResult(errors);
    }

    /// <summary>
    /// Validates common fields present on all messages.
    /// </summary>
    protected virtual List<ValidationError> ValidateCommonFields(T message, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        // MSG-001: message-id must be non-empty string
        if (string.IsNullOrWhiteSpace(message.MessageId))
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_001,
                "Message ID must be a non-empty string",
                "MessageId"));
        }
        // Note: MSG-002 (duplicate message-id) is now checked in the Validate method before registration

        // MSG-003: created-at must be valid ISO 8601 datetime (DateTime type ensures this)
        // MSG-004: created-at must not be in the future
        if (message.CreatedAt > DateTime.UtcNow.AddMinutes(5)) // Allow 5-minute clock skew
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_004,
                $"Message created-at '{message.CreatedAt:O}' cannot be in the future",
                "CreatedAt"));
        }

        // MSG-005: author-name must not exceed 100 characters
        if (!string.IsNullOrEmpty(message.AuthorName) && message.AuthorName.Length > 100)
        {
            errors.Add(CreateError(
                ValidationErrorCode.MSG_005,
                $"Author name must not exceed 100 characters (actual: {message.AuthorName.Length})",
                "AuthorName"));
        }

        // MSG-006: parent-message-id must reference existing message in thread
        if (!string.IsNullOrWhiteSpace(message.ParentMessageId))
        {
            if (context != null && !context.MessageExists(message.ParentMessageId))
            {
                errors.Add(CreateError(
                    ValidationErrorCode.MSG_006,
                    $"Parent message ID '{message.ParentMessageId}' not found in thread",
                    "ParentMessageId"));
            }
        }

        return errors;
    }

    /// <summary>
    /// Validates fields specific to the message type.
    /// </summary>
    protected abstract List<ValidationError> ValidateSpecificFields(T message, ValidationContext? context);

    /// <summary>
    /// Helper method to create a validation error.
    /// </summary>
    protected ValidationError CreateError(string code, string message, string? field = null)
    {
        return new ValidationError(code, message, field);
    }

    /// <summary>
    /// Validates content items in the message.
    /// </summary>
    protected List<ValidationError> ValidateContentItems(List<AIContent>? contents, ValidationContext? context)
    {
        var errors = new List<ValidationError>();

        if (contents == null || contents.Count == 0)
            return errors;

        foreach (var content in contents)
        {
            // Use pattern matching to call the validator with the correct concrete type
            // This ensures the generic type parameter T is properly resolved
            var result = content switch
            {
                TextContent text => new Validators.ContentValidators.TextContentValidator().Validate(text, context),
                FunctionCallContent call => new Validators.ContentValidators.FunctionCallContentValidator().Validate(call, context),
                FunctionResultContent funcResult => new Validators.ContentValidators.FunctionResultContentValidator().Validate(funcResult, context),
                ImageContent img => new Validators.ContentValidators.ImageContentValidator().Validate(img, context),
                ErrorContent err => new Validators.ContentValidators.ErrorContentValidator().Validate(err, context),
                AudioContent audio => new Validators.ContentValidators.AudioContentValidator().Validate(audio, context),
                VideoContent video => new Validators.ContentValidators.VideoContentValidator().Validate(video, context),
                SearchResultContent search => new Validators.ContentValidators.SearchResultContentValidator().Validate(search, context),
                DocumentContent doc => new Validators.ContentValidators.DocumentContentValidator().Validate(doc, context),
                _ => ValidationResult.Success()
            };
            errors.AddRange(result.Errors);
        }

        return errors;
    }

    /// <summary>
    /// Gets the appropriate content validator for the given content type.
    /// </summary>
    private IValidator<AIContent>? GetContentValidator(AIContent content)
    {
        // This is a simplified approach - in production, use dependency injection or a factory
        return content switch
        {
            TextContent => new Validators.ContentValidators.TextContentValidator() as IValidator<AIContent>,
            FunctionCallContent => new Validators.ContentValidators.FunctionCallContentValidator() as IValidator<AIContent>,
            FunctionResultContent => new Validators.ContentValidators.FunctionResultContentValidator() as IValidator<AIContent>,
            ImageContent => new Validators.ContentValidators.ImageContentValidator() as IValidator<AIContent>,
            ErrorContent => new Validators.ContentValidators.ErrorContentValidator() as IValidator<AIContent>,
            AudioContent => new Validators.ContentValidators.AudioContentValidator() as IValidator<AIContent>,
            VideoContent => new Validators.ContentValidators.VideoContentValidator() as IValidator<AIContent>,
            SearchResultContent => new Validators.ContentValidators.SearchResultContentValidator() as IValidator<AIContent>,
            DocumentContent => new Validators.ContentValidators.DocumentContentValidator() as IValidator<AIContent>,
            AdaptiveCardContent => new Validators.ContentValidators.AdaptiveCardContentValidator() as IValidator<AIContent>,
            EventContent => new Validators.ContentValidators.EventContentValidator() as IValidator<AIContent>,
            _ => null
        };
    }
}
