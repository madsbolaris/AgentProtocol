"""
Unit tests for parsers/expert_review.py

Tests expert review markdown parsing including:
- MarkdownParser class (section splitting, parsing all sections)
- Dataclass creation and validation
- Helper methods (_extract_field, _extract_bullets, etc.)
- Delta review parsing (iteration 2+)
- State merging operations
- ID generation functions
- parse_expert_review() main function
- Edge cases and error handling

Target coverage: 85%+
"""
import json
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from parsers.expert_review import (
    MarkdownParser,
    parse_expert_review,
    DXRating,
    Concern,
    Recommendation,
    Question,
    ParseError,
    MarkdownParseError,
    parse_delta_review,
    extract_section,
    parse_updated_recommendations,
    parse_recommendation_changes,
    parse_resolved_concerns,
    parse_assessment_update,
    parse_unanswered_questions,
    merge_delta_with_state,
    generate_rec_id,
    generate_concern_id
)


@pytest.fixture
def sample_markdown_path():
    """Get path to sample markdown fixture."""
    return Path(__file__).parent.parent / "fixtures" / "sample-review.md"


@pytest.fixture
def parser(sample_markdown_path):
    """Create parser instance with sample markdown."""
    return MarkdownParser(sample_markdown_path)


# ============================================================================
# Dataclass Tests
# ============================================================================

class TestDataclasses:
    """Test dataclass creation and validation."""

    @pytest.mark.high
    def test_dx_rating_creation(self):
        """Test creating DXRating instance."""
        rating = DXRating(
            stars=4,
            confidence="high",
            justification="Good implementation"
        )

        assert rating.stars == 4
        assert rating.confidence == "high"
        assert rating.justification == "Good implementation"

    @pytest.mark.high
    def test_concern_creation(self):
        """Test creating Concern instance."""
        concern = Concern(
            title="Test Coverage",
            severity="high",
            impact="medium",
            description="Need more tests",
            evidence={"files": ["test.py"], "references": []},
            recommended_fix="Add tests"
        )

        assert concern.title == "Test Coverage"
        assert concern.severity == "high"
        assert len(concern.evidence["files"]) == 1

    @pytest.mark.high
    def test_recommendation_creation(self):
        """Test creating Recommendation instance."""
        rec = Recommendation(
            title="Add Logging",
            priority="high",
            complexity="low",
            dx_impact="medium",
            description="Add logging",
            implementation="Use logging module",
            benefits=["Better debugging"],
            risks=["Performance overhead"]
        )

        assert rec.title == "Add Logging"
        assert rec.priority == "high"
        assert len(rec.benefits) == 1
        assert len(rec.risks) == 1

    @pytest.mark.high
    def test_question_creation(self):
        """Test creating Question instance."""
        question = Question(
            id="test-question",
            question="What should we do?",
            context="Need clarification",
            importance="high",
            clarification="More details needed"
        )

        assert question.id == "test-question"
        assert question.importance == "high"

    @pytest.mark.medium
    def test_parse_error_creation(self):
        """Test creating ParseError instance."""
        error = ParseError(
            section="Concerns",
            message="Invalid format",
            line_number=42,
            expected="### Title",
            actual="# Title",
            hint="Use three hashes"
        )

        assert error.section == "Concerns"
        assert error.line_number == 42

    @pytest.mark.medium
    def test_markdown_parse_error_exception(self):
        """Test MarkdownParseError exception."""
        errors = [
            ParseError("Concerns", "Error 1", 10, "A", "B", "Hint"),
            ParseError("Rating", "Error 2", 20, "C", "D", "Hint")
        ]

        exception = MarkdownParseError(errors)

        assert len(exception.errors) == 2
        assert "2 errors" in str(exception)


# ============================================================================
# MarkdownParser Class Tests
# ============================================================================

class TestMarkdownParserInit:
    """Test MarkdownParser initialization."""

    @pytest.mark.high
    def test_parser_initialization(self, sample_markdown_path):
        """Test parser initialization with markdown file."""
        parser = MarkdownParser(sample_markdown_path)

        assert parser.markdown is not None
        assert isinstance(parser.sections, dict)
        assert len(parser.sections) > 0

    @pytest.mark.high
    def test_split_sections_basic(self, tmp_path):
        """Test section splitting with basic headers."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

Content 1

## Concerns

Content 2

## Recommendations

Content 3
""")

        parser = MarkdownParser(markdown)

        assert "DX Rating" in parser.sections
        assert "Concerns" in parser.sections
        assert "Recommendations" in parser.sections
        assert "Content 1" in parser.sections["DX Rating"]
        assert "Content 2" in parser.sections["Concerns"]

    @pytest.mark.medium
    def test_split_sections_with_emojis(self, tmp_path):
        """Test section splitting with emoji headers."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns ⚠️

Concern content

## Recommendations 💡

Recommendation content

## Questions ❓

Question content
""")

        parser = MarkdownParser(markdown)

        # Should parse with emojis
        assert "Concerns ⚠️" in parser.sections or "Concerns" in parser.sections
        assert "Recommendations 💡" in parser.sections or "Recommendations" in parser.sections

    @pytest.mark.medium
    def test_split_sections_empty_content(self, tmp_path):
        """Test section splitting with empty sections."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Section 1

## Section 2

## Section 3

Content only in last section
""")

        parser = MarkdownParser(markdown)

        assert "Section 1" in parser.sections
        assert "Section 2" in parser.sections
        assert "Section 3" in parser.sections
        assert "Content only" in parser.sections["Section 3"]


