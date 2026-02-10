/**
 * Evaluation Models
 *
 * This file defines evaluation and testing primitives for agent testing.
 *
 * BASED ON: EvalXML v3 specification
 * FROM: .workspace/eval-v2/
 *
 * KEY FEATURES:
 * - Linear script evaluation (messages + expect blocks in execution order)
 * - CEL-based assertions and expressions
 * - Deterministic and LLM-based judges
 * - Flaky test tolerance via per-assertion pass rates
 * - Goal-based evaluation with run/review pattern
 *
 * @usage
 * Evaluation threads extend standard Thread with testing-specific features.
 * Supports deterministic testing (text_contains, tool_call_match) and
 * LLM-based evaluation (semantic_similarity, llm_helpfulness).
 *
 * @example Simple deterministic test
 * ```xml
 * <thread id="test_001" desc="Agent provides correct answer">
 *   <user>What is 2+2?</user>
 *
 *   <expect>
 *     <agent><text>4</text></agent>
 *     <judge agent="text_contains" as="t" scope="last" contains="4"/>
 *     <assert>t.passed</assert>
 *   </expect>
 * </thread>
 * ```
 *
 * @example Goal-based evaluation
 * ```xml
 * <thread id="test_002" desc="Agent creates file">
 *   <user>Create report.md with sales data</user>
 *
 *   <run maxSteps="10" />
 *
 *   <review>
 *     <judge agent="file_exists" as="f" scope="thread" path="report.md"/>
 *     <assert>run.completed && f.passed</assert>
 *   </review>
 * </thread>
 * ```
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./messages.tsp";
import "./threads.tsp";
import "./xml-decorators.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using AgentXml.Decorators;

namespace Microsoft.Agents.AI;

// ============================================
// ENUMS
// ============================================

/**
 * Judge Scope
 *
 * Determines what content the judge evaluates.
 *
 * SCOPES:
 * - last: Last agent emission only (most common)
 * - turn: Last agent emission + tool calls in that turn
 * - thread: Full thread history (all messages)
 */
enum JudgeScope {
  /** Last agent emission only */
  last,

  /** Last agent emission + tool calls */
  turn,

  /** Full thread history */
  thread,
}

/**
 * Match Type
 *
 * Text comparison strategy for judges.
 */
enum MatchType {
  /** Exact string match */
  exact,

  /** Substring match */
  contains,

  /** Regular expression */
  regex,

  /** Embedding similarity */
  semantic,

  /** JSON subset match */
  jsonSubset,

  /** JSON schema validation */
  jsonSchema,
}

// ============================================
// CORE MODELS
// ============================================

/**
 * Thread Element Union
 *
 * Union of all possible thread children.
 * Enables heterogeneous content with preserved ordering.
 *
 * ELEMENTS:
 * - ChatMessage: User, agent, tool, system messages
 * - Expect: Evaluation expectation with judges and assertions
 * - EvalRun: Goal-based execution instruction
 * - Review: Post-run evaluation
 *
 * SERIALIZATION:
 * - XML: Element type determined by XML element name (<user>, <expect>, <run>, <review>)
 * - JSON: Type determined by object structure/properties
 */
union ThreadElement {
  ChatMessage,
  Expect,
  EvalRun,
  Review,
}

