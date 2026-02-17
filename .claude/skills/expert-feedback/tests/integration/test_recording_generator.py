"""
Generate multi-turn conversation recordings using pytest infrastructure.

This test generates recordings for 2-iteration workflows with session resumption.
Unlike standalone scripts, this uses the proven MockClaudeAgentSDK approach from conftest.py.

Usage:
    # Generate recordings (makes real API calls)
    EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_recording_generator.py -v -s

    # Test replay (fast, no API calls)
    EXPERT_FEEDBACK_TEST_MODE=replay pytest tests/integration/test_recording_generator.py -v
"""
import pytest
import sys
import json
from pathlib import Path

# Add scripts directory to path
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))


async def simulate_user_qa_with_llm(
    questions: list,
    topic: str,
    mock_claude_sdk
) -> dict:
    """
    Use LLM to generate realistic user answers to questions.

    This runs within pytest and uses the MockClaudeAgentSDK,
    so it works in both record and replay modes.

    Args:
        questions: List of question dicts from synthesis
        topic: The topic being reviewed
        mock_claude_sdk: The pytest fixture (for mode detection)

    Returns:
        Q&A answers dict matching expected format
    """
    # Import AFTER mock is set up
    from claude_agent_sdk import query, ClaudeAgentOptions

    print(f"\n🤖 Simulating user Q&A responses with LLM...")
    print(f"   Mode: {mock_claude_sdk.mode if mock_claude_sdk else 'record'}")

    # Format questions for LLM
    formatted_questions = "\n\n".join([
        f"**Question {i+1}** (asked by {q.get('asked_by', ['synthesis'])[0]}):\n{q['question']}"
        for i, q in enumerate(questions)
    ])

    # Use string prompt (not array!)
    prompt = f"""You are a product manager answering questions about: {topic}

The expert panel has reviewed your project and has these questions:

{formatted_questions}

Provide realistic, actionable answers that:
1. Are specific and show domain knowledge
2. Include occasional clarifications or constraints
3. Show some evolution in thinking
4. Maintain consistency with the topic scope

Output ONLY a JSON object with this structure:
{{
  "answers": [
    {{
      "question": "original question text",
      "answer": "your detailed answer",
      "context": "any additional context"
    }}
  ]
}}"""

    print(f"  🚀 Sending prompt to LLM ({len(prompt)} chars)...")

    try:
        # Call Claude Agent SDK to generate answers
        options = ClaudeAgentOptions(allowed_tools=[])
        response_text = ""

        async for event in query(prompt=prompt, options=options):
            # Extract text from assistant messages
            if hasattr(event, 'content'):
                for block in event.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
                        print(".", end="", flush=True)

        print(f"\n  📥 Got response ({len(response_text)} chars)")

        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            # Find JSON object boundaries
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]

        qa_answers = json.loads(json_text)
        print(f"  ✅ Generated {len(qa_answers.get('answers', []))} answers")

        return qa_answers

    except Exception as e:
        print(f"  ⚠️  Error generating answers: {e}")
        # Fallback: generate simple answers
        return {
            "answers": [
                {
                    "question": q["question"],
                    "answer": f"We'll adopt a phased approach for this. First, we'll {q['question'].split()[:3]} then iterate based on feedback.",
                    "context": "Product management decision"
                }
                for q in questions
            ]
        }


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_two_iteration_workflow(
    mock_claude_sdk,
    initialized_workspace
):
    """
    Generate recordings for complete 2-iteration workflow.

    This test runs the full workflow end-to-end:
    - Iteration 1: Initial expert reviews (2 experts)
    - Iteration 1: Synthesis with questions
    - User Q&A simulation (LLM-powered)
    - Iteration 2: Expert refinements with session resumption
    - Iteration 2: Synthesis with session resumption

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_recording_generator.py::test_generate_two_iteration_workflow -v -s

    This generates ~6 recordings (2 experts x 2 iterations + 2 syntheses).
    """
    # Import AFTER mock is set up
    from core.spawn_experts import spawn_all_experts
    from core.synthesize import synthesize_feedback
    from state.manager import StateManager
    from file_io.json_ops import save_json
    from config import get_config
    from ui.progress_tracker import ProgressTracker
    
    workspace = initialized_workspace
    config = get_config()
    state_path = workspace / "state.json"

    experts = ["typescript", "python"]
    topic = "Review API design for SDK client library"

    print(f"\n{'='*80}")
    print(f"🎬 Recording 2-Iteration Workflow")
    print(f"{'='*80}")
    print(f"Workspace: {workspace}")
    print(f"Experts: {', '.join(experts)}")
    print(f"Topic: {topic}")
    print(f"Mode: {mock_claude_sdk.mode if mock_claude_sdk else 'record'}")
    print(f"{'='*80}\n")

    # ========== ITERATION 1: Initial Reviews ==========
    print("\n🔹 ITERATION 1: Initial Expert Reviews")
    print("-" * 60)

    progress_1 = ProgressTracker(1, workspace)
    result_1 = await spawn_all_experts(
        experts=experts,
        topic=topic,
        workspace=str(workspace),
        iteration=1,
        state_path=state_path,
        config=config,
        progress=progress_1,
        correlation_id="recording-iter1-experts"
    )

    print(f"\n✅ Iteration 1 experts complete:")
    for expert_result in result_1.get("results", []):
        expert = expert_result.get("expert")
        status = expert_result.get("status")
        duration = expert_result.get("duration_seconds", 0)
        print(f"  - {expert}: {status} ({duration:.1f}s)")

    # ========== ITERATION 1: Synthesis ==========
    print("\n🔹 ITERATION 1: Synthesis")
    print("-" * 60)

    synthesis_1 = await synthesize_feedback(
        workspace=workspace,
        iteration=1,
        config=config,
        progress=progress_1,
        correlation_id="recording-iter1-synthesis"
    )

    convergence_1 = synthesis_1.get("convergence_percent", 0)
    questions = synthesis_1.get("questions", [])

    print(f"\n✅ Iteration 1 synthesis complete:")
    print(f"  - Convergence: {convergence_1}%")
    print(f"  - Questions: {len(questions)}")

    # ========== USER Q&A (LLM Simulated) ==========
    print("\n🔹 USER Q&A SIMULATION")
    print("-" * 60)

    if questions:
        qa_answers = await simulate_user_qa_with_llm(questions, topic, mock_claude_sdk)

        # Save Q&A answers for iteration 2
        qa_path = workspace / "qa-answers.json"
        save_json(qa_answers, qa_path)
        print(f"\n✅ Q&A answers saved to {qa_path}")
    else:
        print("  ⚠️  No questions generated, skipping Q&A")
        qa_answers = {"answers": []}

    # ========== ITERATION 2: Refinement ==========
    print("\n🔹 ITERATION 2: Expert Refinements (Session Resumption)")
    print("-" * 60)

    # Increment iteration
    state_manager = StateManager(workspace)
    state_manager.increment_iteration()

    progress_2 = ProgressTracker(2, workspace)

    result_2 = await spawn_all_experts(
        experts=experts,
        topic=topic,
        workspace=str(workspace),
        iteration=2,
        state_path=state_path,
        config=config,
        progress=progress_2,
        correlation_id="recording-iter2-experts"
    )

    print(f"\n✅ Iteration 2 experts complete (sessions resumed):")
    for expert_result in result_2.get("results", []):
        expert = expert_result.get("expert")
        status = expert_result.get("status")
        duration = expert_result.get("duration_seconds", 0)
        session = expert_result.get("session_id", "N/A")
        print(f"  - {expert}: {status} ({duration:.1f}s, session: {session[:12]}...)")

    # ========== ITERATION 2: Synthesis ==========
    print("\n🔹 ITERATION 2: Synthesis (Session Resumption)")
    print("-" * 60)

    synthesis_2 = await synthesize_feedback(
        workspace=workspace,
        iteration=2,
        config=config,
        progress=progress_2,
        correlation_id="recording-iter2-synthesis"
    )

    convergence_2 = synthesis_2.get("convergence_percent", 0)
    consensus = synthesis_2.get("consensus_reached", False)

    print(f"\n✅ Iteration 2 synthesis complete:")
    print(f"  - Convergence: {convergence_2}% (was {convergence_1}%)")
    print(f"  - Consensus: {consensus}")
    print(f"  - Trend: {'📈 Improving' if convergence_2 > convergence_1 else '📉 Declining'}")

    # ========== SUMMARY ==========
    print(f"\n{'='*80}")
    print("🎉 Recording Generation Complete!")
    print(f"{'='*80}")
    print(f"Workspace: {workspace}")
    print(f"\nRecordings generated:")
    print(f"  - Iteration 1: {len(experts)} expert reviews + 1 synthesis")
    print(f"  - Iteration 2: {len(experts)} expert refinements + 1 synthesis")
    print(f"  - Q&A simulation: 1 recording")
    print(f"  - Total: {(len(experts) * 2) + 3} recordings")
    print(f"\nConvergence: {convergence_1}% → {convergence_2}%")
    print(f"Consensus: {consensus}")
    print(f"{'='*80}\n")

    # Verify convergence improved (optional assertion)
    # NOTE: This might not always be true in real scenarios, so we just log it
    if convergence_2 > convergence_1:
        print("✅ Convergence improved as expected")
    else:
        print(f"⚠️  Convergence did not improve ({convergence_1}% → {convergence_2}%)")

    # Verify at least some recordings were made
    if mock_claude_sdk:
        print(f"\n📊 Total LLM calls made: {mock_claude_sdk.call_count}")
        assert mock_claude_sdk.call_count > 0, "Should have made LLM calls"


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_iteration_1_only(
    mock_claude_sdk,
    initialized_workspace
):
    """
    Generate recordings for iteration 1 only (simpler, faster).

    This generates just the initial expert reviews and synthesis,
    useful for testing iteration 1 workflows.

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_recording_generator.py::test_generate_iteration_1_only -v -s
    """
    # Import AFTER mock is set up
    from core.spawn_experts import spawn_all_experts
    from core.synthesize import synthesize_feedback
    from config import get_config
    from ui.progress_tracker import ProgressTracker

    workspace = initialized_workspace
    config = get_config()
    state_path = workspace / "state.json"

    experts = ["typescript", "python"]
    topic = "Review API design for SDK client library"

    print(f"\n{'='*80}")
    print(f"🎬 Recording Iteration 1 Workflow")
    print(f"{'='*80}")
    print(f"Workspace: {workspace}")
    print(f"Experts: {', '.join(experts)}")
    print(f"Topic: {topic}")
    print(f"{'='*80}\n")

    # ========== ITERATION 1: Initial Reviews ==========
    print("\n🔹 ITERATION 1: Initial Expert Reviews")
    print("-" * 60)

    progress = ProgressTracker(1, workspace)

    result = await spawn_all_experts(
        experts=experts,
        topic=topic,
        workspace=str(workspace),
        iteration=1,
        state_path=state_path,
        config=config,
        progress=progress,
        correlation_id="recording-iter1-only-experts"
    )

    print(f"\n✅ Iteration 1 experts complete:")
    for expert_result in result.get("results", []):
        expert = expert_result.get("expert")
        status = expert_result.get("status")
        duration = expert_result.get("duration_seconds", 0)
        print(f"  - {expert}: {status} ({duration:.1f}s)")

    # ========== ITERATION 1: Synthesis ==========
    print("\n🔹 ITERATION 1: Synthesis")
    print("-" * 60)

    synthesis = await synthesize_feedback(
        workspace=workspace,
        iteration=1,
        config=config,
        progress=progress,
        correlation_id="recording-iter1-only-synthesis"
    )

    convergence = synthesis.get("convergence_percent", 0)
    questions = synthesis.get("questions", [])

    print(f"\n✅ Iteration 1 synthesis complete:")
    print(f"  - Convergence: {convergence}%")
    print(f"  - Questions: {len(questions)}")

    print(f"\n{'='*80}")
    print("🎉 Recording Generation Complete!")
    print(f"{'='*80}\n")

    # Verify at least some recordings were made
    if mock_claude_sdk:
        print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
        assert mock_claude_sdk.call_count > 0, "Should have made LLM calls"
