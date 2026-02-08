using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for VideoContent.
/// </summary>
public class VideoContentValidator : ContentValidatorBase<VideoContent>
{
    public override ValidationResult Validate(VideoContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-010: VideoContent frame-rate must be positive
        var frameRateError = ValidatePositive(content.FrameRate, "FrameRate",
            ValidationErrorCode.CNT_010,
            "VideoContent frame-rate must be a positive number");
        if (frameRateError != null)
            errors.Add(frameRateError);

        // Also validate width/height if present
        var widthError = ValidatePositive(content.Width, "Width",
            ValidationErrorCode.CNT_010,
            "VideoContent width must be a positive integer");
        if (widthError != null)
            errors.Add(widthError);

        var heightError = ValidatePositive(content.Height, "Height",
            ValidationErrorCode.CNT_010,
            "VideoContent height must be a positive integer");
        if (heightError != null)
            errors.Add(heightError);

        return new ValidationResult(errors);
    }
}
