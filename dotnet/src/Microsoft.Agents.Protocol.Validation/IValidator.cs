namespace Microsoft.Agents.Protocol.Validation;

/// <summary>
/// Interface for validators that can validate objects of type T.
/// </summary>
/// <typeparam name="T">The type of object this validator can validate.</typeparam>
public interface IValidator<in T>
{
    /// <summary>
    /// Validates the given object and returns a validation result.
    /// </summary>
    /// <param name="obj">The object to validate.</param>
    /// <param name="context">Optional validation context for cross-object validation.</param>
    /// <returns>A validation result containing any errors found.</returns>
    ValidationResult Validate(T obj, ValidationContext? context = null);
}
