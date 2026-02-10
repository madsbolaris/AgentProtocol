#!/usr/bin/env python3
"""
Generate golden evaluation datasets for eval files.

This script:
1. Reads eval XML files from test-data/input/evals/
2. Runs evaluations using EvalRunner with mock agent outputs
3. Generates golden EvalResult datasets in test-data/results/evals/
4. Optionally captures LLM recordings in test-data/llm-recordings/evals/

The golden eval results are language-agnostic and used for cross-platform validation
across .NET, Python, and TypeScript evaluation implementations.

Usage:
    # Generate golden eval results for all eval files
    python scripts/testgen/generate_eval_datasets.py

    # Generate for specific eval file only
    python scripts/testgen/generate_eval_datasets.py --eval-file 01-simple-text-expect.xml

    # Generate with LLM recording capture (for semantic judges)
    python scripts/testgen/generate_eval_datasets.py --record-llm

    # Specify custom directories
    python scripts/testgen/generate_eval_datasets.py --inputs test-data/input/evals/

Prerequisites:
- Uses mock agent responses defined in this script
- For LLM-based judges (semantic_similarity), actual LLM calls are made when --record-llm is set
"""

import json
import sys
import argparse
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from lxml import etree
import hashlib
import time

# Add parent directory to path to import LLMRecorder and EvalXmlPreprocessor
# scripts/testgen/generate_eval_datasets.py -> scripts/testgen -> scripts -> repo_root
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "python" / "microsoft-agents-protocol" / "tests" / "mocks"))
sys.path.insert(0, str(repo_root / "python" / "microsoft-agents-protocol-xml" / "src"))
LLMRecorder = None
LLMRecorder_import_error = None
try:
    from llm_recorder import LLMRecorder
except ImportError as e:
    LLMRecorder_import_error = str(e)

# Import EvalXmlPreprocessor
try:
    from microsoft.agents.xml.eval_xml_preprocessor import preprocess as preprocess_eval_xml
except ImportError as e:
    print(f"⚠️  Warning: Failed to import EvalXmlPreprocessor: {e}")
    print("   EvalXML preprocessing will be disabled.")
    preprocess_eval_xml = lambda x: x  # No-op fallback

# Try to import OpenAI for LLM-based judges
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
    print("⚠️  Warning: openai package not installed. LLM recording will be disabled.")


class MockAgentRunner:
    """
    Provides mock agent responses for eval tests.

    This allows us to generate deterministic golden datasets without
    requiring actual bot implementations.
    """

    def __init__(self):
        """Initialize mock responses for various test scenarios."""
        # Map eval file names or thread IDs to mock agent responses
        self.mock_responses = {
            # Simple text expectations
            "eval-001": [
                {"role": "agent", "contents": [{"kind": "text", "text": "4"}]}
            ],

            # Multiple expects
            "eval-002": [
                {"role": "agent", "contents": [{"kind": "text", "text": "The capital of France is Paris."}]},
                {"role": "agent", "contents": [{"kind": "text", "text": "France is located in Western Europe."}]}
            ],

            # With run config
            "eval-003": [
                {"role": "agent", "contents": [{"kind": "text", "text": "Hello! How can I help you today?"}]}
            ],

            # Tool call expect
            "eval-004": [
                {"role": "agent", "contents": [
                    {"kind": "functionCall", "callId": "call-001", "name": "get_weather",
                     "arguments": '{"location": "San Francisco", "units": "fahrenheit"}'}
                ]},
                {"role": "agent", "contents": [{"kind": "text", "text": "It's 65°F and sunny in San Francisco."}]}
            ],

            # LLM judge (semantic similarity)
            "eval-005": [
                {"role": "agent", "contents": [{"kind": "text", "text":
                    "In circuits deep and code so bright,\nA mind awakens in the night,\n"
                    "With logic swift and learning keen,\nThe smartest helper ever seen."}]}
            ],

            # Regex judge
            "eval-006": [
                {"role": "agent", "contents": [{"kind": "text", "text": "My email is john.doe@example.com"}]}
            ],

            # Multi-turn conversation
            "eval-007": [
                {"role": "agent", "contents": [{"kind": "text", "text": "I'm an AI assistant created by Anthropic."}]},
                {"role": "agent", "contents": [{"kind": "text", "text": "I can help with writing, analysis, coding, and answering questions."}]}
            ],

            # Multiple asserts
            "eval-008": [
                {"role": "agent", "contents": [{"kind": "text", "text": "The result is 42 and the status is OK."}]}
            ],

            # JSON output expect
            "eval-009": [
                {"role": "agent", "contents": [{"kind": "text", "text": '{"name": "John", "age": 30, "city": "New York"}'}]}
            ],

            # Numeric comparison
            "eval-010": [
                {"role": "agent", "contents": [{"kind": "text", "text": "The temperature is 72 degrees."}]}
            ],

            # Default fallback response for any other eval
            "_default": [
                {"role": "agent", "contents": [{"kind": "text", "text": "This is a mock agent response."}]}
            ]
        }

    def get_agent_responses(self, thread_id: str, user_messages: List[Dict]) -> List[Dict]:
        """
        Get mock agent responses for a given thread ID and user messages.

        Args:
            thread_id: The thread ID from the eval file
            user_messages: List of user messages in the thread

        Returns:
            List of mock agent message responses
        """
        # Get responses for this thread ID, or use default
        responses = self.mock_responses.get(thread_id, self.mock_responses["_default"])

        # Return appropriate number of responses based on user message count
        return responses[:len(user_messages)] if len(responses) > len(user_messages) else responses


