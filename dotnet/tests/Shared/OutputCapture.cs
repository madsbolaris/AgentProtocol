using System;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Security.Cryptography;
using System.Collections.Generic;

namespace Microsoft.Agents.Testing
{
    /// <summary>
    /// Captures test outputs for documentation and cross-platform validation.
    ///
    /// This class captures test outputs in a structured JSON format that can be:
    /// 1. Used in documentation as example outputs
    /// 2. Compared across Python and .NET implementations
    /// 3. Validated for consistency
    ///
    /// Modes:
    /// - Validation mode (default): Compares output against existing golden files
    /// - Update mode: Generates/updates golden files
    /// </summary>
    /// <example>
    /// <code>
    /// public class MyTests : IClassFixture&lt;OutputCaptureFixture&gt;
    /// {
    ///     private readonly OutputCapture _capture;
    ///
    ///     public MyTests(OutputCaptureFixture fixture)
    ///     {
    ///         _capture = fixture.Capture;
    ///     }
    ///
    ///     [Fact]
    ///     public void TestSomething()
    ///     {
    ///         var result = DoSomething();
    ///         _capture.Capture("test-id", result);
    ///     }
    /// }
    /// </code>
    /// </example>
    public class OutputCapture
    {
        private readonly string _outputDir;
        private readonly bool _updateMode;

        /// <summary>
        /// Initializes a new instance of the <see cref="OutputCapture"/> class.
        /// </summary>
        /// <param name="outputDir">Directory to store captured outputs.</param>
        /// <param name="updateMode">If true, update golden files. If false, validate against them.</param>
        public OutputCapture(string outputDir, bool updateMode = false)
        {
            _outputDir = outputDir ?? throw new ArgumentNullException(nameof(outputDir));
            _updateMode = updateMode;
            Directory.CreateDirectory(_outputDir);
        }

        /// <summary>
        /// Captures test output to a JSON file or validates against existing golden file.
        /// </summary>
        /// <param name="testId">Unique test identifier (must match [DocExample] TestId).</param>
        /// <param name="output">The output to capture (will be serialized to string).</param>
        /// <param name="metadata">Additional metadata to store with the output.</param>
        /// <param name="normalize">Whether to normalize whitespace for comparison.</param>
        /// <exception cref="Xunit.Sdk.XunitException">If not in update mode and output doesn't match golden file.</exception>
        public void Capture(
            string testId,
            object output,
            object? metadata = null,
            bool normalize = true)
        {
            if (testId == null)
                throw new ArgumentNullException(nameof(testId));
            if (output == null)
                throw new ArgumentNullException(nameof(output));

            var rawOutput = Serialize(output);
            var outputFile = Path.Combine(_outputDir, $"{testId}.json");

            if (_updateMode)
            {
                // Update mode: Write new golden file
                var result = new
                {
                    TestId = testId,
                    Timestamp = DateTime.UtcNow,
                    Output = new
                    {
                        Raw = rawOutput,
                        Normalized = normalize ? Normalize(rawOutput) : null,
                        Hash = Hash(rawOutput)
                    },
                    Metadata = metadata ?? new { }
                };

                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                };

                var json = JsonSerializer.Serialize(result, options);
                File.WriteAllText(outputFile, json, Encoding.UTF8);
                Console.WriteLine($"  ✓ Updated golden file: {testId}");
            }
            else
            {
                // Validation mode: Compare against golden file
                if (!File.Exists(outputFile))
                {
                    throw new Xunit.Sdk.XunitException(
                        $"\n\n❌ Golden file not found: {outputFile}\n" +
                        $"   Test ID: {testId}\n" +
                        $"   Set UPDATE_GOLDEN=1 to create it:\n" +
                        $"   UPDATE_GOLDEN=1 dotnet test --filter \"FullyQualifiedName~{testId}\"\n"
                    );
                }

                // Load golden file
                var goldenJson = File.ReadAllText(outputFile);
                var golden = JsonSerializer.Deserialize<JsonElement>(goldenJson);
                var goldenOutput = golden.GetProperty("output").GetProperty("raw").GetString() ?? "";
                var goldenHash = golden.GetProperty("output").GetProperty("hash").GetString() ?? "";

                // Compare using normalized hash
                var currentHash = Hash(rawOutput);

                if (currentHash != goldenHash)
                {
                    // Generate diff for error message
                    var diff = GenerateDiff(goldenOutput, rawOutput, testId);
                    throw new Xunit.Sdk.XunitException(
                        $"\n\n❌ Output mismatch for test: {testId}\n" +
                        $"   Golden file: {outputFile}\n" +
                        $"   Expected hash: {goldenHash}\n" +
                        $"   Actual hash:   {currentHash}\n\n" +
                        $"{diff}\n\n" +
                        $"   If this change is intentional, update the golden file:\n" +
                        $"   UPDATE_GOLDEN=1 dotnet test --filter \"FullyQualifiedName~{testId}\"\n"
                    );
                }
            }
        }

        /// <summary>
        /// Serializes a value to string.
        /// </summary>
        /// <param name="value">Value to serialize.</param>
        /// <returns>String representation of the value.</returns>
        private string Serialize(object value)
        {
            return value switch
            {
                string s => s,
                byte[] bytes => Encoding.UTF8.GetString(bytes),
                _ when IsJsonSerializable(value) => JsonSerializer.Serialize(value, new JsonSerializerOptions
                {
                    WriteIndented = true
                }),
                _ => value.ToString() ?? ""
            };
        }