/**
 * Evaluation Thread
 *
 * Test specification for evaluating agent behavior.
 * Contains messages, expectations, run instructions, and reviews in execution order.
 *
 * INHERITANCE: Extends ThreadBase (inherits threadId, status, createdAt, metadata)
 *
 * CONTENT MODEL:
 * - Heterogeneous array of messages and evaluation steps
 * - Messages: ChatMessage (user, agent, tool, system)
 * - Evaluation steps: Expect, EvalRun, Review
 * - Ordering preserved from XML document order
 *
 * FEATURES:
 * - Linear script execution (messages + expectations in order)
 * - CEL-based assertions
 * - Deterministic and LLM judges
 * - Flaky test tolerance (repeat + minPassRate)
 * - Goal-based evaluation (run + review)
 *
 * XML SERIALIZATION:
 * All elements become direct children of <thread> in document order:
 * - <user>, <agent>, <tool>, <system> → ChatMessage
 * - <expect> → Expect
 * - <run> → EvalRun
 * - <review> → Review
 *
 * @example Simple test
 * ```xml
 * <thread thread-id="test_001" desc="Agent answers correctly">
 *   <user>What's the capital of California?</user>
 *
 *   <expect>
 *     <agent><text>Sacramento</text></agent>
 *     <judge agent="text_contains" as="t" scope="last" contains="Sacramento"/>
 *     <assert>t.passed</assert>
 *   </expect>
 * </thread>
 * ```
 *
 * @example With tool message
 * ```xml
 * <thread thread-id="test_002" desc="Agent uses weather tool">
 *   <user>What's the weather in Seattle?</user>
 *
 *   <expect>
 *     <judge agent="tool_call_match" as="c" scope="turn" tool="get_weather"/>
 *     <assert>c.passed</assert>
 *   </expect>
 *
 *   <tool name="get_weather" call-id="call_001">
 *     <function-result>{"temp_f": 52, "condition": "cloudy"}</function-result>
 *   </tool>
 *
 *   <expect>
 *     <judge agent="text_contains" as="t" scope="last" contains="Seattle,52"/>
 *     <assert>t.passed</assert>
 *   </expect>
 * </thread>
 * ```
 *
 * @example Flaky test tolerance
 * ```xml
 * <thread thread-id="test_003" desc="Creative response" repeat="5">
 *   <user>Write a creative opening line for a mystery novel.</user>
 *
 *   <expect>
 *     <judge agent="llm_helpfulness" as="q" scope="last"/>
 *     <assert minPassRate="0.8">q.score >= 0.7</assert>
 *   </expect>
 * </thread>
 * ```
 */
@resource("eval/threads")
@xmlRoot("thread")
model EvalThread extends ThreadBase {
  /**
   * Evaluation description.
   * Describes what this test validates.
   */
  @xmlAttribute("desc")
  description?: string;

  /**
   * Number of times to repeat this evaluation.
   * Used for flaky test tolerance with per-assertion pass rate thresholds.
   */
  @xmlAttribute("repeat")
  repeat?: int32;

  /**
   * Ordered thread content.
   * Heterogeneous array of messages and eval blocks in execution order.
   *
   * CONTAINS: ChatMessage (user, agent, tool) + Expect + EvalRun + Review
   *
   * XML: All elements are direct children of <thread> in document order
   */
  elements: ThreadElement[];
}

/**
 * Expect
 *
 * Evaluation expectation with judges and assertions.
 * Evaluated after agent response.
 *
 * STRUCTURE:
 * 1. Optional reference output (expected agent response for comparison)
 * 2. Judges (evaluation functions that produce results)
 * 3. Assertions (CEL expressions using judge results)
 *
 * EXECUTION:
 * - Wait for agent response
 * - Run all judges in parallel
 * - Evaluate all assertions using judge results
 * - Passes if all assertions pass
 *
 * @example
 * ```xml
 * <expect name="correct_answer">
 *   <agent><text>The capital is Sacramento</text></agent>
 *   <judge agent="text_contains" as="t" scope="last" contains="Sacramento"/>
 *   <judge agent="text_contains" as="c" scope="last" contains="California"/>
 *   <assert>t.passed && c.passed</assert>
 * </expect>
 * ```
 */
@xmlElement("expect")
model Expect {
  /**
   * Optional name for this expectation.
   * Used in error messages and reports.
   *
   * RATIONALE: Makes test failures easier to diagnose
   *
   * EXAMPLE: "correct_answer", "calls_weather_tool", "final_response"
   */
  @xmlAttribute("name")
  name?: string;

  /**
   * Reference output for comparison.
   * Expected agent response used by judges.
   *
   * REQUIRED: All expectations must specify expected behavior
   * - Comparison judges (text_exact_match, semantic_similarity) use it for matching
   * - Other judges (text_contains, tool_call_match) receive it but may ignore it
   *
   * USAGE: Passed to all judges
   * - Provides expected behavior documentation
   * - Used by comparison judges for evaluation
   * - May be checked by tooling/linters
   *
   * RATIONALE: Makes test intent explicit and readable
   */
  referenceOutput: ChatMessage;

  /**
   * Judges to evaluate output.
   * Each judge produces a result stored in a variable.
   *
   * EXECUTION: All judges run in parallel
   *
   * RESULTS: Stored in variables (judge.as) for use in assertions
   */
  judges: Judge[];

  /**
   * Assertions using CEL expressions.
   * Must all evaluate to true for expect block to pass.
   *
   * EXECUTION: Evaluated after all judges complete
   *
   * VARIABLES AVAILABLE:
   * - Judge results: {judge.as}.passed, {judge.as}.score, etc.
   * - Thread context: messages, user, agent, etc.
   */
  asserts: Assert[];
}

