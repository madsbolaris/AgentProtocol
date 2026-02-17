"""
Unit tests for parsers/artifact_review.py

Tests artifact review parsing including:
- ArtifactReviewParser class
- Dataclasses: Tweak, CriticalIssue, Question, ArtifactReview
- parse_decision_section() - Decision, confidence, rationale, expert extraction
- parse_tweaks() - Minor tweaks parsing
- parse_critical_issues() - Critical issues parsing
- parse_questions() - Questions for user parsing
- parse_artifact_review() - Main parser
- aggregate_reviews() - Multi-expert aggregation

Target coverage: 80%+
"""
import pytest
from pathlib import Path
import json
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from parsers.artifact_review import (
    ArtifactReviewParser,
    Tweak,
    CriticalIssue,
    Question,
    ArtifactReview,
    parse_artifact_review,
    aggregate_reviews
)


class TestTweakDataclass:
    """Test Tweak dataclass."""

    @pytest.mark.medium
    def test_tweak_creation(self):
        """Test creating Tweak instance."""
        tweak = Tweak(
            title="Fix Typo",
            section="Introduction",
            issue="Spelling error",
            suggestion="Correct the spelling"
        )

        assert tweak.title == "Fix Typo"
        assert tweak.section == "Introduction"
        assert tweak.issue == "Spelling error"
        assert tweak.suggestion == "Correct the spelling"


class TestCriticalIssueDataclass:
    """Test CriticalIssue dataclass."""

    @pytest.mark.medium
    def test_critical_issue_creation(self):
        """Test creating CriticalIssue instance."""
        issue = CriticalIssue(
            title="Architecture Flaw",
            issue="Missing error handling",
            why_critical="Will cause crashes",
            evidence="Lines 45-60 have no error checks"
        )

        assert issue.title == "Architecture Flaw"
        assert issue.issue == "Missing error handling"
        assert issue.why_critical == "Will cause crashes"
        assert issue.evidence == "Lines 45-60 have no error checks"


class TestQuestionDataclass:
    """Test Question dataclass."""

    @pytest.mark.medium
    def test_question_creation(self):
        """Test creating Question instance."""
        question = Question(
            question="What is the deployment strategy?",
            context="Need clarification on infrastructure",
            importance="high"
        )

        assert question.question == "What is the deployment strategy?"
        assert question.context == "Need clarification on infrastructure"
        assert question.importance == "high"


class TestArtifactReviewDataclass:
    """Test ArtifactReview dataclass."""

    @pytest.mark.medium
    def test_artifact_review_approve(self):
        """Test creating ArtifactReview with approve decision."""
        review = ArtifactReview(
            expert="typescript",
            decision="approve",
            confidence="high",
            rationale="Looks good to me"
        )

        assert review.expert == "typescript"
        assert review.decision == "approve"
        assert review.confidence == "high"
        assert review.rationale == "Looks good to me"
        assert review.tweaks is None
        assert review.critical_issues is None
        assert review.questions is None

    @pytest.mark.medium
    def test_artifact_review_minor_tweaks(self):
        """Test creating ArtifactReview with minor_tweaks decision."""
        tweak = Tweak("Fix", "Section", "Issue", "Suggestion")
        review = ArtifactReview(
            expert="python",
            decision="minor_tweaks",
            confidence="medium",
            rationale="Minor fixes needed",
            tweaks=[tweak]
        )

        assert review.decision == "minor_tweaks"
        assert len(review.tweaks) == 1
        assert review.critical_issues is None

class TestArtifactReviewParserInit:
    """Test ArtifactReviewParser initialization."""

    @pytest.mark.high
    def test_parser_initialization(self, tmp_path):
        """Test parser initialization with markdown file."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good work.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)

        assert parser.markdown is not None
        assert len(parser.sections) > 0

    @pytest.mark.medium
    def test_split_sections(self, tmp_path):
        """Test section splitting."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

