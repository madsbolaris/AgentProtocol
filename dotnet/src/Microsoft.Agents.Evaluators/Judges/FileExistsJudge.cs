using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that checks if a file exists at the specified path.
/// </summary>
public class FileExistsJudge : JudgeAgentBase
{
    public override string AgentName => "file_exists";

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

        var exists = File.Exists(filePath);

        if (exists)
        {
            var fileInfo = new FileInfo(filePath);
            return Task.FromResult(new JudgeResult
            {
                Passed = true,
                Score = 1.0f,
                Details = new System.Collections.Generic.Dictionary<string, object>
                {
                    ["file_path"] = filePath,
                    ["file_size"] = fileInfo.Length,
                    ["created"] = fileInfo.CreationTimeUtc,
                    ["modified"] = fileInfo.LastWriteTimeUtc
                }
            });
        }

        return Task.FromResult(Failure(0.0f, $"File does not exist: {filePath}"));
    }
}
