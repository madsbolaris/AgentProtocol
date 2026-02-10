// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using Microsoft.Agents;
using Microsoft.Agents.Evaluators;
using Microsoft.Agents.Evaluators.Tests.Mocks;

namespace Microsoft.Agents.Evaluators.Tests.Helpers;

/// <summary>
/// Test helper utilities for loading test data and golden files.
/// Based on Python's test_helpers.py implementation.
/// </summary>
public static class TestHelpers
{
    /// <summary>
    /// Gets the test mode from environment (generate or test).
    /// </summary>
    public static string GetTestMode()
    {
        var mode = Environment.GetEnvironmentVariable("TEST_MODE") ?? "test";
        mode = mode.ToLowerInvariant();

        if (mode != "generate" && mode != "test")
        {
            throw new InvalidOperationException(
                $"Invalid TEST_MODE: {mode}. Must be 'generate' or 'test'.");
        }

        return mode;
    }

    /// <summary>
    /// Gets the test-data directory path.
    /// </summary>
    public static string GetTestDataDir()
    {
        // Walk up from current directory to find test-data
        var current = Directory.GetCurrentDirectory();
        while (current != null)
        {
            var testDataPath = Path.Combine(current, "test-data");
            if (Directory.Exists(testDataPath))
            {
                return testDataPath;
            }
            current = Directory.GetParent(current)?.FullName;
        }

        throw new DirectoryNotFoundException(
            "Could not find test-data directory. " +
            "Please ensure test-data exists at repository root.");
    }

    /// <summary>
    /// Loads an input XML file for evaluation.
    /// Searches recursively in the evals directory to support hierarchical structure.
    /// </summary>
    public static string LoadInputFile(string testName)
    {
        var testDataDir = GetTestDataDir();
        var evalsDir = Path.Combine(testDataDir, "input", "evals");
        var filename = $"{testName}.xml";

        // First try direct path (for backwards compatibility)
        var directPath = Path.Combine(evalsDir, filename);
        if (File.Exists(directPath))
        {
            return File.ReadAllText(directPath);
        }

        // Search recursively
        var files = Directory.GetFiles(evalsDir, filename, SearchOption.AllDirectories);
        if (files.Length == 0)
        {
            throw new FileNotFoundException(
                $"Input file not found: {testName}.xml\n" +
                $"Searched in: {evalsDir}");
        }

        if (files.Length > 1)
        {
            throw new InvalidOperationException(
                $"Multiple files found with name {filename}:\n" +
                string.Join("\n", files));
        }

        return File.ReadAllText(files[0]);
    }