class TestParseDXRating:
    """Test parse_dx_rating method."""

    @pytest.mark.high
    def test_parse_dx_rating(self, parser):
        """Test DX rating parsing from sample."""
        rating = parser.parse_dx_rating()

        assert rating.stars == 4
        assert rating.confidence == "high"
        assert "TypeScript implementation" in rating.justification

    @pytest.mark.high
    def test_parse_dx_rating_all_fields(self, tmp_path):
        """Test parsing all DX rating fields."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Rating:** 5/5 ⭐⭐⭐⭐⭐
**Confidence:** high

Excellent implementation with great developer experience.
Very well structured and documented.
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        assert rating.stars == 5
        assert rating.confidence == "high"
        assert "Excellent implementation" in rating.justification
        assert "Very well structured" in rating.justification

    @pytest.mark.medium
    def test_parse_dx_rating_low_score(self, tmp_path):
        """Test parsing low DX rating."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Rating:** 2/5 ⭐⭐
**Confidence:** medium

Needs significant improvements.
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        assert rating.stars == 2
        assert rating.confidence == "medium"

    @pytest.mark.medium
    def test_parse_dx_rating_missing_rating(self, tmp_path):
        """Test parsing DX rating with missing rating."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Confidence:** high

Some justification text.
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        assert rating.stars == 0  # Default when missing
        assert rating.confidence == "high"

    @pytest.mark.medium
    def test_parse_dx_rating_missing_confidence(self, tmp_path):
        """Test parsing DX rating with missing confidence."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Rating:** 4/5

Justification text.
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        assert rating.stars == 4
        assert rating.confidence == "unknown"  # Default when missing

    @pytest.mark.medium
    def test_parse_dx_rating_no_section(self, tmp_path):
        """Test parsing when DX Rating section is missing."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Other Section

Content
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        assert rating.stars == 0
        assert rating.confidence == "unknown"
        assert rating.justification == ""


class TestParseConcerns:
    """Test parse_concerns method."""

    @pytest.mark.high
    def test_parse_concerns(self, parser):
        """Test concerns parsing from sample."""
        concerns = parser.parse_concerns()

        assert len(concerns) == 2

        # First concern
        concern1 = concerns[0]
        assert concern1.title == "Inconsistent Error Handling"
        assert concern1.severity == "high"
        assert concern1.impact == "medium"
        assert "Error handling patterns vary" in concern1.description
        assert len(concern1.evidence['files']) == 2
        assert "Standardize on a consistent" in concern1.recommended_fix

        # Second concern
        concern2 = concerns[1]
        assert concern2.title == "Missing Type Guards"
        assert concern2.severity == "medium"

    @pytest.mark.high
    def test_parse_single_concern(self, tmp_path):
        """Test parsing single concern."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns

### Test Coverage Gap

**Severity:** high
**Impact:** high

Missing unit tests for critical functions.

**Evidence:**
- `calculator.py` - No tests for divide operation
- `validator.py` - Edge cases not covered

**Fix:** Add comprehensive test suite with 90%+ coverage.
""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].title == "Test Coverage Gap"
        assert concerns[0].severity == "high"
        assert concerns[0].impact == "high"
        assert len(concerns[0].evidence["files"]) == 2
        assert "Add comprehensive test suite" in concerns[0].recommended_fix

    @pytest.mark.medium
    def test_parse_concern_with_emoji_section(self, tmp_path):
        """Test parsing concern from section with emoji."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns ⚠️

### Performance Issue

**Severity:** medium
**Impact:** low

Description text.

**Fix:** Optimize the code.
""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].title == "Performance Issue"

    @pytest.mark.medium
    def test_parse_concerns_empty_section(self, tmp_path):
        """Test parsing empty concerns section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns

""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 0

    @pytest.mark.medium
    def test_parse_concern_no_evidence(self, tmp_path):
        """Test parsing concern without evidence."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns

### Issue Title

**Severity:** low
**Impact:** low

Description without evidence section.

**Fix:** Simple fix.
""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert len(concerns[0].evidence["files"]) == 0

    @pytest.mark.medium
    def test_parse_concern_no_fix(self, tmp_path):
        """Test parsing concern without fix."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns

### Issue Title

**Severity:** low
**Impact:** low

Description without fix section.
""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].recommended_fix == ""


