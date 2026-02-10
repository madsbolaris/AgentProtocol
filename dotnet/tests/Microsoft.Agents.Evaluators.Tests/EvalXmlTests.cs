using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Agents.Evaluators;
using Microsoft.Agents.Protocol.Xml;
using Xunit;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Evaluators.Tests;

/// <summary>
/// Tests that run actual eval XML files through the evaluator.
/// </summary>
public class EvalXmlTests
{
    private readonly EvalXmlSerializer _serializer;
    private readonly EvalRunner _runner;
    private readonly string _evalFilesPath;

    public EvalXmlTests()
    {
        _serializer = new EvalXmlSerializer();
        _runner = new EvalRunner();

        // Find test-data/input/evals directory relative to the test assembly
        var baseDir = Directory.GetCurrentDirectory();
        while (baseDir != null && !Directory.Exists(Path.Combine(baseDir, "test-data")))
        {
            baseDir = Directory.GetParent(baseDir)?.FullName;
        }

        if (baseDir == null)
        {
            throw new DirectoryNotFoundException("Could not find test-data directory");
        }

        _evalFilesPath = Path.Combine(baseDir, "test-data", "input", "evals");
    }

    [Fact]
    public void TestDataEvalsFolderExists()
    {
        XunitAssert.True(Directory.Exists(_evalFilesPath), $"Evals folder should exist at: {_evalFilesPath}");

        var evalFiles = Directory.GetFiles(_evalFilesPath, "*.xml", SearchOption.AllDirectories);
        XunitAssert.True(evalFiles.Length > 0, "Should have at least one eval XML file");
    }

    [Theory]
    [InlineData("01-simple-text-expect.xml")]
    [InlineData("02-multiple-expects.xml")]
    [InlineData("03-with-run-config.xml")]
    public async Task CanDeserializeEvalXmlFile(string fileName)
    {
        // Arrange - search recursively for the file
        var testName = Path.GetFileNameWithoutExtension(fileName);
        var files = Directory.GetFiles(_evalFilesPath, fileName, SearchOption.AllDirectories);
        XunitAssert.True(files.Length > 0, $"File {fileName} not found in {_evalFilesPath}");
        var filePath = files[0];

        // Act
        var evalThread = _serializer.DeserializeFromFile(filePath);

        // Assert
        XunitAssert.NotNull(evalThread);
        XunitAssert.NotNull(evalThread.ThreadId);
        XunitAssert.NotNull(evalThread.Elements);
        XunitAssert.True(evalThread.Elements.Count > 0, "Should have at least one element");
    }

    [Fact]
    public async Task SimpleTextExpect_ContainsCorrectStructure()
    {
        // Arrange - search recursively for the file
        var files = Directory.GetFiles(_evalFilesPath, "01-simple-text-expect.xml", SearchOption.AllDirectories);
        XunitAssert.True(files.Length > 0, "File 01-simple-text-expect.xml not found");
        var filePath = files[0];
        var evalThread = _serializer.DeserializeFromFile(filePath);

        // Assert structure
        XunitAssert.NotNull(evalThread);
        XunitAssert.Equal("eval-001", evalThread.ThreadId);
        XunitAssert.Contains("Simple text expectation", evalThread.Description ?? "");

        // Check elements
        var userMessage = evalThread.Elements.OfType<UserMessage>().FirstOrDefault();
        XunitAssert.NotNull(userMessage);

        var expect = evalThread.Elements.OfType<Expect>().FirstOrDefault();
        XunitAssert.NotNull(expect);
        XunitAssert.Equal("correct-answer", expect.Name);
        XunitAssert.NotNull(expect.ReferenceOutput);
    }

    [Fact]
    public async Task MultipleExpects_ContainsMultipleExpectations()
    {
        // Arrange - search recursively for the file
        var files = Directory.GetFiles(_evalFilesPath, "02-multiple-expects.xml", SearchOption.AllDirectories);
        XunitAssert.True(files.Length > 0, "File 02-multiple-expects.xml not found");
        var filePath = files[0];
        var evalThread = _serializer.DeserializeFromFile(filePath);

        // Assert
        var expects = evalThread.Elements.OfType<Expect>().ToList();
        XunitAssert.True(expects.Count >= 2, "Should have at least 2 expectations");

        foreach (var expect in expects)
        {
            XunitAssert.NotNull(expect.Name);
            XunitAssert.NotNull(expect.ReferenceOutput);
        }
    }

