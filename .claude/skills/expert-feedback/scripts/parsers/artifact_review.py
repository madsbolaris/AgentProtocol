#!/usr/bin/env python3
"""
Parse artifact review markdown into structured JSON.

Input: artifact-review-{expert}.md (LLM-generated markdown)
Output: artifact-review-{expert}.json (structured data)

The parser handles three decision types:
- approve: Simple approval with rationale
- minor_tweaks: Approval with suggested fixes
- concerns_raised: Rejection with critical issues and questions
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Tweak:
    """A suggested minor fix to the artifact."""
    title: str
    section: str
    issue: str
    suggestion: str


@dataclass
class CriticalIssue:
    """A critical flaw that requires artifact regeneration."""
    title: str
    issue: str
    why_critical: str
    evidence: str


@dataclass
class Question:
    """A question for the user to resolve."""
    question: str
    context: str
    importance: str


@dataclass
class ArtifactReview:
    """Complete artifact review from one expert."""
    expert: str
    decision: str  # "approve", "minor_tweaks", or "concerns_raised"
    confidence: str  # "high", "medium", or "low"
    rationale: str
    tweaks: List[Tweak] = None  # Only for minor_tweaks
    critical_issues: List[CriticalIssue] = None  # Only for concerns_raised
    questions: List[Question] = None  # Only for concerns_raised


class ArtifactReviewParser:
    """Parse artifact review markdown into structured data."""

    def __init__(self, markdown_path: Path):
        self.markdown = markdown_path.read_text()
        self.sections = self._split_sections()

    def _split_sections(self) -> Dict[str, str]:
        """Split markdown by ## headers."""
        sections = {}
        current_section = None
        current_content = []

        for line in self.markdown.split('\n'):
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

        return sections

    def parse_decision_section(self) -> Dict[str, str]:
        """Parse Decision section to get decision type, confidence, rationale, and expert."""
        # Try all possible decision headers
        for decision_type in ['Decision: Approve', 'Decision: Minor Tweaks', 'Decision: Critical Concerns']:
            section = self.sections.get(decision_type)
            if section:
                break
        else:
            raise ValueError(f"No valid decision section found. Available sections: {list(self.sections.keys())}")

        # Extract decision from header
        if 'Approve' in decision_type:
            decision = 'approve'
        elif 'Minor Tweaks' in decision_type:
            decision = 'minor_tweaks'
        elif 'Critical Concerns' in decision_type:
            decision = 'concerns_raised'
        else:
            raise ValueError(f"Unknown decision type in header: {decision_type}")

        # Extract confidence
        confidence_match = re.search(r'\*\*Confidence:\*\*\s*(\w+)', section)
        confidence = confidence_match.group(1) if confidence_match else 'medium'

        # Extract rationale
        rationale_match = re.search(r'\*\*Rationale:\*\*(.*?)(?:\*\*Expert:\*\*|$)', section, re.DOTALL)
        rationale = rationale_match.group(1).strip() if rationale_match else ''

        # Extract expert
        expert_match = re.search(r'\*\*Expert:\*\*\s*(\S+)', section)
        expert = expert_match.group(1) if expert_match else 'unknown'

        return {
            'decision': decision,
            'confidence': confidence,
            'rationale': rationale,
            'expert': expert
        }

    def parse_tweaks(self) -> List[Tweak]:
        """Parse Suggested Tweaks section (for minor_tweaks decision)."""
        section = self.sections.get('Suggested Tweaks', '')
        if not section:
            return []

        tweaks = []
        # Split by ### headers
        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:])

            # Extract section reference
            section_match = re.search(r'\*\*Section:\*\*\s*(.+?)(?:\n|$)', content)
            section_ref = section_match.group(1).strip() if section_match else 'Unknown'

            # Extract issue
            issue_match = re.search(r'\*\*Issue:\*\*(.*?)(?:\*\*Suggestion:\*\*|$)', content, re.DOTALL)
            issue = issue_match.group(1).strip() if issue_match else ''

            # Extract suggestion
            suggestion_match = re.search(r'\*\*Suggestion:\*\*(.*?)$', content, re.DOTALL)
            suggestion = suggestion_match.group(1).strip() if suggestion_match else ''

            tweaks.append(Tweak(
                title=title,
                section=section_ref,
                issue=issue,
                suggestion=suggestion
            ))

        return tweaks

    def parse_critical_issues(self) -> List[CriticalIssue]:
        """Parse Critical Issues section (for concerns_raised decision)."""
        section = self.sections.get('Critical Issues', '')
        if not section:
            return []

        issues = []
        # Split by ### headers
        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:])

            # Extract issue description
            issue_match = re.search(r'\*\*Issue:\*\*(.*?)(?:\*\*Why Critical:\*\*|$)', content, re.DOTALL)
            issue = issue_match.group(1).strip() if issue_match else ''

            # Extract why critical
            why_match = re.search(r'\*\*Why Critical:\*\*(.*?)(?:\*\*Evidence:\*\*|$)', content, re.DOTALL)
            why_critical = why_match.group(1).strip() if why_match else ''

            # Extract evidence
            evidence_match = re.search(r'\*\*Evidence:\*\*(.*?)$', content, re.DOTALL)
            evidence = evidence_match.group(1).strip() if evidence_match else ''

            issues.append(CriticalIssue(
                title=title,
                issue=issue,
                why_critical=why_critical,
                evidence=evidence
            ))

        return issues

    def parse_questions(self) -> List[Question]:
        """Parse Questions for User section (for concerns_raised decision)."""
        section = self.sections.get('Questions for User', '')
        if not section:
            return []

        questions = []
        # Split by ### headers
        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            question_text = lines[0].strip()
            content = '\n'.join(lines[1:])

            # Extract context
            context_match = re.search(r'\*\*Context:\*\*(.*?)(?:\*\*Importance:\*\*|$)', content, re.DOTALL)
            context = context_match.group(1).strip() if context_match else ''

            # Extract importance
            importance_match = re.search(r'\*\*Importance:\*\*\s*(\w+)', content)
            importance = importance_match.group(1) if importance_match else 'medium'

            questions.append(Question(
                question=question_text,
                context=context,
                importance=importance
            ))

        return questions

    def parse(self) -> ArtifactReview:
        """Parse the complete artifact review."""
        # Parse decision section
        decision_data = self.parse_decision_section()

        # Create base review
        review = ArtifactReview(
            expert=decision_data['expert'],
            decision=decision_data['decision'],
            confidence=decision_data['confidence'],
            rationale=decision_data['rationale']
        )

        # Parse additional sections based on decision type
        if decision_data['decision'] == 'minor_tweaks':
            review.tweaks = self.parse_tweaks()
        elif decision_data['decision'] == 'concerns_raised':
            review.critical_issues = self.parse_critical_issues()
            review.questions = self.parse_questions()

        return review

    def to_json(self) -> Dict[str, Any]:
        """Convert parsed review to JSON dict."""
        review = self.parse()
        result = {
            'expert': review.expert,
            'decision': review.decision,
            'confidence': review.confidence,
            'rationale': review.rationale
        }

        if review.tweaks:
            result['tweaks'] = [asdict(t) for t in review.tweaks]
        if review.critical_issues:
            result['critical_issues'] = [asdict(i) for i in review.critical_issues]
        if review.questions:
            result['questions'] = [asdict(q) for q in review.questions]

        return result


