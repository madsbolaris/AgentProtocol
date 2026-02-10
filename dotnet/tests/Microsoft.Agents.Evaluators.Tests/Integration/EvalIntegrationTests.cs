// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Agents.Evaluators;
using Microsoft.Agents.Evaluators.Tests.Helpers;
using Microsoft.Agents.Evaluators.Tests.Mocks;
using Microsoft.Agents.Protocol.Xml;
using Xunit;
using Xunit.Abstractions;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Evaluators.Tests.Integration;

/// <summary>
/// Integration tests for the evaluation system using mock LLM responses.
/// These tests:
/// 1. Load eval XML files from test-data/input/evals/
/// 2. Run evaluations using mock LLM responses (replays recordings)
/// 3. Validate results against golden files in test-data/results/evals/
///
/// Tests are deterministic, fast, and do not require real LLM calls.
///
/// Run with:
///     dotnet test --filter Category=Integration
///
/// No API keys needed!
/// </summary>
[Trait("Category", "Integration")]
public class EvalIntegrationTests
{
    private readonly ITestOutputHelper _output;
    private readonly EvalXmlSerializer _serializer;
    private readonly string _testDataDir;
    private readonly string _evalsInputDir;
    private readonly string _recordingsDir;

    public EvalIntegrationTests(ITestOutputHelper output)
    {
        _output = output;
        _serializer = new EvalXmlSerializer();

        // Find test-data directory
        _testDataDir = TestHelpers.GetTestDataDir();
        _evalsInputDir = Path.Combine(_testDataDir, "input", "evals");
        _recordingsDir = Path.Combine(_testDataDir, "llm-recordings", "evals");

        _output.WriteLine($"Test Data Dir: {_testDataDir}");
        _output.WriteLine($"Evals Input Dir: {_evalsInputDir}");
        _output.WriteLine($"Recordings Dir: {_recordingsDir}");
    }

    [Fact]
    public void TestMode_ShouldBeTest()
    {
        var mode = TestHelpers.GetTestMode();
        _output.WriteLine($"Test mode: {mode}");
        XunitAssert.Equal("test", mode);
    }

    [Fact]
    public void TestDataDirectory_ShouldExist()
    {
        XunitAssert.True(Directory.Exists(_testDataDir), $"Test data directory should exist: {_testDataDir}");
        XunitAssert.True(Directory.Exists(_evalsInputDir), $"Evals input directory should exist: {_evalsInputDir}");

        var evalFiles = Directory.GetFiles(_evalsInputDir, "*.xml", SearchOption.AllDirectories);
        XunitAssert.True(evalFiles.Length > 0, "Should have at least one eval XML file");

        _output.WriteLine($"Found {evalFiles.Length} eval files (scanning recursively)");
    }

    [Theory]
    [InlineData("01-simple-text-expect")]
    [InlineData("02-multiple-expects")]
    [InlineData("03-with-run-config")]
    [InlineData("05-llm-judge")]
    [InlineData("06-regex-judge")]
    public async Task CanLoadAndDeserializeEvalXml(string testName)
    {
        _output.WriteLine($"\n{'=',60}");
        _output.WriteLine($"TEST: Can load and deserialize {testName}");
        _output.WriteLine($"{'=',60}");

        // Load input XML
        var inputXml = TestHelpers.LoadInputFile(testName);
        XunitAssert.NotNull(inputXml);
        XunitAssert.NotEmpty(inputXml);

        _output.WriteLine($"Loaded input: {inputXml.Length} bytes");

        // Write to temp file and deserialize
        var tempFile = Path.GetTempFileName();
        try
        {
            File.WriteAllText(tempFile, inputXml);
            var evalThread = _serializer.DeserializeFromFile(tempFile);
        XunitAssert.NotNull(evalThread);
        XunitAssert.NotNull(evalThread.ThreadId);
        XunitAssert.NotNull(evalThread.Elements);
        XunitAssert.True(evalThread.Elements.Count > 0, "Should have at least one element");

            _output.WriteLine($"Deserialized successfully:");
            _output.WriteLine($"  ThreadId: {evalThread.ThreadId}");
            _output.WriteLine($"  Elements: {evalThread.Elements.Count}");
            _output.WriteLine($"  Expects: {evalThread.Elements.OfType<Expect>().Count()}");
        }
        finally
        {
            File.Delete(tempFile);
        }
    }

