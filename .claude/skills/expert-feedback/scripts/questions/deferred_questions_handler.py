#!/usr/bin/env python3
"""
Deferred questions handler for autonomous execution.

Manages the lifecycle of deferred questions:
- Saving questions when agent asks them
- Loading pending questions for user review
- Recording user answers
- Marking questions as answered
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


def get_questions_file(workspace: Path) -> Path:
    """Get path to deferred questions file."""
    execution_dir = workspace / "execution"
    execution_dir.mkdir(parents=True, exist_ok=True)
    return execution_dir / "deferred-questions.json"


def get_answers_file(workspace: Path) -> Path:
    """Get path to deferred answers file."""
    execution_dir = workspace / "execution"
    execution_dir.mkdir(parents=True, exist_ok=True)
    return execution_dir / "deferred-answers.json"


def load_questions_data(workspace: Path) -> Dict[str, Any]:
    """
    Load existing questions data or create empty structure.

    Returns:
        {
            "questions": [...],
            "metadata": {
                "total_questions": 0,
                "pending_count": 0,
                "answered_count": 0,
                "last_updated": "..."
            }
        }
    """
    questions_file = get_questions_file(workspace)

    if not questions_file.exists():
        return {
            "questions": [],
            "metadata": {
                "total_questions": 0,
                "pending_count": 0,
                "answered_count": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
        }

    try:
        with open(questions_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️  Error loading questions file: {e}", file=sys.stderr)
        return {
            "questions": [],
            "metadata": {
                "total_questions": 0,
                "pending_count": 0,
                "answered_count": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
        }


def save_questions_data(workspace: Path, data: Dict[str, Any]):
    """Save questions data to file."""
    questions_file = get_questions_file(workspace)

    # Update metadata
    data["metadata"]["last_updated"] = datetime.utcnow().isoformat()

    with open(questions_file, 'w') as f:
        json.dump(data, f, indent=2)


def save_deferred_question(
    question: Dict[str, Any],
    workspace: Path,
    iteration: int = None,
    agent_id: str = "executor"
) -> str:
    """
    Save a deferred question.

    Args:
        question: Question dictionary
        workspace: Workspace path
        iteration: Current execution iteration
        agent_id: ID of agent asking the question

    Returns:
        Question ID
    """
    data = load_questions_data(workspace)

    # Generate question ID
    question_id = f"q-{agent_id}-{len(data['questions']) + 1}"

    # Add metadata
    question_record = {
        "id": question_id,
        "question": question.get("question", ""),
        "context": question.get("context", ""),
        "classification": question.get("classification", "optional"),
        "priority": question.get("priority", "low"),
        "asked_at": datetime.utcnow().isoformat(),
        "agent_id": agent_id,
        "iteration": iteration,
        "agent_assumption": question.get("agent_assumption") or question.get("suggested_default"),
        "status": "pending",
        "answer": None,
        "answered_at": None
    }

    data["questions"].append(question_record)

    # Update metadata
    data["metadata"]["total_questions"] = len(data["questions"])
    data["metadata"]["pending_count"] = sum(
        1 for q in data["questions"] if q["status"] == "pending"
    )
    data["metadata"]["answered_count"] = sum(
        1 for q in data["questions"] if q["status"] == "answered"
    )

    save_questions_data(workspace, data)

    print(f"📝 Deferred question {question_id}: {question_record['question'][:60]}...", file=sys.stderr)

    return question_id


def load_pending_questions(workspace: Path) -> List[Dict[str, Any]]:
    """
    Load all pending (unanswered) questions.

    Returns:
        List of question dictionaries with status="pending"
    """
    data = load_questions_data(workspace)
    return [q for q in data["questions"] if q["status"] == "pending"]


def get_unanswered_questions(workspace: Path) -> List[Dict[str, Any]]:
    """Alias for load_pending_questions."""
    return load_pending_questions(workspace)


def get_answered_questions(workspace: Path) -> List[Dict[str, Any]]:
    """
    Load all answered questions.

    Returns:
        List of question dictionaries with status="answered"
    """
    data = load_questions_data(workspace)
    return [q for q in data["questions"] if q["status"] == "answered"]


def save_user_answers(answers: List[Dict[str, Any]], workspace: Path):
    """
    Save user answers to deferred-answers.json.

    Args:
        answers: List of answer dictionaries
            [
                {
                    "question_id": "q-exec-1",
                    "answer": "Use PostgreSQL",
                    "answered_at": "2026-02-16T08:00:00Z"
                }
            ]
        workspace: Workspace path
    """
    answers_file = get_answers_file(workspace)

    # Load existing answers
    if answers_file.exists():
        with open(answers_file, 'r') as f:
            existing_answers = json.load(f)
    else:
        existing_answers = {
            "answers": [],
            "metadata": {
                "total_answers": 0,
                "last_updated": None
            }
        }

    # Add new answers
    for answer in answers:
        # Ensure timestamp
        if "answered_at" not in answer:
            answer["answered_at"] = datetime.utcnow().isoformat()

        existing_answers["answers"].append(answer)

    # Update metadata
    existing_answers["metadata"]["total_answers"] = len(existing_answers["answers"])
    existing_answers["metadata"]["last_updated"] = datetime.utcnow().isoformat()

    # Save
    with open(answers_file, 'w') as f:
        json.dump(existing_answers, f, indent=2)

    print(f"✅ Saved {len(answers)} user answer(s)", file=sys.stderr)


def mark_questions_answered(question_ids: List[str], workspace: Path, answers_dict: Dict[str, str] = None):
    """
    Mark questions as answered in deferred-questions.json.

    Args:
        question_ids: List of question IDs to mark as answered
        workspace: Workspace path
        answers_dict: Optional dict mapping question_id -> answer text
    """
    data = load_questions_data(workspace)

    updated_count = 0

    for question in data["questions"]:
        if question["id"] in question_ids:
            question["status"] = "answered"
            question["answered_at"] = datetime.utcnow().isoformat()

            if answers_dict and question["id"] in answers_dict:
                question["answer"] = answers_dict[question["id"]]

            updated_count += 1

    # Update metadata
    data["metadata"]["pending_count"] = sum(
        1 for q in data["questions"] if q["status"] == "pending"
    )
    data["metadata"]["answered_count"] = sum(
        1 for q in data["questions"] if q["status"] == "answered"
    )

    save_questions_data(workspace, data)

    print(f"✅ Marked {updated_count} question(s) as answered", file=sys.stderr)


def check_for_new_answers(workspace: Path) -> bool:
    """
    Check if user has provided new answers.

    Returns:
        True if deferred-answers.json exists and has unprocessed answers
    """
    answers_file = get_answers_file(workspace)
    return answers_file.exists()


def load_and_process_answers(workspace: Path) -> List[Dict[str, Any]]:
    """
    Load user answers and mark corresponding questions as answered.

    Returns:
        List of answer dictionaries
    """
    answers_file = get_answers_file(workspace)

    if not answers_file.exists():
        return []

    # Load answers
    with open(answers_file, 'r') as f:
        answers_data = json.load(f)

    answers = answers_data.get("answers", [])

    if not answers:
        return []

    # Mark questions as answered
    question_ids = [a["question_id"] for a in answers]
    answers_dict = {a["question_id"]: a["answer"] for a in answers}

    mark_questions_answered(question_ids, workspace, answers_dict)

    # Archive answers file (rename to processed)
    processed_file = answers_file.parent / f"deferred-answers-processed-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    answers_file.rename(processed_file)

    print(f"✅ Processed {len(answers)} answer(s) from user", file=sys.stderr)

    return answers


def get_questions_summary(workspace: Path) -> Dict[str, Any]:
    """
    Get summary of deferred questions.

    Returns:
        {
            "total": 10,
            "pending": 3,
            "answered": 7,
            "critical_pending": 1,
            "optional_pending": 2
        }
    """
    data = load_questions_data(workspace)

    pending = [q for q in data["questions"] if q["status"] == "pending"]
    critical_pending = sum(1 for q in pending if q.get("classification") == "critical")
    optional_pending = sum(1 for q in pending if q.get("classification") == "optional")

    return {
        "total": len(data["questions"]),
        "pending": len(pending),
        "answered": data["metadata"]["answered_count"],
        "critical_pending": critical_pending,
        "optional_pending": optional_pending
    }


if __name__ == "__main__":
    # Test the handler
    from pathlib import Path
    import tempfile

    print("Deferred Questions Handler Test\n" + "="*60)

    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Test saving questions
        print("\n1. Saving deferred questions...")
        q1 = {
            "question": "Should we use tabs or spaces?",
            "context": "Code formatting",
            "classification": "optional",
            "agent_assumption": "Using spaces"
        }
        q2 = {
            "question": "Which database?",
            "context": "Critical architecture decision",
            "classification": "critical"
        }

        id1 = save_deferred_question(q1, workspace, iteration=1)
        id2 = save_deferred_question(q2, workspace, iteration=3)

        print(f"   Saved question IDs: {id1}, {id2}")

        # Test loading pending
        print("\n2. Loading pending questions...")
        pending = load_pending_questions(workspace)
        print(f"   Pending questions: {len(pending)}")
        for q in pending:
            print(f"   - {q['id']}: {q['question']}")

        # Test saving answers
        print("\n3. Saving user answers...")
        answers = [
            {"question_id": id1, "answer": "Use spaces"},
            {"question_id": id2, "answer": "Use PostgreSQL"}
        ]
        save_user_answers(answers, workspace)

        # Test processing answers
        print("\n4. Processing answers...")
        processed = load_and_process_answers(workspace)
        print(f"   Processed: {len(processed)} answers")

        # Test summary
        print("\n5. Getting summary...")
        summary = get_questions_summary(workspace)
        print(f"   Total: {summary['total']}")
        print(f"   Pending: {summary['pending']}")
        print(f"   Answered: {summary['answered']}")

        print("\n✅ All tests passed!")