Content here.

## Suggested Tweaks

More content.

## Critical Issues

Issues here.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)

        assert "Decision: Approve" in parser.sections
        assert "Suggested Tweaks" in parser.sections
        assert "Critical Issues" in parser.sections


class TestParseDecisionSection:
    """Test parse_decision_section function."""

    @pytest.mark.high
    def test_parse_approve_decision(self, tmp_path):
        """Test parsing approve decision."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** The artifact is well-structured and comprehensive.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.parse_decision_section()

        assert result["decision"] == "approve"
        assert result["confidence"] == "high"
        assert "well-structured" in result["rationale"]
        assert result["expert"] == "typescript"

    @pytest.mark.high
    def test_parse_minor_tweaks_decision(self, tmp_path):
        """Test parsing minor tweaks decision."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs small improvements.
**Expert:** python
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.parse_decision_section()

        assert result["decision"] == "minor_tweaks"
        assert result["confidence"] == "medium"
        assert result["expert"] == "python"

    @pytest.mark.high
    @pytest.mark.medium
    def test_parse_decision_default_confidence(self, tmp_path):
        """Test parsing decision with missing confidence defaults to medium."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Rationale:** Good.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.parse_decision_section()

        assert result["confidence"] == "medium"

    @pytest.mark.medium
    def test_parse_decision_default_expert(self, tmp_path):
        """Test parsing decision with missing expert defaults to unknown."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good work.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.parse_decision_section()

        assert result["expert"] == "unknown"

    @pytest.mark.medium
    def test_parse_decision_multiline_rationale(self, tmp_path):
        """Test parsing multi-line rationale."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** This artifact is excellent because:
- It follows best practices
- The structure is clear
- Documentation is comprehensive
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.parse_decision_section()

        assert "best practices" in result["rationale"]
        assert "structure is clear" in result["rationale"]
        assert result["rationale"].count('\n') >= 2

    @pytest.mark.medium
    def test_parse_decision_no_valid_section(self, tmp_path):
        """Test parsing when no valid decision section exists."""
        review_file = tmp_path / "review.md"
        content = """## Some Other Section

Content here.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)

        with pytest.raises(ValueError, match="No valid decision section found"):
            parser.parse_decision_section()


class TestParseTweaks:
    """Test parse_tweaks function."""

    @pytest.mark.high
    def test_parse_single_tweak(self, tmp_path):
        """Test parsing a single tweak."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs fixes.
**Expert:** typescript

## Suggested Tweaks

### Fix Typo in Introduction

**Section:** Introduction
**Issue:** Spelling error in first paragraph.
**Suggestion:** Change "teh" to "the".
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        tweaks = parser.parse_tweaks()

        assert len(tweaks) == 1
        assert tweaks[0].title == "Fix Typo in Introduction"
        assert tweaks[0].section == "Introduction"
        assert "Spelling error" in tweaks[0].issue
        assert "teh" in tweaks[0].suggestion

    @pytest.mark.high
    def test_parse_multiple_tweaks(self, tmp_path):
        """Test parsing multiple tweaks."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs fixes.
**Expert:** python

## Suggested Tweaks

### Fix Documentation

**Section:** API Reference
**Issue:** Missing parameter docs.
**Suggestion:** Add parameter descriptions.

### Improve Error Messages

**Section:** Error Handling
**Issue:** Generic error messages.
**Suggestion:** Make errors more specific.

### Update Examples

