using Microsoft.Agents.Protocol.Model;
using Microsoft.Agents.Protocol.Model.Testing;

namespace Microsoft.Agents.Protocol.Hosting.Tests.Recording;

/// <summary>
/// Helper for creating test agents with LLM recording support.
/// </summary>
public static class LlmRecordingTestHelper
{
    private const string RecordingsPath = "Recordings";

    /// <summary>
    /// Get the recordings directory for a specific test.
    /// </summary>
    public static string GetRecordingsDirectory(string testName)
    {
        var baseDir = Path.Combine(
            AppContext.BaseDirectory,
            RecordingsPath,
            testName);

        Directory.CreateDirectory(baseDir);
        return baseDir;
    }

    /// <summary>
    /// Check if we're in recording mode (based on environment variable).
    /// </summary>
    public static bool IsRecordMode()
    {
        var recordEnv = Environment.GetEnvironmentVariable("RECORD_LLM");
        return !string.IsNullOrEmpty(recordEnv) &&
               (recordEnv.Equals("true", StringComparison.OrdinalIgnoreCase) ||
                recordEnv.Equals("1"));
    }

    /// <summary>
    /// Create an IProtocolLLMClient with recording support.
    /// </summary>
    /// <param name="testName">Name of the test (used for recording directory)</param>
    /// <param name="innerClient">The real LLM client (only used in record mode)</param>
    public static IProtocolLLMClient CreateRecordingLlmClient(
        string testName,
        IProtocolLLMClient? innerClient = null)
    {
        var recordingsDir = GetRecordingsDirectory(testName);
        var recordMode = IsRecordMode();

        if (recordMode)
        {
            if (innerClient == null)
            {
                throw new InvalidOperationException(
                    "Recording mode requires a real LLM client. " +
                    "Please provide an innerClient parameter with your LLM configuration.");
            }

            return new RecordingProtocolLLMClient(innerClient, recordingsDir);
        }
        else
        {
            // Replay mode - use a mock client that reads from recordings
            return new ReplayProtocolLlmClient(recordingsDir);
        }
    }
}
