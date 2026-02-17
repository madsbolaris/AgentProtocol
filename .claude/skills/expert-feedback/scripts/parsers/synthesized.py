#!/usr/bin/env python3
"""
Parse synthesized review markdown into structured JSON.

Input: synthesized.md (LLM-generated markdown)
Output: state.json updates, questions.json (derived)

This parser extracts:
- Convergence metrics from Executive Summary
- Questions from Open Questions section
- Convergence trend and consensus status
"""
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def parse_convergence_from_summary(section: str) -> Dict[str, Any]:
    """Parse convergence metrics from Executive Summary."""
    data = {
        "convergence_percent": 0,
        "consensus_reached": False,
        "convergence_trend": None,
        "high_agreement": 0,
        "partial_agreement": 0,
        "individual": 0
    }

    # Extract convergence percentage: "**Convergence:** 75%"
    conv_match = re.search(r'\*\*Convergence:\*\*\s*(\d+)%', section)
    if conv_match:
        data["convergence_percent"] = int(conv_match.group(1))

    # Extract consensus: "**Consensus Reached:** yes|no"
    consensus_match = re.search(r'\*\*Consensus Reached:\*\*\s*(yes|no)', section, re.IGNORECASE)
    if consensus_match:
        data["consensus_reached"] = consensus_match.group(1).lower() == "yes"

    # Extract convergence trend: "**Convergence Trend:** improving|stable|diverging"
    trend_match = re.search(r'\*\*Convergence Trend:\*\*\s*\{?(\w+)\}?', section, re.IGNORECASE)
    if trend_match:
        data["convergence_trend"] = trend_match.group(1).lower()

    # Extract metrics from "**Metrics:**" section
    # "- **High Agreement:** X recommendations"
    high_match = re.search(r'\*\*High Agreement:\*\*\s*(\d+)', section)
    if high_match:
        data["high_agreement"] = int(high_match.group(1))

    partial_match = re.search(r'\*\*Partial Agreement:\*\*\s*(\d+)', section)
    if partial_match:
        data["partial_agreement"] = int(partial_match.group(1))

    individual_match = re.search(r'\*\*Individual:\*\*\s*(\d+)', section)
    if individual_match:
        data["individual"] = int(individual_match.group(1))

    return data


def parse_questions_section(section: str) -> List[Dict[str, Any]]:
    """Parse Open Questions section."""
    questions = []

    # Split by ### headers
    subsections = re.split(r'\n### ', '\n' + section)[1:]

    for subsection in subsections:
        lines = subsection.split('\n')
        question_text = lines[0].strip()
        content = '\n'.join(lines[1:])

        # Extract metadata
        asked_by_match = re.search(r'\*\*Asked by:\*\*\s*\[(.*?)\]', content)
        asked_by = []
        if asked_by_match:
            experts_str = asked_by_match.group(1)
            asked_by = [e.strip() for e in experts_str.split(',')]

        importance_match = re.search(r'\*\*Importance:\*\*\s*\{?(\w+)\}?', content, re.IGNORECASE)
        importance = importance_match.group(1).lower() if importance_match else 'medium'

        # NEW: Extract selection type
        selection_match = re.search(r'\*\*Selection:\*\*\s*\{?(radio|checkbox)\}?', content, re.IGNORECASE)
        selection_type = selection_match.group(1).lower() if selection_match else None

        # NEW: Extract options
        options = []
        options_match = re.search(r'\*\*Options:\*\*(.*?)(?:\*\*|###|$)', content, re.DOTALL)
        if options_match:
            options_text = options_match.group(1)
            for line in options_text.split('\n'):
                if line.strip().startswith('-'):
                    option_text = line.strip()[1:].strip()
                    # Remove "**Option X:**" prefix if present
                    option_text = re.sub(r'^\*\*Option [A-Z]:\*\*\s*', '', option_text)
                    options.append(option_text)

        requires_decision_match = re.search(r'\*\*Requires User Decision:\*\*\s*\{?(yes|no)\}?', content, re.IGNORECASE)
        requires_decision = requires_decision_match and requires_decision_match.group(1).lower() == 'yes'

        # Extract context
        context_match = re.search(r'\*\*Context:\*\*(.*?)(?:\*\*|###|$)', content, re.DOTALL)
        context = context_match.group(1).strip() if context_match else ''

        # Generate ID from question
        question_id = re.sub(r'[^a-z0-9]+', '-', question_text.lower()).strip('-')[:50]

        # Extract references (basic parsing)
        references = []
        ref_section = re.search(r'\*\*References:\*\*(.*?)(?:###|$)', content, re.DOTALL)
        if ref_section:
            ref_lines = ref_section.group(1).split('\n')
            for line in ref_lines:
                if line.strip().startswith('-'):
                    # Parse reference line: "- **expert:** `file` - context"
                    ref_match = re.match(r'-\s*\*\*(.+?):\*\*\s*`(.+?)`\s*-\s*(.+)', line.strip())
                    if ref_match:
                        references.append({
                            "expert": ref_match.group(1).strip(),
                            "file": ref_match.group(2).strip(),
                            "excerpt": ref_match.group(3).strip()
                        })

        question_data = {
            "id": question_id,
            "question": question_text,
            "context": context,
            "importance": importance,
            "asked_by": asked_by,
            "requires_user_decision": requires_decision,
            "references": references
        }

        # Add optional fields only if present
        if selection_type:
            question_data["selection_type"] = selection_type
        if options:
            question_data["options"] = options

        questions.append(question_data)

    return questions