**Section:** Examples
**Issue:** Examples are outdated.
**Suggestion:** Update to latest syntax.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        tweaks = parser.parse_tweaks()

        assert len(tweaks) == 3
        assert tweaks[0].title == "Fix Documentation"
        assert tweaks[1].title == "Improve Error Messages"
        assert tweaks[2].title == "Update Examples"

    @pytest.mark.medium
    def test_parse_tweak_multiline_content(self, tmp_path):
        """Test parsing tweak with multi-line issue and suggestion."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs fixes.
**Expert:** dotnet

## Suggested Tweaks

### Complex Fix

**Section:** Architecture
**Issue:**
The current implementation has several issues:
- Missing validation
- No error handling
- Poor performance
**Suggestion:**
Refactor to:
1. Add input validation
2. Implement proper error handling
3. Optimize the algorithm
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        tweaks = parser.parse_tweaks()

        assert len(tweaks) == 1
        assert "Missing validation" in tweaks[0].issue
        assert "Add input validation" in tweaks[0].suggestion

    @pytest.mark.medium
    def test_parse_empty_tweaks_section(self, tmp_path):
        """Test parsing when Suggested Tweaks section is empty."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        tweaks = parser.parse_tweaks()

        assert tweaks == []

    @pytest.mark.medium
    def test_parse_tweak_default_section(self, tmp_path):
        """Test parsing tweak without section field defaults to Unknown."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs fixes.
**Expert:** typescript

## Suggested Tweaks

### Fix Something

**Issue:** There is an issue.
**Suggestion:** Fix it.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        tweaks = parser.parse_tweaks()

        assert len(tweaks) == 1
        assert tweaks[0].section == "Unknown"


class TestParseCriticalIssues:
    """Test parse_critical_issues function."""

    @pytest.mark.high
    def test_parse_single_critical_issue(self, tmp_path):
        """Test parsing a single critical issue."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Cannot approve.
**Expert:** typescript

## Critical Issues

### Missing Error Handling

**Issue:** No error handling in core functions.
**Why Critical:** Will cause production crashes.
**Evidence:** Functions at lines 45-60 have no try-catch blocks.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        issues = parser.parse_critical_issues()

        assert len(issues) == 1
        assert issues[0].title == "Missing Error Handling"
        assert "No error handling" in issues[0].issue
        assert "production crashes" in issues[0].why_critical
        assert "lines 45-60" in issues[0].evidence

    @pytest.mark.high
    def test_parse_multiple_critical_issues(self, tmp_path):
        """Test parsing multiple critical issues."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Multiple critical flaws.
**Expert:** python

## Critical Issues

### Security Vulnerability

**Issue:** SQL injection risk.
**Why Critical:** Data breach potential.
**Evidence:** Direct string concatenation in queries.

### Performance Problem

**Issue:** O(n^2) algorithm in hot path.
**Why Critical:** Won't scale to production data.
**Evidence:** Nested loops in data processing.

### Data Loss Risk

**Issue:** No transaction handling.
**Why Critical:** Can corrupt database.
**Evidence:** Multiple writes without transactions.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        issues = parser.parse_critical_issues()

        assert len(issues) == 3
        assert issues[0].title == "Security Vulnerability"
        assert issues[1].title == "Performance Problem"
        assert issues[2].title == "Data Loss Risk"

    @pytest.mark.medium
    def test_parse_critical_issue_multiline(self, tmp_path):
        """Test parsing critical issue with multi-line content."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Critical flaw.
**Expert:** dotnet

## Critical Issues

### Complex Architecture Flaw

**Issue:**
The architecture has fundamental problems:
- Tight coupling between layers
- No separation of concerns
- Hard to test
**Why Critical:**
This will make the system:
- Unmaintainable
- Difficult to extend
- Prone to bugs
**Evidence:**
Multiple code smells found:
- God classes in core module
- Global state everywhere
- No dependency injection
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        issues = parser.parse_critical_issues()

        assert len(issues) == 1
        assert "Tight coupling" in issues[0].issue
        assert "Unmaintainable" in issues[0].why_critical
        assert "God classes" in issues[0].evidence

    @pytest.mark.medium
    def test_parse_empty_critical_issues_section(self, tmp_path):
        """Test parsing when Critical Issues section is empty."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        issues = parser.parse_critical_issues()

        assert issues == []


class TestParseQuestions:
    """Test parse_questions function."""

    @pytest.mark.high
    def test_parse_single_question(self, tmp_path):
        """Test parsing a single question."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Need clarification.
