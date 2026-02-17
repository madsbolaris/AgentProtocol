#!/usr/bin/env python3
"""
Parse expert review markdown into structured JSON.

Input: review-{expert}.md (LLM-generated markdown at iteration-N/experts/ level)
Output: {expert}/state.json, {expert}/questions.json (derived, in expert subdirectories)

Parsing Strategy:
1. Find sections by headers (## DX Rating, ## Concerns, etc.)
2. Extract structured data from markdown format
3. Validate against schema
4. Output JSON files

Supports both full reviews (iteration 1) and delta reviews (iteration 2+)
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DXRating:
    stars: int  # Extracted from "**Rating:** 4/5 ⭐⭐⭐⭐"
    confidence: str  # Extracted from "**Confidence:** high"
    justification: str  # Paragraph after rating


@dataclass
class Concern:
    title: str  # From "### Concern Title"
    severity: str  # From "**Severity:** high"
    impact: str  # From "**Impact:** medium"
    description: str  # Markdown content after metadata
    evidence: Dict[str, List[str]]  # From **Evidence:** bullets
    recommended_fix: str  # From **Fix:** section


@dataclass
class Recommendation:
    title: str  # From "### Recommendation Title"
    priority: str  # From "**Priority:** critical"
    complexity: str  # From "**Complexity:** low"
    dx_impact: str  # From "**DX Impact:** high"
    description: str  # Markdown content
    implementation: str  # From **Implementation:** section
    benefits: List[str]  # From **Benefits:** bullets
    risks: List[str]  # From **Risks:** bullets


@dataclass
class Question:
    id: str  # Generated: slugify(question)
    question: str  # From "### Question text?"
    context: str  # From **Context:** paragraph
    importance: str  # From "**Importance:** high"
    clarification: str  # Additional context
    options: List[str] = None  # NEW: 2-3 options for the question
    selection_type: str = None  # NEW: radio or checkbox


@dataclass
class ParseError:
    """Detailed parsing error information."""
    section: str
    message: str
    line_number: int
    expected: str
    actual: str
    hint: str


class MarkdownParseError(Exception):
    """Raised when markdown parsing fails."""
    def __init__(self, errors: List[ParseError]):
        self.errors = errors
        super().__init__(f"Parsing failed with {len(errors)} errors")


class MarkdownParser:
    """Parse expert review markdown into structured data."""

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

    def parse_dx_rating(self) -> DXRating:
        """Parse DX Rating section."""
        section = self.sections.get('DX Rating', '')

        # Extract stars: "**Rating:** 4/5 ⭐⭐⭐⭐"
        stars_match = re.search(r'\*\*Rating:\*\*\s*(\d+)/5', section)
        stars = int(stars_match.group(1)) if stars_match else 0

        # Extract confidence: "**Confidence:** high"
        confidence_match = re.search(r'\*\*Confidence:\*\*\s*(\w+)', section)
        confidence = confidence_match.group(1) if confidence_match else 'unknown'

        # Justification is remaining text after metadata
        justification_lines = []
        for line in section.split('\n'):
            if not line.startswith('**') and line.strip():
                justification_lines.append(line)
        justification = '\n'.join(justification_lines).strip()

        return DXRating(stars=stars, confidence=confidence, justification=justification)

    def parse_concerns(self) -> List[Concern]:
        """Parse Concerns section with ### subsections."""
        section = self.sections.get('Concerns', '')
        if not section or section.strip() == '⚠️':
            section = self.sections.get('Concerns ⚠️', '')

        concerns = []

        # Split by ### headers
        subsections = re.split(r'\n### ', '\n' + section)[1:]  # Skip first empty

        for subsection in subsections:
            lines = subsection.split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:])

            # Extract metadata
            severity = self._extract_field(content, 'Severity')
            impact = self._extract_field(content, 'Impact')

            # Extract description (text before **Evidence:** or **Fix:**)
            desc_match = re.search(r'^(.*?)(?:\*\*Evidence:\*\*|\*\*Fix:\*\*|$)', content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else content
            # Remove metadata lines from description
            description = re.sub(r'\*\*Severity:\*\*.*?\n', '', description)
            description = re.sub(r'\*\*Impact:\*\*.*?\n', '', description)
            description = description.strip()

            # Extract evidence bullets
            evidence = {'files': [], 'references': []}
            evidence_match = re.search(r'\*\*Evidence:\*\*(.*?)(?:\*\*Fix:\*\*|$)', content, re.DOTALL)
            if evidence_match:
                evidence_text = evidence_match.group(1)
                evidence['files'] = self._extract_bullets(evidence_text)

            # Extract fix
            fix_match = re.search(r'\*\*Fix:\*\*(.*?)$', content, re.DOTALL)
            recommended_fix = fix_match.group(1).strip() if fix_match else ''

            concerns.append(Concern(
                title=title,
                severity=severity,
                impact=impact,
                description=description,
                evidence=evidence,
                recommended_fix=recommended_fix
            ))

        return concerns

    def parse_recommendations(self) -> List[Recommendation]:
        """Parse Recommendations section."""
        section = self.sections.get('Recommendations', '')
        if not section or section.strip() == '💡':
            section = self.sections.get('Recommendations 💡', '')

        recommendations = []

        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            title = lines[0].strip()
            content = '\n'.join(lines[1:])

            priority = self._extract_field(content, 'Priority')
            complexity = self._extract_field(content, 'Complexity')
            dx_impact = self._extract_field(content, 'DX Impact')

            # Description before **Implementation:**
            desc_match = re.search(r'^(.*?)(?:\*\*Implementation:\*\*|$)', content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else content
            # Remove metadata lines from description
            description = re.sub(r'\*\*Priority:\*\*.*?\n', '', description)
            description = re.sub(r'\*\*Complexity:\*\*.*?\n', '', description)
            description = re.sub(r'\*\*DX Impact:\*\*.*?\n', '', description)
            description = description.strip()

            # Implementation
            impl_match = re.search(r'\*\*Implementation:\*\*(.*?)(?:\*\*Benefits:\*\*|$)', content, re.DOTALL)
            implementation = impl_match.group(1).strip() if impl_match else ''

            # Benefits bullets
            benefits_match = re.search(r'\*\*Benefits:\*\*(.*?)(?:\*\*Risks:\*\*|$)', content, re.DOTALL)
            benefits = self._extract_bullets(benefits_match.group(1)) if benefits_match else []

            # Risks bullets
            risks_match = re.search(r'\*\*Risks:\*\*(.*?)$', content, re.DOTALL)
            risks = self._extract_bullets(risks_match.group(1)) if risks_match else []

            recommendations.append(Recommendation(
                title=title,
                priority=priority,
                complexity=complexity,
                dx_impact=dx_impact,
                description=description,
                implementation=implementation,
                benefits=benefits,
                risks=risks
            ))

        return recommendations

    def parse_strengths(self) -> List[Dict[str, str]]:
        """Parse Strengths section."""
        section = self.sections.get('Strengths', '')
        if not section or section.strip() == '✅':
            section = self.sections.get('Strengths ✅', '')

        strengths = []

        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            title = lines[0].strip()
            description = '\n'.join(lines[1:]).strip()
            strengths.append({'title': title, 'description': description})

        return strengths

    def parse_questions(self) -> List[Question]:
        """Parse Questions section."""
        section = self.sections.get('Questions', '')
        if not section or section.strip() == '❓':
            section = self.sections.get('Questions ❓', '')

        questions = []

        subsections = re.split(r'\n### ', '\n' + section)[1:]

        for subsection in subsections:
            lines = subsection.split('\n')
            question_text = lines[0].strip()
            content = '\n'.join(lines[1:])

            # Generate ID from question
            question_id = re.sub(r'[^a-z0-9]+', '-', question_text.lower()).strip('-')[:50]

            context = self._extract_field_paragraph(content, 'Context')
            importance = self._extract_field(content, 'Importance')

            # NEW: Extract selection type
            selection_type = self._extract_field(content, 'Selection')

            # NEW: Extract options
            options = []
            options_match = re.search(r'\*\*Options:\*\*(.*?)(?:\*\*|###|$)', content, re.DOTALL)
            if options_match:
                options_text = options_match.group(1)
                options = self._extract_bullets(options_text)

            # Clarification is remaining text after context
            clarification = content
            if '**Context:**' in content:
                clarification = content.split('**Context:**')[-1]
            if '**Importance:**' in clarification:
                clarification = clarification.split('**Importance:**')[-1]
            if '**Selection:**' in clarification:
                clarification = clarification.split('**Selection:**')[-1]
            if '**Options:**' in clarification:
                clarification = clarification.split('**Options:**')[-1]
            clarification = clarification.strip()

            questions.append(Question(
                id=question_id,
                question=question_text,
                context=context,
                importance=importance,
                clarification=clarification,
                options=options if options else None,
                selection_type=selection_type if selection_type != 'unknown' else None
            ))

        return questions

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field value: '**Field:** value'"""
        match = re.search(rf'\*\*{field_name}:\*\*\s*(\w+)', text)
        return match.group(1) if match else 'unknown'

    def _extract_field_paragraph(self, text: str, field_name: str) -> str:
        """Extract paragraph after field marker."""
        match = re.search(rf'\*\*{field_name}:\*\*\s*(.*?)(?:\*\*|$)', text, re.DOTALL)
        return match.group(1).strip() if match else ''

    def _extract_bullets(self, text: str) -> List[str]:
        """Extract bullet list items."""
        bullets = []
        for line in text.split('\n'):
            if line.strip().startswith('-') or line.strip().startswith('*'):
                bullets.append(line.strip()[1:].strip())
        return bullets

    def to_state_json(self) -> Dict[str, Any]:
        """Generate state JSON from parsed data."""
        dx_rating = self.parse_dx_rating()
        concerns = self.parse_concerns()
        recommendations = self.parse_recommendations()
        strengths = self.parse_strengths()
        questions = self.parse_questions()

        return {
            'expert_name': 'Extracted from filename',  # Set by caller
            'dx_rating': asdict(dx_rating),
            'concerns': [asdict(c) for c in concerns],
            'recommendations': [asdict(r) for r in recommendations],
            'strengths': strengths,
            'questions': [asdict(q) for q in questions]
        }

    def to_questions_json(self) -> List[Dict[str, Any]]:
        """Generate questions JSON."""
        questions = self.parse_questions()
        return [asdict(q) for q in questions]


def parse_delta_review(content: str, iteration: int) -> Dict[str, Any]:
    """Parse delta-only refinement review.

    Args:
        content: Markdown content
        iteration: Iteration number

    Returns:
        Delta review dict with structure:
        {
            "type": "delta",
            "iteration": int,
            "what_changed": str,
            "updated_recommendations": {id: changes},
            "new_recommendations": [rec],
            "new_concerns": [concern],
            "resolved_concerns": [id],
            "updated_assessment": {rating, why},
            "unanswered_questions": [question_id],
            "new_questions": [question]
        }
    """
    result = {
        "type": "delta",
        "iteration": iteration,
        "what_changed": "",
        "updated_recommendations": {},
        "new_recommendations": [],
        "new_concerns": [],
        "resolved_concerns": [],
        "updated_assessment": None,
        "unanswered_questions": [],
        "new_questions": []
    }

    # Parse "What Changed" section
    what_changed = extract_section(content, "### 1. What Changed")
    if what_changed:
        result["what_changed"] = what_changed.strip()

    # Parse "Updated Recommendations"
    updated_section = extract_section(content, "### 2. Updated Recommendations")
    if updated_section:
        result["updated_recommendations"] = parse_updated_recommendations(updated_section)

    # Parse "New Recommendations"
    new_rec_section = extract_section(content, "### 3. New Recommendations")
    if new_rec_section and new_rec_section.strip():
        # Use MarkdownParser to parse new recommendations
        temp_md = f"## Recommendations 💡\n{new_rec_section}"
        temp_parser = MarkdownParser.__new__(MarkdownParser)
        temp_parser.markdown = temp_md
        temp_parser.sections = {"Recommendations 💡": new_rec_section}
        recs = temp_parser.parse_recommendations()
        result["new_recommendations"] = [asdict(r) for r in recs]

    # Parse "New Concerns"
    new_concerns_section = extract_section(content, "### 4. New Concerns")
    if new_concerns_section and new_concerns_section.strip():
        # Use MarkdownParser to parse new concerns
        temp_md = f"## Concerns ⚠️\n{new_concerns_section}"
        temp_parser = MarkdownParser.__new__(MarkdownParser)
        temp_parser.markdown = temp_md
        temp_parser.sections = {"Concerns ⚠️": new_concerns_section}
        concerns = temp_parser.parse_concerns()
        result["new_concerns"] = [asdict(c) for c in concerns]

    # Parse "Resolved Concerns"
    resolved_section = extract_section(content, "### 5. Resolved Concerns")
    if resolved_section:
        result["resolved_concerns"] = parse_resolved_concerns(resolved_section)

    # Parse "Updated Assessment"
    assessment_section = extract_section(content, "### 6. Updated Assessment")
    if assessment_section and assessment_section.strip():
        result["updated_assessment"] = parse_assessment_update(assessment_section)

    # Parse "Unanswered Questions from Previous Iteration" - section 6.5
    unanswered_section = extract_section(content, "### 6.5. Unanswered Questions from Previous Iteration")
    if unanswered_section:
        result["unanswered_questions"] = parse_unanswered_questions(unanswered_section)

    # Parse "New Questions" - section 7
    questions_section = extract_section(content, "### 7. New Questions")
    if questions_section and questions_section.strip():
        # Use MarkdownParser to parse questions
        temp_md = f"## Questions ❓\n{questions_section}"
        temp_parser = MarkdownParser.__new__(MarkdownParser)
        temp_parser.markdown = temp_md
        temp_parser.sections = {"Questions ❓": questions_section}
        questions = temp_parser.parse_questions()
        result["new_questions"] = [asdict(q) for q in questions]

    # Validation: Warn if delta is too long
    delta_length = len(content)
    if delta_length > 10000:  # ~10K chars is ~50% of typical full review
        logger.warning(
            f"Delta review is long ({delta_length} chars). "
            f"Iteration {iteration} should only include changes, not repeated content."
        )

    return result


def extract_section(content: str, header: str) -> str:
    """Extract content between a header and the next ### header."""
    # Find the header
    pattern = re.escape(header) + r'\s*\n(.*?)(?=\n###|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def parse_updated_recommendations(section: str) -> Dict[str, Dict]:
    """Parse updated recommendations by ID.

    Format:
    - **Recommendation ID:** rec-001
    - **What changed:** ...
    - **Updated rationale:** ...
    """
    updates = {}

    # Match pattern: - **Recommendation ID:** rec-001
    id_pattern = r'-\s*\*\*Recommendation ID:\*\*\s+([a-z]+-\d+)'

    for match in re.finditer(id_pattern, section):
        rec_id = match.group(1)

        # Extract the full recommendation block for this ID
        start = match.end()
        # Find next ID or end of section
        next_match = re.search(id_pattern, section[start:])
        end = start + next_match.start() if next_match else len(section)

        rec_block = section[start:end]
        updates[rec_id] = parse_recommendation_changes(rec_block)

    return updates


def parse_recommendation_changes(block: str) -> Dict:
    """Parse changes to a single recommendation."""
    changes = {}

    # Parse what changed
    what_changed_match = re.search(r'-\s*\*\*What changed:\*\*\s*(.*?)(?=\n-|\Z)', block, re.DOTALL)
    if what_changed_match:
        changes["change_description"] = what_changed_match.group(1).strip()

    # Parse updated fields
    priority_match = re.search(r'\*\*Priority:\*\*\s*(\w+)', block)
    if priority_match:
        changes["priority"] = priority_match.group(1)

    complexity_match = re.search(r'\*\*Complexity:\*\*\s*(\w+)', block)
    if complexity_match:
        changes["complexity"] = complexity_match.group(1)

    rationale_match = re.search(r'-\s*\*\*Updated rationale:\*\*\s*(.*?)(?=\n-|\Z)', block, re.DOTALL)
    if rationale_match:
        changes["rationale"] = rationale_match.group(1).strip()

    return changes


def parse_resolved_concerns(section: str) -> List[str]:
    """Parse list of resolved concern IDs.

    Format:
    - con-003 (explanation)
    - con-007 (explanation)
    """
    ids = []

    # Match pattern: - con-003 (explanation)
    pattern = r'-\s+([a-z]+-\d+)'

    for match in re.finditer(pattern, section):
        ids.append(match.group(1))

    return ids


def parse_assessment_update(section: str) -> Dict:
    """Parse updated assessment section.

    Format:
    **Previous rating:** 3/5
    **New rating:** 4/5
    **Why it changed:** ...
    """
    update = {}

    # Parse previous rating
    prev_match = re.search(r'\*\*Previous rating:\*\*\s*(\d+)/5', section)
    if prev_match:
        update["previous_rating"] = int(prev_match.group(1))

    # Parse new rating
    new_match = re.search(r'\*\*New rating:\*\*\s*(\d+)/5', section)
    if new_match:
        update["new_rating"] = int(new_match.group(1))

    # Parse why it changed
    why_match = re.search(r'\*\*Why it changed:\*\*\s*(.*?)(?=\n\*\*|\Z)', section, re.DOTALL)
    if why_match:
        update["why_changed"] = why_match.group(1).strip()

    return update


def parse_unanswered_questions(section: str) -> List[Dict[str, str]]:
    """Parse unanswered questions from previous iteration.

    Format:
    UNANSWERED_QUESTIONS:
    - q-001: [Original question text] - Reason: [explanation]
    - q-003: [Original question text] - Reason: [explanation]

    Returns:
        List of dicts with question_id, question_text, and reason
    """
    unanswered = []

    # Look for UNANSWERED_QUESTIONS: block
    block_match = re.search(r'UNANSWERED_QUESTIONS:\s*(.*?)(?=\n[^-\s]|\Z)', section, re.DOTALL)
    if not block_match:
        return unanswered

    block_content = block_match.group(1)

    # Parse each line: - q-001: [question] - Reason: [reason]
    pattern = r'-\s+([a-z]+-\d+):\s*(.*?)\s*-\s*Reason:\s*(.*?)(?=\n-|\Z)'

    for match in re.finditer(pattern, block_content, re.DOTALL):
        unanswered.append({
            "question_id": match.group(1).strip(),
            "question_text": match.group(2).strip(),
            "reason": match.group(3).strip()
        })

    return unanswered


def merge_delta_with_state(previous_state: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
    """Merge delta review with previous iteration's state.

    Args:
        previous_state: State from previous iteration
        delta: Delta review data

    Returns:
        New merged state
    """
    import copy
    new_state = copy.deepcopy(previous_state)
    new_state['iteration'] = delta['iteration']

    # Apply updated recommendations
    if delta.get('updated_recommendations'):
        recommendations = new_state.get('recommendations', [])
        for rec in recommendations:
            rec_id = generate_rec_id(rec['title'])
            if rec_id in delta['updated_recommendations']:
                changes = delta['updated_recommendations'][rec_id]
                # Apply changes
                if 'priority' in changes:
                    rec['priority'] = changes['priority']
                if 'complexity' in changes:
                    rec['complexity'] = changes['complexity']
                if 'rationale' in changes:
                    # Append to description or replace
                    rec['description'] = f"{rec['description']}\n\n**Update:** {changes['rationale']}"
                if 'change_description' in changes:
                    # Store change description in metadata
                    if 'metadata' not in rec:
                        rec['metadata'] = {}
                    rec['metadata']['last_change'] = changes['change_description']

    # Add new recommendations
    if delta.get('new_recommendations'):
        if 'recommendations' not in new_state:
            new_state['recommendations'] = []
        new_state['recommendations'].extend(delta['new_recommendations'])

    # Add new concerns
    if delta.get('new_concerns'):
        if 'concerns' not in new_state:
            new_state['concerns'] = []
        new_state['concerns'].extend(delta['new_concerns'])

    # Remove resolved concerns
    if delta.get('resolved_concerns'):
        concerns = new_state.get('concerns', [])
        resolved_ids = set(delta['resolved_concerns'])
        new_state['concerns'] = [
            c for c in concerns
            if generate_concern_id(c['title']) not in resolved_ids
        ]

    # Update DX rating if changed
    if delta.get('updated_assessment'):
        assessment = delta['updated_assessment']
        if 'new_rating' in assessment:
            new_state['dx_rating'] = {
                'stars': assessment['new_rating'],
                'confidence': new_state.get('dx_rating', {}).get('confidence', 'medium'),
                'justification': assessment.get('why_changed', '')
            }

    # Update questions: unanswered + new questions
    all_questions = []

    # Add unanswered questions from previous iteration
    if delta.get('unanswered_questions'):
        # Convert unanswered to full question format
        for unanswered in delta['unanswered_questions']:
            all_questions.append({
                'id': unanswered['question_id'],
                'question': unanswered['question_text'],
                'context': f"Previously asked but {unanswered['reason']}",
                'importance': 'high',  # Unanswered questions are high priority
                'clarification': ''
            })

    # Add new questions
    if delta.get('new_questions'):
        all_questions.extend(delta['new_questions'])

    if all_questions:
        new_state['questions'] = all_questions
    elif 'questions' in new_state:
        # No new or unanswered questions, clear the list
        new_state['questions'] = []

    return new_state


def generate_rec_id(title: str) -> str:
    """Generate recommendation ID from title (rec-nnn format)."""
    # Simple slug: lowercase, replace spaces with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:30]
    return f"rec-{slug}"


def generate_concern_id(title: str) -> str:
    """Generate concern ID from title (con-nnn format)."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:30]
    return f"con-{slug}"


def parse_expert_review(markdown_path: Path, output_dir: Path, expert_name: str, iteration: int = 1, workspace: Optional[Path] = None) -> None:
    """Parse expert review markdown and generate JSON files.

    Args:
        markdown_path: Path to markdown file
        output_dir: Output directory
        expert_name: Expert name
        iteration: Iteration number (1 = full review, 2+ = delta)
        workspace: Workspace root (required for iteration 2+ to load previous state)
    """
    content = markdown_path.read_text()

    if iteration == 1:
        # Full review parsing
        parser = MarkdownParser(markdown_path)

        # Generate state JSON
        state = parser.to_state_json()
        state['expert_name'] = expert_name
        state['iteration'] = iteration
        # Create expert subdirectory for JSON files
        expert_dir = output_dir / expert_name
        expert_dir.mkdir(parents=True, exist_ok=True)

        # Generate state JSON (in expert subdirectory)
        state_path = expert_dir / "state.json"
        state_path.write_text(json.dumps(state, indent=2))
        print(f"✅ Generated: {state_path}")

        # Generate questions JSON (in expert subdirectory)
        questions = parser.to_questions_json()
        questions_path = expert_dir / "questions.json"
        questions_path.write_text(json.dumps(questions, indent=2))
        print(f"✅ Generated: {questions_path}")
    else:
        # Delta review parsing (iteration 2+)
        if not workspace:
            raise ValueError("workspace parameter required for iteration 2+ parsing")

        # Parse delta review
        delta = parse_delta_review(content, iteration)
        delta['expert_name'] = expert_name

        # Create expert subdirectory for JSON files
        expert_dir = output_dir / expert_name
        expert_dir.mkdir(parents=True, exist_ok=True)

        # Save delta JSON for debugging (in expert subdirectory)
        delta_path = expert_dir / "delta.json"
        delta_path.write_text(json.dumps(delta, indent=2))
        print(f"✅ Generated delta: {delta_path}")

        # Load previous iteration's state (from expert subdirectory)
        prev_iteration = iteration - 1
        prev_expert_dir = workspace / f"iteration-{prev_iteration}" / "experts"
        prev_state_path = prev_expert_dir / expert_name / "state.json"

        if not prev_state_path.exists():
            logger.error(
                f"Cannot find previous state: {prev_state_path}\n"
                f"Delta parsing requires previous iteration's state to merge changes."
            )
            # Still generate questions if available
            if delta.get('unanswered_questions') or delta.get('new_questions'):
                all_questions = []
                if delta.get('unanswered_questions'):
                    for unanswered in delta['unanswered_questions']:
                        all_questions.append({
                            'id': unanswered['question_id'],
                            'question': unanswered['question_text'],
                            'context': f"Previously asked but {unanswered['reason']}",
                            'importance': 'high',
                            'clarification': ''
                        })
                if delta.get('new_questions'):
                    all_questions.extend(delta['new_questions'])

                questions_path = expert_dir / "questions.json"
                questions_path.write_text(json.dumps(all_questions, indent=2))
                print(f"✅ Generated: {questions_path}")
            return

        # Load previous state
        with open(prev_state_path) as f:
            previous_state = json.load(f)

        # Merge delta with previous state
        merged_state = merge_delta_with_state(previous_state, delta)
        merged_state['expert_name'] = expert_name

        # Generate new state JSON (in expert subdirectory)
        state_path = expert_dir / "state.json"
        state_path.write_text(json.dumps(merged_state, indent=2))
        print(f"✅ Generated merged state: {state_path}")

        # Generate questions JSON (unanswered + new, in expert subdirectory)
        if merged_state.get('questions'):
            questions_path = expert_dir / "questions.json"
            questions_path.write_text(json.dumps(merged_state['questions'], indent=2))
            print(f"✅ Generated: {questions_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse expert review markdown to JSON")
    parser.add_argument("--markdown", type=Path, required=True, help="Path to review markdown")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory")
    parser.add_argument("--expert", type=str, required=True, help="Expert name")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration number (1=full, 2+=delta)")
    parser.add_argument("--workspace", type=Path, help="Workspace root (required for iteration 2+ to load previous state)")

    args = parser.parse_args()
    parse_expert_review(args.markdown, args.output_dir, args.expert, args.iteration, args.workspace)


if __name__ == "__main__":
    main()
