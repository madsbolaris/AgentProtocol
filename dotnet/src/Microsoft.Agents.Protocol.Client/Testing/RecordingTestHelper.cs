namespace Microsoft.Agents.Protocol.Client.Testing;

/// <summary>
/// Helper for creating test clients with recording support.
/// Uses shared test-data/llm-recordings/docs/ for cross-language compatibility.
/// </summary>
public static class RecordingTestHelper
{
    // Shared recordings directory (repository root /test-data/llm-recordings/docs/)
    private const string SharedRecordingsPath = "../../../../../test-data/llm-recordings/docs";

    /// <summary>
    /// Get the recordings directory for a specific test scenario.
    /// Uses shared test-data/llm-recordings/docs/ for cross-language compatibility.
    /// </summary>
    public static string GetRecordingsDirectory(string scenarioName)
    {
        // Navigate to repo root, then to shared recordings
        var baseDir = Path.Combine(
            AppContext.BaseDirectory,
            SharedRecordingsPath,
            scenarioName);

        Directory.CreateDirectory(baseDir);
        return Path.GetFullPath(baseDir);
    }

    /// <summary>
    /// Check if we're in recording mode (based on environment variable).
    /// </summary>
    public static bool IsRecordMode()
    {
        var recordEnv = Environment.GetEnvironmentVariable("RECORD_HTTP");
        return !string.IsNullOrEmpty(recordEnv) &&
               (recordEnv.Equals("true", StringComparison.OrdinalIgnoreCase) ||
                recordEnv.Equals("1"));
    }

    /// <summary>
    /// Create an AgentProtocolClient with recording support.
    /// </summary>
    /// <param name="testName">Name of the test (used for recording directory)</param>
    /// <param name="baseUrl">Base URL of the agent server (only used in record mode)</param>
    public static AgentProtocolClient CreateRecordingClient(
        string testName,
        string baseUrl = "http://localhost:5000")
    {
        var recordingsDir = GetRecordingsDirectory(testName);
        var recordMode = IsRecordMode();

        var handler = new RecordingHttpMessageHandler(recordingsDir, recordMode);
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri(baseUrl)
        };

        // Create client using the recording-enabled HttpClient
        return new AgentProtocolClient(baseUrl, httpClient);
    }
}
