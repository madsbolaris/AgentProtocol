using Microsoft.Agents.Xml.Generated.Models;

namespace Microsoft.Agents.Xml.Validation.Validators.ContentValidators;

/// <summary>
/// Validator for DocumentContent.
/// </summary>
public class DocumentContentValidator : ContentValidatorBase<DocumentContent>
{
    public override ValidationResult Validate(DocumentContent content, ValidationContext? context = null)
    {
        var errors = new List<ValidationError>();

        // CNT-013: DocumentContent document-id must be non-empty
        var docIdError = ValidateNotEmpty(content.DocumentId, "DocumentId",
            ValidationErrorCode.CNT_013,
            "DocumentContent document-id must be non-empty");
        if (docIdError != null)
            errors.Add(docIdError);

        return new ValidationResult(errors);
    }
}
