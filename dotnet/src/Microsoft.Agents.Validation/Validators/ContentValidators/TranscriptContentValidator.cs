using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for TranscriptContent.
/// </summary>
public class TranscriptContentValidator : ContentValidatorBase<TranscriptContent>
{
    public override ValidationResult Validate(TranscriptContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for TranscriptContent
        return ValidationResult.Success();
    }
}