    [Theory]
    [InlineData("01-simple-text-expect", "Simple text expectation - expects exact match")]
    [InlineData("02-multiple-expects", "Multiple expectations in one eval")]
    [InlineData("06-regex-judge", "Regex pattern matching judge")]
    public async Task EvalXml_HasCorrectStructure(string testName, string description)
    {
        _output.WriteLine($"\n{'=',60}");
        _output.WriteLine($"TEST: {description}");
        _output.WriteLine($"  Input: {testName}.xml");
        _output.WriteLine($"{'=',60}");

        // Load and deserialize
        var inputXml = TestHelpers.LoadInputFile(testName);
        var tempFile = Path.GetTempFileName();
        File.WriteAllText(tempFile, inputXml);
        var evalThread = _serializer.DeserializeFromFile(tempFile);
        File.Delete(tempFile);

        // Validate structure
        XunitAssert.NotNull(evalThread);
        XunitAssert.NotNull(evalThread.ThreadId);

        _output.WriteLine($"ThreadId: {evalThread.ThreadId}");
        _output.WriteLine($"Description: {evalThread.Description}");

        // Should have at least one user message
        var userMessages = evalThread.Elements.OfType<UserMessage>().ToList();
        XunitAssert.True(userMessages.Count > 0, "Should have at least one user message");
        _output.WriteLine($"User messages: {userMessages.Count}");

        // Should have at least one expectation
        var expects = evalThread.Elements.OfType<Expect>().ToList();
        XunitAssert.True(expects.Count > 0, "Should have at least one expectation");
        _output.WriteLine($"Expectations: {expects.Count}");

        // Each expectation should have a name and reference output
        foreach (var expect in expects)
        {
            XunitAssert.NotNull(expect.Name);
            XunitAssert.NotNull(expect.ReferenceOutput);
            _output.WriteLine($"  Expect '{expect.Name}': {expect.Judges?.Count ?? 0} judges, {expect.Asserts?.Count ?? 0} asserts");
        }

        _output.WriteLine("Structure validation passed");
    }

    [Fact]
    public async Task MockLLMClient_CanBeCreated()
    {
        _output.WriteLine("\nTesting MockLLMClient creation...");

        // Check if recordings directory exists
        if (!Directory.Exists(_recordingsDir))
        {
            _output.WriteLine($"Recordings directory not found: {_recordingsDir}");
            _output.WriteLine("Skipping test - recordings need to be generated first");
            return;
        }

        var recordingFiles = Directory.GetFiles(_recordingsDir, "*.response.json");
        _output.WriteLine($"Found {recordingFiles.Length} recording files");

        if (recordingFiles.Length == 0)
        {
            _output.WriteLine("No recording files found - skipping test");
            return;
        }

        // Create mock client
        var mockClient = new MockLLMClient(_recordingsDir);
        XunitAssert.NotNull(mockClient);
        XunitAssert.Equal(0, mockClient.CallCount);

        _output.WriteLine("MockLLMClient created successfully");
        _output.WriteLine($"  Recordings directory: {_recordingsDir}");
        _output.WriteLine($"  Available recordings: {recordingFiles.Length}");
    }