**Expert:** typescript

## Questions for User

### What is the expected load?

**Context:** Performance optimization depends on expected traffic.
**Importance:** high
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        questions = parser.parse_questions()

        assert len(questions) == 1
        assert questions[0].question == "What is the expected load?"
        assert "Performance optimization" in questions[0].context
        assert questions[0].importance == "high"

    @pytest.mark.high
    def test_parse_multiple_questions(self, tmp_path):
        """Test parsing multiple questions."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Need answers.
**Expert:** python

## Questions for User

### What is the deployment strategy?

**Context:** Need to know infrastructure requirements.
**Importance:** high

### What is the backup plan?

**Context:** Disaster recovery strategy unclear.
**Importance:** medium

### Should we support legacy browsers?

**Context:** Browser compatibility requirements.
**Importance:** low
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        questions = parser.parse_questions()

        assert len(questions) == 3
        assert questions[0].question == "What is the deployment strategy?"
        assert questions[1].question == "What is the backup plan?"
        assert questions[2].question == "Should we support legacy browsers?"

    @pytest.mark.medium
    def test_parse_question_multiline_context(self, tmp_path):
        """Test parsing question with multi-line context."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Need info.
**Expert:** dotnet

## Questions for User

### How should we handle migrations?

**Context:**
Database migration strategy is unclear:
- Should we use automated migrations?
- What about rollback procedures?
- How to handle data transformations?
**Importance:** high
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        questions = parser.parse_questions()

        assert len(questions) == 1
        assert "automated migrations" in questions[0].context
        assert "rollback procedures" in questions[0].context

    @pytest.mark.medium
    def test_parse_question_default_importance(self, tmp_path):
        """Test parsing question without importance defaults to medium."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Veto

**Confidence:** high
**Rationale:** Need clarification.
**Expert:** typescript

## Questions for User

### What about testing?

**Context:** Testing strategy unclear.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        questions = parser.parse_questions()

        assert len(questions) == 1
        assert questions[0].importance == "medium"

    @pytest.mark.medium
    def test_parse_empty_questions_section(self, tmp_path):
        """Test parsing when Questions for User section is empty."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        questions = parser.parse_questions()

        assert questions == []


class TestParserParse:
    """Test ArtifactReviewParser.parse() method."""

    @pytest.mark.high
    def test_parse_approve_review(self, tmp_path):
        """Test parsing complete approve review."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Excellent work. All requirements met.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        review = parser.parse()

        assert review.expert == "typescript"
        assert review.decision == "approve"
        assert review.confidence == "high"
        assert "Excellent work" in review.rationale
        assert review.tweaks is None
        assert review.critical_issues is None
        assert review.questions is None

    @pytest.mark.high
    def test_parse_minor_tweaks_review(self, tmp_path):
        """Test parsing complete minor_tweaks review."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Good overall, minor fixes needed.
**Expert:** python

## Suggested Tweaks

### Fix Documentation

**Section:** API Docs
**Issue:** Missing params.
**Suggestion:** Add param docs.

### Update Examples

**Section:** Examples
**Issue:** Outdated.
**Suggestion:** Update syntax.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        review = parser.parse()

        assert review.decision == "minor_tweaks"
        assert len(review.tweaks) == 2
        assert review.critical_issues is None
        assert review.questions is None


class TestParserToJson:
    """Test ArtifactReviewParser.to_json() method."""

    @pytest.mark.high
    def test_to_json_approve(self, tmp_path):
        """Test converting approve review to JSON."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good work.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.to_json()

        assert result["decision"] == "approve"
        assert result["confidence"] == "high"
        assert result["expert"] == "typescript"
        assert "tweaks" not in result
        assert "critical_issues" not in result
        assert "questions" not in result

    @pytest.mark.high
    def test_to_json_minor_tweaks(self, tmp_path):
        """Test converting minor_tweaks review to JSON."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Minor Tweaks

