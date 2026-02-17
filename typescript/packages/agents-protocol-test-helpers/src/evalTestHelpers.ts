/**
 * Test helper utilities for loading test data and golden files.
 * Based on .NET's TestHelpers.cs and Python's test_helpers.py implementations.
 */

import * as fs from 'fs';
import * as path from 'path';
import { MockLLMClient } from './mockLLMClient.js';

/**
 * Eval result structure for validation
 */
export interface EvalResult {
  threadId: string;
  passed: boolean;
  totalRuns: number;
  passedRuns: number;
  failedRuns: number;
  totalAsserts: number;
  passedAsserts: number;
  failedAsserts: number;
  totalDurationMs: number;
  runs: EvalRun[];
}

/**
 * Individual eval run result
 */
export interface EvalRun {
  runNumber: number;
  passed: boolean;
  error?: string;
  expects?: ExpectResult[];
}

/**
 * Expectation result
 */
export interface ExpectResult {
  name: string;
  passed: boolean;
  judges?: JudgeResult[];
  asserts?: AssertResult[];
}

/**
 * Judge result
 */
export interface JudgeResult {
  agent: string;
  passed: boolean;
  score: number;
  error?: string;
}

/**
 * Assert result
 */
export interface AssertResult {
  expression: string;
  passed: boolean;
  error?: string;
}

/**
 * Gets the test mode from environment (generate or test).
 *
 * @returns Test mode ('generate' or 'test')
 */
export function getTestMode(): 'generate' | 'test' {
  const mode = (process.env.TEST_MODE || 'test').toLowerCase();

  if (mode !== 'generate' && mode !== 'test') {
    throw new Error(
      `Invalid TEST_MODE: ${mode}. Must be 'generate' or 'test'.`
    );
  }

  return mode as 'generate' | 'test';
}

/**
 * Gets the test-data directory path.
 *
 * @returns Absolute path to test-data directory
 */
export function getTestDataDir(): string {
  // Walk up from current directory to find test-data
  let current = process.cwd();

  while (current) {
    const testDataPath = path.join(current, 'test-data');
    if (fs.existsSync(testDataPath)) {
      return testDataPath;
    }

    const parent = path.dirname(current);
    if (parent === current) {
      // Reached root
      break;
    }
    current = parent;
  }

  throw new Error(
    'Could not find test-data directory. ' +
    'Please ensure test-data exists at repository root.'
  );
}

/**
 * Loads an input XML file for evaluation.
 * Searches recursively in the evals directory to support hierarchical structure.
 *
 * @param testName - Name of test (without .xml extension)
 * @returns XML content as string
 */
export function loadInputFile(testName: string): string {
  const testDataDir = getTestDataDir();
  const evalsDir = path.join(testDataDir, 'input', 'evals');
  const filename = `${testName}.xml`;

  // Try direct path first (for backwards compatibility)
  const directPath = path.join(evalsDir, filename);
  if (fs.existsSync(directPath)) {
    return fs.readFileSync(directPath, 'utf8');
  }

  // Search recursively
  const foundPath = findFileRecursively(evalsDir, filename);
  if (foundPath) {
    return fs.readFileSync(foundPath, 'utf8');
  }

  throw new Error(
    `Input file not found: ${testName}.xml\n` +
    `Searched in: ${evalsDir}`
  );
}

/**
 * Recursively searches for a file by name in a directory.
 *
 * @param dir - Directory to search in
 * @param filename - File name to search for
 * @returns Full path to file if found, null otherwise
 */
function findFileRecursively(dir: string, filename: string): string | null {
  if (!fs.existsSync(dir)) {
    return null;
  }

  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = path.join(dir, file.name);

    if (file.isDirectory()) {
      const found = findFileRecursively(fullPath, filename);
      if (found) return found;
    } else if (file.name === filename) {
      return fullPath;
    }
  }

  return null;
}

/**
 * Loads a golden file for comparison.
 * Searches recursively in the results directory to support hierarchical structure.
 *
 * @param testName - Name of test
 * @param format - File format ('json' or 'xml')
 * @param category - Category subdirectory (default: 'evals')
 * @returns Parsed golden data (for JSON) or string (for XML)
 */
