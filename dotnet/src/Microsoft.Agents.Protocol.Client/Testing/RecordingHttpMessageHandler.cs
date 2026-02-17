using System.Net;

namespace Microsoft.Agents.Protocol.Client.Testing;

/// <summary>
/// HTTP message handler that records or replays HTTP interactions.
/// </summary>
public class RecordingHttpMessageHandler : HttpMessageHandler
{
    private readonly bool _recordMode;
    private readonly string _recordingsDir;
    private readonly HttpRecorder? _recorder;
    private readonly HttpPlayer? _player;
    private readonly HttpClient? _innerHttpClient;

    /// <summary>
    /// Create a recording handler.
    /// </summary>
    /// <param name="recordingsDir">Directory to save/load recordings</param>
    /// <param name="recordMode">True to record real HTTP calls, false to replay</param>
    /// <param name="innerHandler">Inner handler for making real requests (only used in record mode)</param>
    public RecordingHttpMessageHandler(
        string recordingsDir,
        bool recordMode = false,
        HttpMessageHandler? innerHandler = null)
    {
        _recordMode = recordMode;
        _recordingsDir = recordingsDir;

        if (_recordMode)
        {
            _recorder = new HttpRecorder(_recordingsDir);
            var handler = innerHandler ?? new HttpClientHandler();
            _innerHttpClient = new HttpClient(handler);
        }
        else
        {
            _player = new HttpPlayer(_recordingsDir);
        }
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var method = request.Method.Method;
        var path = request.RequestUri?.PathAndQuery ?? "/";
        var requestBody = request.Content != null
            ? await request.Content.ReadAsStringAsync(cancellationToken)
            : null;

        if (_recordMode && _recorder != null && _innerHttpClient != null)
        {
            // Record mode: make real request and save recording
            var response = await _innerHttpClient.SendAsync(request, cancellationToken);
            var responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

            await _recorder.RecordAsync(
                method,
                path,
                requestBody,
                response.StatusCode,
                responseBody,
                cancellationToken);

            // Return response with new content (original stream was consumed)
            return new HttpResponseMessage(response.StatusCode)
            {
                Content = new StringContent(responseBody),
                RequestMessage = request
            };
        }
        else if (_player != null)
        {
            // Replay mode: load recorded response
            var (statusCode, body) = await _player.ReplayAsync(
                method,
                path,
                requestBody,
                cancellationToken);

            return new HttpResponseMessage(statusCode)
            {
                Content = new StringContent(body),
                RequestMessage = request
            };
        }
        else
        {
            throw new InvalidOperationException("RecordingHttpMessageHandler not properly initialized");
        }
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            _innerHttpClient?.Dispose();
        }
        base.Dispose(disposing);
    }
}