class EvalGoldenDatasetGenerator:
    """Generate golden datasets for evaluation tests."""

    def __init__(
        self,
        inputs_dir: Path,
        results_dir: Path,
        llm_recordings_dir: Path,
        record_llm: bool = False,
        repo_root: Optional[Path] = None
    ):
        """
        Initialize the generator.

        Args:
            inputs_dir: Directory containing eval XML files
            results_dir: Directory to write golden results
            llm_recordings_dir: Directory to write LLM recordings
            record_llm: Whether to record LLM interactions
            repo_root: Repository root path
        """
        self.inputs_dir = inputs_dir
        self.results_dir = results_dir
        self.llm_recordings_dir = llm_recordings_dir
        self.record_llm = record_llm
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.mock_runner = MockAgentRunner()

        # Initialize LLM client and recorder if recording is enabled
        self.llm_client = None
        self.llm_recorder = None
        self.llm_model = "gpt-4o-mini"  # Use cheaper model for semantic similarity
        self.llm_temperature = 0.0  # Default temperature
        self.llm_seed = 42  # Default seed
        self.llm_call_count = 0

        if self.record_llm:
            # Check if dependencies are available
            if AsyncOpenAI is None:
                print("❌ Error: openai package required for LLM recording")
                print("   Install with: pip install openai")
                sys.exit(1)

            if LLMRecorder is None:
                print("❌ Error: LLMRecorder not available")
                if LLMRecorder_import_error:
                    print(f"   Import error: {LLMRecorder_import_error}")
                sys.exit(1)

            # Check for Foundry credentials first (preferred)
            foundry_endpoint = os.environ.get("FOUNDRY_ENDPOINT")
            foundry_api_key = os.environ.get("FOUNDRY_API_KEY")
            foundry_model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT")

            if foundry_endpoint and foundry_api_key:
                # Use Foundry (Microsoft AI platform)
                self.llm_client = AsyncOpenAI(
                    api_key=foundry_api_key,
                    base_url=f"{foundry_endpoint}/openai/v1/"
                )
                self.llm_model = foundry_model or "gpt-4"

                # gpt-5-nano doesn't support temperature=0.0, use default (1.0)
                if "gpt-5-nano" in self.llm_model.lower():
                    self.llm_temperature = 1.0
                    self.llm_seed = None  # gpt-5-nano may not support seed

                print(f"✅ LLM recording enabled (Foundry):")
                print(f"   Endpoint: {foundry_endpoint}")
                print(f"   Model: {self.llm_model}")
                print(f"   Temperature: {self.llm_temperature}")
            else:
                # Fall back to OpenAI
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                if not openai_api_key:
                    print("❌ Error: No LLM credentials found")
                    print("   Set either:")
                    print("     - FOUNDRY_ENDPOINT, FOUNDRY_API_KEY, FOUNDRY_MODEL_DEPLOYMENT")
                    print("     - OPENAI_API_KEY")
                    sys.exit(1)

                self.llm_client = AsyncOpenAI(api_key=openai_api_key)
                self.llm_model = "gpt-4o-mini"
                print(f"✅ LLM recording enabled (OpenAI):")
                print(f"   Model: {self.llm_model}")

            # Initialize recorder
            self.llm_recordings_dir.mkdir(parents=True, exist_ok=True)
            self.llm_recorder = LLMRecorder(self.llm_recordings_dir)
            print(f"   Recordings: {self.llm_recordings_dir}")

    def _parse_eval_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse eval XML file into a structured format.

        Args:
            xml_content: Raw XML content

        Returns:
            Parsed eval structure
        """
        # Preprocess EvalXML to wrap raw block content in CDATA
        preprocessed_xml = preprocess_eval_xml(xml_content)
        root = etree.fromstring(preprocessed_xml.encode('utf-8'))

        # Extract thread attributes
        thread_id = root.get("thread-id", "")
        description = root.get("desc", "")
        repeat = root.get("repeat")

        eval_data = {
            "threadId": thread_id,
            "description": description,
            "repeat": int(repeat) if repeat else None,
            "elements": []
        }

        # Parse elements (user messages, agent messages, expects, etc.)
        for child in root:
            if child.tag in ["user", "agent", "tool", "system"]:
                message = self._parse_message(child)
                eval_data["elements"].append(message)
            elif child.tag == "expect":
                expect = self._parse_expect(child)
                eval_data["elements"].append(expect)
            elif child.tag == "run":
                run_config = self._parse_run_config(child)
                eval_data["elements"].append(run_config)

        return eval_data

    def _parse_message(self, element: etree.Element) -> Dict[str, Any]:
        """Parse a message element (user, agent, tool, system)."""
        message = {
            "_type": "message",
            "role": element.tag,
            "messageId": element.get("message-id", ""),
            "contents": []
        }

        # Add optional attributes
        for attr in ["user-id", "agent-id", "created-at"]:
            value = element.get(attr)
            if value:
                key = "".join(word.capitalize() if i > 0 else word
                             for i, word in enumerate(attr.split("-")))
                message[key] = value

        # Parse contents
        for content_elem in element:
            if content_elem.tag == "text":
                message["contents"].append({
                    "kind": "text",
                    "text": content_elem.text or ""
                })
            elif content_elem.tag == "function-call":
                args_text = content_elem.text or ""
                message["contents"].append({
                    "kind": "functionCall",
                    "callId": content_elem.get("call-id", ""),
                    "name": content_elem.get("name", ""),
                    "arguments": args_text.strip()
                })
            elif content_elem.tag == "function-result":
                result_elem = content_elem.find("result")
                result_text = result_elem.text if result_elem is not None else (content_elem.text or "")
                message["contents"].append({
                    "kind": "functionResult",
                    "callId": content_elem.get("call-id", ""),
                    "name": content_elem.get("name", ""),
                    "result": result_text.strip() if result_text else ""
                })

        return message

    def _parse_expect(self, element: etree.Element) -> Dict[str, Any]:
        """Parse an expect element."""
        expect = {
            "_type": "expect",
            "name": element.get("name", ""),
            "judges": [],
            "asserts": []
        }

        # Parse reference output (agent message)
        for child in element:
            if child.tag in ["agent", "assistant"]:
                expect["referenceOutput"] = self._parse_message(child)
            elif child.tag == "judge":
                judge = {
                    "agent": child.get("agent", ""),
                    "as": child.get("as", child.get("agent", "")),
                    "args": child.text.strip() if child.text else ""
                }
                expect["judges"].append(judge)
            elif child.tag == "assert":
                assert_expr = child.text.strip() if child.text else ""
                expect["asserts"].append({
                    "expression": assert_expr
                })

        return expect

    def _parse_run_config(self, element: etree.Element) -> Dict[str, Any]:
        """Parse a run configuration element."""
        return {
            "_type": "run",
            "maxSteps": int(element.get("maxSteps")) if element.get("maxSteps") else None,
            "timeoutMs": int(element.get("timeoutMs")) if element.get("timeoutMs") else None
        }

    def _run_evaluation(self, eval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run evaluation using mock agent responses.

        Args:
            eval_data: Parsed eval data structure

        Returns:
            EvalResult as dict
        """
        start_time = datetime.now(timezone.utc).replace(tzinfo=None)
        thread_id = eval_data["threadId"]

        # Build thread history from messages
        thread_history = []
        user_messages = []

        for element in eval_data["elements"]:
            if element.get("_type") == "message":
                thread_history.append(element)
                if element["role"] == "user":
                    user_messages.append(element)

        # Get mock agent responses
        mock_agent_responses = self.mock_runner.get_agent_responses(thread_id, user_messages)

        # Run through expects and generate results
        repeat_count = eval_data.get("repeat", 1) or 1
        all_runs = []

        for run_num in range(repeat_count):
            run_result = self._execute_single_run(
                eval_data,
                thread_history,
                mock_agent_responses,
                run_num + 1
            )
            all_runs.append(run_result)

        # Aggregate results
        end_time = datetime.now(timezone.utc).replace(tzinfo=None)
        total_duration_ms = int((end_time - start_time).total_seconds() * 1000)

        passed_runs = sum(1 for run in all_runs if run["passed"])
        total_asserts = sum(len(exp.get("asserts", [])) for run in all_runs for exp in run.get("expects", []))
        passed_asserts = sum(
            sum(1 for assert_res in exp.get("asserts", []) if assert_res.get("passed", False))
            for run in all_runs
            for exp in run.get("expects", [])
        )

        return {
            "threadId": thread_id,
            "description": eval_data.get("description", ""),
            "passed": passed_runs == len(all_runs),
            "runs": all_runs,
            "totalRuns": len(all_runs),
            "passedRuns": passed_runs,
            "failedRuns": len(all_runs) - passed_runs,
            "totalAsserts": total_asserts,
            "passedAsserts": passed_asserts,
            "failedAsserts": total_asserts - passed_asserts,
            "avgDurationMs": total_duration_ms / len(all_runs) if all_runs else 0.0,
            "timestamp": start_time.isoformat() + "Z",
            "totalDurationMs": total_duration_ms
        }

    def _execute_single_run(
        self,
        eval_data: Dict[str, Any],
        thread_history: List[Dict],
        mock_responses: List[Dict],
        run_number: int
    ) -> Dict[str, Any]:
        """
        Execute a single evaluation run.

        Args:
            eval_data: Parsed eval data
            thread_history: Message history
            mock_responses: Mock agent responses
            run_number: Current run number

        Returns:
            EvalRunResult as dict
        """
        run_start = datetime.now(timezone.utc).replace(tzinfo=None)

        run_result = {
            "runNumber": run_number,
            "passed": True,
            "expects": [],
            "error": None
        }

        # Track which mock response to use
        mock_response_idx = 0

        # Process expects
        for element in eval_data["elements"]:
            if element.get("_type") == "expect":
                # Get the next mock response as the "actual output"
                actual_output = None
                if mock_response_idx < len(mock_responses):
                    actual_output = mock_responses[mock_response_idx]
                    mock_response_idx += 1
                else:
                    # Use last response if we run out
                    actual_output = mock_responses[-1] if mock_responses else None

                expect_result = self._evaluate_expect(element, actual_output)
                run_result["expects"].append(expect_result)

                if not expect_result["passed"]:
                    run_result["passed"] = False

        run_end = datetime.now(timezone.utc).replace(tzinfo=None)
        run_result["durationMs"] = int((run_end - run_start).total_seconds() * 1000)

        return run_result

    def _evaluate_expect(self, expect: Dict[str, Any], actual_output: Optional[Dict]) -> Dict[str, Any]:
        """
        Evaluate a single expectation.

        Args:
            expect: Expect element data
            actual_output: Actual agent output message

        Returns:
            ExpectResult as dict
        """
        expect_result = {
            "name": expect.get("name", ""),
            "passed": True,
            "judges": [],
            "asserts": []
        }

        if actual_output is None:
            expect_result["passed"] = False
            expect_result["error"] = "No actual output available"
            return expect_result

        reference_output = expect.get("referenceOutput")

        # Run judges
        judge_results = {}
        for judge in expect.get("judges", []):
            judge_result = self._evaluate_judge(
                judge,
                actual_output,
                reference_output
            )
            judge_results[judge_result["as"]] = judge_result
            expect_result["judges"].append(judge_result)

        # Evaluate assertions
        for assert_def in expect.get("asserts", []):
            assert_result = self._evaluate_assertion(
                assert_def,
                judge_results
            )
            expect_result["asserts"].append(assert_result)

            if not assert_result.get("passed", False):
                expect_result["passed"] = False

        return expect_result

    def _evaluate_judge(
        self,
        judge: Dict[str, Any],
        actual_output: Dict,
        reference_output: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Evaluate using a judge agent.

        Args:
            judge: Judge configuration
            actual_output: Actual agent message
            reference_output: Reference agent message

        Returns:
            JudgeResult as dict
        """
        judge_name = judge["agent"]
        judge_as = judge.get("as", judge_name)

        # Extract text from messages
        actual_text = self._extract_text_from_message(actual_output)
        reference_text = self._extract_text_from_message(reference_output) if reference_output else ""

        # Simple deterministic judge implementations
        judge_result = {
            "agent": judge_name,
            "as": judge_as,
            "passed": False,
            "score": 0.0,
            "details": {}
        }

        if judge_name == "text_exact_match":
            matches = actual_text.strip() == reference_text.strip()
            judge_result["passed"] = matches
            judge_result["score"] = 1.0 if matches else 0.0
            judge_result["details"]["reason"] = "Exact match" if matches else "Text does not match"

        elif judge_name == "text_contains":
            # Parse args to get expected substrings
            args = judge.get("args", "")
            try:
                expected_items = json.loads(args) if args else []
                if not isinstance(expected_items, list):
                    expected_items = [str(expected_items)]
            except:
                expected_items = [args] if args else []

            all_found = all(item.lower() in actual_text.lower() for item in expected_items)
            judge_result["passed"] = all_found
            judge_result["score"] = 1.0 if all_found else 0.0
            judge_result["details"]["expected_items"] = expected_items
            judge_result["details"]["all_found"] = all_found

        elif judge_name == "text_regex":
            # Parse regex pattern from args
            args = judge.get("args", "")
            try:
                import re
                args_dict = json.loads(args) if args else {}
                pattern = args_dict.get("pattern", "")
                flags_str = args_dict.get("flags", "")

                flags = 0
                if "i" in flags_str.lower():
                    flags |= re.IGNORECASE

                if pattern:
                    match = re.search(pattern, actual_text, flags)
                    judge_result["passed"] = match is not None
                    judge_result["score"] = 1.0 if match else 0.0
                    judge_result["details"]["pattern"] = pattern
                    judge_result["details"]["matched"] = match is not None
            except Exception as e:
                judge_result["error"] = f"Regex evaluation failed: {str(e)}"

        elif judge_name == "tool_call_match":
            # Check if actual output contains function call with expected arguments
            actual_func_calls = [c for c in actual_output.get("contents", []) if c.get("kind") == "functionCall"]

            if actual_func_calls:
                # Check if args match
                args = judge.get("args", "")
                try:
                    expected_args = json.loads(args) if args else {}
                    actual_args_str = actual_func_calls[0].get("arguments", "{}")
                    actual_args = json.loads(actual_args_str) if actual_args_str else {}

                    # Check if expected args are subset of actual args
                    matches = all(
                        actual_args.get(key) == value
                        for key, value in expected_args.items()
                    )
                    judge_result["passed"] = matches
                    judge_result["score"] = 1.0 if matches else 0.5
                except:
                    judge_result["passed"] = True  # Has function call, args parse failed
                    judge_result["score"] = 0.5
            else:
                judge_result["passed"] = False
                judge_result["score"] = 0.0

        elif judge_name == "semantic_similarity":
            # Use LLM for semantic similarity if recording is enabled
            if self.record_llm and self.llm_client and self.llm_recorder:
                try:
                    # Call LLM to evaluate semantic similarity
                    similarity_result = asyncio.run(
                        self._call_llm_semantic_similarity(actual_text, reference_text)
                    )
                    judge_result["passed"] = similarity_result["passed"]
                    judge_result["score"] = similarity_result["score"]
                    judge_result["details"]["similarity_score"] = similarity_result["score"]
                    judge_result["details"]["llm_reasoning"] = similarity_result.get("reasoning", "")
                except Exception as e:
                    print(f"  ⚠️  LLM call failed, falling back to heuristic: {e}")
                    # Fall back to heuristic
                    actual_words = set(actual_text.lower().split())
                    reference_words = set(reference_text.lower().split())

                    if reference_words:
                        overlap = len(actual_words & reference_words)
                        similarity = overlap / len(reference_words)
                        judge_result["score"] = min(1.0, similarity * 1.5)
                        judge_result["passed"] = judge_result["score"] >= 0.7
                        judge_result["details"]["similarity_score"] = judge_result["score"]
                    else:
                        judge_result["passed"] = True
                        judge_result["score"] = 1.0
            else:
                # Simple word overlap heuristic for mock
                actual_words = set(actual_text.lower().split())
                reference_words = set(reference_text.lower().split())

                if reference_words:
                    overlap = len(actual_words & reference_words)
                    similarity = overlap / len(reference_words)
                    judge_result["score"] = min(1.0, similarity * 1.5)  # Boost score a bit
                    judge_result["passed"] = judge_result["score"] >= 0.7
                    judge_result["details"]["similarity_score"] = judge_result["score"]
                else:
                    judge_result["passed"] = True
                    judge_result["score"] = 1.0
        else:
            # Unknown judge - mark as error
            judge_result["error"] = f"Unknown judge: {judge_name}"

        return judge_result

    async def _call_llm_semantic_similarity(
        self,
        actual_text: str,
        reference_text: str
    ) -> Dict[str, Any]:
        """
        Call LLM to evaluate semantic similarity between two texts.

        Args:
            actual_text: The actual output text
            reference_text: The expected/reference text

        Returns:
            Dict with 'passed', 'score', and 'reasoning' keys
        """
        # Construct prompt for semantic similarity
        system_prompt = """You are a semantic similarity evaluator. Compare the actual output to the reference output and determine if they are semantically similar.

Consider:
- Do they convey the same meaning?
- Do they contain the same key information?
- Are they answering the same question?

Respond with a JSON object:
{
  "similar": true/false,
  "score": 0.0-1.0,
  "reasoning": "brief explanation"
}"""

        user_prompt = f"""Reference Output:
{reference_text}

Actual Output:
{actual_text}

Are these semantically similar?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Hash the request
        self.llm_call_count += 1
        call_id = self.llm_call_count
        request_hash = self.llm_recorder.hash_request(
            model=self.llm_model,
            messages=messages,
            temperature=self.llm_temperature,
            seed=self.llm_seed
        )

        # Save request
        request_data = {
            "callId": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": request_hash,
            "model": self.llm_model,
            "messages": messages,
            "temperature": self.llm_temperature,
            "seed": self.llm_seed
        }
        self.llm_recorder.save_request(request_hash, request_data)

        # Make LLM call
        print(f"  🤖 Calling LLM for semantic similarity (hash: {request_hash})")
        llm_params = {
            "model": self.llm_model,
            "messages": messages,
            "temperature": self.llm_temperature,
            "response_format": {"type": "json_object"}
        }
        # Only add seed if it's not None (some models don't support it)
        if self.llm_seed is not None:
            llm_params["seed"] = self.llm_seed

        response = await self.llm_client.chat.completions.create(**llm_params)

        # Extract response
        content = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason

        # Parse JSON response
        try:
            result = json.loads(content)
            passed = result.get("similar", False)
            score = result.get("score", 0.0)
            reasoning = result.get("reasoning", "")
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            passed = "true" in content.lower() or "similar" in content.lower()
            score = 1.0 if passed else 0.0
            reasoning = content

        # Save response
        response_data = {
            "callId": call_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": request_hash,
            "response": {
                "id": response.id,
                "model": response.model,
                "created": response.created,
                "finishReason": finish_reason,
                "content": [{"text": content}],
                "toolCalls": []
            }
        }
        self.llm_recorder.save_response(request_hash, response_data)

        return {
            "passed": passed,
            "score": score,
            "reasoning": reasoning
        }

    def _evaluate_assertion(
        self,
        assert_def: Dict[str, Any],
        judge_results: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Evaluate an assertion expression.

        Args:
            assert_def: Assertion definition
            judge_results: Results from judges (keyed by 'as' name)

        Returns:
            AssertResult as dict
        """
        expression = assert_def.get("expression", "")

        assert_result = {
            "expression": expression,
            "passed": False,
            "value": None
        }

        try:
            # Simple expression evaluation
            # Format: {judge_name}.passed or {judge_name}.score > 0.7

            if ".passed" in expression:
                var_name = expression.split(".")[0].strip()
                if var_name in judge_results:
                    assert_result["passed"] = judge_results[var_name]["passed"]
                    assert_result["value"] = judge_results[var_name]["passed"]
                else:
                    assert_result["error"] = f"Judge result '{var_name}' not found"

            elif ".score" in expression:
                # Extract variable name and comparison
                parts = expression.split()
                var_name = parts[0].split(".")[0].strip()

                if var_name in judge_results:
                    score = judge_results[var_name]["score"]

                    # Simple threshold check (>= 0.7)
                    if ">=" in expression or ">" in expression:
                        try:
                            threshold = float([p for p in parts if p.replace(".", "").isdigit()][0])
                            assert_result["passed"] = score >= threshold
                        except:
                            assert_result["passed"] = score >= 0.7
                    else:
                        assert_result["passed"] = score >= 0.7

                    assert_result["value"] = score
                else:
                    assert_result["error"] = f"Judge result '{var_name}' not found"
            else:
                # Complex expression - for mock, just check if all judges passed
                assert_result["passed"] = all(jr["passed"] for jr in judge_results.values())
                assert_result["value"] = assert_result["passed"]

        except Exception as e:
            assert_result["error"] = f"Assert evaluation failed: {str(e)}"
            assert_result["passed"] = False

        return assert_result

    def _extract_text_from_message(self, message: Optional[Dict]) -> str:
        """Extract text content from a message."""
        if not message:
            return ""

        texts = []
        for content in message.get("contents", []):
            if content.get("kind") == "text":
                texts.append(content.get("text", ""))

        return "\n".join(texts)

    def _hash_content(self, content: str) -> str:
        """
        Generate SHA-256 hash of content.

        Args:
            content: String content to hash

        Returns:
            Hex-encoded hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _save_golden_file(
        self,
        output_dir: Path,
        filename: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        relative_dir: Optional[Path] = None
    ) -> None:
        """
        Save a golden file with metadata.

        Args:
            output_dir: Base directory to save file
            filename: Output filename
            content: Content to save (dict)
            metadata: Optional metadata to include
            relative_dir: Optional relative directory path to preserve structure
        """
        # Preserve directory structure if relative_dir is provided
        if relative_dir:
            output_dir = output_dir / relative_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        golden_data = {
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z",
            "content": content,
            "hash": self._hash_content(json.dumps(content, sort_keys=True)),
            "metadata": metadata or {}
        }

        output_file = output_dir / filename
        output_file.write_text(json.dumps(golden_data, indent=2) + "\n")

    def generate_for_eval_file(self, eval_file: Path, relative_dir: Optional[Path] = None) -> None:
        """
        Generate golden dataset for a specific eval file.

        Args:
            eval_file: Path to eval XML file
            relative_dir: Optional relative directory path to preserve structure
        """
        display_path = str(relative_dir / eval_file.name) if relative_dir else eval_file.name
        print(f"\nProcessing: {display_path}")

        try:
            # Read and parse XML
            xml_content = eval_file.read_text()
            eval_data = self._parse_eval_xml(xml_content)

            print(f"  → Thread ID: {eval_data['threadId']}")
            print(f"  → Description: {eval_data.get('description', 'N/A')}")

            # Run evaluation with mock responses
            print(f"  → Running evaluation with mock agent responses...")
            eval_result = self._run_evaluation(eval_data)

            # Save golden result (preserving directory structure)
            result_filename = f"{eval_file.stem}-result.json"
            self._save_golden_file(
                self.results_dir / "json",
                result_filename,
                eval_result,
                metadata={
                    "input_file": display_path,
                    "thread_id": eval_data["threadId"],
                    "description": eval_data.get("description", ""),
                    "mock_data": True,
                    "generator": "python"
                },
                relative_dir=relative_dir
            )

            print(f"  ✅ Saved: {relative_dir / result_filename if relative_dir else result_filename}")
            print(f"     Passed: {eval_result['passed']}")
            print(f"     Runs: {eval_result['totalRuns']} (Passed: {eval_result['passedRuns']}, Failed: {eval_result['failedRuns']})")
            print(f"     Asserts: {eval_result['totalAsserts']} (Passed: {eval_result['passedAsserts']}, Failed: {eval_result['failedAsserts']})")

            # LLM recordings summary
            if self.record_llm and self.llm_call_count > 0:
                print(f"  📹 LLM calls recorded: {self.llm_call_count} requests/responses")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    def generate_all(self, eval_file_filter: Optional[str] = None, dry_run: bool = False) -> None:
        """
        Generate golden datasets for all eval files (recursively scanning subdirectories).

        Args:
            eval_file_filter: Optional eval filename to generate for (e.g., "01-simple-text-expect.xml")
            dry_run: If True, show what would be generated without writing files
        """
        # Get all eval XML files (recursively)
        if eval_file_filter:
            # Search recursively for the specific file
            eval_files_with_dirs = []
            for eval_file in self.inputs_dir.rglob(eval_file_filter):
                relative_dir = eval_file.parent.relative_to(self.inputs_dir)
                eval_files_with_dirs.append((eval_file, relative_dir if str(relative_dir) != '.' else None))

            if not eval_files_with_dirs:
                print(f"❌ Eval file '{eval_file_filter}' not found in {self.inputs_dir}")
                sys.exit(1)
        else:
            # Get all XML files recursively
            eval_files_with_dirs = []
            for eval_file in sorted(self.inputs_dir.rglob("*.xml")):
                relative_dir = eval_file.parent.relative_to(self.inputs_dir)
                eval_files_with_dirs.append((eval_file, relative_dir if str(relative_dir) != '.' else None))

        if not eval_files_with_dirs:
            print(f"❌ No eval files found in {self.inputs_dir}")
            sys.exit(1)

        print(f"{'='*70}")
        print(f"Generating Golden Evaluation Datasets")
        print(f"{'='*70}")
        print(f"\nFound {len(eval_files_with_dirs)} eval files in {self.inputs_dir} (scanning recursively)")
        print(f"Output directory: {self.results_dir}")
        if self.record_llm:
            print(f"LLM recordings: {self.llm_recordings_dir}")

        # Dry-run mode: show what would be generated without writing files
        if dry_run:
            print(f"\n🔍 DRY RUN - Preview of evaluation dataset generation")
            print()
            print(f"Would process {len(eval_files_with_dirs)} eval files:")
            for eval_file, relative_dir in eval_files_with_dirs[:10]:  # Show first 10
                display_path = str(relative_dir / eval_file.name) if relative_dir else eval_file.name
                print(f"  - {display_path}")
            if len(eval_files_with_dirs) > 10:
                print(f"  ... and {len(eval_files_with_dirs) - 10} more")
            print()
            print(f"Would generate:")
            print(f"  - {len(eval_files_with_dirs)} JSON result files")
            if self.record_llm:
                print(f"  - LLM recordings for semantic judges")
            print()
            print(f"Output directories:")
            print(f"  - {self.results_dir / 'json'}")
            if self.record_llm:
                print(f"  - {self.llm_recordings_dir / 'json'}")
            print()
            print("🔍 Dry run complete - no files were written")
            print("   Run without --dry-run to generate files")
            return

        # Clean up old results
        print(f"\n🧹 Cleaning old results...")
        json_dir = self.results_dir / "json"
        if json_dir.exists():
            import shutil
            shutil.rmtree(json_dir)
            print(f"  ✅ Cleared: {json_dir}")

        if self.record_llm:
            recordings_json_dir = self.llm_recordings_dir / "json"
            if recordings_json_dir.exists():
                import shutil
                shutil.rmtree(recordings_json_dir)
                print(f"  ✅ Cleared: {recordings_json_dir}")

        # Generate for each eval file (preserving directory structure)
        success_count = 0
        error_count = 0

        for eval_file, relative_dir in eval_files_with_dirs:
            try:
                self.generate_for_eval_file(eval_file, relative_dir)
                success_count += 1
                time.sleep(0.05)  # Small delay between files
            except Exception as e:
                display_path = str(relative_dir / eval_file.name) if relative_dir else eval_file.name
                print(f"\n❌ Failed to process {display_path}: {e}")
                error_count += 1

        # Summary
        print(f"\n{'='*70}")
        print(f"Summary:")
        print(f"  ✅ Success: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📁 Results: {self.results_dir}")
        if self.record_llm:
            print(f"  📹 Recordings: {self.llm_recordings_dir}")
        print(f"{'='*70}")

        print(f"\n🎯 Golden evaluation datasets generated using mock agent responses")
        print(f"   These files serve as cross-platform validation targets.")
        print(f"   Directory structure has been preserved in results/evals/")
        if self.record_llm:
            print(f"📹 LLM interactions recorded for semantic judges")
        print("\nNext steps:")
        print("1. Review generated golden eval result files")
        print("2. Run evaluation tests for .NET, Python, and TypeScript:")
        print("   dotnet test --filter EvalTests")
        print("   pytest python/microsoft-agents-evaluators/tests/")
        print("   npm test -- eval")
        print("3. Update mock responses in this script as needed for new eval files")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate golden evaluation datasets from eval XML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for all eval files
  python scripts/testgen/generate_eval_datasets.py

  # Generate for specific eval file
  python scripts/testgen/generate_eval_datasets.py --eval-file 01-simple-text-expect.xml

  # Use custom paths
  python scripts/testgen/generate_eval_datasets.py --inputs test-data/input/evals --results test-data/results/evals
        """
    )

    parser.add_argument(
        "--inputs",
        type=Path,
        default=None,
        help="Directory containing eval XML files (default: test-data/input/evals)"
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=None,
        help="Directory to write results (default: test-data/results/evals)"
    )
    parser.add_argument(
        "--llm-recordings",
        type=Path,
        default=None,
        help="Directory to write LLM recordings (default: test-data/llm-recordings/evals)"
    )
    parser.add_argument(
        "--eval-file",
        type=str,
        help="Generate only for specific eval file (e.g., '01-simple-text-expect.xml')"
    )
    parser.add_argument(
        "--record-llm",
        action="store_true",
        help="Record LLM interactions for semantic judges (requires LLM API access)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )

    args = parser.parse_args()

    # Resolve paths
    # Go up two levels from script location: scripts/testgen -> scripts -> repo_root
    repo_root = Path(__file__).parent.parent.parent
    inputs_dir = args.inputs or repo_root / "test-data" / "input" / "evals"
    results_dir = args.results or repo_root / "test-data" / "results" / "evals"
    llm_recordings_dir = args.llm_recordings or repo_root / "test-data" / "llm-recordings" / "evals"

    # Validate inputs directory exists
    if not inputs_dir.exists():
        print(f"❌ Inputs directory does not exist: {inputs_dir}")
        sys.exit(1)

    # Create generator
    generator = EvalGoldenDatasetGenerator(
        inputs_dir=inputs_dir,
        results_dir=results_dir,
        llm_recordings_dir=llm_recordings_dir,
        record_llm=args.record_llm,
        repo_root=repo_root
    )

    # Generate
    generator.generate_all(eval_file_filter=args.eval_file, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
