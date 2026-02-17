#!/usr/bin/env python3
"""
Deduplicate questions by filtering out already-answered questions from previous iterations.

This fixes the bug where consolidation re-asks questions that users already answered.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from difflib import SequenceMatcher


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def find_answered_questions(workspace: Path, current_iteration: int) -> Dict[str, Dict[str, Any]]:
    """Find all previously answered questions from all iterations.

    Returns:
        Dict mapping question_id -> {question, answer, iteration}
    """
    answered = {}

    # Check all previous iterations
    for iteration in range(1, current_iteration):
        qa_file = workspace / f"iteration-{iteration}" / "qa-answers.json"
        if qa_file.exists():
            qa_data = load_json(qa_file)
            for answer in qa_data.get("answers", []):
                answered[answer["question_id"]] = {
                    "question": answer["question"],
                    "answer": answer["answer"],
                    "iteration": iteration
                }

    return answered


def fuzzy_similarity(text1: str, text2: str) -> float:
    """Calculate fuzzy similarity between two texts using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def is_duplicate_question(
    new_question: Dict[str, Any],
    answered_questions: Dict[str, Dict[str, Any]],
    similarity_threshold: float = 0.85
) -> tuple[bool, str | None]:
    """Check if a question was already answered.

    Returns:
        (is_duplicate, duplicate_id)
    """
    new_text = new_question["question"].lower().strip()

    # First check: exact question_id match
    if new_question["id"] in answered_questions:
        return True, new_question["id"]

    # Second check: fuzzy similarity
    for qid, answered in answered_questions.items():
        answered_text = answered["question"].lower().strip()

        # Quick exact match check
        if new_text == answered_text:
            return True, qid

        # Fuzzy similarity check
        similarity = fuzzy_similarity(new_text, answered_text)
        if similarity >= similarity_threshold:
            return True, qid

    return False, None


def deduplicate_questions(
    questions_file: Path,
    workspace: Path,
    current_iteration: int,
    similarity_threshold: float = 0.85,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Deduplicate questions by removing already-answered ones.

    Args:
        questions_file: Path to questions.json to deduplicate
        workspace: Workspace root directory
        current_iteration: Current iteration number
        similarity_threshold: Semantic similarity threshold (0.85 = 85% similar)
        dry_run: If True, don't modify files, just report

    Returns:
        Statistics about deduplication
    """
    # Load questions
    questions_data = load_json(questions_file)
    questions = questions_data.get("questions", [])

    # Find all previously answered questions
    answered = find_answered_questions(workspace, current_iteration)

    if not answered:
        print(f"ℹ️  No previously answered questions found")
        return {
            "total_questions": len(questions),
            "duplicates_removed": 0,
            "unique_questions": len(questions)
        }

    print(f"ℹ️  Found {len(answered)} previously answered questions")

    # Filter out duplicates using fuzzy matching
    unique_questions = []
    duplicates = []

    for question in questions:
        is_dup, dup_id = is_duplicate_question(question, answered, similarity_threshold)

        if is_dup:
            duplicates.append({
                "question": question["question"],
                "duplicate_of": dup_id,
                "answered_iteration": answered[dup_id]["iteration"],
                "answer": answered[dup_id]["answer"]
            })
            print(f"🔍 Duplicate found: '{question['question'][:80]}...'")
            print(f"   Already answered in iteration {answered[dup_id]['iteration']}: '{answered[dup_id]['answer'][:80]}...'")
        else:
            unique_questions.append(question)

    # Save deduplicated questions
    if not dry_run and duplicates:
        questions_data["questions"] = unique_questions
        save_json(questions_file, questions_data)
        print(f"✅ Saved {len(unique_questions)} unique questions to {questions_file}")

    # Save report
    report = {
        "total_questions": len(questions),
        "duplicates_removed": len(duplicates),
        "unique_questions": len(unique_questions),
        "duplicates": duplicates
    }

    if not dry_run:
        report_file = questions_file.parent / "deduplication-report.json"
        save_json(report_file, report)
        print(f"📊 Saved deduplication report to {report_file}")

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Deduplicate questions by filtering out already-answered ones"
    )
    parser.add_argument(
        "--questions-file",
        type=Path,
        required=True,
        help="Path to questions.json file to deduplicate"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Workspace root directory"
    )
    parser.add_argument(
        "--iteration",
        type=int,
        required=True,
        help="Current iteration number"
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.85,
        help="Semantic similarity threshold (default: 0.85)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify files, just report what would be done"
    )

    args = parser.parse_args()

    if not args.questions_file.exists():
        print(f"❌ Error: Questions file not found: {args.questions_file}")
        sys.exit(1)

    if not args.workspace.exists():
        print(f"❌ Error: Workspace not found: {args.workspace}")
        sys.exit(1)

    print(f"🔍 Deduplicating questions for iteration {args.iteration}")
    print(f"   Questions file: {args.questions_file}")
    print(f"   Workspace: {args.workspace}")
    print(f"   Similarity threshold: {args.similarity_threshold}")

    if args.dry_run:
        print("   🏃 DRY RUN - No files will be modified")

    print()

    stats = deduplicate_questions(
        questions_file=args.questions_file,
        workspace=args.workspace,
        current_iteration=args.iteration,
        similarity_threshold=args.similarity_threshold,
        dry_run=args.dry_run
    )

    print()
    print("📊 Summary:")
    print(f"   Total questions: {stats['total_questions']}")
    print(f"   Duplicates removed: {stats['duplicates_removed']}")
    print(f"   Unique questions: {stats['unique_questions']}")
    print(f"   Reduction: {stats['duplicates_removed'] / stats['total_questions'] * 100:.1f}%")


if __name__ == "__main__":
    main()
