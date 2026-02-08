using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for EventContent.
/// </summary>
public class EventContentValidator : ContentValidatorBase<EventContent>
{
    public override ValidationResult Validate(EventContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-015: EventContent name must be non-empty
        var nameError = ValidateNotEmpty(content.Name, "Name",
            ValidationErrorCode.CNT_015,
            "EventContent name must be non-empty");
        if (nameError != null)
            errors.Add(nameError);

        return new ValidationResult(errors);
    }
}