export function loadGoldenFile<T = any>(
  testName: string,
  format: 'json' | 'xml' = 'json',
  category: string = 'evals'
): T {
  const testDataDir = getTestDataDir();
  const filename = `${testName}-result.${format}`;
  let searchDir: string;
  let oldPath: string;

  if (format === 'json') {
    searchDir = path.join(testDataDir, 'results', category);
    oldPath = path.join(searchDir, 'json', filename);
  } else if (format === 'xml') {
    searchDir = path.join(testDataDir, 'results', category);
    oldPath = path.join(searchDir, 'xml', filename);
  } else {
    throw new Error(`Unknown format: ${format}`);
  }

  // Try old flat structure first (backwards compatibility)
  if (fs.existsSync(oldPath)) {
    const content = fs.readFileSync(oldPath, 'utf8');
    if (format === 'json') {
      return JSON.parse(content) as T;
    }
    return content as any as T;
  }

  // Search recursively in new hierarchical structure
  const foundPath = findFileRecursively(searchDir, filename);
  if (foundPath) {
    const content = fs.readFileSync(foundPath, 'utf8');
    if (format === 'json') {
      return JSON.parse(content) as T;
    }
    return content as any as T;
  }

  throw new Error(
    `Golden file not found: ${filename}\n` +
    `Searched in: ${searchDir}\n` +
    `Run tests with TEST_MODE=generate to create golden files.`
  );
}

/**
 * Saves a golden file, preserving the input directory structure.
 *
 * @param content - Content to save
 * @param testName - Name of test
 * @param format - File format ('json' or 'xml')
 * @param category - Category subdirectory (default: 'evals')
 */
export function saveGoldenFile(
  content: any,
  testName: string,
  format: 'json' | 'xml' = 'json',
  category: string = 'evals'
): void {
  const testDataDir = getTestDataDir();
  const filename = `${testName}-result.${format}`;

  // Find the input file to determine the subdirectory structure
  const inputDir = path.join(testDataDir, 'input', category);
  const inputFilename = `${testName}.xml`;
  let relativeDir: string | null = null;

  if (fs.existsSync(inputDir)) {
    // Search for the input file
    const foundInputPath = findFileRecursively(inputDir, inputFilename);
    if (foundInputPath) {
      const inputFileDir = path.dirname(foundInputPath);
      // Get relative path from input category directory
      relativeDir = path.relative(inputDir, inputFileDir);
      if (relativeDir === '') {
        relativeDir = null;
      }
    }
  }

  // Build the golden file path
  let resultsDir = path.join(testDataDir, 'results', category);
  if (relativeDir) {
    resultsDir = path.join(resultsDir, relativeDir);
  }
  const goldenPath = path.join(resultsDir, filename);

  fs.mkdirSync(path.dirname(goldenPath), { recursive: true });

  if (format === 'json') {
    const json = typeof content === 'string'
      ? content
      : JSON.stringify(content, null, 2);
    fs.writeFileSync(goldenPath, json, 'utf8');
  } else if (format === 'xml') {
    const xml = typeof content === 'string' ? content : String(content);
    fs.writeFileSync(goldenPath, xml, 'utf8');
  } else {
    throw new Error(`Unknown format: ${format}`);
  }

  console.log(`  ✅ Generated golden file: ${goldenPath}`);
}

/**
 * Creates a MockLLMClient for evaluation testing.
 *
 * @param recordingsDir - Optional custom recordings directory
 * @returns MockLLMClient instance
 */
export function createMockLLMClient(recordingsDir?: string): MockLLMClient {
  const testMode = getTestMode();

  if (testMode === 'generate') {
    throw new Error(
      'LLM recording (generation mode) should be done by the agent itself.\n' +
      'Use TEST_MODE=test to run validation tests.'
    );
  }

  const dir = recordingsDir || path.join(getTestDataDir(), 'llm-recordings', 'evals');
  return new MockLLMClient(dir);
}

/**
 * Asserts that eval result structure is valid.
 *
 * @param result - Eval result to validate
 * @param expectedThreadId - Optional expected thread ID
 */
