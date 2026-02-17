"""
Integration tests for generating question branch recordings (Q1-Q5).

These tests generate recordings for different user answer patterns:
- Q1: User answers all questions clearly (GOLDEN PATH - continues to artifact)
- Q2: User skips 1 question (stops after synthesis)
- Q3: User provides additional requirements (stops after synthesis)
- Q4: User confused, requests clarification (stops after synthesis)
- Q5: User requests mode switch to CREATE (stops after synthesis)

Usage:
    # Generate recordings (requires ANTHROPIC_API_KEY):
    EXPERT_FEEDBACK_TEST_MODE=record \\
    pytest tests/integration/test_generate_question_branches.py -v -s

    # Replay recordings (no API key needed):
    pytest tests/integration/test_generate_question_branches.py -v
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path

# Add scripts and tests directories to path (use absolute paths)
_scripts_dir = (Path(__file__).parent.parent.parent / "scripts").resolve()
_tests_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_tests_dir))


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_question_branch_q1_all_answered(
    mock_claude_sdk,
    test_workspace
):
        """
        Q1: User answers all questions clearly (GOLDEN PATH).

        TEST CONTROL: None (user simulator uses "clear_answers" pattern)

        Stages:
        1. Load questions from iteration 1
        2. User answers ALL questions clearly
        3. Iteration 2 with user answers (2 experts)
        4. Synthesis iteration 2
        5. CONTINUES TO ARTIFACT WORKFLOW

        Expected recordings: 3 (2 iter2 + 1 synthesis)
        Time: ~35s

        Run with:
            EXPERT_FEEDBACK_TEST_MODE=record \\
            pytest tests/integration/test_generate_question_branches.py::TestGenerateQuestionBranches::test_generate_question_branch_q1_all_answered -v -s
        """
        # Ensure scripts directory is in sys.path (absolute path)
        import sys
        from pathlib import Path
        _scripts_path = str((Path(__file__).parent.parent.parent / "scripts").resolve())
        
        # Remove and re-add to ensure it's at position 0
        if _scripts_path in sys.path:
            sys.path.remove(_scripts_path)
        sys.path.insert(0, _scripts_path)
        

        # Import AFTER mock is set up and sys.path is configured
        from core.spawn_experts import spawn_all_experts
        from core.synthesize import synthesize_feedback
        from config import get_config
        from ui.progress_tracker import ProgressTracker
        from file_io.json_ops import load_json, save_json
        from fixtures.workspace_snapshot import has_snapshot, restore_workspace, snapshot_workspace

        workspace = test_workspace  # Using test_workspace to avoid fixture import issues
        config = get_config()
        state_path = workspace / "state.json"
        recordings_base = Path(__file__).parent.parent / "recordings"

        print(f"\n{'='*80}")
        print(f"🎬 Recording Q1 Branch - All Questions Answered (GOLDEN PATH)")
        print(f"{'='*80}")

        # ========== RESTORE PREDECESSOR WORKSPACE ==========
        predecessor = "test_generate_synthesis_iteration_1"

        print(f"\n🔹 Restoring workspace from: {predecessor}")
        if has_snapshot(predecessor, recordings_base):
            restore_workspace(predecessor, workspace, recordings_base)
            print(f"  ✅ Workspace restored from snapshot")
        else:
            pytest.fail(f"Prerequisite test not found: {predecessor}. Run it first.")

        # ========== LOAD QUESTIONS ==========
        print(f"\n🔹 Loading questions from iteration 1")
        questions_file = workspace / "iteration-1" / "questions.json"

        if not questions_file.exists():
            pytest.fail(f"Questions file not found: {questions_file}")

        questions_data = load_json(questions_file)
        questions = questions_data.get("questions", [])

        print(f"  ✅ Loaded {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q.get('question', 'N/A')[:60]}...")

        if len(questions) == 0:
            pytest.fail("No questions found in iteration 1")

        # ========== GENERATE USER ANSWERS ==========
        print(f"\n🔹 Generating user answers (clear answers for all questions)")

        # Create qa_answers.json with all questions answered
        qa_answers = []
        for q in questions:
            question_text = q.get("question", "")
            question_id = q.get("id", f"q-{questions.index(q)}")

            # Generate realistic answer based on question content
            if "numeric" in question_text.lower() or "range" in question_text.lower():
                answer = "Support standard JavaScript Number range (±2^53 - 1). For values outside this range, return an error with clear guidance to use BigInt or string-based precision libraries."
            elif "error" in question_text.lower() or "validation" in question_text.lower():
                answer = "Return HTTP 400 with structured JSON error including: error code, user-friendly message, field-specific validation details, and suggested corrections."
            elif "test" in question_text.lower() or "coverage" in question_text.lower():
                answer = "Aim for 80%+ code coverage with unit tests (Jest/pytest), integration tests for API endpoints, and E2E tests for critical user flows. Use CI/CD to enforce coverage thresholds."
            else:
                answer = f"Yes, this is important. Please implement with production-quality error handling, input validation, and comprehensive tests."

            qa_answers.append({
                "question_id": question_id,
                "question": question_text,
                "user_answer": answer,
                "answered_at": "2026-02-16T12:00:00Z"
            })

        # Save qa_answers.json
        qa_answers_file = workspace / "iteration-1" / "qa_answers.json"
        save_json({"answers": qa_answers}, qa_answers_file)

        print(f"  ✅ Generated {len(qa_answers)} answers")
        print(f"  ✅ Saved to: {qa_answers_file}")

        # ========== ITERATION 2: Experts with User Answers ==========
        print(f"\n🔹 ITERATION 2: Expert refinement with user answers")
        print("-" * 60)

        experts = ["typescript", "python"]
        review_context = """Refine the simple-calculator API review based on user answers to your questions.

