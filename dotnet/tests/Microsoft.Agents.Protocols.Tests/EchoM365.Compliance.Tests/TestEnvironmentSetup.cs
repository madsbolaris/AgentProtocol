using System;
using System.Runtime.CompilerServices;

namespace Microsoft.Agents.Protocols.Tests.EchoM365.Compliance;

/// <summary>
/// Automatically configures environment variables for all tests.
///
/// All tests automatically use LLM recordings instead of real API calls.
/// This ensures:
/// - Fast test execution (no API calls)
/// - Deterministic results (same responses every time)
/// - Free testing (no API costs)
/// - Offline testing capability
/// </summary>
internal static class TestEnvironmentSetup
{
    /// <summary>
    /// Module initializer that runs before any tests.
    /// Sets up environment variables for test execution.
    /// </summary>
    [ModuleInitializer]
    public static void Initialize()
    {
        // Set environment variables for all tests
        // Only set if not already set (allows manual override)
        Environment.SetEnvironmentVariable("USE_LLM_RECORDINGS",
            Environment.GetEnvironmentVariable("USE_LLM_RECORDINGS") ?? "true");

        Environment.SetEnvironmentVariable("RECORD_LLM",
            Environment.GetEnvironmentVariable("RECORD_LLM") ?? "false");
    }
}