export function assertEvalResultStructure(
  result: EvalResult,
  expectedThreadId?: string
): void {
  if (!result) {
    throw new Error('EvalResult is null or undefined');
  }

  if (expectedThreadId && result.threadId !== expectedThreadId) {
    throw new Error(
      `ThreadId mismatch: expected '${expectedThreadId}', got '${result.threadId}'`
    );
  }

  if (!result.runs || result.runs.length === 0) {
    throw new Error('EvalResult has no runs');
  }

  if (result.totalRuns !== result.runs.length) {
    throw new Error(
      `TotalRuns mismatch: expected ${result.runs.length}, got ${result.totalRuns}`
    );
  }

  const passedRuns = result.runs.filter(r => r.passed).length;
  if (result.passedRuns !== passedRuns) {
    throw new Error(
      `PassedRuns mismatch: expected ${passedRuns}, got ${result.passedRuns}`
    );
  }
}

/**
 * Asserts that expect result passed.
 *
 * @param expectResult - Expect result to validate
 * @param expectName - Name of expectation
 */
export function assertExpectPassed(
  expectResult: ExpectResult,
  expectName: string
): void {
  if (!expectResult) {
    throw new Error(`ExpectResult for '${expectName}' is null or undefined`);
  }

  if (!expectResult.passed) {
    let errorMsg = `Expect '${expectName}' failed`;

    if (expectResult.judges) {
      for (const judge of expectResult.judges) {
        if (judge.error) {
          errorMsg += `\n  Judge '${judge.agent}': ${judge.error}`;
        } else if (!judge.passed) {
          errorMsg += `\n  Judge '${judge.agent}': failed (score: ${judge.score})`;
        }
      }
    }

    if (expectResult.asserts) {
      for (const assert of expectResult.asserts) {
        if (!assert.passed) {
          errorMsg += `\n  Assert '${assert.expression}': ${assert.error || 'failed'}`;
        }
      }
    }

    throw new Error(errorMsg);
  }
}

/**
 * Compares two eval results for similarity (allowing some flexibility).
 *
 * @param actual - Actual eval result
 * @param expected - Expected eval result
 */
export function assertEvalResultsSimilar(
  actual: EvalResult,
  expected: EvalResult
): void {
  if (!actual) {
    throw new Error('Actual EvalResult is null or undefined');
  }
  if (!expected) {
    throw new Error('Expected EvalResult is null or undefined');
  }

  // In test mode with mocked LLM, results should be deterministic
  const testMode = getTestMode();
  if (testMode === 'test') {
    // Structure checks
    if (actual.threadId !== expected.threadId) {
      throw new Error(
        `ThreadId mismatch: expected '${expected.threadId}', got '${actual.threadId}'`
      );
    }

    if (actual.totalRuns !== expected.totalRuns) {
      throw new Error(
        `TotalRuns mismatch: expected ${expected.totalRuns}, got ${actual.totalRuns}`
      );
    }

    if (actual.passed !== expected.passed) {
      throw new Error(
        `Passed status mismatch: expected ${expected.passed}, got ${actual.passed}`
      );
    }

    // Run count should match
    if (actual.runs.length !== expected.runs.length) {
      throw new Error(
        `Run count mismatch: expected ${expected.runs.length}, got ${actual.runs.length}`
      );
    }

    // Each run should have matching pass status
    for (let i = 0; i < actual.runs.length; i++) {
      const actualRun = actual.runs[i];
      const expectedRun = expected.runs[i];

      if (actualRun.passed !== expectedRun.passed) {
        throw new Error(
          `Run ${i + 1} passed status mismatch: expected ${expectedRun.passed}, got ${actualRun.passed}`
        );
      }
    }
  }
}

/**
 * Checks if golden files exist for a test.
 *
 * @param testName - Name of test
 * @param format - File format ('json' or 'xml')
 * @param category - Category subdirectory (default: 'evals')
 * @returns True if golden file exists
 */
export function goldenFileExists(
  testName: string,
  format: 'json' | 'xml' = 'json',
  category: string = 'evals'
): boolean {
  try {
    const testDataDir = getTestDataDir();
    let goldenPath: string;

    if (format === 'json') {
      goldenPath = path.join(
        testDataDir,
        'results',
        category,
        'json',
        `${testName}-result.json`
      );
    } else {
      goldenPath = path.join(
        testDataDir,
        'results',
        category,
        'xml',
        `${testName}-result.xml`
      );
    }

    return fs.existsSync(goldenPath);
  } catch {
    return false;
  }
}