        /// <summary>
        /// Normalizes whitespace for comparison.
        ///
        /// Removes extra whitespace and normalizes line endings to make
        /// cross-platform comparison more reliable.
        /// </summary>
        /// <param name="value">String to normalize.</param>
        /// <returns>Normalized string.</returns>
        private string Normalize(string value)
        {
            // Normalize line endings
            var s = value.Replace("\r\n", "\n").Replace("\r", "\n");

            // Remove extra whitespace
            s = Regex.Replace(s, @"[ \t]+", " ");

            // Remove blank lines
            s = Regex.Replace(s, @"\n\s*\n", "\n");

            // Trim
            return s.Trim();
        }

        /// <summary>
        /// Generates SHA-256 hash of normalized value.
        /// </summary>
        /// <param name="value">String to hash.</param>
        /// <returns>Hexadecimal hash string.</returns>
        private string Hash(string value)
        {
            var normalized = Normalize(value);
            using var sha256 = SHA256.Create();
            var bytes = Encoding.UTF8.GetBytes(normalized);
            var hash = sha256.ComputeHash(bytes);
            return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
        }

        /// <summary>
        /// Generates a unified diff between expected and actual output.
        /// </summary>
        /// <param name="expected">Expected output (from golden file).</param>
        /// <param name="actual">Actual output (from test).</param>
        /// <param name="testId">Test identifier for context.</param>
        /// <returns>Formatted diff string.</returns>
        private string GenerateDiff(string expected, string actual, string testId)
        {
            var expectedLines = expected.Split('\n');
            var actualLines = actual.Split('\n');

            var diff = new StringBuilder();
            diff.AppendLine("   Diff:");

            // Simple line-by-line comparison (not a true unified diff, but good enough)
            var maxLines = Math.Max(expectedLines.Length, actualLines.Length);
            var shownLines = 0;
            const int maxDisplayLines = 50;

            for (int i = 0; i < maxLines && shownLines < maxDisplayLines; i++)
            {
                var expectedLine = i < expectedLines.Length ? expectedLines[i] : null;
                var actualLine = i < actualLines.Length ? actualLines[i] : null;

                if (expectedLine != actualLine)
                {
                    if (expectedLine != null)
                        diff.AppendLine($"   - {expectedLine}");
                    if (actualLine != null)
                        diff.AppendLine($"   + {actualLine}");
                    shownLines++;
                }
            }

            if (maxLines > maxDisplayLines)
            {
                diff.AppendLine($"   ... (diff truncated, showing first {maxDisplayLines} differences)");
            }

            return diff.ToString();
        }

        /// <summary>
        /// Checks if a type can be JSON serialized.
        /// </summary>
        private bool IsJsonSerializable(object value)
        {
            var type = value.GetType();
            return !type.IsPrimitive && type != typeof(string);
        }
    }

    /// <summary>
    /// xUnit fixture for output capture.
    /// </summary>
    /// <example>
    /// <code>
    /// public class MyTests : IClassFixture&lt;OutputCaptureFixture&gt;
    /// {
    ///     private readonly OutputCapture _capture;
    ///
    ///     public MyTests(OutputCaptureFixture fixture)
    ///     {
    ///         _capture = fixture.Capture;
    ///     }
    /// }
    /// </code>
    /// </example>
    public class OutputCaptureFixture : IDisposable
    {
        /// <summary>
        /// Gets the output capture instance.
        /// </summary>
        public OutputCapture Capture { get; }

        /// <summary>
        /// Initializes a new instance of the <see cref="OutputCaptureFixture"/> class.
        /// </summary>
        public OutputCaptureFixture()
        {
            // Determine output directory relative to test assembly
            var baseDir = AppDomain.CurrentDomain.BaseDirectory;
            var repoRoot = FindRepositoryRoot(baseDir);
            // Use docs results directory for documentation examples
            var outputDir = Path.Combine(repoRoot, "test-data", "results", "docs");

            // Check if we're in update mode via environment variable
            var updateMode = Environment.GetEnvironmentVariable("UPDATE_GOLDEN") == "1";

            if (updateMode)
            {
                Console.WriteLine("\n🔄 Running in UPDATE mode - golden files will be updated");
            }

            Capture = new OutputCapture(outputDir, updateMode);
        }

        /// <summary>
        /// Finds the repository root by looking for .git directory.
        /// </summary>
        private string FindRepositoryRoot(string startPath)
        {
            var dir = new DirectoryInfo(startPath);
            while (dir != null)
            {
                if (Directory.Exists(Path.Combine(dir.FullName, ".git")) ||
                    File.Exists(Path.Combine(dir.FullName, "mkdocs.yml")))
                {
                    return dir.FullName;
                }
                dir = dir.Parent;
            }

            // Fallback to multiple levels up from base directory
            return Path.GetFullPath(Path.Combine(startPath, "..", "..", "..", "..", ".."));
        }

        /// <summary>
        /// Disposes resources.
        /// </summary>
        public void Dispose()
        {
            // Cleanup if needed
            GC.SuppressFinalize(this);
        }
    }
}
