using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for SearchResultContent.
/// </summary>
public class SearchResultContentValidator : ContentValidatorBase<SearchResultContent>
{
    public override ValidationResult Validate(SearchResultContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-012: SearchResultContent url must be valid URI
        var uriError = ValidateUri(content.Url, "Url",
            ValidationErrorCode.CNT_012,
            $"SearchResultContent url '{content.Url}' must be a valid URI");
        if (uriError != null)
            errors.Add(uriError);

        return new ValidationResult(errors);
    }
}