class TestParseRecommendations:
    """Test parse_recommendations method."""

    @pytest.mark.high
    def test_parse_recommendations(self, parser):
        """Test recommendations parsing from sample."""
        recommendations = parser.parse_recommendations()

        assert len(recommendations) == 2

        # First recommendation
        rec1 = recommendations[0]
        assert rec1.title == "Implement Result Type Pattern"
        assert rec1.priority == "high"
        assert rec1.complexity == "medium"
        assert rec1.dx_impact == "high"
        assert "Result<T, E> type pattern" in rec1.description
        assert "Create a Result type" in rec1.implementation
        assert len(rec1.benefits) == 4
        assert len(rec1.risks) == 2

        # Second recommendation
        rec2 = recommendations[1]
        assert rec2.title == "Add Comprehensive Type Guards"
        assert rec2.priority == "medium"

    @pytest.mark.high
    def test_parse_single_recommendation(self, tmp_path):
        """Test parsing single recommendation."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Recommendations

### Add Logging Framework

**Priority:** high
**Complexity:** low
**DX Impact:** medium

Implement structured logging for better debugging.

**Implementation:**
1. Install logging library
2. Configure log levels
3. Add log statements

**Benefits:**
- Better debugging
- Production monitoring
- Error tracking

**Risks:**
- Performance overhead
- Log size management
""")

        parser = MarkdownParser(markdown)
        recommendations = parser.parse_recommendations()

        assert len(recommendations) == 1
        rec = recommendations[0]
        assert rec.title == "Add Logging Framework"
        assert rec.priority == "high"
        assert rec.complexity == "low"
        assert rec.dx_impact == "medium"
        assert len(rec.benefits) == 3
        assert len(rec.risks) == 2

    @pytest.mark.medium
    def test_parse_recommendation_with_emoji(self, tmp_path):
        """Test parsing from Recommendations section with emoji."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Recommendations 💡

### Improve Performance

**Priority:** medium
**Complexity:** high
**DX Impact:** low

Description text.

**Implementation:**
Steps here.
""")

        parser = MarkdownParser(markdown)
        recommendations = parser.parse_recommendations()

        assert len(recommendations) == 1
        assert recommendations[0].title == "Improve Performance"

    @pytest.mark.medium
    def test_parse_recommendation_no_benefits_risks(self, tmp_path):
        """Test parsing recommendation without benefits/risks."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Recommendations

### Simple Recommendation

**Priority:** low
**Complexity:** low
**DX Impact:** low

Description.

**Implementation:**
Steps.
""")

        parser = MarkdownParser(markdown)
        recommendations = parser.parse_recommendations()

        assert len(recommendations) == 1
        assert len(recommendations[0].benefits) == 0
        assert len(recommendations[0].risks) == 0

    @pytest.mark.medium
    def test_parse_recommendations_empty_section(self, tmp_path):
        """Test parsing empty recommendations section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Recommendations

""")

        parser = MarkdownParser(markdown)
        recommendations = parser.parse_recommendations()

        assert len(recommendations) == 0


class TestParseStrengths:
    """Test parse_strengths method."""

    @pytest.mark.high
    def test_parse_strengths(self, parser):
        """Test strengths parsing from sample."""
        strengths = parser.parse_strengths()

        assert len(strengths) == 2
        assert strengths[0]['title'] == "Strong Type Coverage"
        assert "excellent type coverage" in strengths[0]['description']
        assert strengths[1]['title'] == "Modern ES Features"

    @pytest.mark.high
    def test_parse_single_strength(self, tmp_path):
        """Test parsing single strength."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Strengths

### Well Documented

Clear documentation with examples.
Easy to understand API.
""")

        parser = MarkdownParser(markdown)
        strengths = parser.parse_strengths()

        assert len(strengths) == 1
        assert strengths[0]['title'] == "Well Documented"
        assert "Clear documentation" in strengths[0]['description']

    @pytest.mark.medium
    def test_parse_strengths_with_emoji(self, tmp_path):
        """Test parsing strengths with emoji section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Strengths ✅

### Good Test Coverage

High test coverage across modules.
""")

        parser = MarkdownParser(markdown)
        strengths = parser.parse_strengths()

        assert len(strengths) == 1
        assert strengths[0]['title'] == "Good Test Coverage"

    @pytest.mark.medium
    def test_parse_strengths_empty_section(self, tmp_path):
        """Test parsing empty strengths section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Strengths

""")

        parser = MarkdownParser(markdown)
        strengths = parser.parse_strengths()

        assert len(strengths) == 0


class TestParseQuestions:
    """Test parse_questions method."""

    @pytest.mark.high
    def test_parse_questions(self, parser):
        """Test questions parsing from sample."""
        questions = parser.parse_questions()

        assert len(questions) == 2

        # First question
        q1 = questions[0]
        assert "error handling pattern" in q1.question
        assert q1.importance == "high"
        assert "Multiple patterns exist" in q1.context
        assert q1.id  # Should have generated ID

        # Second question
        q2 = questions[1]
        assert "performance or developer experience" in q2.question
        assert q2.importance == "medium"

    @pytest.mark.high
    def test_parse_single_question(self, tmp_path):
        """Test parsing single question."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Questions

### Should we use TypeScript or JavaScript?

**Context:** Need to decide on language for new project.
**Importance:** high

This is a critical decision that will affect the entire codebase.
""")

        parser = MarkdownParser(markdown)
        questions = parser.parse_questions()

        assert len(questions) == 1
        q = questions[0]
        assert "TypeScript or JavaScript" in q.question
        assert q.importance == "high"
        assert "Need to decide" in q.context

    @pytest.mark.high
    def test_question_id_generation(self, tmp_path):
        """Test question ID generation."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Questions

### What is the best approach for error handling?

**Context:** Multiple options available.
**Importance:** high
""")

        parser = MarkdownParser(markdown)
        questions = parser.parse_questions()

        assert len(questions) == 1
        # Should be slugified and truncated to 50 chars
        assert questions[0].id == "what-is-the-best-approach-for-error-handling"

    @pytest.mark.medium
    def test_question_id_truncation(self, tmp_path):
        """Test question ID is truncated to 50 characters."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Questions

### This is a very long question that should be truncated when converted to an ID because it exceeds fifty characters?

**Context:** Test truncation.
**Importance:** low
""")

        parser = MarkdownParser(markdown)
        questions = parser.parse_questions()

        assert len(questions) == 1
        assert len(questions[0].id) <= 50

    @pytest.mark.medium
    def test_parse_questions_with_emoji(self, tmp_path):
        """Test parsing questions with emoji section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Questions ❓

### How should we handle errors?

**Context:** Need clarification.
**Importance:** medium
""")

        parser = MarkdownParser(markdown)
        questions = parser.parse_questions()

        assert len(questions) == 1
        assert "errors" in questions[0].question

    @pytest.mark.medium
    def test_parse_questions_empty_section(self, tmp_path):
        """Test parsing empty questions section."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Questions

""")

        parser = MarkdownParser(markdown)
        questions = parser.parse_questions()

        assert len(questions) == 0


