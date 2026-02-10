using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that checks if a file has a minimum size in bytes.
/// </summary>
public class FileMinBytesJudge : JudgeAgentBase
{
    public override string AgentName => "file_min_bytes";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var filePath = GetTextContent(actualOutput).Trim();

        if (string.IsNullOrWhiteSpace(filePath))
        {
            return Task.FromResult(Failure(0.0f, "No file path specified in output"));
        }

        if (!File.Exists(filePath))
        {
            return Task.FromResult(Failure(0.0f, $"File does not exist: {filePath}"));
        }

        var minBytes = 0L;
        if (!string.IsNullOrWhiteSpace(judge.Args))
        {
            if (!long.TryParse(judge.Args, out minBytes))
            {
                return Task.FromResult(Failure(0.0f, $"Invalid min bytes value: {judge.Args}"));
            }
        }

        var fileInfo = new FileInfo(filePath);
        var actualBytes = fileInfo.Length;

        if (actualBytes >= minBytes)
        {
            return Task.FromResult(new JudgeResult
            {
                Passed = true,
                Score = 1.0f,
                Details = new System.Collections.Generic.Dictionary<string, object>
                {
                    ["file_path"] = filePath,
                    ["actual_bytes"] = actualBytes,
                    ["min_bytes"] = minBytes
                }
            });
        }

        return Task.FromResult(Failure(
            (float)actualBytes / minBytes,
            $"File size {actualBytes} bytes is less than minimum {minBytes} bytes"));
    }
}