    /// <summary>
    /// Loads a golden file for comparison.
    /// Searches recursively in the results directory to support hierarchical structure.
    /// </summary>
    public static T LoadGoldenFile<T>(string testName, string pattern = "json", string category = "evals")
    {
        var testDataDir = GetTestDataDir();
        string searchDir;
        string filename;

        if (pattern == "json")
        {
            searchDir = Path.Combine(testDataDir, "results", category);
            filename = $"{testName}-result.json";
        }
        else if (pattern == "xml")
        {
            searchDir = Path.Combine(testDataDir, "results", category);
            filename = $"{testName}-result.xml";
        }
        else
        {
            throw new ArgumentException($"Unknown pattern: {pattern}");
        }

        // Search recursively for the golden file
        if (!Directory.Exists(searchDir))
        {
            throw new DirectoryNotFoundException(
                $"Results directory not found: {searchDir}\n" +
                $"Run tests with TEST_MODE=generate to create golden files.");
        }

        var files = Directory.GetFiles(searchDir, filename, SearchOption.AllDirectories);
        if (files.Length == 0)
        {
            throw new FileNotFoundException(
                $"Golden file not found: {filename}\n" +
                $"Searched in: {searchDir}\n" +
                $"Run tests with TEST_MODE=generate to create golden files.");
        }

        if (files.Length > 1)
        {
            throw new InvalidOperationException(
                $"Multiple golden files found with name {filename}:\n" +
                string.Join("\n", files));
        }

        var goldenPath = files[0];
        var content = File.ReadAllText(goldenPath);

        if (typeof(T) == typeof(string))
        {
            return (T)(object)content;
        }

        return JsonSerializer.Deserialize<T>(content,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
            ?? throw new InvalidOperationException($"Failed to deserialize golden file: {goldenPath}");
    }

    /// <summary>
    /// Saves a golden file, preserving the input directory structure.
    /// </summary>
    public static void SaveGoldenFile<T>(T content, string testName, string pattern = "json", string category = "evals")
    {
        var testDataDir = GetTestDataDir();
        string goldenPath;

        // Find the input file to determine the subdirectory structure
        var inputDir = Path.Combine(testDataDir, "input", category);
        var inputFilename = $"{testName}.xml";
        var inputFiles = Directory.GetFiles(inputDir, inputFilename, SearchOption.AllDirectories);

        string? relativeDir = null;
        if (inputFiles.Length > 0)
        {
            // Get relative path from input category directory
            var inputFile = inputFiles[0];
            var inputFileDir = Path.GetDirectoryName(inputFile);
            if (inputFileDir != null && inputFileDir.StartsWith(inputDir))
            {
                relativeDir = inputFileDir.Substring(inputDir.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            }
        }

        if (pattern == "json")
        {
            var resultsDir = Path.Combine(testDataDir, "results", category);
            if (!string.IsNullOrEmpty(relativeDir))
            {
                resultsDir = Path.Combine(resultsDir, relativeDir);
            }
            goldenPath = Path.Combine(resultsDir, $"{testName}-result.json");
            Directory.CreateDirectory(Path.GetDirectoryName(goldenPath)!);

            var json = content is string str
                ? str
                : JsonSerializer.Serialize(content, new JsonSerializerOptions { WriteIndented = true });

            File.WriteAllText(goldenPath, json);
        }
        else if (pattern == "xml")
        {
            var resultsDir = Path.Combine(testDataDir, "results", category);
            if (!string.IsNullOrEmpty(relativeDir))
            {
                resultsDir = Path.Combine(resultsDir, relativeDir);
            }
            goldenPath = Path.Combine(resultsDir, $"{testName}-result.xml");
            Directory.CreateDirectory(Path.GetDirectoryName(goldenPath)!);

            var xml = content as string ?? content?.ToString() ?? "";
            File.WriteAllText(goldenPath, xml);
        }
        else
        {
            throw new ArgumentException($"Unknown pattern: {pattern}");
        }

        Console.WriteLine($"  ✅ Generated golden file: {goldenPath}");
    }

    /// <summary>
    /// Creates a MockLLMClient for evaluation testing.
    /// </summary>
    public static MockLLMClient CreateMockLLMClient(string? recordingsDir = null)
    {
        var testMode = GetTestMode();

        if (testMode == "generate")
        {
            throw new InvalidOperationException(
                "LLM recording (generation mode) should be done by the agent itself.\n" +
                "Use TEST_MODE=test to run validation tests.");
        }

        recordingsDir ??= Path.Combine(GetTestDataDir(), "llm-recordings", "evals");
        return new MockLLMClient(recordingsDir);
    }

    /// <summary>
    /// Asserts that eval result structure is valid.
    /// </summary>
    public static void AssertEvalResultStructure(EvalResult result, string? expectedThreadId = null)
    {
        if (result == null)
        {
            throw new ArgumentNullException(nameof(result), "EvalResult is null");
        }

        if (expectedThreadId != null && result.ThreadId != expectedThreadId)
        {
            throw new InvalidOperationException(
                $"ThreadId mismatch: expected '{expectedThreadId}', got '{result.ThreadId}'");
        }

        if (result.Runs == null || result.Runs.Count == 0)
        {
            throw new InvalidOperationException("EvalResult has no runs");
        }

        if (result.TotalRuns != result.Runs.Count)
        {
            throw new InvalidOperationException(
                $"TotalRuns mismatch: expected {result.Runs.Count}, got {result.TotalRuns}");
        }

        var passedRuns = result.Runs.Count(r => r.Passed);
        if (result.PassedRuns != passedRuns)
        {
            throw new InvalidOperationException(
                $"PassedRuns mismatch: expected {passedRuns}, got {result.PassedRuns}");
        }
    }

    /// <summary>
    /// Asserts that expect result passed.
    /// </summary>
    public static void AssertExpectPassed(ExpectResult expectResult, string expectName)
    {
        if (expectResult == null)
        {
            throw new ArgumentNullException(nameof(expectResult), $"ExpectResult for '{expectName}' is null");
        }

        if (!expectResult.Passed)
        {
            var errorMsg = $"Expect '{expectName}' failed";

            if (expectResult.Judges != null)
            {
                foreach (var judge in expectResult.Judges)
                {
                    if (!string.IsNullOrEmpty(judge.Error))
                    {
                        errorMsg += $"\n  Judge '{judge.Agent}': {judge.Error}";
                    }
                    else if (!judge.Passed)
                    {
                        errorMsg += $"\n  Judge '{judge.Agent}': failed (score: {judge.Score})";
                    }
                }
            }

            if (expectResult.Asserts != null)
            {
                foreach (var assert in expectResult.Asserts)
                {
                    if (!assert.Passed)
                    {
                        errorMsg += $"\n  Assert '{assert.Expression}': {(string.IsNullOrEmpty(assert.Error) ? "failed" : assert.Error)}";
                    }
                }
            }

            throw new InvalidOperationException(errorMsg);
        }
    }

    /// <summary>
    /// Compares two eval results for similarity (allowing some flexibility).
    /// </summary>
    public static void AssertEvalResultsSimilar(EvalResult actual, EvalResult expected)
    {
        if (actual == null) throw new ArgumentNullException(nameof(actual));
        if (expected == null) throw new ArgumentNullException(nameof(expected));

        // In test mode with mocked LLM, results should be deterministic
        var testMode = GetTestMode();
        if (testMode == "test")
        {
            // Structure checks
            if (actual.ThreadId != expected.ThreadId)
            {
                throw new InvalidOperationException(
                    $"ThreadId mismatch: expected '{expected.ThreadId}', got '{actual.ThreadId}'");
            }

            if (actual.TotalRuns != expected.TotalRuns)
            {
                throw new InvalidOperationException(
                    $"TotalRuns mismatch: expected {expected.TotalRuns}, got {actual.TotalRuns}");
            }

            if (actual.Passed != expected.Passed)
            {
                throw new InvalidOperationException(
                    $"Passed status mismatch: expected {expected.Passed}, got {actual.Passed}");
            }

            // Run count should match
            if (actual.Runs.Count != expected.Runs.Count)
            {
                throw new InvalidOperationException(
                    $"Run count mismatch: expected {expected.Runs.Count}, got {actual.Runs.Count}");
            }

            // Each run should have matching pass status
            for (int i = 0; i < actual.Runs.Count; i++)
            {
                var actualRun = actual.Runs[i];
                var expectedRun = expected.Runs[i];

                if (actualRun.Passed != expectedRun.Passed)
                {
                    throw new InvalidOperationException(
                        $"Run {i + 1} passed status mismatch: expected {expectedRun.Passed}, got {actualRun.Passed}");
                }
            }
        }
    }
}