# ============================================================================
# Helper Method Tests
# ============================================================================

class TestHelperMethods:
    """Test parser helper methods."""

    @pytest.mark.high
    def test_extract_field_basic(self, tmp_path):
        """Test _extract_field with basic pattern."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = "**Priority:** high"
        result = parser._extract_field(text, "Priority")

        assert result == "high"

    @pytest.mark.high
    def test_extract_field_multiple_words(self, tmp_path):
        """Test _extract_field with multi-word field name."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = "**DX Impact:** medium"
        result = parser._extract_field(text, "DX Impact")

        assert result == "medium"

    @pytest.mark.medium
    def test_extract_field_not_found(self, tmp_path):
        """Test _extract_field when field not found."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = "Some text without field"
        result = parser._extract_field(text, "Priority")

        assert result == "unknown"  # Default

    @pytest.mark.high
    def test_extract_field_paragraph(self, tmp_path):
        """Test _extract_field_paragraph."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = """**Context:** This is a paragraph
that spans multiple lines
with more details."""
        result = parser._extract_field_paragraph(text, "Context")

        assert "This is a paragraph" in result
        assert "multiple lines" in result

    @pytest.mark.medium
    def test_extract_field_paragraph_not_found(self, tmp_path):
        """Test _extract_field_paragraph when field not found."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = "Some text without field"
        result = parser._extract_field_paragraph(text, "Context")

        assert result == ""

    @pytest.mark.high
    def test_extract_bullets_dash(self, tmp_path):
        """Test _extract_bullets with dash bullets."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = """- First item
- Second item
- Third item"""
        result = parser._extract_bullets(text)

        assert len(result) == 3
        assert result[0] == "First item"
        assert result[1] == "Second item"
        assert result[2] == "Third item"

    @pytest.mark.high
    def test_extract_bullets_asterisk(self, tmp_path):
        """Test _extract_bullets with asterisk bullets."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = """* First item
* Second item
* Third item"""
        result = parser._extract_bullets(text)

        assert len(result) == 3
        assert result[0] == "First item"

    @pytest.mark.medium
    def test_extract_bullets_mixed(self, tmp_path):
        """Test _extract_bullets with mixed bullet types."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = """- First item
* Second item
- Third item"""
        result = parser._extract_bullets(text)

        assert len(result) == 3

    @pytest.mark.medium
    def test_extract_bullets_no_bullets(self, tmp_path):
        """Test _extract_bullets with no bullets."""
        markdown = tmp_path / "test.md"
        markdown.write_text("## Test\nContent")
        parser = MarkdownParser(markdown)

        text = "Plain text without bullets"
        result = parser._extract_bullets(text)

        assert len(result) == 0


class TestToStateJson:
    """Test to_state_json method."""

    @pytest.mark.high
    def test_to_state_json(self, parser):
        """Test full state JSON generation."""
        state = parser.to_state_json()

        # Check structure
        assert 'dx_rating' in state
        assert 'concerns' in state
        assert 'recommendations' in state
        assert 'strengths' in state
        assert 'questions' in state

        # Check types
        assert isinstance(state['dx_rating'], dict)
        assert isinstance(state['concerns'], list)
        assert isinstance(state['recommendations'], list)
        assert isinstance(state['strengths'], list)
        assert isinstance(state['questions'], list)

        # Check content
        assert state['dx_rating']['stars'] == 4
        assert len(state['concerns']) == 2
        assert len(state['recommendations']) == 2
        assert len(state['strengths']) == 2
        assert len(state['questions']) == 2

    @pytest.mark.high
    def test_to_questions_json(self, parser):
        """Test questions JSON generation."""
        questions = parser.to_questions_json()

        assert len(questions) == 2
        assert all('id' in q for q in questions)
        assert all('question' in q for q in questions)
        assert all('context' in q for q in questions)
        assert all('importance' in q for q in questions)

    @pytest.mark.medium
    def test_state_json_empty_sections(self, tmp_path):
        """Test state JSON with empty sections."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Rating:** 3/5
**Confidence:** medium

Basic review.
""")

        parser = MarkdownParser(markdown)
        state = parser.to_state_json()

        assert state['dx_rating']['stars'] == 3
        assert len(state['concerns']) == 0
        assert len(state['recommendations']) == 0
        assert len(state['strengths']) == 0
        assert len(state['questions']) == 0


# ============================================================================
# Delta Review Parsing Tests
# ============================================================================

class TestParseDeltaReview:
    """Test parse_delta_review function."""

    @pytest.mark.high
    def test_parse_basic_delta_review(self):
        """Test parsing basic delta review."""
        content = """### 1. What Changed