**Confidence:** medium
**Rationale:** Needs fixes.
**Expert:** python

## Suggested Tweaks

### Fix Something

**Section:** Section A
**Issue:** Problem found.
**Suggestion:** Fix it.
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)
        result = parser.to_json()

        assert result["decision"] == "minor_tweaks"
        assert "tweaks" in result
        assert len(result["tweaks"]) == 1
        assert result["tweaks"][0]["title"] == "Fix Something"
        assert "critical_issues" not in result


class TestParseArtifactReview:
    """Test parse_artifact_review main function."""

    @pytest.mark.high
    def test_parse_and_save_review(self, tmp_path, capsys):
        """Test parsing and saving artifact review to JSON."""
        markdown_path = tmp_path / "artifact-review-typescript.md"
        output_path = tmp_path / "artifact-review-typescript.json"

        content = """## Decision: Approve

**Confidence:** high
**Rationale:** All requirements met.
**Expert:** typescript
"""
        markdown_path.write_text(content)

        result = parse_artifact_review(markdown_path, output_path)

        # Check return value
        assert result["decision"] == "approve"
        assert result["expert"] == "typescript"

        # Check file was written
        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["decision"] == "approve"
        assert data["confidence"] == "high"

        # Check output
        captured = capsys.readouterr()
        assert "Parsed artifact review" in captured.out
        assert "typescript" in captured.out

    @pytest.mark.medium
    def test_parse_creates_parent_directories(self, tmp_path):
        """Test that parse creates parent directories."""
        markdown_path = tmp_path / "input" / "review.md"
        output_path = tmp_path / "deep" / "nested" / "output.json"

        markdown_path.parent.mkdir(parents=True)
        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good.