The user has provided answers to all clarifying questions. Use these answers to:
1. Address any uncertainties from iteration 1
2. Provide more specific recommendations based on user requirements
3. Identify any new concerns raised by the user's answers

Focus on production readiness: validation, error handling, testing, security, and documentation."""

        progress = ProgressTracker(2, workspace)

        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=2,
            state_path=state_path,
            config=config,
            progress=progress,
            qa_answers_path=str(qa_answers_file),
            correlation_id="q1-iteration-2-experts"
        )

        print(f"\n✅ Iteration 2 experts complete:")
        for expert_result in result.get("results", []):
            expert = expert_result.get("expert")
            status = expert_result.get("status")
            duration = expert_result.get("duration_seconds", 0)
            session_id = expert_result.get("session_id", "N/A")
            print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

        # Verify success
        assert result.get("success_count", 0) == len(experts), \
            f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

        # ========== SYNTHESIS ITERATION 2 ==========
        print(f"\n🔹 SYNTHESIS: Consolidate iteration 2 feedback")
        print("-" * 60)

        progress = ProgressTracker(2, workspace)

        synthesis_result = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress,
            correlation_id="q1-synthesis-iter2"
        )

        print(f"\n✅ Synthesis complete:")
        print(f"  - Status: {synthesis_result.get('status')}")
        print(f"  - Convergence: {synthesis_result.get('convergence_percent', 0)}%")
        print(f"  - Consensus: {synthesis_result.get('consensus_reached', False)}")
        print(f"  - Duration: {synthesis_result.get('duration_seconds', 0):.1f}s")
        print(f"  - Session: {synthesis_result.get('session_id', 'N/A')[:12]}...")

        # Verify synthesis produced expected outputs
        assert synthesis_result.get("status") == "complete", "Synthesis should complete successfully"

        # ========== SUMMARY ==========
        print(f"\n{'='*80}")
        print("✅ Q1 Branch Recording Complete! (GOLDEN PATH)")
        print(f"{'='*80}")
        print(f"Workspace: {workspace}")
        print(f"\nRecordings generated:")
        print(f"  - Iteration 2: {len(experts)} expert reviews")
        print(f"  - Iteration 2 Synthesis: 1 recording")
        print(f"  - Total: {len(experts) + 1} recordings")
        print(f"\n🚀 This branch continues to artifact workflow")
        print(f"{'='*80}\n")

        # Save workspace snapshot for artifact workflow tests
        if mock_claude_sdk and mock_claude_sdk.mode == "record":
            snapshot_workspace(
                test_name="test_generate_question_branch_q1_all_answered",
                workspace=workspace,
                recordings_dir=recordings_base
            )
            print("  📸 Workspace snapshot saved for artifact workflow tests\n")

        # Verify recordings were made
        if mock_claude_sdk:
            print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
            assert mock_claude_sdk.call_count >= len(experts) + 1, \
                f"Should have made at least {len(experts) + 1} LLM calls"

async def test_generate_question_branch_q2_some_skipped(

        mock_claude_sdk,
        test_workspace
    ):
        """
        Q2: User skips 1 of 3 questions.

        TEST CONTROL: None (user simulator uses "partial_answers" pattern)

        Stages:
        1. Load questions from iteration 1
        2. User answers 2/3 questions, skips 1
        3. Iteration 2 with partial answers
        4. Synthesis iteration 2
        5. STOPS (no artifact workflow)

        Expected recordings: 3 (2 iter2 + 1 synthesis)
        Time: ~35s

        Run with:
            EXPERT_FEEDBACK_TEST_MODE=record \\
            pytest tests/integration/test_generate_question_branches.py::TestGenerateQuestionBranches::test_generate_question_branch_q2_some_skipped -v -s
        """
        # Ensure scripts directory is in sys.path (absolute path)
        import sys
        from pathlib import Path
        _scripts_path = str((Path(__file__).parent.parent.parent / "scripts").resolve())

        # Remove and re-add to ensure it's at position 0
        if _scripts_path in sys.path:
            sys.path.remove(_scripts_path)
        sys.path.insert(0, _scripts_path)

        # Import AFTER mock is set up and sys.path is configured
        from core.spawn_experts import spawn_all_experts
        from core.synthesize import synthesize_feedback
        from config import get_config
        from ui.progress_tracker import ProgressTracker
        from file_io.json_ops import load_json, save_json
        from fixtures.workspace_snapshot import has_snapshot, restore_workspace, snapshot_workspace

        workspace = test_workspace  # Using test_workspace to avoid fixture import issues
        config = get_config()
        state_path = workspace / "state.json"
        recordings_base = Path(__file__).parent.parent / "recordings"

        print(f"\n{'='*80}")
        print(f"🎬 Recording Q2 Branch - Some Questions Skipped")
        print(f"{'='*80}")

        # ========== RESTORE PREDECESSOR WORKSPACE ==========
        predecessor = "test_generate_synthesis_iteration_1"

        print(f"\n🔹 Restoring workspace from: {predecessor}")
        if has_snapshot(predecessor, recordings_base):
            restore_workspace(predecessor, workspace, recordings_base)
            print(f"  ✅ Workspace restored from snapshot")
        else:
            pytest.fail(f"Prerequisite test not found: {predecessor}. Run it first.")

        # ========== LOAD QUESTIONS ==========
        print(f"\n🔹 Loading questions from iteration 1")
        questions_file = workspace / "iteration-1" / "questions.json"

        if not questions_file.exists():
            pytest.fail(f"Questions file not found: {questions_file}")

        questions_data = load_json(questions_file)
        questions = questions_data.get("questions", [])

        print(f"  ✅ Loaded {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q.get('question', 'N/A')[:60]}...")

        if len(questions) < 2:
            pytest.fail("Need at least 2 questions to test partial answers")

        # ========== GENERATE PARTIAL USER ANSWERS ==========
        print(f"\n🔹 Generating partial answers (skipping question #{len(questions)})")

        # Create qa_answers.json with only some questions answered
        qa_answers = []
        for i, q in enumerate(questions[:-1]):  # Skip last question
            question_text = q.get("question", "")
            question_id = q.get("id", f"q-{i}")

            # Generate realistic answer
            if "numeric" in question_text.lower() or "range" in question_text.lower():
                answer = "Support standard JavaScript Number range (±2^53 - 1)."
            elif "error" in question_text.lower() or "validation" in question_text.lower():
                answer = "Return HTTP 400 with structured JSON error messages."
            else:
                answer = "Yes, please implement this with proper error handling."

            qa_answers.append({
                "question_id": question_id,
                "question": question_text,
                "user_answer": answer,
                "answered_at": "2026-02-16T12:00:00Z"
            })

        # Save qa_answers.json
        qa_answers_file = workspace / "iteration-1" / "qa_answers.json"
        save_json({"answers": qa_answers}, qa_answers_file)

        print(f"  ✅ Answered {len(qa_answers)}/{len(questions)} questions")
        print(f"  ⚠️  Skipped question: {questions[-1].get('question', 'N/A')[:60]}...")
        print(f"  ✅ Saved to: {qa_answers_file}")

        # ========== ITERATION 2: Experts with Partial Answers ==========
        print(f"\n🔹 ITERATION 2: Expert refinement with partial answers")
        print("-" * 60)

        experts = ["typescript", "python"]
        review_context = """Refine the simple-calculator API review based on partial user answers.

