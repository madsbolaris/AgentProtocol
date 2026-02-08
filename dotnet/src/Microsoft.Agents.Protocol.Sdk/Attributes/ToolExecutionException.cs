namespace Microsoft.Agents.Protocol.Sdk.Attributes;

/// <summary>
/// Exception thrown by tool methods to indicate a controlled failure.
/// The message will be sent to the LLM as the tool result, allowing it to handle the error gracefully.
/// </summary>
/// <example>
/// <code>
/// [Tool("Process refund")]
/// public async Task&lt;RefundResult&gt; ProcessRefund(decimal amount)
/// {
///     if (amount &lt;= 0)
///     {
///         throw new ToolExecutionException("Amount must be greater than zero");
///     }
///
///     if (amount &gt; 1000)
///     {
///         throw new ToolExecutionException("Maximum refund amount is $1000");
///     }
///
///     return await _billingService.RefundAsync(amount);
/// }
/// </code>
/// </example>
public class ToolExecutionException : Exception
{
    /// <summary>
    /// Creates a new ToolExecutionException with a message that will be sent to the LLM.
    /// </summary>
    /// <param name="message">Error message explaining what went wrong</param>
    public ToolExecutionException(string message) : base(message)
    {
    }

    /// <summary>
    /// Creates a new ToolExecutionException with a message and inner exception.
    /// </summary>
    /// <param name="message">Error message explaining what went wrong</param>
    /// <param name="innerException">The exception that caused this error</param>
    public ToolExecutionException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