/**
 * Eval Run
 *
 * Goal-based evaluation instruction.
 * Executes agent until completion or max steps reached.
 *
 * PATTERN: Like Playwright's "navigate and wait for load"
 * - Start execution
 * - Wait for completion or timeout
 * - Evaluate results with review block
 *
 * USE CASES:
 * - File creation: "Create report.md" → check file exists
 * - Multi-step tasks: "Research and summarize" → check final output
 * - Tool usage: "Search and book flight" → verify tool calls
 *
 * @example
 * ```xml
 * <user>Create report.md with Q4 sales data</user>
 * <run maxSteps="15" timeoutMs="30000" />
 * <review>
 *   <judge agent="file_exists" as="f" scope="thread" path="report.md"/>
 *   <assert>run.completed && f.passed</assert>
 * </review>
 * ```
 */
@xmlElement("run")
model EvalRun {
  /**
   * Maximum steps before stopping.
   * Prevents infinite loops.
   *
   * RATIONALE: Safety limit for agent execution
   *
   * DEFAULT: 10
   * TYPICAL: 10-20 for most tasks
   */
  @xmlAttribute("maxSteps")
  maxSteps?: int32;

  /**
   * Timeout in milliseconds.
   * Stops execution if time limit exceeded.
   *
   * RATIONALE: Prevent hanging on external dependencies
   *
   * TYPICAL: 30000 (30 seconds)
   */
  @xmlAttribute("timeoutMs")
  timeoutMs?: int32;
}

/**
 * Review
 *
 * Post-run evaluation.
 * Evaluated after run completion to check final state.
 *
 * STRUCTURE: Similar to Expect but focused on final state
 * - Judges evaluate final state (files, tool calls, messages)
 * - Assertions check run success + judge results
 * - No reference output (evaluates actual results only)
 *
 * VARIABLES AVAILABLE:
 * - run.completed: Whether run finished successfully
 * - run.steps: Number of steps executed
 * - run.durationMs: Execution time
 * - Judge results: {judge.as}.passed, {judge.as}.score, etc.
 *
 * @example
 * ```xml
 * <review>
 *   <judge agent="file_exists" as="f" scope="thread" path="report.md"/>
 *   <judge agent="file_min_bytes" as="s" scope="thread" path="report.md" minBytes="200"/>
 *   <assert>run.completed && f.passed && s.passed</assert>
 * </review>
 * ```
 */
@xmlElement("review")
model Review {
  /**
   * Judges to evaluate final state.
   */
  judges: Judge[];

  /**
   * Assertions using CEL expressions.
   */
  asserts: Assert[];
}

/**
 * Judge
 *
 * Evaluation function invocation.
 * Runs a judge agent and stores result in variable.
 *
 * JUDGES: Functions that evaluate output and produce pass/fail + score
 *
 * DETERMINISTIC JUDGES (free, zero-cost):
 * - text_contains: Keyword presence
 * - text_regex: Pattern matching
 * - text_exact_match: Exact string comparison
 * - tool_call_match: Tool validation
 * - file_exists: File presence check
 * - file_min_bytes: File size check
 *
 * LLM JUDGES (optional, costs money):
 * - semantic_similarity: Embedding similarity (uses embedding model)
 * - llm_helpfulness: Subjective quality (uses LLM)
 * - llm_groundedness: Factual grounding (uses LLM)
 * - llm_policy_compliance: Policy checks (uses LLM)
 *
 * RESULT STORAGE:
 * Judge result stored in variable named by `as` attribute.
 * Available in assertions as: {as}.passed, {as}.score, {as}.details
 *
 * @example Deterministic judge
 * ```xml
 * <judge agent="text_contains" as="t" scope="last" contains="Seattle,52"/>
 * <assert>t.passed</assert>
 * ```
 *
 * @example LLM judge
 * ```xml
 * <judge agent="llm_helpfulness" as="h" scope="last"/>
 * <assert>h.score >= 0.8</assert>
 * ```
 *
 * @example Judge with JSON args
 * ```xml
 * <judge agent="tool_call_match" as="c" scope="turn" tool="get_weather">
 *   { "location": "Seattle", "units": "imperial" }
 * </judge>
 * ```
 */
