using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for TextContent.
/// </summary>
public class TextContentValidator : ContentValidatorBase<TextContent>
{
    private const int MaxTextLength = 100000;

    public override ValidationResult Validate(TextContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-001: TextContent text must be non-empty
        var emptyError = ValidateNotEmpty(content.Text, "Text",
            ValidationErrorCode.CNT_001,
            "TextContent text must be non-empty");
        if (emptyError != null)
            errors.Add(emptyError);

        // CNT-002: TextContent text must not exceed 100,000 characters
        if (!string.IsNullOrEmpty(content.Text) && content.Text.Length > MaxTextLength)
        {
            errors.Add(CreateError(
                ValidationErrorCode.CNT_002,
                $"TextContent text must not exceed {MaxTextLength:N0} characters (actual: {content.Text.Length:N0})",
                "Text"));
        }

        return new ValidationResult(errors);
    }
}