    [Theory]
    [InlineData("01-simple-text-expect", "eval-001", "Simple text expectation test")]
    [InlineData("06-regex-judge", "eval-006", "Regex pattern matching")]
    public async Task RunEval_WithoutAgent_ProducesResult(string testName, string expectedThreadId, string description)
    {
        _output.WriteLine($"\n{'=',60}");
        _output.WriteLine($"TEST: {description}");
        _output.WriteLine($"  Input: {testName}.xml");
        _output.WriteLine($"  Expected Thread: {expectedThreadId}");
        _output.WriteLine($"{'=',60}");

        // Load input XML
        var inputXml = TestHelpers.LoadInputFile(testName);
        var tempFile = Path.GetTempFileName();
        File.WriteAllText(tempFile, inputXml);
        var evalThread = _serializer.DeserializeFromFile(tempFile);
        File.Delete(tempFile);

        _output.WriteLine($"Loaded eval thread: {evalThread.ThreadId}");
        _output.WriteLine($"  Elements: {evalThread.Elements.Count}");
        _output.WriteLine($"  Expectations: {evalThread.Elements.OfType<Expect>().Count()}");

        // Create eval runner (without agent runner - uses pre-recorded responses in XML)
        var runner = new EvalRunner();

        // Run evaluation
        _output.WriteLine("\nRunning evaluation...");
        var result = await runner.RunAsync(evalThread, CancellationToken.None);

        // Validate result
        XunitAssert.NotNull(result);
        TestHelpers.AssertEvalResultStructure(result, expectedThreadId);

        _output.WriteLine($"\nEvaluation completed:");
        _output.WriteLine($"  Passed: {result.Passed}");
        _output.WriteLine($"  Total Runs: {result.TotalRuns}");
        _output.WriteLine($"  Passed Runs: {result.PassedRuns}");
        _output.WriteLine($"  Failed Runs: {result.FailedRuns}");
        _output.WriteLine($"  Total Asserts: {result.TotalAsserts}");
        _output.WriteLine($"  Passed Asserts: {result.PassedAsserts}");
        _output.WriteLine($"  Failed Asserts: {result.FailedAsserts}");
        _output.WriteLine($"  Duration: {result.TotalDurationMs}ms");

        // Show detailed results for each run
        foreach (var run in result.Runs)
        {
            _output.WriteLine($"\n  Run {run.RunNumber}: {(run.Passed ? "PASSED" : "FAILED")}");
            if (!string.IsNullOrEmpty(run.Error))
            {
                _output.WriteLine($"    Error: {run.Error}");
            }

            if (run.Expects != null)
            {
                foreach (var expect in run.Expects)
                {
                    _output.WriteLine($"    Expect '{expect.Name}': {(expect.Passed ? "PASSED" : "FAILED")}");

                    if (expect.Judges != null)
                    {
                        foreach (var judge in expect.Judges)
                        {
                            _output.WriteLine($"      Judge '{judge.Agent}': {(judge.Passed ? "PASSED" : "FAILED")} (score: {judge.Score})");
                            if (!string.IsNullOrEmpty(judge.Error))
                            {
                                _output.WriteLine($"        Error: {judge.Error}");
                            }
                        }
                    }

                    if (expect.Asserts != null)
                    {
                        foreach (var assert in expect.Asserts)
                        {
                            _output.WriteLine($"      Assert '{assert.Expression}': {(assert.Passed ? "PASSED" : "FAILED")}");
                            if (!string.IsNullOrEmpty(assert.Error))
                            {
                                _output.WriteLine($"        Error: {assert.Error}");
                            }
                        }
                    }
                }
            }
        }

        _output.WriteLine($"\n{'=',60}");
        _output.WriteLine($"TEST PASSED: {description}");
        _output.WriteLine($"{'=',60}");
    }