The user has answered some questions but left others unanswered. Use the provided answers to refine your analysis, but note that some areas may still require clarification.

Focus on production readiness where user input is available: validation, error handling, testing, security, and documentation."""

        progress = ProgressTracker(2, workspace)

        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=2,
            state_path=state_path,
            config=config,
            progress=progress,
            qa_answers_path=str(qa_answers_file),
            correlation_id="q2-iteration-2-partial-experts"
        )

        print(f"\n✅ Iteration 2 experts complete:")
        for expert_result in result.get("results", []):
            expert = expert_result.get("expert")
            status = expert_result.get("status")
            duration = expert_result.get("duration_seconds", 0)
            session_id = expert_result.get("session_id", "N/A")
            print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

        # Verify success
        assert result.get("success_count", 0) == len(experts), \
            f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

        # ========== SYNTHESIS ITERATION 2 ==========
        print(f"\n🔹 SYNTHESIS: Consolidate iteration 2 feedback")
        print("-" * 60)

        progress = ProgressTracker(2, workspace)

        synthesis_result = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress,
            correlation_id="q2-synthesis-iter2-partial"
        )

        print(f"\n✅ Synthesis complete:")
        print(f"  - Status: {synthesis_result.get('status')}")
        print(f"  - Convergence: {synthesis_result.get('convergence_percent', 0)}%")
        print(f"  - Consensus: {synthesis_result.get('consensus_reached', False)}")
        print(f"  - Duration: {synthesis_result.get('duration_seconds', 0):.1f}s")
        print(f"  - Session: {synthesis_result.get('session_id', 'N/A')[:12]}...")

        # Verify synthesis produced expected outputs
        assert synthesis_result.get("status") == "complete", "Synthesis should complete successfully"

        # ========== SUMMARY ==========
        print(f"\n{'='*80}")
        print("✅ Q2 Branch Recording Complete! (Partial Answers)")
        print(f"{'='*80}")
        print(f"Workspace: {workspace}")
        print(f"\nRecordings generated:")
        print(f"  - Iteration 2: {len(experts)} expert reviews")
        print(f"  - Iteration 2 Synthesis: 1 recording")
        print(f"  - Total: {len(experts) + 1} recordings")
        print(f"\n⚠️  Workflow STOPS after synthesis (incomplete answers)")
        print(f"{'='*80}\n")

        # Save workspace snapshot
        if mock_claude_sdk and mock_claude_sdk.mode == "record":
            snapshot_workspace(
                test_name="test_generate_question_branch_q2_some_skipped",
                workspace=workspace,
                recordings_dir=recordings_base
            )
            print("  📸 Workspace snapshot saved\n")

        # Verify recordings were made
        if mock_claude_sdk:
            print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
            assert mock_claude_sdk.call_count >= len(experts) + 1, \
                f"Should have made at least {len(experts) + 1} LLM calls"

async def test_generate_question_branch_q3_expanded_scope(

        mock_claude_sdk,
        test_workspace
    ):
        """
        Q3: User provides additional requirements in answers.

        TEST CONTROL: None (user simulator uses "expanded_scope" pattern)

        Stages:
        1. Load questions from iteration 1
        2. User answers with extra context/requirements
        3. Iteration 2 with expanded scope
        4. Synthesis iteration 2
        5. STOPS (no artifact workflow)

        Expected recordings: 3 (2 iter2 + 1 synthesis)
        Time: ~35s

        Run with:
            EXPERT_FEEDBACK_TEST_MODE=record \\
            pytest tests/integration/test_generate_question_branches.py::TestGenerateQuestionBranches::test_generate_question_branch_q3_expanded_scope -v -s
        """
        # Ensure scripts directory is in sys.path (absolute path)
        import sys
        from pathlib import Path
        _scripts_path = str((Path(__file__).parent.parent.parent / "scripts").resolve())

        # Remove and re-add to ensure it's at position 0
        if _scripts_path in sys.path:
            sys.path.remove(_scripts_path)
        sys.path.insert(0, _scripts_path)

        # Import AFTER mock is set up and sys.path is configured
        from core.spawn_experts import spawn_all_experts
        from core.synthesize import synthesize_feedback
        from config import get_config
        from ui.progress_tracker import ProgressTracker
        from file_io.json_ops import load_json, save_json
        from fixtures.workspace_snapshot import has_snapshot, restore_workspace, snapshot_workspace

        workspace = test_workspace  # Using test_workspace to avoid fixture import issues
        config = get_config()
        state_path = workspace / "state.json"
        recordings_base = Path(__file__).parent.parent / "recordings"

        print(f"\n{'='*80}")
        print(f"🎬 Recording Q3 Branch - Expanded Scope")
        print(f"{'='*80}")

        # ========== RESTORE PREDECESSOR WORKSPACE ==========
        predecessor = "test_generate_synthesis_iteration_1"

        print(f"\n🔹 Restoring workspace from: {predecessor}")
        if has_snapshot(predecessor, recordings_base):
            restore_workspace(predecessor, workspace, recordings_base)
            print(f"  ✅ Workspace restored from snapshot")
        else:
            pytest.fail(f"Prerequisite test not found: {predecessor}. Run it first.")

        # ========== LOAD QUESTIONS ==========
        print(f"\n🔹 Loading questions from iteration 1")
        questions_file = workspace / "iteration-1" / "questions.json"

        if not questions_file.exists():
            pytest.fail(f"Questions file not found: {questions_file}")

        questions_data = load_json(questions_file)
        questions = questions_data.get("questions", [])

        print(f"  ✅ Loaded {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q.get('question', 'N/A')[:60]}...")

        if len(questions) == 0:
            pytest.fail("No questions found in iteration 1")

        # ========== GENERATE EXPANDED ANSWERS ==========
        print(f"\n🔹 Generating answers with expanded scope/requirements")

        # Create qa_answers.json with expanded requirements
        qa_answers = []
        for i, q in enumerate(questions):
            question_text = q.get("question", "")
            question_id = q.get("id", f"q-{i}")

            # Generate answer with ADDITIONAL requirements beyond the question
            if "numeric" in question_text.lower() or "range" in question_text.lower():
                answer = """Support standard JavaScript Number range (±2^53 - 1). For values outside this range, return an error.