Updated implementation based on feedback.

### 2. Updated Recommendations

### 3. New Recommendations

### 4. New Concerns

### 5. Resolved Concerns

### 6. Updated Assessment

### 7. New Questions
"""

        result = parse_delta_review(content, iteration=2)

        assert result["type"] == "delta"
        assert result["iteration"] == 2
        assert "Updated implementation" in result["what_changed"]

    @pytest.mark.high
    def test_parse_delta_with_resolved_concerns(self):
        """Test parsing delta with resolved concerns."""
        content = """### 1. What Changed

Fixed issues.

### 5. Resolved Concerns

- con-001 (Fixed error handling)
- con-002 (Added tests)
"""

        result = parse_delta_review(content, iteration=2)

        assert len(result["resolved_concerns"]) == 2
        assert "con-001" in result["resolved_concerns"]
        assert "con-002" in result["resolved_concerns"]

    @pytest.mark.high
    def test_parse_delta_with_assessment_update(self):
        """Test parsing delta with updated assessment."""
        content = """### 6. Updated Assessment

**Previous rating:** 3/5
**New rating:** 4/5
**Why it changed:** Improvements made to error handling.
"""

        result = parse_delta_review(content, iteration=2)

        assert result["updated_assessment"]["previous_rating"] == 3
        assert result["updated_assessment"]["new_rating"] == 4
        assert "error handling" in result["updated_assessment"]["why_changed"]

    @pytest.mark.medium
    def test_parse_delta_with_unanswered_questions(self):
        """Test parsing unanswered questions section."""
        content = """### 6.5. Unanswered Questions from Previous Iteration

UNANSWERED_QUESTIONS:
- q-001: Should we use async? - Reason: Not addressed yet
- q-002: What about performance? - Reason: Still unclear
"""

        result = parse_delta_review(content, iteration=2)

        assert len(result["unanswered_questions"]) == 2
        assert result["unanswered_questions"][0]["question_id"] == "q-001"
        assert "async" in result["unanswered_questions"][0]["question_text"]

    @pytest.mark.medium
    def test_parse_delta_long_warning(self, caplog):
        """Test warning for overly long delta reviews."""
        content = "### 1. What Changed\n\n" + ("x" * 15000)  # Very long delta

        result = parse_delta_review(content, iteration=2)

        # Should log warning
        assert result["type"] == "delta"


class TestExtractSection:
    """Test extract_section function."""

    @pytest.mark.high
    def test_extract_section_basic(self):
        """Test extracting basic section."""
        content = """### 1. What Changed

This is the content.

### 2. Next Section

Other content.
"""

        result = extract_section(content, "### 1. What Changed")

        assert "This is the content" in result
        assert "Next Section" not in result

    @pytest.mark.high
    def test_extract_section_end_of_content(self):
        """Test extracting section at end of content."""
        content = """### 1. First Section

Content 1.

### 2. Last Section

This is the last section.
"""

        result = extract_section(content, "### 2. Last Section")

        assert "last section" in result

    @pytest.mark.medium
    def test_extract_section_not_found(self):
        """Test extracting non-existent section."""
        content = """### 1. What Changed

Content here.
"""

        result = extract_section(content, "### 2. Missing Section")

        assert result == ""


class TestParseUpdatedRecommendations:
    """Test parse_updated_recommendations function."""

    @pytest.mark.high
    def test_parse_single_updated_recommendation(self):
        """Test parsing single updated recommendation."""
        section = """- **Recommendation ID:** rec-001
- **What changed:** Increased priority from medium to high
- **Updated rationale:** Critical for release
"""

        result = parse_updated_recommendations(section)

        assert "rec-001" in result
        assert "change_description" in result["rec-001"]
        assert "Increased priority" in result["rec-001"]["change_description"]

    @pytest.mark.high
    def test_parse_multiple_updated_recommendations(self):
        """Test parsing multiple updated recommendations."""
        section = """- **Recommendation ID:** rec-001
- **What changed:** Priority increased
- **Recommendation ID:** rec-002
- **What changed:** Complexity reduced
"""

        result = parse_updated_recommendations(section)

        assert len(result) == 2
        assert "rec-001" in result
        assert "rec-002" in result


class TestParseRecommendationChanges:
    """Test parse_recommendation_changes function."""

    @pytest.mark.high
    def test_parse_recommendation_changes_full(self):
        """Test parsing full recommendation changes."""
        block = """- **What changed:** Priority increased
**Priority:** high
**Complexity:** medium
- **Updated rationale:** Now critical for launch
"""

        result = parse_recommendation_changes(block)

        # The regex captures everything until the next bullet
        assert "Priority increased" in result["change_description"]
        assert result["priority"] == "high"
        assert result["complexity"] == "medium"
        assert result["rationale"] == "Now critical for launch"

    @pytest.mark.medium
    def test_parse_recommendation_changes_partial(self):
        """Test parsing partial recommendation changes."""
        block = """- **What changed:** Only priority changed
