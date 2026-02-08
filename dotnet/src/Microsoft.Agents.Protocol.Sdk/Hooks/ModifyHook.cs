namespace Microsoft.Agents.Protocol.Sdk.Hooks;

/// <summary>
/// Modify hook that transforms message content.
/// Used for PII redaction, formatting, translation, etc.
/// </summary>
public class ModifyHook : ProtocolHook
{
    /// <summary>
    /// Predefined patterns to redact (email, phone, ssn, credit_card, etc.)
    /// </summary>
    public string[]? PredefinedPatterns { get; set; }

    /// <summary>
    /// Custom regex patterns to find
    /// </summary>
    public string[]? CustomPatterns { get; set; }

    /// <summary>
    /// Replacement text (can include capture groups like $1)
    /// </summary>
    public string Replacement { get; set; } = "[REDACTED]";

    /// <summary>
    /// Whether to apply to message text
    /// </summary>
    public bool ApplyToText { get; set; } = true;

    /// <summary>
    /// Whether to apply to tool arguments
    /// </summary>
    public bool ApplyToToolArgs { get; set; } = true;

    /// <summary>
    /// Whether to apply to tool results
    /// </summary>
    public bool ApplyToToolResults { get; set; } = true;
}