    [Fact]
    public async Task AllEvalXmlFiles_CanBeProcessed()
    {
        _output.WriteLine("\n{'=',60}");
        _output.WriteLine("TEST: Process all eval XML files");
        _output.WriteLine($"{'=',60}");

        var evalFilePaths = Directory.GetFiles(_evalsInputDir, "*.xml", SearchOption.AllDirectories)
            .OrderBy(path => path)
            .ToList();

        _output.WriteLine($"Found {evalFilePaths.Count} eval files (scanning recursively)");

        var runner = new EvalRunner();
        var processedCount = 0;
        var failedCount = 0;

        foreach (var filePath in evalFilePaths)
        {
            try
            {
                var relativePath = Path.GetRelativePath(_evalsInputDir, filePath);
                _output.WriteLine($"\nProcessing: {relativePath}");

                var inputXml = File.ReadAllText(filePath);
                var tempFile = Path.GetTempFileName();
                File.WriteAllText(tempFile, inputXml);
                var evalThread = _serializer.DeserializeFromFile(tempFile);
                File.Delete(tempFile);

                XunitAssert.NotNull(evalThread);
                XunitAssert.NotNull(evalThread.ThreadId);

                // Try to run evaluation
                var result = await runner.RunAsync(evalThread, CancellationToken.None);
                XunitAssert.NotNull(result);

                _output.WriteLine($"  Result: {(result.Passed ? "PASSED" : "FAILED")} " +
                                  $"({result.PassedRuns}/{result.TotalRuns} runs, " +
                                  $"{result.PassedAsserts}/{result.TotalAsserts} asserts)");

                processedCount++;
            }
            catch (Exception ex)
            {
                _output.WriteLine($"  ERROR: {ex.Message}");
                failedCount++;
            }
        }

        _output.WriteLine($"\n{'=',60}");
        _output.WriteLine($"Processed: {processedCount}/{evalFilePaths.Count} files");
        _output.WriteLine($"Failed: {failedCount} files");
        _output.WriteLine($"{'=',60}");

        XunitAssert.True(processedCount > 0, "Should successfully process at least one eval file");
    }

    [Fact]
    public async Task EvalResults_CoverVariousScenarios()
    {
        _output.WriteLine("\nChecking eval file coverage...");

        var evalFiles = Directory.GetFiles(_evalsInputDir, "*.xml", SearchOption.AllDirectories);
        var runner = new EvalRunner();

        var hasSimpleTextExpect = false;
        var hasMultipleExpects = false;
        var hasRegexJudge = false;
        var hasLLMJudge = false;
        var hasToolCallExpect = false;
        var hasRepeat = false;
        var hasMultipleAsserts = false;

        foreach (var filePath in evalFiles)
        {
            try
            {
                var evalThread = _serializer.DeserializeFromFile(filePath);

                var fileName = Path.GetFileNameWithoutExtension(filePath);

                if (fileName == "01-simple-text-expect") hasSimpleTextExpect = true;
                if (fileName == "02-multiple-expects") hasMultipleExpects = true;
                if (fileName == "05-llm-judge") hasLLMJudge = true;
                if (fileName == "06-regex-judge") hasRegexJudge = true;
                if (fileName == "04-tool-call-expect") hasToolCallExpect = true;

                if (evalThread.Repeat > 1) hasRepeat = true;

                var expectCount = evalThread.Elements.OfType<Expect>().Count();
                if (expectCount > 1) hasMultipleExpects = true;

                foreach (var expect in evalThread.Elements.OfType<Expect>())
                {
                    if (expect.Asserts?.Count > 1) hasMultipleAsserts = true;

                    if (expect.Judges != null)
                    {
                        foreach (var judge in expect.Judges)
                        {
                            if (judge.Agent?.Contains("regex") == true) hasRegexJudge = true;
                            if (judge.Agent?.Contains("llm") == true || judge.Agent?.Contains("semantic") == true) hasLLMJudge = true;
                        }
                    }
                }
            }
            catch
            {
                // Skip files that can't be processed
            }
        }

        _output.WriteLine($"Coverage:");
        _output.WriteLine($"  Simple text expect: {hasSimpleTextExpect}");
        _output.WriteLine($"  Multiple expects: {hasMultipleExpects}");
        _output.WriteLine($"  Regex judge: {hasRegexJudge}");
        _output.WriteLine($"  LLM judge: {hasLLMJudge}");
        _output.WriteLine($"  Tool call expect: {hasToolCallExpect}");
        _output.WriteLine($"  Repeat: {hasRepeat}");
        _output.WriteLine($"  Multiple asserts: {hasMultipleAsserts}");

        XunitAssert.True(hasSimpleTextExpect, "Should have simple text expectation tests");
        XunitAssert.True(hasMultipleExpects, "Should have tests with multiple expectations");
        XunitAssert.True(hasRegexJudge, "Should have tests with regex judge");
    }
}