ADDITIONAL REQUIREMENTS:
- Also support BigInt for arbitrary precision integers
- Add a 'precision' parameter to specify decimal places for division
- Support scientific notation in input/output
- Add validation for NaN and Infinity edge cases"""

            elif "error" in question_text.lower() or "validation" in question_text.lower():
                answer = """Return HTTP 400 with structured JSON error messages.

ADDITIONAL REQUIREMENTS:
- Implement i18n for error messages (support en, es, fr initially)
- Add error tracking/telemetry (send to monitoring service)
- Include request ID in all error responses for debugging
- Support both JSON and XML error formats based on Accept header
- Add rate limiting with 429 Too Many Requests"""

            else:
                answer = f"""Yes, this is important. Please implement with proper error handling.

ADDITIONAL REQUIREMENTS:
- Add comprehensive logging (structured JSON logs)
- Implement circuit breaker pattern for external dependencies
- Add health check endpoint (/health)
- Support graceful shutdown
- Add request tracing with correlation IDs"""

            qa_answers.append({
                "question_id": question_id,
                "question": question_text,
                "user_answer": answer,
                "answered_at": "2026-02-16T12:00:00Z"
            })

        # Save qa_answers.json
        qa_answers_file = workspace / "iteration-1" / "qa_answers.json"
        save_json({"answers": qa_answers}, qa_answers_file)

        print(f"  ✅ Generated {len(qa_answers)} answers with expanded requirements")
        print(f"  ⚠️  User added significant scope beyond original questions")
        print(f"  ✅ Saved to: {qa_answers_file}")

        # ========== ITERATION 2: Experts with Expanded Scope ==========
        print(f"\n🔹 ITERATION 2: Expert refinement with expanded scope")
        print("-" * 60)

        experts = ["typescript", "python"]
        review_context = """Refine the simple-calculator API review based on user answers.

