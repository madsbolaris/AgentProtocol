"""Tests for markdown parser."""
import json
import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from parsers.expert_review import MarkdownParser, parse_expert_review


@pytest.fixture
def sample_markdown_path():
    """Get path to sample markdown fixture."""
    return Path(__file__).parent.parent / "fixtures" / "sample-review.md"


@pytest.fixture
def parser(sample_markdown_path):
    """Create parser instance with sample markdown."""
    return MarkdownParser(sample_markdown_path)


def test_parse_dx_rating(parser):
    """Test DX rating parsing."""
    rating = parser.parse_dx_rating()

    assert rating.stars == 4
    assert rating.confidence == "high"
    assert "TypeScript implementation" in rating.justification


def test_parse_concerns(parser):
    """Test concerns parsing."""
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


def test_parse_recommendations(parser):
    """Test recommendations parsing."""
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


def test_parse_strengths(parser):
    """Test strengths parsing."""
    strengths = parser.parse_strengths()

    assert len(strengths) == 2
    assert strengths[0]['title'] == "Strong Type Coverage"
    assert "excellent type coverage" in strengths[0]['description']
    assert strengths[1]['title'] == "Modern ES Features"


def test_parse_questions(parser):
    """Test questions parsing."""
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


def test_to_state_json(parser):
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


def test_to_questions_json(parser):
    """Test questions JSON generation."""
    questions = parser.to_questions_json()

    assert len(questions) == 2
    assert all('id' in q for q in questions)
    assert all('question' in q for q in questions)
    assert all('context' in q for q in questions)
    assert all('importance' in q for q in questions)


def test_parse_expert_review_integration(sample_markdown_path, tmp_path):
    """Test full parsing workflow."""
    expert_name = "typescript"

    # Parse markdown to JSON
    parse_expert_review(sample_markdown_path, tmp_path, expert_name)

    # Check files created
    state_file = tmp_path / f"state-{expert_name}.json"
    questions_file = tmp_path / f"questions-{expert_name}.json"

    assert state_file.exists()
    assert questions_file.exists()

    # Validate JSON
    state = json.loads(state_file.read_text())
    questions = json.loads(questions_file.read_text())

    assert state['expert_name'] == expert_name
    assert len(questions) == 2


def test_missing_sections():
    """Test parser handles missing sections gracefully."""
    minimal_markdown = """# Test Review

## DX Rating

**Rating:** 3/5
**Confidence:** medium

Basic review.
"""

    # Create temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(minimal_markdown)
        temp_path = Path(f.name)

    try:
        parser = MarkdownParser(temp_path)

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
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