**Expert:** python
"""
        markdown_path.write_text(content)

        parse_artifact_review(markdown_path, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestAggregateReviews:
    """Test aggregate_reviews function."""

    @pytest.mark.high
    def test_aggregate_all_approvals(self, tmp_path, capsys):
        """Test aggregating when all experts approve."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create review files
        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))
        (workspace / "artifact-review-python.json").write_text(json.dumps({
            "expert": "python",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))

        output_path = workspace / "artifact-review-result.json"
        result = aggregate_reviews(workspace, output_path)

        assert result["status"] == "approved"
        assert result["total_experts"] == 2
        assert result["approvals"] == 2
        assert result["minor_tweaks_count"] == 0
        assert set(result["approved_by"]) == {"typescript", "python"}

        # Check file was written
        assert output_path.exists()

        # Check output
        captured = capsys.readouterr()
        assert "Aggregated artifact reviews" in captured.out
        assert "approved" in captured.out.lower()

    @pytest.mark.high
    def test_aggregate_with_minor_tweaks(self, tmp_path):
        """Test aggregating with minor tweaks."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))
        (workspace / "artifact-review-python.json").write_text(json.dumps({
            "expert": "python",
            "decision": "minor_tweaks",
            "confidence": "medium",
            "rationale": "Needs fixes",
            "tweaks": [
                {"title": "Fix Typo", "section": "Intro", "issue": "Typo", "suggestion": "Fix it"}
            ]
        }))

        output_path = workspace / "artifact-review-result.json"
        result = aggregate_reviews(workspace, output_path)

        assert result["status"] == "minor_tweaks"
        assert result["approvals"] == 1
        assert result["minor_tweaks_count"] == 1
        assert "python" in result["tweaks_from"]
        assert len(result["all_tweaks"]) == 1
        assert result["all_tweaks"][0]["expert"] == "python"

    @pytest.mark.high
    @pytest.mark.medium
    @pytest.mark.medium
    def test_aggregate_no_reviews(self, tmp_path):
        """Test aggregating when no review files exist."""
        workspace = tmp_path / "empty-workspace"
        workspace.mkdir()

        output_path = workspace / "result.json"

        with pytest.raises(FileNotFoundError, match="No artifact review JSON files found"):
            aggregate_reviews(workspace, output_path)

    @pytest.mark.medium
    def test_aggregate_creates_parent_directories(self, tmp_path):
        """Test that aggregate creates parent directories."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))

        output_path = workspace / "deep" / "nested" / "result.json"
        aggregate_reviews(workspace, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.medium
    def test_parse_empty_markdown(self, tmp_path):
        """Test parsing empty markdown file."""
        review_file = tmp_path / "empty.md"
        review_file.write_text("")

        parser = ArtifactReviewParser(review_file)

        with pytest.raises(ValueError, match="No valid decision section found"):
            parser.parse_decision_section()

    @pytest.mark.medium
    def test_parse_malformed_decision_header(self, tmp_path):
        """Test parsing with malformed decision header."""
        review_file = tmp_path / "review.md"
        content = """## Decision: Unknown Type

**Confidence:** high
**Rationale:** Test.
**Expert:** typescript
"""
        review_file.write_text(content)

        parser = ArtifactReviewParser(review_file)

        # Unknown decision types won't match any of the valid headers
        # so it will raise "No valid decision section found"
        with pytest.raises(ValueError, match="No valid decision section found"):
            parser.parse_decision_section()

    @pytest.mark.medium
    def test_aggregate_with_missing_fields(self, tmp_path):
        """Test aggregating reviews with missing optional fields."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Review missing some fields
        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "minor_tweaks",
            "confidence": "medium",
            "rationale": "Needs fixes"
            # Missing tweaks field
        }))

        output_path = workspace / "result.json"
        result = aggregate_reviews(workspace, output_path)

        # Should handle missing fields gracefully
        assert result["status"] == "minor_tweaks"
        assert result["all_tweaks"] == []  # No tweaks collected


class TestMainFunction:
    """Test main function and CLI argument parsing."""

    @pytest.mark.low
    def test_main_single_file_mode(self, tmp_path, monkeypatch):
        """Test main function in single file parsing mode."""
        import sys
        from parsers import artifact_review

        markdown_path = tmp_path / "review.md"
        output_path = tmp_path / "output.json"

        content = """## Decision: Approve

**Confidence:** high
**Rationale:** Good.
**Expert:** typescript
"""
        markdown_path.write_text(content)

        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", [
            "artifact_review.py",
            "--markdown", str(markdown_path),
            "--output", str(output_path)
        ])

        # Call main
        artifact_review.main()

        # Check output file was created
        assert output_path.exists()

    @pytest.mark.low
    def test_main_aggregate_mode(self, tmp_path, monkeypatch):
        """Test main function in aggregate mode."""
        import sys
        from parsers import artifact_review

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))

        output_path = workspace / "result.json"

        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", [
            "artifact_review.py",
            "--aggregate", str(workspace),
            "--aggregate-output", str(output_path)
        ])

        # Call main
        artifact_review.main()

        # Check output file was created
        assert output_path.exists()

    @pytest.mark.low
    def test_main_aggregate_default_output(self, tmp_path, monkeypatch):
        """Test main function aggregate mode with default output path."""
        import sys
        from parsers import artifact_review

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        (workspace / "artifact-review-typescript.json").write_text(json.dumps({
            "expert": "typescript",
            "decision": "approve",
            "confidence": "high",
            "rationale": "Good"
        }))

        # Mock sys.argv (no --aggregate-output specified)
        monkeypatch.setattr(sys, "argv", [
            "artifact_review.py",
            "--aggregate", str(workspace)
        ])

        # Call main
        artifact_review.main()

        # Check default output file was created
        default_output = workspace / "artifact-review-result.json"
        assert default_output.exists()