The user has provided answers WITH ADDITIONAL REQUIREMENTS beyond the original questions. Carefully note the expanded scope and assess:
1. Which additional requirements are essential vs. nice-to-have
2. How the expanded scope affects the architecture
3. Whether the scope expansion is manageable or needs prioritization

Focus on production readiness with the expanded requirements in mind."""

        progress = ProgressTracker(2, workspace)

        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=2,
            state_path=state_path,
            config=config,
            progress=progress,
            qa_answers_path=str(qa_answers_file),
            correlation_id="q3-iteration-2-expanded-experts"
        )

        print(f"\n✅ Iteration 2 experts complete:")
        for expert_result in result.get("results", []):
            expert = expert_result.get("expert")
            status = expert_result.get("status")
            duration = expert_result.get("duration_seconds", 0)
            session_id = expert_result.get("session_id", "N/A")
            print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

        # Verify success
        assert result.get("success_count", 0) == len(experts), \
            f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

        # ========== SYNTHESIS ITERATION 2 ==========
        print(f"\n🔹 SYNTHESIS: Consolidate iteration 2 feedback")
        print("-" * 60)

        progress = ProgressTracker(2, workspace)

        synthesis_result = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress,
            correlation_id="q3-synthesis-iter2-expanded"
        )

        print(f"\n✅ Synthesis complete:")
        print(f"  - Status: {synthesis_result.get('status')}")
        print(f"  - Convergence: {synthesis_result.get('convergence_percent', 0)}%")
        print(f"  - Consensus: {synthesis_result.get('consensus_reached', False)}")
        print(f"  - Duration: {synthesis_result.get('duration_seconds', 0):.1f}s")
        print(f"  - Session: {synthesis_result.get('session_id', 'N/A')[:12]}...")

        # Verify synthesis produced expected outputs
        assert synthesis_result.get("status") == "complete", "Synthesis should complete successfully"

        # ========== SUMMARY ==========
        print(f"\n{'='*80}")
        print("✅ Q3 Branch Recording Complete! (Expanded Scope)")
        print(f"{'='*80}")
        print(f"Workspace: {workspace}")
        print(f"\nRecordings generated:")
        print(f"  - Iteration 2: {len(experts)} expert reviews")
        print(f"  - Iteration 2 Synthesis: 1 recording")
        print(f"  - Total: {len(experts) + 1} recordings")
        print(f"\n⚠️  Workflow STOPS after synthesis (scope expansion needs review)")
        print(f"{'='*80}\n")

        # Save workspace snapshot
        if mock_claude_sdk and mock_claude_sdk.mode == "record":
            snapshot_workspace(
                test_name="test_generate_question_branch_q3_expanded_scope",
                workspace=workspace,
                recordings_dir=recordings_base
            )
            print("  📸 Workspace snapshot saved\n")

        # Verify recordings were made
        if mock_claude_sdk:
            print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
            assert mock_claude_sdk.call_count >= len(experts) + 1, \
                f"Should have made at least {len(experts) + 1} LLM calls"

async def test_generate_question_branch_q4_user_confused(

        mock_claude_sdk,
        test_workspace
    ):
        """
        Q4: User confused, requests clarification.

        TEST CONTROL: None (user simulator uses "clarification" pattern)

        Stages:
        1. Load questions from iteration 1
        2. User asks clarifying questions back
        3. Iteration 2 with clarification requests
        4. Synthesis iteration 2
        5. STOPS (no artifact workflow)

        Expected recordings: 3 (2 iter2 + 1 synthesis)
        Time: ~35s

        Run with:
            EXPERT_FEEDBACK_TEST_MODE=record \\
            pytest tests/integration/test_generate_question_branches.py::TestGenerateQuestionBranches::test_generate_question_branch_q4_user_confused -v -s
        """
        # Ensure scripts directory is in sys.path (absolute path)
        import sys
        from pathlib import Path
        _scripts_path = str((Path(__file__).parent.parent.parent / "scripts").resolve())

        # Remove and re-add to ensure it's at position 0
        if _scripts_path in sys.path:
            sys.path.remove(_scripts_path)
        sys.path.insert(0, _scripts_path)

        # Import AFTER mock is set up and sys.path is configured
        from core.spawn_experts import spawn_all_experts
        from core.synthesize import synthesize_feedback
        from config import get_config
        from ui.progress_tracker import ProgressTracker
        from file_io.json_ops import load_json, save_json
        from fixtures.workspace_snapshot import has_snapshot, restore_workspace, snapshot_workspace

        workspace = test_workspace  # Using test_workspace to avoid fixture import issues
        config = get_config()
        state_path = workspace / "state.json"
        recordings_base = Path(__file__).parent.parent / "recordings"

        print(f"\n{'='*80}")
        print(f"🎬 Recording Q4 Branch - User Confused (Clarification)")
        print(f"{'='*80}")

        # ========== RESTORE PREDECESSOR WORKSPACE ==========
        predecessor = "test_generate_synthesis_iteration_1"

        print(f"\n🔹 Restoring workspace from: {predecessor}")
        if has_snapshot(predecessor, recordings_base):
            restore_workspace(predecessor, workspace, recordings_base)
            print(f"  ✅ Workspace restored from snapshot")
        else:
            pytest.fail(f"Prerequisite test not found: {predecessor}. Run it first.")

        # ========== LOAD QUESTIONS ==========
        print(f"\n🔹 Loading questions from iteration 1")
        questions_file = workspace / "iteration-1" / "questions.json"

        if not questions_file.exists():
            pytest.fail(f"Questions file not found: {questions_file}")

        questions_data = load_json(questions_file)
        questions = questions_data.get("questions", [])

        print(f"  ✅ Loaded {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q.get('question', 'N/A')[:60]}...")

        if len(questions) == 0:
            pytest.fail("No questions found in iteration 1")

        # ========== GENERATE CONFUSED/CLARIFICATION ANSWERS ==========
        print(f"\n🔹 Generating confused answers (clarification requests)")

        # Create qa_answers.json with clarification requests
        qa_answers = []
        for i, q in enumerate(questions):
            question_text = q.get("question", "")
            question_id = q.get("id", f"q-{i}")

            # Generate confused/clarification response
            if "numeric" in question_text.lower() or "range" in question_text.lower():
                answer = """I'm not sure I understand the question about numeric ranges. Could you clarify:

1. Are you asking about what range we WANT to support, or what the current code supports?
2. When you say "handle values outside the range" - do you mean return errors, use BigInt, or something else?
3. Is this about integer ranges specifically, or does it include floats/decimals?
4. Are there any performance implications I should consider?

I want to make sure I answer correctly, so more context would help."""

            elif "error" in question_text.lower() or "validation" in question_text.lower():
                answer = """I'm confused about the error handling question:

1. Are you asking what we SHOULD do, or what we're CURRENTLY doing?
2. By "structured error responses" - do you have a specific format in mind (JSON schema, error codes, etc.)?
3. Should we use standard HTTP status codes (400, 422, etc.) or custom codes?
4. Are you referring to client-facing errors only, or also internal error handling?

Sorry for the confusion - I want to give you the right information."""

            else:
                answer = f"""I'm not entirely clear on what you're asking. Could you rephrase or provide more context?

Specifically:
1. What problem are you trying to solve?
2. Are there any constraints I should be aware of?
3. Is this a technical question or more about business requirements?

I'd like to help, but I need a bit more clarity first. Thank you!"""

            qa_answers.append({
                "question_id": question_id,
                "question": question_text,
                "user_answer": answer,
                "answered_at": "2026-02-16T12:00:00Z"
            })

        # Save qa_answers.json
        qa_answers_file = workspace / "iteration-1" / "qa_answers.json"
        save_json({"answers": qa_answers}, qa_answers_file)

        print(f"  ✅ Generated {len(qa_answers)} clarification requests")
        print(f"  ⚠️  User needs clarification on all questions")
        print(f"  ✅ Saved to: {qa_answers_file}")

        # ========== ITERATION 2: Experts with Clarification Requests ==========
        print(f"\n🔹 ITERATION 2: Expert responses to clarification requests")
        print("-" * 60)

        experts = ["typescript", "python"]
        review_context = """Refine the simple-calculator API review based on user clarification requests.

The user is confused and has asked for clarification on the questions. Respond by:
1. Clarifying what you meant in your original questions
2. Providing additional context to help the user understand
3. Potentially rephrasing questions to be clearer
4. Identifying if there are knowledge gaps that need to be addressed

Focus on helping the user understand what information is needed for production readiness."""

        progress = ProgressTracker(2, workspace)

        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=2,
            state_path=state_path,
            config=config,
            progress=progress,
            qa_answers_path=str(qa_answers_file),
            correlation_id="q4-iteration-2-clarification-experts"
        )

        print(f"\n✅ Iteration 2 experts complete:")
        for expert_result in result.get("results", []):
            expert = expert_result.get("expert")
            status = expert_result.get("status")
            duration = expert_result.get("duration_seconds", 0)
            session_id = expert_result.get("session_id", "N/A")
            print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

        # Verify success
        assert result.get("success_count", 0) == len(experts), \
            f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

        # ========== SYNTHESIS ITERATION 2 ==========
        print(f"\n🔹 SYNTHESIS: Consolidate iteration 2 feedback")
        print("-" * 60)

        progress = ProgressTracker(2, workspace)

        synthesis_result = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress,
            correlation_id="q4-synthesis-iter2-clarification"
        )

        print(f"\n✅ Synthesis complete:")
        print(f"  - Status: {synthesis_result.get('status')}")
        print(f"  - Convergence: {synthesis_result.get('convergence_percent', 0)}%")
        print(f"  - Consensus: {synthesis_result.get('consensus_reached', False)}")
        print(f"  - Duration: {synthesis_result.get('duration_seconds', 0):.1f}s")
        print(f"  - Session: {synthesis_result.get('session_id', 'N/A')[:12]}...")

        # Verify synthesis produced expected outputs
        assert synthesis_result.get("status") == "complete", "Synthesis should complete successfully"

        # ========== SUMMARY ==========
        print(f"\n{'='*80}")
        print("✅ Q4 Branch Recording Complete! (Clarification)")
        print(f"{'='*80}")
        print(f"Workspace: {workspace}")
        print(f"\nRecordings generated:")
        print(f"  - Iteration 2: {len(experts)} expert clarifications")
        print(f"  - Iteration 2 Synthesis: 1 recording")
        print(f"  - Total: {len(experts) + 1} recordings")
        print(f"\n⚠️  Workflow STOPS after synthesis (needs further clarification)")
        print(f"{'='*80}\n")

        # Save workspace snapshot
        if mock_claude_sdk and mock_claude_sdk.mode == "record":
            snapshot_workspace(
                test_name="test_generate_question_branch_q4_user_confused",
                workspace=workspace,
                recordings_dir=recordings_base
            )
            print("  📸 Workspace snapshot saved\n")

        # Verify recordings were made
        if mock_claude_sdk:
            print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
            assert mock_claude_sdk.call_count >= len(experts) + 1, \
                f"Should have made at least {len(experts) + 1} LLM calls"