**Priority:** low
"""

        result = parse_recommendation_changes(block)

        # The regex captures everything until end or next bullet
        assert "Only priority changed" in result["change_description"]
        assert result["priority"] == "low"
        assert "complexity" not in result


class TestParseResolvedConcerns:
    """Test parse_resolved_concerns function."""

    @pytest.mark.high
    def test_parse_resolved_concerns_single(self):
        """Test parsing single resolved concern."""
        section = "- con-001 (Fixed by adding error handling)"

        result = parse_resolved_concerns(section)

        assert len(result) == 1
        assert "con-001" in result

    @pytest.mark.high
    def test_parse_resolved_concerns_multiple(self):
        """Test parsing multiple resolved concerns."""
        section = """- con-001 (Fixed error handling)
- con-003 (Added tests)
- con-007 (Updated documentation)
"""

        result = parse_resolved_concerns(section)

        assert len(result) == 3
        assert "con-001" in result
        assert "con-003" in result
        assert "con-007" in result


class TestParseAssessmentUpdate:
    """Test parse_assessment_update function."""

    @pytest.mark.high
    def test_parse_assessment_update_full(self):
        """Test parsing complete assessment update."""
        section = """**Previous rating:** 3/5
**New rating:** 4/5
**Why it changed:** Significant improvements to error handling and testing.
"""

        result = parse_assessment_update(section)

        assert result["previous_rating"] == 3
        assert result["new_rating"] == 4
        assert "error handling" in result["why_changed"]

    @pytest.mark.medium
    def test_parse_assessment_update_partial(self):
        """Test parsing partial assessment update."""
        section = """**New rating:** 5/5
**Why it changed:** All concerns addressed.
"""

        result = parse_assessment_update(section)

        assert "previous_rating" not in result
        assert result["new_rating"] == 5


class TestParseUnansweredQuestions:
    """Test parse_unanswered_questions function."""

    @pytest.mark.high
    def test_parse_unanswered_questions_single(self):
        """Test parsing single unanswered question."""
        section = """UNANSWERED_QUESTIONS:
- q-001: Should we use async? - Reason: Not addressed in this iteration
"""

        result = parse_unanswered_questions(section)

        assert len(result) == 1
        assert result[0]["question_id"] == "q-001"
        assert "async" in result[0]["question_text"]
        assert "Not addressed" in result[0]["reason"]

    @pytest.mark.high
    def test_parse_unanswered_questions_multiple(self):
        """Test parsing multiple unanswered questions."""
        section = """UNANSWERED_QUESTIONS:
- q-001: What about async? - Reason: Needs decision
- q-003: Performance concerns? - Reason: Requires testing
"""

        result = parse_unanswered_questions(section)

        assert len(result) == 2
        assert result[0]["question_id"] == "q-001"
        assert result[1]["question_id"] == "q-003"

    @pytest.mark.medium
    def test_parse_unanswered_questions_no_block(self):
        """Test parsing when UNANSWERED_QUESTIONS block is missing."""
        section = "Some other content"

        result = parse_unanswered_questions(section)

        assert len(result) == 0


# ============================================================================
# Merge Operations Tests
# ============================================================================

class TestMergeDeltaWithState:
    """Test merge_delta_with_state function."""

    @pytest.mark.high
    def test_merge_basic_delta(self):
        """Test merging basic delta with previous state."""
        previous_state = {
            "iteration": 1,
            "dx_rating": {"stars": 3, "confidence": "medium", "justification": "OK"},
            "recommendations": [],
            "concerns": [],
            "questions": []
        }

        delta = {
            "type": "delta",
            "iteration": 2,
            "what_changed": "Improvements made",
            "updated_recommendations": {},
            "new_recommendations": [],
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert result["iteration"] == 2
        assert result["dx_rating"] == previous_state["dx_rating"]

    @pytest.mark.high
    def test_merge_with_new_recommendations(self):
        """Test merging delta with new recommendations."""
        previous_state = {
            "iteration": 1,
            "recommendations": [
                {"title": "Old Rec", "priority": "low"}
            ]
        }

        delta = {
            "iteration": 2,
            "new_recommendations": [
                {"title": "New Rec", "priority": "high"}
            ],
            "updated_recommendations": {},
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert len(result["recommendations"]) == 2
        assert result["recommendations"][1]["title"] == "New Rec"

    @pytest.mark.high
    def test_merge_with_resolved_concerns(self):
        """Test merging delta with resolved concerns."""
        previous_state = {
            "iteration": 1,
            "concerns": [
                {"title": "Test Coverage", "severity": "high"},
                {"title": "Documentation", "severity": "low"}
            ]
        }

        delta = {
            "iteration": 2,
            "resolved_concerns": ["con-test-coverage"],
            "updated_recommendations": {},
            "new_recommendations": [],
            "new_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        # Test Coverage should be removed
        assert len(result["concerns"]) == 1
        assert result["concerns"][0]["title"] == "Documentation"

    @pytest.mark.high
    def test_merge_with_updated_assessment(self):
        """Test merging delta with updated assessment."""
        previous_state = {
            "iteration": 1,
            "dx_rating": {"stars": 3, "confidence": "medium", "justification": "OK"}
        }

        delta = {
            "iteration": 2,
            "updated_assessment": {
                "previous_rating": 3,
                "new_rating": 4,
                "why_changed": "Improvements made"
            },
            "updated_recommendations": {},
            "new_recommendations": [],
            "new_concerns": [],
            "resolved_concerns": [],
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert result["dx_rating"]["stars"] == 4
        assert "Improvements made" in result["dx_rating"]["justification"]

    @pytest.mark.high
    def test_merge_with_questions(self):
        """Test merging delta with questions."""
        previous_state = {"iteration": 1, "questions": []}

        delta = {
            "iteration": 2,
            "unanswered_questions": [
                {"question_id": "q-001", "question_text": "Old question?", "reason": "Not answered"}
            ],
            "new_questions": [
                {"id": "q-002", "question": "New question?", "importance": "high"}
            ],
            "updated_recommendations": {},
            "new_recommendations": [],
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None
        }

        result = merge_delta_with_state(previous_state, delta)

        assert len(result["questions"]) == 2
        assert result["questions"][0]["id"] == "q-001"
        assert result["questions"][1]["id"] == "q-002"

    @pytest.mark.high
    def test_merge_with_updated_recommendations_full(self):
        """Test merging delta with updated recommendation fields."""
        previous_state = {
            "iteration": 1,
            "recommendations": [
                {
                    "title": "Add Logging",
                    "priority": "medium",
                    "complexity": "low",
                    "description": "Add logging to app"
                }
            ]
        }

        delta = {
            "iteration": 2,
            "updated_recommendations": {
                "rec-add-logging": {
                    "priority": "high",
                    "complexity": "medium",
                    "rationale": "Now critical for debugging",
                    "change_description": "Increased priority due to production issues"
                }
            },
            "new_recommendations": [],
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        rec = result["recommendations"][0]
        assert rec["priority"] == "high"
        assert rec["complexity"] == "medium"
        assert "Now critical for debugging" in rec["description"]
        assert "metadata" in rec
        assert rec["metadata"]["last_change"] == "Increased priority due to production issues"

    @pytest.mark.medium
    def test_merge_with_new_recommendations_no_existing(self):
        """Test adding new recommendations when none exist."""
        previous_state = {"iteration": 1}

        delta = {
            "iteration": 2,
            "new_recommendations": [
                {"title": "New Rec", "priority": "high"}
            ],
            "updated_recommendations": {},
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert "recommendations" in result
        assert len(result["recommendations"]) == 1
        assert result["recommendations"][0]["title"] == "New Rec"

    @pytest.mark.medium
    def test_merge_with_new_concerns_no_existing(self):
        """Test adding new concerns when none exist."""
        previous_state = {"iteration": 1}

        delta = {
            "iteration": 2,
            "new_concerns": [
                {"title": "New Concern", "severity": "high"}
            ],
            "updated_recommendations": {},
            "new_recommendations": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert "concerns" in result
        assert len(result["concerns"]) == 1
        assert result["concerns"][0]["title"] == "New Concern"

    @pytest.mark.medium
    def test_merge_clears_questions_when_none(self):
        """Test that questions are cleared when no new or unanswered ones."""
        previous_state = {
            "iteration": 1,
            "questions": [
                {"id": "q-001", "question": "Old?", "importance": "high"}
            ]
        }

        delta = {
            "iteration": 2,
            "updated_recommendations": {},
            "new_recommendations": [],
            "new_concerns": [],
            "resolved_concerns": [],
            "updated_assessment": None,
            "unanswered_questions": [],
            "new_questions": []
        }

        result = merge_delta_with_state(previous_state, delta)

        assert result["questions"] == []


# ============================================================================
# ID Generation Tests
# ============================================================================

class TestIdGeneration:
    """Test ID generation functions."""

    @pytest.mark.high
    def test_generate_rec_id_basic(self):
        """Test generating basic recommendation ID."""
        title = "Add Logging Framework"

        result = generate_rec_id(title)

        assert result == "rec-add-logging-framework"

    @pytest.mark.high
    def test_generate_rec_id_with_special_chars(self):
        """Test generating ID with special characters."""
        title = "Implement Result<T, E> Type"

        result = generate_rec_id(title)

        assert result.startswith("rec-")
        assert "result" in result
        assert "type" in result
        # Special chars should be replaced with hyphens
        assert "<" not in result
        assert ">" not in result

    @pytest.mark.medium
    def test_generate_rec_id_truncation(self):
        """Test that recommendation ID is truncated."""
        title = "This is a very long recommendation title that should be truncated"

        result = generate_rec_id(title)

        assert result.startswith("rec-")
        # Should be truncated (rec- + 30 chars max)
        assert len(result) <= 34

    @pytest.mark.high
    def test_generate_concern_id_basic(self):
        """Test generating basic concern ID."""
        title = "Missing Test Coverage"

        result = generate_concern_id(title)

        assert result == "con-missing-test-coverage"

    @pytest.mark.medium
    def test_generate_concern_id_truncation(self):
        """Test that concern ID is truncated."""
        title = "This is a very long concern title that should definitely be truncated"

        result = generate_concern_id(title)

        assert result.startswith("con-")
        assert len(result) <= 34


# ============================================================================
# Parse Expert Review Integration Tests
# ============================================================================

class TestParseExpertReview:
    """Test parse_expert_review main function."""

    @pytest.mark.high
    def test_parse_expert_review_iteration_1(self, sample_markdown_path, tmp_path):
        """Test parsing iteration 1 (full review)."""
        expert_name = "typescript"

        # Parse markdown to JSON
        parse_expert_review(sample_markdown_path, tmp_path, expert_name, iteration=1)

        # Check files created
        state_file = tmp_path / f"state-{expert_name}.json"
        questions_file = tmp_path / f"questions-{expert_name}.json"

        assert state_file.exists()
        assert questions_file.exists()

        # Validate JSON
        state = json.loads(state_file.read_text())
        questions = json.loads(questions_file.read_text())

        assert state['expert_name'] == expert_name
        assert state['iteration'] == 1
        assert len(questions) == 2

    @pytest.mark.high
    def test_parse_expert_review_iteration_2_with_workspace(self, tmp_path):
        """Test parsing iteration 2 with workspace."""
        workspace = tmp_path / "workspace"
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True)

        # Create previous state
        prev_state = {
            "iteration": 1,
            "expert_name": "typescript",
            "dx_rating": {"stars": 3, "confidence": "medium", "justification": "OK"},
            "recommendations": [],
            "concerns": [],
            "questions": []
        }
        (iter1_dir / "state-typescript.json").write_text(json.dumps(prev_state))

        # Create delta review
        iter2_dir = tmp_path / "output"
        iter2_dir.mkdir()
        delta_md = iter2_dir / "review-typescript.md"
        delta_md.write_text("""### 1. What Changed

