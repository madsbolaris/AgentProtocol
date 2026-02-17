using System.Net;
using System.Text.Json;

namespace Microsoft.Agents.Protocol.Client.Testing;

/// <summary>
/// Replays recorded HTTP responses for deterministic testing.
/// Similar to LLMPlayer but for HTTP interactions.
/// </summary>
public class HttpPlayer
{
    private readonly string _recordingsDir;
    private readonly HttpRecorder _recorder;
    private int _callCount = 0;

    public HttpPlayer(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));
        if (!Directory.Exists(_recordingsDir))
        {
            throw new DirectoryNotFoundException($"Recordings directory not found: {_recordingsDir}");
        }
        _recorder = new HttpRecorder(_recordingsDir);
    }

    /// <summary>
    /// Replay a recorded HTTP response.
    /// </summary>
    public async Task<(HttpStatusCode statusCode, string body)> ReplayAsync(
        string method,
        string path,
        string? requestBody,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);

        // Generate hash to find recording
        var hashKey = _recorder.HashRequest(method, path, requestBody);

        // Load recorded response
        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        if (!File.Exists(responseFile))
        {
            throw new FileNotFoundException(
                $"No recorded HTTP response found for request hash: {hashKey}\n" +
                $"Expected file: {responseFile}\n\n" +
                $"This usually means:\n" +
                $"1. Tests need to be run in generation mode first: RECORD_HTTP=true\n" +
                $"2. The request parameters have changed (different hash)\n" +
                $"3. The recording file was deleted\n\n" +
                $"Request details:\n" +
                $"  Method: {method}\n" +
                $"  Path: {path}\n" +
                $"  Body: {requestBody ?? "(null)"}\n",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying HTTP call #{callId}: {method} {path} → {hashKey}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseData = JsonDocument.Parse(responseJson);

        var statusCode = (HttpStatusCode)responseData.RootElement.GetProperty("statusCode").GetInt32();
        var body = responseData.RootElement.GetProperty("body").GetString() ?? "";

        return (statusCode, body);
    }
}