async def test_generate_question_branch_q5_mode_switch(

        mock_claude_sdk,
        test_workspace
    ):
        """
        Q5: User requests mode switch to CREATE in answers.

        TEST CONTROL: None (user simulator uses "mode_switch" pattern)

        Stages:
        1. Load questions from iteration 1
        2. User answers include CREATE mode requests
        3. Iteration 2 detects CREATE intent
        4. Synthesis iteration 2
        5. STOPS (no artifact workflow)

        Expected recordings: 3 (2 iter2 + 1 synthesis)
        Time: ~35s

        Run with:
            EXPERT_FEEDBACK_TEST_MODE=record \\
            pytest tests/integration/test_generate_question_branches.py::TestGenerateQuestionBranches::test_generate_question_branch_q5_mode_switch -v -s
        """
        # Ensure scripts directory is in sys.path (absolute path)
        import sys
        from pathlib import Path
        _scripts_path = str((Path(__file__).parent.parent.parent / "scripts").resolve())

        # Remove and re-add to ensure it's at position 0
        if _scripts_path in sys.path:
            sys.path.remove(_scripts_path)
        sys.path.insert(0, _scripts_path)

        # Import AFTER mock is set up and sys.path is configured
        from core.spawn_experts import spawn_all_experts
        from core.synthesize import synthesize_feedback
        from config import get_config
        from ui.progress_tracker import ProgressTracker
        from file_io.json_ops import load_json, save_json
        from fixtures.workspace_snapshot import has_snapshot, restore_workspace, snapshot_workspace

        workspace = test_workspace  # Using test_workspace to avoid fixture import issues
        config = get_config()
        state_path = workspace / "state.json"
        recordings_base = Path(__file__).parent.parent / "recordings"

        print(f"\n{'='*80}")
        print(f"🎬 Recording Q5 Branch - Mode Switch to CREATE")
        print(f"{'='*80}")

        # ========== RESTORE PREDECESSOR WORKSPACE ==========
        predecessor = "test_generate_synthesis_iteration_1"

        print(f"\n🔹 Restoring workspace from: {predecessor}")
        if has_snapshot(predecessor, recordings_base):
            restore_workspace(predecessor, workspace, recordings_base)
            print(f"  ✅ Workspace restored from snapshot")
        else:
            pytest.fail(f"Prerequisite test not found: {predecessor}. Run it first.")

        # ========== LOAD QUESTIONS ==========
        print(f"\n🔹 Loading questions from iteration 1")
        questions_file = workspace / "iteration-1" / "questions.json"

        if not questions_file.exists():
            pytest.fail(f"Questions file not found: {questions_file}")

        questions_data = load_json(questions_file)
        questions = questions_data.get("questions", [])

        print(f"  ✅ Loaded {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            print(f"     {i}. {q.get('question', 'N/A')[:60]}...")

        if len(questions) == 0:
            pytest.fail("No questions found in iteration 1")

        # ========== GENERATE MODE SWITCH ANSWERS ==========
        print(f"\n🔹 Generating answers with CREATE mode switch requests")

        # Create qa_answers.json with mode switch intent
        qa_answers = []
        for i, q in enumerate(questions):
            question_text = q.get("question", "")
            question_id = q.get("id", f"q-{i}")

            # Generate answer with CREATE mode switch intent
            if i == 0:  # First question - explicit mode switch
                answer = """Actually, I've been thinking about this, and I don't think we should just review the existing calculator.

**I want to CREATE a new calculator system from scratch instead.**

The current implementation has too many fundamental issues. Let's design a brand new calculator API with:
- Modern architecture (microservices)
- Proper validation and error handling from the start
- Comprehensive test coverage built in
- Security best practices
- Production-ready monitoring and observability

Can we switch to CREATE mode and design this properly from the ground up?"""

            elif i == 1:  # Second question - reinforce CREATE intent
                answer = """As I mentioned, I'd prefer to CREATE a new solution rather than patch the existing one.

For the new design:
- Use TypeScript with strict typing throughout
- Implement a plugin architecture for operations
- Add rate limiting and authentication
- Use OpenAPI/Swagger for API documentation
- Deploy with Docker and Kubernetes

Let's focus on greenfield design rather than reviewing legacy code."""

            else:  # Remaining questions - also mention CREATE preference
                answer = """This confirms my thinking that we should CREATE a new system.

The existing code has too many gaps to review effectively. Let's design from scratch with all these requirements in mind from day one.

Switch to CREATE mode please."""

            qa_answers.append({
                "question_id": question_id,
                "question": question_text,
                "user_answer": answer,
                "answered_at": "2026-02-16T12:00:00Z"
            })

        # Save qa_answers.json
        qa_answers_file = workspace / "iteration-1" / "qa_answers.json"
        save_json({"answers": qa_answers}, qa_answers_file)

        print(f"  ✅ Generated {len(qa_answers)} answers with CREATE mode intent")
        print(f"  ⚠️  User requesting switch to CREATE mode (greenfield design)")
        print(f"  ✅ Saved to: {qa_answers_file}")

        # ========== ITERATION 2: Experts Detect Mode Switch ==========
        print(f"\n🔹 ITERATION 2: Experts detect CREATE mode switch request")
        print("-" * 60)

        experts = ["typescript", "python"]
        review_context = """Refine the simple-calculator API review based on user answers.

IMPORTANT: The user has requested a MODE SWITCH to CREATE mode. They want to design a NEW system from scratch rather than review the existing code.

Respond by:
1. Acknowledging the mode switch request
2. Identifying whether CREATE mode is appropriate given the situation
3. Outlining what a CREATE mode approach would entail
4. Noting any risks or considerations for switching modes

Be prepared to pivot from REVIEW mode to CREATE mode if appropriate."""

        progress = ProgressTracker(2, workspace)

        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=2,
            state_path=state_path,
            config=config,
            progress=progress,
            qa_answers_path=str(qa_answers_file),
            correlation_id="q5-iteration-2-mode-switch-experts"
        )

        print(f"\n✅ Iteration 2 experts complete:")
        for expert_result in result.get("results", []):
            expert = expert_result.get("expert")
            status = expert_result.get("status")
            duration = expert_result.get("duration_seconds", 0)
            session_id = expert_result.get("session_id", "N/A")
            print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

        # Verify success
        assert result.get("success_count", 0) == len(experts), \
            f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

        # ========== SYNTHESIS ITERATION 2 ==========
        print(f"\n🔹 SYNTHESIS: Consolidate iteration 2 feedback and mode switch")
        print("-" * 60)

        progress = ProgressTracker(2, workspace)

        synthesis_result = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress,
            correlation_id="q5-synthesis-iter2-mode-switch"
        )

        print(f"\n✅ Synthesis complete:")
        print(f"  - Status: {synthesis_result.get('status')}")
        print(f"  - Convergence: {synthesis_result.get('convergence_percent', 0)}%")
        print(f"  - Consensus: {synthesis_result.get('consensus_reached', False)}")
        print(f"  - Duration: {synthesis_result.get('duration_seconds', 0):.1f}s")
        print(f"  - Session: {synthesis_result.get('session_id', 'N/A')[:12]}...")

        # Verify synthesis produced expected outputs
        assert synthesis_result.get("status") == "complete", "Synthesis should complete successfully"

        # ========== SUMMARY ==========
        print(f"\n{'='*80}")
        print("✅ Q5 Branch Recording Complete! (Mode Switch to CREATE)")
        print(f"{'='*80}")
        print(f"Workspace: {workspace}")
        print(f"\nRecordings generated:")
        print(f"  - Iteration 2: {len(experts)} expert reviews (mode switch)")
        print(f"  - Iteration 2 Synthesis: 1 recording (mode switch detected)")
        print(f"  - Total: {len(experts) + 1} recordings")
        print(f"\n⚠️  Workflow STOPS after synthesis (mode switch to CREATE)")
        print(f"{'='*80}\n")

        # Save workspace snapshot
        if mock_claude_sdk and mock_claude_sdk.mode == "record":
            snapshot_workspace(
                test_name="test_generate_question_branch_q5_mode_switch",
                workspace=workspace,
                recordings_dir=recordings_base
            )
            print("  📸 Workspace snapshot saved\n")

        # Verify recordings were made
        if mock_claude_sdk:
            print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
            assert mock_claude_sdk.call_count >= len(experts) + 1, \
                f"Should have made at least {len(experts) + 1} LLM calls"