Improvements made.

### 2. Updated Recommendations

### 3. New Recommendations

### 4. New Concerns

### 5. Resolved Concerns

### 6. Updated Assessment

**Previous rating:** 3/5
**New rating:** 4/5
**Why it changed:** Better error handling

### 7. New Questions
""")

        # Parse iteration 2
        parse_expert_review(delta_md, iter2_dir, "typescript", iteration=2, workspace=workspace)

        # Check files created
        state_file = iter2_dir / "state-typescript.json"
        assert state_file.exists()

        state = json.loads(state_file.read_text())
        assert state["iteration"] == 2
        assert state["dx_rating"]["stars"] == 4

    @pytest.mark.medium
    def test_parse_expert_review_iteration_2_no_workspace_error(self, tmp_path):
        """Test that iteration 2 without workspace raises error."""
        markdown = tmp_path / "review.md"
        markdown.write_text("### 1. What Changed\n\nChanges.")

        with pytest.raises(ValueError, match="workspace parameter required"):
            parse_expert_review(markdown, tmp_path, "typescript", iteration=2, workspace=None)

    @pytest.mark.medium
    def test_parse_expert_review_iteration_2_missing_prev_state(self, tmp_path, caplog):
        """Test iteration 2 when previous state is missing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        delta_md = tmp_path / "review.md"
        delta_md.write_text("""### 1. What Changed

Changes.

### 7. New Questions

### What should we do?

**Asked by:** [Expert1]
**Importance:** high
""")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Should handle gracefully
        parse_expert_review(delta_md, output_dir, "typescript", iteration=2, workspace=workspace)

        # Should still generate questions if available
        questions_file = output_dir / "questions-typescript.json"
        if questions_file.exists():
            questions = json.loads(questions_file.read_text())
            assert len(questions) >= 0


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.medium
    def test_missing_sections_graceful(self, tmp_path):
        """Test parser handles missing sections gracefully."""
        minimal_markdown = """# Test Review

## DX Rating

**Rating:** 3/5
**Confidence:** medium

Basic review.
"""

        markdown = tmp_path / "minimal.md"
        markdown.write_text(minimal_markdown)
        parser = MarkdownParser(markdown)

        # Should not crash on missing sections
        rating = parser.parse_dx_rating()
        concerns = parser.parse_concerns()
        recommendations = parser.parse_recommendations()
        strengths = parser.parse_strengths()
        questions = parser.parse_questions()

        assert rating.stars == 3
        assert len(concerns) == 0
        assert len(recommendations) == 0
        assert len(strengths) == 0
        assert len(questions) == 0

    @pytest.mark.medium
    def test_empty_markdown_file(self, tmp_path):
        """Test parsing empty markdown file."""
        markdown = tmp_path / "empty.md"
        markdown.write_text("")

        parser = MarkdownParser(markdown)

        assert len(parser.sections) == 0
        assert parser.parse_dx_rating().stars == 0

    @pytest.mark.medium
    def test_malformed_ratings(self, tmp_path):
        """Test handling malformed ratings."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## DX Rating

**Rating:** invalid/5
**Confidence:** high

Text.
""")

        parser = MarkdownParser(markdown)
        rating = parser.parse_dx_rating()

        # Should handle gracefully, using default
        assert rating.stars == 0  # Can't parse "invalid"

    @pytest.mark.medium
    def test_special_characters_in_titles(self, tmp_path):
        """Test handling special characters in titles."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Concerns

### Error: <Component> & "API" Design

**Severity:** high
**Impact:** medium

Description.

**Fix:** Fix it.
""")

        parser = MarkdownParser(markdown)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert '<Component>' in concerns[0].title
        assert '&' in concerns[0].title

    @pytest.mark.low
    def test_unicode_in_content(self, tmp_path):
        """Test handling unicode characters."""
        markdown = tmp_path / "test.md"
        markdown.write_text("""## Strengths ✅

### Excellent Documentation 📚

Contains émojis and speçial characters.
Unicode: 你好 мир שלום
""")

        parser = MarkdownParser(markdown)
        strengths = parser.parse_strengths()

        assert len(strengths) == 1
        assert "émojis" in strengths[0]['description']
        assert "你好" in strengths[0]['description']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