def parse_artifact_review(markdown_path: Path, output_path: Path) -> Dict[str, Any]:
    """Parse artifact review markdown and save to JSON.

    Args:
        markdown_path: Path to artifact-review-{expert}.md
        output_path: Path to write artifact-review-{expert}.json

    Returns:
        Parsed review as dict
    """
    parser = ArtifactReviewParser(markdown_path)
    review_data = parser.to_json()

    # Write JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(review_data, indent=2))

    print(f"✅ Parsed artifact review: {markdown_path.name}")
    print(f"   Decision: {review_data['decision']}")
    print(f"   Expert: {review_data['expert']}")

    return review_data


def aggregate_reviews(workspace: Path, output_path: Path) -> Dict[str, Any]:
    """Aggregate all expert artifact reviews into single result.

    Args:
        workspace: Workspace directory
        output_path: Path to write artifact-review-result.json

    Returns:
        Aggregated results with counts and status
    """
    review_files = list(workspace.glob('artifact-review-*.json'))

    if not review_files:
        raise FileNotFoundError(f"No artifact review JSON files found in {workspace}")

    approvals = []
    minor_tweaks = []
    concerns_raised = []

    for review_file in review_files:
        with open(review_file) as f:
            review = json.load(f)

        decision = review.get('decision', '')
        expert = review.get('expert', 'unknown')

        if decision == 'approve':
            approvals.append(expert)
        elif decision == 'minor_tweaks':
            minor_tweaks.append(review)
        elif decision == 'concerns_raised':
            concerns_raised.append(review)

    # Determine overall status
    if concerns_raised:
        status = 'concerns_raised'
    elif minor_tweaks:
        status = 'minor_tweaks'
    else:
        status = 'approved'

    # Aggregate result
    result = {
        'status': status,
        'total_experts': len(review_files),
        'approvals': len(approvals),
        'minor_tweaks_count': len(minor_tweaks),
        'concerns_count': len(concerns_raised),
        'approved_by': approvals,
        'tweaks_from': [r['expert'] for r in minor_tweaks],
        'concerns_raised_by': [r['expert'] for r in concerns_raised],
        'all_tweaks': [],
        'all_critical_issues': [],
        'all_questions': []
    }

    # Collect all tweaks
    for review in minor_tweaks:
        for tweak in review.get('tweaks', []):
            result['all_tweaks'].append({
                'expert': review['expert'],
                **tweak
            })

    # Collect all critical issues
    for review in concerns_raised:
        for issue in review.get('critical_issues', []):
            result['all_critical_issues'].append({
                'expert': review['expert'],
                **issue
            })

    # Collect all questions
    for review in concerns_raised:
        for question in review.get('questions', []):
            result['all_questions'].append({
                'expert': review['expert'],
                **question
            })

    # Write result
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))

    print(f"\n✅ Aggregated artifact reviews:")
    print(f"   Status: {status}")
    print(f"   Approved by: {len(approvals)} experts")
    print(f"   Minor tweaks from: {len(minor_tweaks)} experts")
    print(f"   Concerns raised by: {len(concerns_raised)} experts")

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse artifact review markdown")
    parser.add_argument("--markdown", type=Path, help="Path to markdown file")
    parser.add_argument("--output", type=Path, help="Path to write JSON")
    parser.add_argument("--aggregate", type=Path, help="Aggregate all reviews in workspace")
    parser.add_argument("--aggregate-output", type=Path, help="Path to write aggregated result")

    args = parser.parse_args()

    if args.aggregate:
        # Aggregate mode
        output_path = args.aggregate_output or args.aggregate / "artifact-review-result.json"
        aggregate_reviews(args.aggregate, output_path)
    elif args.markdown and args.output:
        # Single file parsing
        parse_artifact_review(args.markdown, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