    [Fact]
    public async Task WithRunConfig_ContainsEvalRunElement()
    {
        // Arrange - search recursively for the file
        var files = Directory.GetFiles(_evalFilesPath, "03-with-run-config.xml", SearchOption.AllDirectories);
        XunitAssert.True(files.Length > 0, "File 03-with-run-config.xml not found");
        var filePath = files[0];
        var evalThread = _serializer.DeserializeFromFile(filePath);

        // Assert
        var evalRun = evalThread.Elements.OfType<EvalRun>().FirstOrDefault();
        XunitAssert.NotNull(evalRun);
        XunitAssert.True(evalRun.MaxSteps > 0 || evalRun.TimeoutMs > 0, "Should have max steps or timeout configured");
    }

    [Fact]
    public void AllEvalXmlFilesCanBeDeserialized()
    {
        // Arrange - search recursively for all XML files
        var evalFiles = Directory.GetFiles(_evalFilesPath, "*.xml", SearchOption.AllDirectories);

        // Act & Assert
        foreach (var filePath in evalFiles)
        {
            var fileName = Path.GetFileName(filePath);
            try
            {
                var evalThread = _serializer.DeserializeFromFile(filePath);
                XunitAssert.NotNull(evalThread);
                XunitAssert.NotNull(evalThread.ThreadId);
            }
            catch (Exception ex)
            {
                XunitAssert.Fail($"Failed to deserialize {fileName}: {ex.Message}");
            }
        }
    }

    [Fact]
    public void AllEvalXmlFiles_HaveValidStructure()
    {
        // Arrange - search recursively for all XML files
        var evalFiles = Directory.GetFiles(_evalFilesPath, "*.xml", SearchOption.AllDirectories);

        // Act & Assert
        foreach (var filePath in evalFiles)
        {
            var fileName = Path.GetFileName(filePath);
            var evalThread = _serializer.DeserializeFromFile(filePath);

            // Basic structure validation
            XunitAssert.NotNull(evalThread.ThreadId);
            XunitAssert.NotNull(evalThread.Elements);
            XunitAssert.True(evalThread.Elements.Count > 0, $"{fileName}: Should have elements");

            // Should have at least one Expect
            var hasExpect = evalThread.Elements.Any(e => e is Expect);
            XunitAssert.True(hasExpect, $"{fileName}: Should have at least one Expect element");

            // All Expects should have reference output
            foreach (var expect in evalThread.Elements.OfType<Expect>())
            {
                XunitAssert.NotNull(expect.ReferenceOutput);
                XunitAssert.NotNull(expect.Name);
            }
        }
    }

    [Fact]
    public void EvalXmlFiles_CoverVariousScenarios()
    {
        // Arrange - search recursively for all XML files
        var evalFiles = Directory.GetFiles(_evalFilesPath, "*.xml", SearchOption.AllDirectories);

        // Track coverage of different features
        var hasMultipleExpects = false;
        var hasRunConfig = false;
        var hasToolCall = false;
        var hasRepeat = false;
        var hasSystemMessage = false;
        var hasMultimodal = false;

        // Act
        foreach (var filePath in evalFiles)
        {
            var evalThread = _serializer.DeserializeFromFile(filePath);

            var expectCount = evalThread.Elements.OfType<Expect>().Count();
            if (expectCount > 1) hasMultipleExpects = true;

            if (evalThread.Elements.Any(e => e is EvalRun)) hasRunConfig = true;

            if (evalThread.Repeat > 1) hasRepeat = true;

            if (evalThread.Elements.Any(e => e is SystemMessage)) hasSystemMessage = true;

            // Check for tool calls in messages (both direct elements and within Expect.ReferenceOutput)
            var allMessages = evalThread.Elements.OfType<ChatMessage>().ToList();

            // Also check messages in Expect.ReferenceOutput
            foreach (var expect in evalThread.Elements.OfType<Expect>())
            {
                if (expect.ReferenceOutput is ChatMessage refMessage)
                {
                    allMessages.Add(refMessage);
                }
            }

            foreach (var message in allMessages)
            {
                if (message.Contents?.Any(c => c is FunctionCallContent) == true)
                {
                    hasToolCall = true;
                }
                if (message.Contents?.Any(c => c is ImageContent || c is AudioContent || c is VideoContent) == true)
                {
                    hasMultimodal = true;
                }
            }
        }

        // Assert - we should have coverage of various scenarios
        XunitAssert.True(hasMultipleExpects, "Should have tests with multiple expectations");
        XunitAssert.True(hasRunConfig, "Should have tests with run configuration");
        XunitAssert.True(hasToolCall, "Should have tests with tool calls");
        XunitAssert.True(hasRepeat, "Should have tests with repeat");
        XunitAssert.True(hasSystemMessage, "Should have tests with system messages");
        XunitAssert.True(hasMultimodal, "Should have tests with multimodal content");
    }
}