@xmlElement("judge")
model Judge {
  /**
   * Judge agent name.
   *
   * DETERMINISTIC: text_contains, text_regex, text_exact_match,
   *                tool_call_match, file_exists, file_min_bytes
   * LLM-BASED: semantic_similarity, llm_helpfulness, llm_groundedness,
   *            llm_policy_compliance
   */
  @xmlAttribute("agent")
  agent: string;

  /**
   * Variable name to store result.
   * Used in assert expressions.
   *
   * NAMING: Short, descriptive (t, call, f, quality)
   *
   * RESULT STRUCTURE:
   * - {as}.passed: Boolean pass/fail
   * - {as}.score: Float 0.0-1.0 score
   * - {as}.details: Additional judge-specific data
   * - {as}.error: Error message if judge failed
   */
  @xmlAttribute("as")
  as: string;

  /**
   * Evaluation scope.
   * Determines what content the judge evaluates.
   *
   * DEFAULT: last
   */
  @xmlAttribute("scope")
  scope?: JudgeScope;

  /**
   * Judge-specific arguments.
   * Can be simple attributes in XML or complex JSON/CEL in text content.
   *
   * XML PATTERNS:
   * Simple args (as attributes):
   *   <judge agent="text_contains" contains="Seattle,52"/>
   *
   * Complex args (as text content):
   *   <judge agent="tool_call_match">
   *     { "location": "Seattle", "units": "imperial" }
   *   </judge>
   *
   * FORMAT: JSON object or CEL expression
   */
  @xmlText
  @contentType(["json", "cel"])
  args?: string;
}

/**
 * Assert
 *
 * CEL expression assertion.
 * Evaluates to boolean using judge results.
 *
 * CEL EXPRESSIONS:
 * - Boolean operators: &&, ||, !
 * - Comparison: ==, !=, <, >, <=, >=
 * - Math: +, -, *, /, %
 * - Functions: len(), contains(), matches()
 *
 * VARIABLES:
 * - Judge results: {as}.passed, {as}.score, {as}.details
 * - Run context: run.completed, run.steps, run.durationMs
 * - Thread context: messages, user, agent
 *
 * FLAKY TEST TOLERANCE:
 * - minPassRate: Required pass rate for repeated evaluations
 * - If repeat=5 and minPassRate=0.8, assertion must pass 4/5 times
 *
 * @example Simple assertion
 * ```xml
 * <assert>t.passed</assert>
 * ```
 *
 * @example Complex assertion
 * ```xml
 * <assert>t.passed && c.passed && quality.score >= 0.8</assert>
 * ```
 *
 * @example Flaky test tolerance
 * ```xml
 * <assert minPassRate="0.8">creative.score >= 0.7</assert>
 * ```
 */
@xmlElement("assert")
model Assert {
  /**
   * Minimum pass rate for repeated evaluations (0.0-1.0).
   *
   * RATIONALE: Flaky test tolerance for non-deterministic outputs
   *
   * DEFAULT: 1.0 (must pass every time)
   * TYPICAL: 0.8 (pass 80% of the time)
   *
   * REQUIRES: thread.repeat > 1
   *
   * EXAMPLE: If repeat=5 and minPassRate=0.8, must pass 4/5 runs
   */
  @xmlAttribute("minPassRate")
  minPassRate?: float32;

  /**
   * CEL expression that evaluates to boolean.
   *
   * RAW TEXT BLOCK: Content is not XML-escaped (no manual CDATA needed)
   * The @contentType("cel") decorator signals to the serializer that this
   * is a raw text block requiring preprocessing.
   *
   * EXAMPLES:
   * - "t.passed"
   * - "t.passed && c.passed"
   * - "score >= 0.75 && count > 0"
   * - "run.completed && file.passed"
   */
  @xmlText
  @contentType("cel")
  expression: string;
}


// ============================================
// RESULT MODELS
// ============================================