def parse_conflicts_section(section: str) -> List[Dict[str, Any]]:
    """Parse Conflicts to Resolve section and extract as special questions."""
    conflicts = []

    # Find conflict subsections: "### ⚠️ CONFLICT: [Title]"
    conflict_pattern = r'### ⚠️ CONFLICT: (.+?)(?=\n### ⚠️ CONFLICT:|$)'
    matches = re.finditer(conflict_pattern, section, re.DOTALL)

    for match in matches:
        title = match.group(1).split('\n')[0].strip()
        content = match.group(1)

        # Generate ID
        conflict_id = f"conflict-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]}"

        # Extract positions
        position_a_match = re.search(r'\*\*Position A\*\*\s*\((.*?)\):', content)
        position_b_match = re.search(r'\*\*Position B\*\*\s*\((.*?)\):', content)

        experts_a = []
        experts_b = []
        if position_a_match:
            experts_a = [e.strip() for e in position_a_match.group(1).split(',')]
        if position_b_match:
            experts_b = [e.strip() for e in position_b_match.group(1).split(',')]

        # Extract context from "The Disagreement:" section
        disagreement_match = re.search(r'\*\*The Disagreement:\*\*(.*?)(?:\*\*Position|$)', content, re.DOTALL)
        context = disagreement_match.group(1).strip() if disagreement_match else ''

        conflicts.append({
            "id": conflict_id,
            "question": f"How should we resolve: {title}?",
            "context": context,
            "importance": "high",
            "requires_user_decision": True,
            "asked_by": experts_a + experts_b,
            "conflict_details": {
                "experts_position_a": experts_a,
                "experts_position_b": experts_b
            }
        })

    return conflicts


def parse_synthesized_markdown(markdown_path: Path) -> Dict[str, Any]:
    """Parse synthesized markdown and extract structured data."""
    markdown = markdown_path.read_text()

    # Split into sections by ## headers
    sections = {}
    current_section = None
    current_content = []

    for line in markdown.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    # Parse executive summary for convergence
    exec_summary = sections.get('Executive Summary', '')
    convergence_data = parse_convergence_from_summary(exec_summary)

    # Parse questions
    questions_section = sections.get('Open Questions', '')
    questions = parse_questions_section(questions_section)

    # Parse conflicts as special questions
    conflicts_section = sections.get('Conflicts to Resolve', '')
    conflict_questions = parse_conflicts_section(conflicts_section)

    # Combine questions
    all_questions = questions + conflict_questions

    return {
        "convergence_data": convergence_data,
        "questions": all_questions
    }


