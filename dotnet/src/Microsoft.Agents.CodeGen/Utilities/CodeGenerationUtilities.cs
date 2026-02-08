using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Formatting;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.Utilities;

/// <summary>
/// Common utilities for Roslyn-based code generation.
/// Consolidated from multiple generators to ensure consistency.
/// </summary>
public static class CodeGenerationUtilities
{
    /// <summary>
    /// Creates XML documentation comment trivia from documentation text.
    /// </summary>
    /// <param name="documentation">Documentation text (may contain multiple lines)</param>
    /// <param name="maxLines">Maximum number of documentation lines to include (default: unlimited)</param>
    /// <returns>SyntaxTriviaList containing XML comment trivia</returns>
    public static SyntaxTriviaList CreateXmlComment(string documentation, int maxLines = int.MaxValue)
    {
        if (string.IsNullOrWhiteSpace(documentation))
        {
            // Return minimal summary for empty documentation
            return TriviaList(
                Comment("/// <summary>"),
                Comment("/// </summary>"),
                CarriageReturnLineFeed
            );
        }

        var lines = documentation.Split('\n')
            .Select(line => line.Trim())
            .Where(line => !string.IsNullOrWhiteSpace(line))
            .Take(maxLines);

        var triviaList = new List<SyntaxTrivia>
        {
            Comment("/// <summary>")
        };

        foreach (var line in lines)
        {
            // Escape XML special characters in documentation
            var escapedLine = EscapeXmlComment(line);
            triviaList.Add(Comment($"/// {escapedLine}"));
        }

        triviaList.Add(Comment("/// </summary>"));
        triviaList.Add(CarriageReturnLineFeed);

        return TriviaList(triviaList);
    }

    /// <summary>
    /// Formats a Roslyn CompilationUnitSyntax using standard formatting rules.
    /// </summary>
    /// <param name="compilationUnit">The compilation unit to format</param>
    /// <returns>Formatted code as a string</returns>
    public static string FormatCode(CompilationUnitSyntax compilationUnit)
    {
        using var workspace = new AdhocWorkspace();
        var formatted = Formatter.Format(compilationUnit, workspace);
        return formatted.ToFullString();
    }

    /// <summary>
    /// Escapes XML special characters in documentation text.
    /// </summary>
    /// <param name="text">Text to escape</param>
    /// <returns>Escaped text safe for XML comments</returns>
    private static string EscapeXmlComment(string text)
    {
        return text
            .Replace("&", "&amp;")
            .Replace("<", "&lt;")
            .Replace(">", "&gt;");
    }
}
