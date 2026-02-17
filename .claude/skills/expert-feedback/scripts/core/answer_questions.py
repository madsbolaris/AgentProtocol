#!/usr/bin/env python3
"""
CLI tool for answering deferred questions from autonomous execution.

This tool displays pending questions to the user and collects their answers,
allowing the autonomous execution agent to refine the implementation based on
the user's input.

Usage:
    python3 answer_questions.py --workspace /path/to/workspace
    python3 answer_questions.py --workspace /path/to/workspace --batch answers.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from questions.deferred_questions_handler import (
    load_pending_questions,
    save_user_answers,
    load_and_process_answers
)


def display_question(question: Dict[str, Any], index: int, total: int) -> None:
    """
    Display a question to the user in a formatted way.

    Args:
        question: Question dictionary
        index: Current question index (1-based)
        total: Total number of questions
    """
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"Question {index}/{total}", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    print(f"ID: {question['id']}", file=sys.stderr)
    print(f"\n{question['question']}\n", file=sys.stderr)

    if question.get('context'):
        print(f"Context:", file=sys.stderr)
        print(f"  {question['context']}\n", file=sys.stderr)

    if question.get('agent_assumption'):
        print(f"Agent's Current Assumption:", file=sys.stderr)
        print(f"  {question['agent_assumption']}\n", file=sys.stderr)

    classification = question.get('classification', 'optional')
    priority = question.get('priority', 'medium')
    print(f"Classification: {classification} | Priority: {priority}", file=sys.stderr)

    asked_at = question.get('asked_at')
    if asked_at:
        print(f"Asked at: {asked_at}", file=sys.stderr)


def get_user_answer(question: Dict[str, Any]) -> str:
    """
    Prompt user for an answer to a question.

    Args:
        question: Question dictionary

    Returns:
        User's answer string
    """
    print(f"\n{'─'*70}", file=sys.stderr)
    print("Your Answer:", file=sys.stderr)
    print("(Type your answer and press Enter. Type 'skip' to skip this question)", file=sys.stderr)
    print(f"{'─'*70}", file=sys.stderr)

    answer = input("> ").strip()

    if answer.lower() == 'skip':
        print("Question skipped.\n", file=sys.stderr)
        return None

    if not answer:
        print("Empty answer. Question skipped.\n", file=sys.stderr)
        return None

    return answer


def interactive_mode(workspace: Path) -> int:
    """
    Run interactive question-answering session.

    Args:
        workspace: Workspace path

    Returns:
        Number of questions answered
    """
    # Load pending questions
    pending = load_pending_questions(workspace)

    if not pending:
        print("\n✅ No pending questions to answer.", file=sys.stderr)
        return 0

    print(f"\n📝 Found {len(pending)} pending question(s) from autonomous execution.\n", file=sys.stderr)

    answers = []

    for i, question in enumerate(pending, start=1):
        display_question(question, i, len(pending))

        answer = get_user_answer(question)

        if answer:
            answers.append({
                "question_id": question["id"],
                "question": question["question"],
                "answer": answer,
                "agent_assumption": question.get("agent_assumption"),
                "context": question.get("context"),
                "answered_at": datetime.utcnow().isoformat()
            })
            print(f"✅ Answer recorded: {answer[:50]}...", file=sys.stderr)

    if not answers:
        print("\n⚠️  No answers provided. Execution will not be refined.", file=sys.stderr)
        return 0

    # Save answers
    print(f"\n💾 Saving {len(answers)} answer(s)...", file=sys.stderr)
    save_user_answers(answers, workspace)

    print(f"\n✅ Answers saved! The autonomous execution agent will refine the implementation on next run.", file=sys.stderr)
    print(f"\nTo resume execution:", file=sys.stderr)
    print(f"  python3 {Path(__file__).parent / 'execute_autonomous.py'} --workspace {workspace} --resume", file=sys.stderr)

    return len(answers)


def batch_mode(workspace: Path, answers_file: Path) -> int:
    """
    Load answers from a JSON file.

    Args:
        workspace: Workspace path
        answers_file: Path to JSON file with answers

    Returns:
        Number of answers processed

    Expected JSON format:
    {
        "answers": [
            {
                "question_id": "q-exec-1",
                "answer": "Use PostgreSQL for the database"
            },
            {
                "question_id": "q-exec-2",
                "answer": "Set rate limit to 100 requests per minute"
            }
        ]
    }
    """
    if not answers_file.exists():
        print(f"❌ Answers file not found: {answers_file}", file=sys.stderr)
        return 0

    try:
        data = json.loads(answers_file.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in answers file: {e}", file=sys.stderr)
        return 0

    batch_answers = data.get("answers", [])
    if not batch_answers:
        print("⚠️  No answers found in batch file.", file=sys.stderr)
        return 0

    # Load pending questions to validate IDs
    pending = load_pending_questions(workspace)
    pending_ids = {q["id"] for q in pending}

    valid_answers = []
    for answer_item in batch_answers:
        question_id = answer_item.get("question_id")
        answer = answer_item.get("answer")

        if not question_id or not answer:
            print(f"⚠️  Skipping invalid answer item: {answer_item}", file=sys.stderr)
            continue

        if question_id not in pending_ids:
            print(f"⚠️  Question ID not found in pending questions: {question_id}", file=sys.stderr)
            continue

        # Find the original question
        question = next((q for q in pending if q["id"] == question_id), None)

        valid_answers.append({
            "question_id": question_id,
            "question": question["question"] if question else "Unknown",
            "answer": answer,
            "agent_assumption": question.get("agent_assumption") if question else None,
            "context": question.get("context") if question else None,
            "answered_at": datetime.utcnow().isoformat()
        })

    if not valid_answers:
        print("❌ No valid answers to process.", file=sys.stderr)
        return 0

    # Save answers
    print(f"💾 Saving {len(valid_answers)} answer(s) from batch file...", file=sys.stderr)
    save_user_answers(valid_answers, workspace)

    print(f"\n✅ Batch answers saved!", file=sys.stderr)
    print(f"   Answers processed: {len(valid_answers)}/{len(batch_answers)}", file=sys.stderr)

    return len(valid_answers)


def list_mode(workspace: Path) -> None:
    """
    List all pending questions without answering.

    Args:
        workspace: Workspace path
    """
    pending = load_pending_questions(workspace)

    if not pending:
        print("\n✅ No pending questions.", file=sys.stderr)
        return

    print(f"\n📋 Pending Questions ({len(pending)})", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    for i, question in enumerate(pending, start=1):
        print(f"{i}. [{question['id']}] {question['question']}", file=sys.stderr)
        if question.get('agent_assumption'):
            print(f"   Assumption: {question['agent_assumption']}", file=sys.stderr)
        print(f"   Classification: {question.get('classification', 'optional')} | Priority: {question.get('priority', 'medium')}", file=sys.stderr)
        print("", file=sys.stderr)


def export_template(workspace: Path, output_file: Path) -> None:
    """
    Export a template JSON file for batch answering.

    Args:
        workspace: Workspace path
        output_file: Path to write template file
    """
    pending = load_pending_questions(workspace)

    if not pending:
        print("\n✅ No pending questions to export.", file=sys.stderr)
        return

    template = {
        "answers": [
            {
                "question_id": q["id"],
                "question": q["question"],
                "answer": "YOUR_ANSWER_HERE",
                "notes": f"Classification: {q.get('classification', 'optional')}, Agent assumption: {q.get('agent_assumption', 'None')}"
            }
            for q in pending
        ]
    }

    output_file.write_text(json.dumps(template, indent=2))
    print(f"\n✅ Template exported to: {output_file}", file=sys.stderr)
    print(f"   Fill in the answers and use: --batch {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Answer deferred questions from autonomous execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python3 answer_questions.py --workspace /path/to/workspace

  # List pending questions
  python3 answer_questions.py --workspace /path/to/workspace --list

  # Export template for batch answering
  python3 answer_questions.py --workspace /path/to/workspace --export-template answers-template.json

  # Batch mode (provide answers from JSON file)
  python3 answer_questions.py --workspace /path/to/workspace --batch answers.json

Batch JSON format:
  {
    "answers": [
      {"question_id": "q-exec-1", "answer": "Your answer here"},
      {"question_id": "q-exec-2", "answer": "Another answer"}
    ]
  }
        """
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Workspace path"
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--batch",
        type=Path,
        help="Batch mode: load answers from JSON file"
    )
    mode_group.add_argument(
        "--list",
        action="store_true",
        help="List pending questions without answering"
    )
    mode_group.add_argument(
        "--export-template",
        type=Path,
        help="Export a template JSON file for batch answering"
    )

    args = parser.parse_args()

    # Validate workspace
    if not args.workspace.exists():
        print(f"❌ Workspace not found: {args.workspace}", file=sys.stderr)
        sys.exit(1)

    # Run appropriate mode
    if args.list:
        list_mode(args.workspace)
    elif args.export_template:
        export_template(args.workspace, args.export_template)
    elif args.batch:
        answered = batch_mode(args.workspace, args.batch)
        sys.exit(0 if answered > 0 else 1)
    else:
        # Interactive mode (default)
        answered = interactive_mode(args.workspace)
        sys.exit(0 if answered > 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