def update_state_from_synthesized(
    state_path: Path,
    convergence_data: Dict[str, Any],
    iteration: int
) -> None:
    """Update state.json with convergence data from synthesized markdown."""
    # Load existing state
    if state_path.exists():
        with open(state_path, 'r') as f:
            state = json.load(f)
    else:
        state = {}

    # Update with convergence data
    state.update({
        "iteration": iteration,
        "convergence_percent": convergence_data["convergence_percent"],
        "consensus_reached": convergence_data["consensus_reached"],
        "high_agreement_count": convergence_data["high_agreement"],
        "partial_agreement_count": convergence_data["partial_agreement"],
        "individual_count": convergence_data["individual"]
    })

    if convergence_data["convergence_trend"]:
        state["convergence_trend"] = convergence_data["convergence_trend"]

    # Write back
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def merge_all_questions(workspace: Path, current_iteration: int) -> List[Dict[str, Any]]:
    """Merge UNANSWERED questions from previous iterations + new questions from current iteration.

    This function collects questions from:
    - All expert reviews across all iterations
    - All synthesized reviews across all iterations
    - BUT SKIPS questions that were already answered in previous iterations

    It deduplicates by question ID and preserves metadata about which
    iteration and expert asked each question.

    Args:
        workspace: Workspace directory
        current_iteration: Current iteration number

    Returns:
        List of unique UNANSWERED questions with iteration metadata
    """
    all_questions = {}  # Use dict to dedupe by ID

    # Load answered questions from ALL previous iterations to filter them out
    answered_questions = set()
    for iter_num in range(1, current_iteration + 1):
        qa_file = workspace / f"iteration-{iter_num}" / "qa-answers.json"
        if qa_file.exists():
            try:
                with open(qa_file) as f:
                    qa_data = json.load(f)
                    for answer in qa_data.get("answers", []):
                        # Store both question ID and normalized question text
                        if "question_id" in answer:
                            answered_questions.add(answer["question_id"])
                        # Also store normalized question text for fuzzy matching
                        if "question" in answer:
                            answered_questions.add(answer["question"].lower().strip())
            except Exception as e:
                print(f"Warning: Could not load qa-answers from iteration {iter_num}: {e}")

    # Iterate through all iterations from 1 to current
    for iteration in range(1, current_iteration + 1):
        iteration_dir = workspace / f"iteration-{iteration}"

        if not iteration_dir.exists():
            continue

        # 1. Collect questions from expert reviews
        experts_dir = iteration_dir / "experts"
        if experts_dir.exists():
            # Check for questions.json in expert subdirectories
            for expert_subdir in experts_dir.iterdir():
                if not expert_subdir.is_dir():
                    continue
                questions_file = expert_subdir / "questions.json"
                if not questions_file.exists():
                    continue
                try:
                    with open(questions_file, 'r') as f:
                        expert_questions = json.load(f)

                    # Handle both list and dict formats
                    questions_list = expert_questions if isinstance(expert_questions, list) else expert_questions.get("questions", [])

                    for q in questions_list:
                        q_id = q.get("id", "")
                        if not q_id:
                            continue

                        # Skip questions that were already answered
                        question_text = q.get("question", "").lower().strip()
                        if q_id in answered_questions or question_text in answered_questions:
                            # Question was answered in a previous iteration, skip it
                            continue

                        # Add or update question
                        if q_id not in all_questions:
                            all_questions[q_id] = q.copy()
                            # Add metadata
                            all_questions[q_id]["first_asked_iteration"] = iteration
                            all_questions[q_id]["asked_in_iterations"] = [iteration]
                        else:
                            # Update existing question if it appears in later iteration
                            if iteration not in all_questions[q_id].get("asked_in_iterations", []):
                                all_questions[q_id]["asked_in_iterations"].append(iteration)

                except Exception as e:
                    print(f"Warning: Could not parse {questions_file}: {e}")

        # 2. Collect questions from synthesized review
        synthesized_questions_file = iteration_dir / "questions.json"
        if synthesized_questions_file.exists():
            try:
                with open(synthesized_questions_file, 'r') as f:
                    consolidated_data = json.load(f)

                questions_list = consolidated_data.get("questions", [])

                for q in questions_list:
                    q_id = q.get("id", "")
                    if not q_id:
                        continue

                    # Skip questions that were already answered
                    question_text = q.get("question", "").lower().strip()
                    if q_id in answered_questions or question_text in answered_questions:
                        # Question was answered in a previous iteration, skip it
                        continue

                    if q_id not in all_questions:
                        all_questions[q_id] = q.copy()
                        all_questions[q_id]["first_asked_iteration"] = iteration
                        all_questions[q_id]["asked_in_iterations"] = [iteration]
                    else:
                        # Merge asked_by lists if present
                        if "asked_by" in q:
                            existing_asked_by = set(all_questions[q_id].get("asked_by", []))
                            new_asked_by = set(q["asked_by"])
                            all_questions[q_id]["asked_by"] = sorted(list(existing_asked_by | new_asked_by))

                        # Track iterations
                        if iteration not in all_questions[q_id].get("asked_in_iterations", []):
                            all_questions[q_id]["asked_in_iterations"].append(iteration)

            except Exception as e:
                print(f"Warning: Could not parse {synthesized_questions_file}: {e}")

    # Convert dict back to list, sorted by importance and first appearance
    importance_order = {"high": 0, "critical": 0, "medium": 1, "low": 2, "unknown": 3}

    def sort_key(q):
        importance = q.get("importance", "medium")
        iteration = q.get("first_asked_iteration", 999)
        return (importance_order.get(importance, 3), iteration)

    return sorted(all_questions.values(), key=sort_key)


