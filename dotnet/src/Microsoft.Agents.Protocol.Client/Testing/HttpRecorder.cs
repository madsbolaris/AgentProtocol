using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Microsoft.Agents.Protocol.Client.Testing;

/// <summary>
/// Records HTTP request/response pairs for Agent Protocol client tests.
/// Similar to LLMRecorder but for HTTP interactions.
/// </summary>
public class HttpRecorder
{
    private readonly string _recordingsDir;
    private int _callCount = 0;
    private readonly JsonSerializerOptions _jsonOptions;

    public HttpRecorder(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));
        Directory.CreateDirectory(_recordingsDir);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    /// <summary>
    /// Generate deterministic hash from request parameters.
    /// </summary>
    public string HashRequest(string method, string path, string? body)
    {
        var requestDict = new Dictionary<string, object>
        {
            ["method"] = method,
            ["path"] = path,
            ["body"] = body ?? ""
        };

        var json = JsonSerializer.Serialize(requestDict, new JsonSerializerOptions
        {
            WriteIndented = false,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(json));
        return Convert.ToHexString(hash)[..16].ToLowerInvariant();
    }

    /// <summary>
    /// Record an HTTP request/response pair.
    /// </summary>
    public async Task RecordAsync(
        string method,
        string path,
        string? requestBody,
        HttpStatusCode statusCode,
        string responseBody,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);
        var timestamp = DateTime.UtcNow;
        var hashKey = HashRequest(method, path, requestBody);

        // Record request
        var requestData = new
        {
            callId,
            timestamp,
            hash = hashKey,
            method,
            path,
            body = requestBody
        };

        var requestFile = Path.Combine(_recordingsDir, $"{hashKey}.request.json");
        await File.WriteAllTextAsync(
            requestFile,
            JsonSerializer.Serialize(requestData, _jsonOptions),
            cancellationToken);

        // Record response
        var responseData = new
        {
            callId,
            timestamp = DateTime.UtcNow,
            hash = hashKey,
            statusCode = (int)statusCode,
            body = responseBody
        };

        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        await File.WriteAllTextAsync(
            responseFile,
            JsonSerializer.Serialize(responseData, _jsonOptions),
            cancellationToken);

        Console.WriteLine($"  📼 Recorded HTTP call #{callId}: {method} {path} → {hashKey}");
    }
}