/**
 * Judge Result
 *
 * Result from judge evaluation.
 */
model JudgeResult {
  /** Judge agent name */
  agent: string;

  /** Variable name result was stored in */
  as: string;

  /** Whether judge passed */
  passed: boolean;

  /** Score (0.0-1.0) */
  score: float32;

  /** Additional judge-specific details */
  details: Record<unknown>;

  /** Error message if judge failed */
  error?: string;
}

/**
 * Assert Result
 *
 * Result from assertion evaluation.
 */
model AssertResult {
  /** CEL expression that was evaluated */
  expression: string;

  /** Whether assertion passed */
  passed: boolean;

  /** Boolean result of expression */
  value: boolean;

  /** Pass rate for repeated evaluations (0.0-1.0) */
  passRate?: float32;

  /** Number of passes (for repeated evaluations) */
  passes?: int32;

  /** Total number of runs (for repeated evaluations) */
  runs?: int32;

  /** Required minimum pass rate */
  minPassRate?: float32;

  /** Error message if evaluation failed */
  error?: string;
}

/**
 * Evaluation Result
 *
 * Complete result from running evaluation thread.
 */
model EvalResult {
  /** Thread ID that was evaluated */
  threadId: string;

  /** Evaluation description */
  description?: string;

  /** Overall pass/fail */
  passed: boolean;

  /** Results from each run (if repeated) */
  runs: EvalRunResult[];

  /** Aggregate summary statistics */
  summary: {
    totalRuns: int32;
    passedRuns: int32;
    failedRuns: int32;
    totalAsserts: int32;
    passedAsserts: int32;
    failedAsserts: int32;
    avgDurationMs: float32;
  };

  /** Timestamp when evaluation completed */
  timestamp: utcDateTime;

  /** Total duration across all runs */
  totalDurationMs: int32;
}

/**
 * Evaluation Run Result
 *
 * Result from a single run of the evaluation.
 */
model EvalRunResult {
  /** Run number (1-based) */
  runNumber: int32;

  /** Whether this run passed */
  passed: boolean;

  /** Results from expect blocks */
  expects: ExpectResult[];

  /** Result from review block (if present) */
  review?: ReviewResult;

  /** Duration of this run in milliseconds */
  durationMs: int32;

  /** Error message if run failed */
  error?: string;
}

/**
 * Expect Result
 *
 * Result from evaluating an expect block.
 */
model ExpectResult {
  /** Expect block name (if provided) */
  name?: string;

  /** Whether expect block passed */
  passed: boolean;

  /** Judge results */
  judges: JudgeResult[];

  /** Assertion results */
  asserts: AssertResult[];
}

/**
 * Review Result
 *
 * Result from evaluating a review block.
 */
model ReviewResult {
  /** Whether review passed */
  passed: boolean;

  /** Judge results */
  judges: JudgeResult[];

  /** Assertion results */
  asserts: AssertResult[];
}

/**
 * Validation Error
 *
 * Error from validation operation.
 */
model ValidationError {
  /** Error code */
  code: string;

  /** Error message */
  message: string;

  /** Location in file (line number) */
  line?: int32;

  /** Element or attribute that caused error */
  element?: string;
}

/**
 * Lint Error
 *
 * Error from linting operation.
 */
model LintError {
  /** Severity level */
  severity: "error" | "warning" | "info";

  /** Error message */
  message: string;

  /** Location in file (line number) */
  line?: int32;

  /** Element or attribute that caused error */
  element?: string;

  /** Suggested fix */
  fix?: string;
}

// ============================================
// REST OPERATIONS
// ============================================

/**
 * Evaluation Thread Operations
 */
@route("/eval/threads")
namespace EvalThreads {
  /**
   * Run evaluation thread.
   *
   * Executes evaluation and returns results.
   */
  @post
  op runEval(@body thread: EvalThread): EvalResult;

  /**
   * Validate evaluation thread.
   *
   * Checks for structural and semantic errors.
   */
  @post
  @route("validate")
  op validateEval(@body thread: EvalThread): {
    valid: boolean;
    errors: ValidationError[];
  };

  /**
   * Lint evaluation thread.
   *
   * Checks for style issues and best practices.
   */
  @post
  @route("lint")
  op lintEval(@body thread: EvalThread): {
    errors: LintError[];
  };
}
