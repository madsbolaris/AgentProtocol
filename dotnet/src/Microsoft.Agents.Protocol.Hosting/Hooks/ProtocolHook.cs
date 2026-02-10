namespace Microsoft.Agents.Protocol.Hosting.Hooks;

/// <summary>
/// Base class for Protocol hooks (declarative hooks in Agent Protocol spec)
/// </summary>
public abstract class ProtocolHook
{
    /// <summary>
    /// Unique name for this hook
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// When this hook should execute
    /// </summary>
    public HookLifecycle Lifecycle { get; set; }

    /// <summary>
    /// Optional condition for when this hook applies
    /// </summary>
    public HookCondition? Condition { get; set; }

    /// <summary>
    /// Whether the hook is enabled
    /// </summary>
    public bool Enabled { get; set; } = true;
}

/// <summary>
/// Protocol hook lifecycle points
/// </summary>
public enum HookLifecycle
{
    /// <summary>
    /// Before the run starts
    /// </summary>
    BeforeRun,

    /// <summary>
    /// After the run completes
    /// </summary>
    AfterRun,

    /// <summary>
    /// Before each tool execution
    /// </summary>
    BeforeToolExecution,

    /// <summary>
    /// After each tool execution
    /// </summary>
    AfterToolExecution
}

/// <summary>
/// Base class for hook conditions
/// </summary>
public abstract class HookCondition
{
}

/// <summary>
/// Keyword-based condition
/// </summary>
public class KeywordCondition : HookCondition
{
    public string[] Keywords { get; set; } = Array.Empty<string>();
    public bool CaseSensitive { get; set; } = false;
}

/// <summary>
/// Regex-based condition
/// </summary>
public class RegexCondition : HookCondition
{
    public string Pattern { get; set; } = string.Empty;
}

/// <summary>
/// Tool-specific condition
/// </summary>
public class ToolCondition : HookCondition
{
    public string[] ToolNames { get; set; } = Array.Empty<string>();
}
