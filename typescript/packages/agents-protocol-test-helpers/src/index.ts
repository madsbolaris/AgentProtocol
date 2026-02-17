/**
 * Test helpers for Microsoft Agents SDK.
 *
 * This package provides utilities for creating test-driven documentation:
 * - Decorators for marking tests as documentation examples
 * - Output capture for validating test results across languages
 * - Mock LLM client for deterministic testing
 * - Eval test helpers for loading golden files
 *
 * @packageDocumentation
 */

export { docExample, getAllDocExamples, getDocExample } from './docMarkers';
export type { DocExampleMetadata } from './docMarkers';

export { OutputCapture, createOutputCaptureFixture } from './outputCapture';
export type { CaptureOptions } from './outputCapture';

export { LLMRecorder } from './llmRecorder';
export type { RawMessage, RawTool, LLMResponseData } from './llmRecorder';

export { MockLLMClient } from './mockLLMClient';
export type {
  MockChatCompletion,
  MockChatMessage,
  MockTool,
  MockToolCall,
  MockFunction,
  MockContentPart
} from './mockLLMClient';

export {
  getTestMode,
  getTestDataDir,
  loadInputFile,
  loadGoldenFile,
  saveGoldenFile,
  createMockLLMClient,
  assertEvalResultStructure,
  assertExpectPassed,
  assertEvalResultsSimilar,
  goldenFileExists
} from './evalTestHelpers';
export type {
  EvalResult,
  EvalRun,
  ExpectResult,
  JudgeResult,
  AssertResult
} from './evalTestHelpers';
