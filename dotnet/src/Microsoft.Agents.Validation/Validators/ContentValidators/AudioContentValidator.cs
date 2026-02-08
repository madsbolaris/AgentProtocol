using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for AudioContent.
/// </summary>
public class AudioContentValidator : ContentValidatorBase<AudioContent>
{
    public override ValidationResult Validate(AudioContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-009: AudioContent duration must be positive
        var durationError = ValidatePositive(content.Duration, "Duration",
            ValidationErrorCode.CNT_009,
            "AudioContent duration must be a positive number");
        if (durationError != null)
            errors.Add(durationError);

        return new ValidationResult(errors);
    }
}
