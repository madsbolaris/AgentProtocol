using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for ImageContent.
/// </summary>
public class ImageContentValidator : ContentValidatorBase<ImageContent>
{
    public override ValidationResult Validate(ImageContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-006: ImageContent must have uri OR data (at least one)
        if (string.IsNullOrWhiteSpace(content.Uri))
        {
            errors.Add(CreateError(
                ValidationErrorCode.CNT_006,
                "ImageContent must have a uri",
                "Uri"));
        }

        // CNT-007: ImageContent width/height must be positive integers
        var widthError = ValidatePositive(content.Width, "Width",
            ValidationErrorCode.CNT_007,
            "ImageContent width must be a positive integer");
        if (widthError != null)
            errors.Add(widthError);

        var heightError = ValidatePositive(content.Height, "Height",
            ValidationErrorCode.CNT_007,
            "ImageContent height must be a positive integer");
        if (heightError != null)
            errors.Add(heightError);

        // CNT-008: ImageContent mime-type must be valid (image/*)
        if (!string.IsNullOrWhiteSpace(content.MimeType) &&
            !content.MimeType.StartsWith("image/", StringComparison.OrdinalIgnoreCase))
        {
            errors.Add(CreateError(
                ValidationErrorCode.CNT_008,
                $"ImageContent mime-type '{content.MimeType}' must start with 'image/'",
                "MimeType"));
        }

        return new ValidationResult(errors);
    }
}
