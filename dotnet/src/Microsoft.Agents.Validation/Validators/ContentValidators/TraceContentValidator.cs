using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for TraceContent.
/// </summary>
public class TraceContentValidator : ContentValidatorBase<TraceContent>
{
    public override ValidationResult Validate(TraceContent content, ValidationContext? context = null)
    {
        // TODO: Implement specific validation rules for TraceContent
        return ValidationResult.Success();
    }
}
