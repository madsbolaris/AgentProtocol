/**
 * Output capture for test results in documentation.
 *
 * This module captures test outputs in a structured JSON format that can be:
 * 1. Used in documentation as example outputs
 * 2. Compared across Python, .NET, and TypeScript implementations
 * 3. Validated for consistency
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

/**
 * Options for capturing test output
 */
export interface CaptureOptions {
  /** Unique test identifier (must match @docExample testId) */
  testId: string;
  /** The output to capture (will be serialized to string) */
  output: any;
  /** Additional metadata to store with the output */
  metadata?: Record<string, any>;
  /** Whether to normalize whitespace for comparison */
  normalize?: boolean;
}

/**
 * Captured output structure (matches cross-platform format)
 */
interface CapturedOutput {
  testId: string;
  timestamp: string;
  output: {
    raw: string;
    normalized: string | null;
    hash: string;
  };
  metadata: Record<string, any>;
}

/**
 * Captures test outputs for documentation and cross-platform validation.
 *
 * Modes:
 * - Validation mode (default): Compares output against existing golden files
 * - Update mode: Generates/updates golden files
 *
 * @example
 * ```typescript
 * const capture = new OutputCapture(outputDir, false);
 *
 * capture.capture({
 *   testId: 'basic-serialization',
 *   output: xmlString,
 *   metadata: { description: 'Basic XML output', format: 'xml' }
 * });
 * ```
 */
export class OutputCapture {
  /**
   * Creates a new OutputCapture instance.
   *
   * @param outputDir - Directory to store captured outputs
   * @param updateMode - If true, update golden files. If false, validate against them.
   */
  constructor(
    private readonly outputDir: string,
    private readonly updateMode: boolean = false
  ) {
    // Ensure output directory exists
    fs.mkdirSync(outputDir, { recursive: true });
  }

  /**
   * Capture test output to JSON file or validate against existing golden file.
   *
   * @param options - Capture options
   * @throws Error if not in update mode and output doesn't match golden file
   */
  capture({ testId, output, metadata = {}, normalize = true }: CaptureOptions): void {
    const rawOutput = this.serialize(output);
    const outputFile = path.join(this.outputDir, `${testId}.json`);

    if (this.updateMode) {
      // Update mode: Write new golden file
      const result: CapturedOutput = {
        testId,
        timestamp: new Date().toISOString(),
        output: {
          raw: rawOutput,
          normalized: normalize ? this.normalize(rawOutput) : null,
          hash: this.hash(rawOutput)
        },
        metadata
      };

      fs.writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf-8');
    } else {
      // Validation mode: Compare against golden file
      if (!fs.existsSync(outputFile)) {
        throw new Error(
          `Golden file not found: ${outputFile}\n` +
          `Run tests with UPDATE_GOLDEN=1 to generate golden files.`
        );
      }

      const expected: CapturedOutput = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
      const actualHash = this.hash(rawOutput);

      if (expected.output.hash !== actualHash) {
        const diff = this.generateDiff(expected.output.raw, rawOutput, testId);
        throw new Error(
          `Output mismatch for test '${testId}'\n` +
          `Expected hash: ${expected.output.hash}\n` +
          `Actual hash:   ${actualHash}\n\n` +
          `Diff:\n${diff}\n\n` +
          `To update golden file, run: UPDATE_GOLDEN=1 npm test`
        );
      }
    }
  }

  /**
   * Serialize a value to string for output.
   *
   * @param value - Value to serialize
   * @returns String representation
   */
  private serialize(value: any): string {
    if (typeof value === 'string') {
      return value;
    }

    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value, null, 2);
    }

    return String(value);
  }

  /**
   * Normalize whitespace for cross-platform comparison.
   *
   * @param value - String to normalize
   * @returns Normalized string
   */
  private normalize(value: string): string {
    return value
      .replace(/\r\n/g, '\n')  // Normalize line endings
      .replace(/\s+/g, ' ')    // Collapse whitespace
      .trim();
  }

  /**
   * Generate SHA-256 hash of a string.
   *
   * @param value - String to hash
   * @returns Hex-encoded hash
   */
  private hash(value: string): string {
    return crypto
      .createHash('sha256')
      .update(value, 'utf-8')
      .digest('hex');
  }

  /**
   * Generate unified diff between expected and actual output.
   *
   * @param expected - Expected output
   * @param actual - Actual output
   * @param testId - Test identifier
   * @returns Diff string
   */
  private generateDiff(expected: string, actual: string, testId: string): string {
    const expectedLines = expected.split('\n');
    const actualLines = actual.split('\n');

    const maxLines = Math.max(expectedLines.length, actualLines.length);
    const diffLines: string[] = [`--- expected/${testId}`, `+++ actual/${testId}`];

    for (let i = 0; i < maxLines; i++) {
      const expectedLine = expectedLines[i] ?? '';
      const actualLine = actualLines[i] ?? '';

      if (expectedLine !== actualLine) {
        if (expectedLine) {
          diffLines.push(`- ${expectedLine}`);
        }
        if (actualLine) {
          diffLines.push(`+ ${actualLine}`);
        }
      } else {
        diffLines.push(`  ${expectedLine}`);
      }
    }

    return diffLines.join('\n');
  }
}

/**
 * Create an OutputCapture fixture for use in tests.
 *
 * Automatically detects:
 * - Repository root directory
 * - Output directory (test-data/results/docs)
 * - Update mode from UPDATE_GOLDEN environment variable
 *
 * @returns OutputCapture instance configured for tests
 *
 * @example
 * ```typescript
 * import { createOutputCaptureFixture } from '@microsoft/agents-test-helpers';
 *
 * describe('My Tests', () => {
 *   const outputCapture = createOutputCaptureFixture();
 *
 *   it('should serialize message', () => {
 *     const result = serialize(message);
 *     outputCapture.capture({ testId: 'test-id', output: result });
 *   });
 * });
 * ```
 */
export function createOutputCaptureFixture(): OutputCapture {
  // Find repository root by looking for test-data directory
  let repoRoot = __dirname;
  while (repoRoot !== '/' && repoRoot !== '.') {
    const testDataDir = path.join(repoRoot, 'test-data');
    if (fs.existsSync(testDataDir)) {
      break;
    }
    repoRoot = path.dirname(repoRoot);
  }

  // Use docs results directory for documentation examples
  const outputDir = path.join(repoRoot, 'test-data', 'results', 'docs');
  const updateMode = process.env.UPDATE_GOLDEN === '1';

  if (updateMode) {
    console.log('\n🔄 Running in UPDATE mode - golden files will be updated');
  } else {
    console.log('\n✅ Validating against golden files');
  }

  return new OutputCapture(outputDir, updateMode);
}