def generate_questions_json(
    questions: List[Dict[str, Any]],
    output_path: Path,
    iteration: int,
    workspace: Optional[Path] = None,
    merge_all: bool = False
) -> None:
    """Generate questions.json from parsed questions.

    Args:
        questions: Questions from current iteration
        output_path: Path to write questions.json
        iteration: Current iteration number
        workspace: Workspace path (required if merge_all=True)
        merge_all: If True, merge questions from all iterations (not just current)
    """
    if merge_all and workspace:
        # Merge questions from all iterations
        all_questions = merge_all_questions(workspace, iteration)

        # Add current iteration's questions to the merge
        # merge_all_questions() only reads from disk (previous iterations)
        # so we need to manually add the current iteration's new questions
        all_questions_dict = {q["id"]: q for q in all_questions}
        for q in questions:
            if q["id"] not in all_questions_dict:
                all_questions_dict[q["id"]] = q

        questions_data = {
            "iteration": iteration,
            "questions": list(all_questions_dict.values()),
            "merged_from_iterations": list(range(1, iteration + 1))
        }
    else:
        # Just current iteration questions
        questions_data = {
            "iteration": iteration,
            "questions": questions
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(questions_data, f, indent=2)


def parse_and_update(
    markdown_path: Path,
    workspace: Path,
    iteration: int,
    merge_all: bool = True
) -> None:
    """Parse synthesized markdown and update state + questions.

    Args:
        markdown_path: Path to synthesized markdown file
        workspace: Workspace directory
        iteration: Current iteration number
        merge_all: If True, merge questions from all iterations (default: True for iteration 2+)
    """
    print(f"📄 Parsing synthesized markdown: {markdown_path}")

    # Parse markdown
    parsed = parse_synthesized_markdown(markdown_path)

    # Update state.json
    state_path = workspace / "state.json"
    update_state_from_synthesized(
        state_path,
        parsed["convergence_data"],
        iteration
    )
    print(f"✅ Updated state.json with convergence: {parsed['convergence_data']['convergence_percent']}%")

    # Generate questions.json
    # For iteration 2+, merge questions from all iterations by default
    should_merge = merge_all and iteration > 1

    questions_path = workspace / f"iteration-{iteration}" / "questions.json"
    generate_questions_json(
        parsed["questions"],
        questions_path,
        iteration,
        workspace=workspace,
        merge_all=should_merge
    )

    if should_merge:
        print(f"✅ Generated questions.json with {len(parsed['questions'])} questions (merged from all iterations)")
    else:
        print(f"✅ Generated questions.json with {len(parsed['questions'])} questions")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse synthesized markdown")
    parser.add_argument("--markdown", type=Path, required=True, help="Path to synthesized markdown")
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace directory")
    parser.add_argument("--iteration", type=int, required=True, help="Iteration number")
    parser.add_argument("--merge-all", action="store_true", default=True, help="Merge questions from all iterations (default: True)")
    parser.add_argument("--no-merge-all", dest="merge_all", action="store_false", help="Don't merge questions from all iterations")

    args = parser.parse_args()
    parse_and_update(args.markdown, args.workspace, args.iteration, args.merge_all)


if __name__ == "__main__":
    main()
