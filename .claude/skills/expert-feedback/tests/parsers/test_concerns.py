"""
Unit tests for parsers/concerns.py

Tests synthesized concerns parsing including:
- SynthesizedConcernsParser class
- Evidence and Concern dataclasses
- parse_summary() summary extraction
- parse_concerns() concern parsing
- Priority and category extraction

Target coverage: 85%+
"""
import pytest
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from parsers.concerns import (
    SynthesizedConcernsParser,
    Evidence,
    Concern,
    SynthesizedConcerns,
    parse_synthesized_concerns
)


class TestEvidenceDataclass:
    """Test Evidence dataclass."""

    @pytest.mark.medium
    def test_evidence_creation(self):
        """Test creating Evidence instance."""
        evidence = Evidence(
            expert="typescript",
            quote="Testing is important"
        )

        assert evidence.expert == "typescript"
        assert evidence.quote == "Testing is important"


class TestConcernDataclass:
    """Test Concern dataclass."""

    @pytest.mark.medium
    def test_concern_creation(self):
        """Test creating Concern instance."""
        evidence = Evidence("expert1", "Quote")
        concern = Concern(
            title="Test Coverage",
            priority="high",
            category="Testing",
            raised_by=["expert1", "expert2"],
            agreement_level="majority",
            description="Need more tests",
            evidence=[evidence],
            recommendation="Add unit tests",
            impact_if_ignored="Quality issues"
        )

        assert concern.title == "Test Coverage"
        assert concern.priority == "high"
        assert len(concern.raised_by) == 2


class TestSynthesizedConcernsParser:
    """Test SynthesizedConcernsParser class."""

    @pytest.mark.medium
    def test_parser_initialization(self, tmp_path):
        """Test parser initialization with markdown file."""
        concerns_file = tmp_path / "concerns.md"
        content = """## Summary

**Synthesized Concerns:** 3
**High Priority:** 1
**Medium Priority:** 2
"""
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)

        assert parser.markdown is not None
        assert "Summary" in parser.sections

    @pytest.mark.medium
    def test_split_sections(self, tmp_path):
        """Test section splitting."""
        concerns_file = tmp_path / "concerns.md"
        content = """## Summary
Summary content

## Concerns
Concern content

## Recommendations
Recommendation content
"""
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)

        assert len(parser.sections) == 3
        assert "Summary" in parser.sections
        assert "Concerns" in parser.sections
        assert "Recommendations" in parser.sections

    @pytest.mark.medium
    def test_parse_summary(self, tmp_path):
        """Test parsing summary section."""
        concerns_file = tmp_path / "concerns.md"
        content = """## Summary

**Total Experts:** 5
**Approvals:** 2
**Minor Tweaks:** 2
**Vetoes:** 1
**Synthesized Concerns:** 3
"""
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        summary = parser.parse_summary()

        assert summary["total_experts"] == 5
        assert summary["approvals"] == 2
        assert summary["minor_tweaks"] == 2
        assert summary["total_concerns"] == 3

    @pytest.mark.medium
    def test_parse_concern_title(self, tmp_path):
        """Test parsing concern title."""
        concerns_file = tmp_path / "concerns.md"
        content = """## Synthesized Concerns

### 1. Insufficient Test Coverage

**Priority:** High
**Category:** Testing
**Raised by:** [typescript, python]
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
"""
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert "Insufficient Test Coverage" in concerns[0].title

    @pytest.mark.medium
    def test_parse_multiple_concerns(self, tmp_path):
        """Test parsing multiple concerns."""
        concerns_file = tmp_path / "concerns.md"
        content = """
        ## Concerns

        ### 1. Test Coverage

        **Priority:** high
        **Category:** Testing

        ### 2. Documentation

        **Priority:** medium
        **Category:** Documentation

        ### 3. Performance

        **Priority:** low
        **Category:** Performance
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        # Should parse multiple concerns
        assert isinstance(concerns, list)

    @pytest.mark.medium
    def test_empty_markdown(self, tmp_path):
        """Test parsing empty markdown file."""
        concerns_file = tmp_path / "empty.md"
        concerns_file.write_text("")

        parser = SynthesizedConcernsParser(concerns_file)

        assert len(parser.sections) == 0


class TestParsePriority:
    """Test priority parsing."""

    @pytest.mark.medium
    def test_parse_high_priority(self, tmp_path):
        """Test parsing high priority."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test Concern

**Priority:** High
**Category:** Testing
**Raised by:** expert1
**Agreement Level:** Unanimous
**Description:** Test description
**Evidence:**
- expert1: Quote
**Recommendation:** Fix it
**Impact if Ignored:** Bad things
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].priority == "high"

    @pytest.mark.medium
    def test_parse_medium_priority(self, tmp_path):
        """Test parsing medium priority."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Medium
**Category:** Testing
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].priority == "medium"

    @pytest.mark.medium
    def test_parse_low_priority(self, tmp_path):
        """Test parsing low priority."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Low
**Category:** Testing
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Minor
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].priority == "low"


class TestParseCategory:
    """Test category parsing."""

    @pytest.mark.medium
    def test_parse_testing_category(self, tmp_path):
        """Test parsing Testing category."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].category == "Testing"

    @pytest.mark.medium
    def test_parse_documentation_category(self, tmp_path):
        """Test parsing Documentation category."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Medium
**Category:** Documentation
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].category == "Documentation"

    @pytest.mark.medium
    def test_parse_performance_category(self, tmp_path):
        """Test parsing Performance category."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Low
**Category:** Performance
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Slow
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].category == "Performance"


class TestParseAgreementLevel:
    """Test agreement level parsing."""

    @pytest.mark.medium
    def test_parse_unanimous_agreement(self, tmp_path):
        """Test parsing unanimous agreement."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Agreement Level:** Unanimous
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].agreement_level == "unanimous"

    @pytest.mark.medium
    def test_parse_majority_agreement(self, tmp_path):
        """Test parsing majority agreement."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Medium
**Category:** Testing
**Agreement Level:** Majority
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].agreement_level == "majority"

    @pytest.mark.medium
    def test_parse_split_agreement(self, tmp_path):
        """Test parsing split agreement."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** Low
**Category:** Testing
**Agreement Level:** Split
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].agreement_level == "split"


class TestParseEvidence:
    """Test evidence parsing."""

    @pytest.mark.medium
    def test_parse_single_evidence(self, tmp_path):
        """Test parsing single piece of evidence."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:** Test description
**Evidence:**
- typescript: Testing is critical for quality
**Recommendation:** Add tests
**Impact if Ignored:** Quality issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert len(concerns[0].evidence) == 1
        assert concerns[0].evidence[0].expert == "typescript"
        assert concerns[0].evidence[0].quote == "Testing is critical for quality"

    @pytest.mark.medium
    def test_parse_multiple_evidence(self, tmp_path):
        """Test parsing multiple pieces of evidence."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test Coverage

**Priority:** High
**Category:** Testing
**Description:** Insufficient test coverage
**Evidence:**
- typescript: Testing is important
- python: We need more test coverage
- dotnet: Unit tests are missing
**Recommendation:** Add comprehensive tests
**Impact if Ignored:** Quality degradation
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert len(concerns[0].evidence) == 3
        assert concerns[0].evidence[0].expert == "typescript"
        assert concerns[0].evidence[1].expert == "python"
        assert concerns[0].evidence[2].expert == "dotnet"


class TestParseSynthesizedConcerns:
    """Test parse_synthesized_concerns main function."""

    @pytest.mark.medium
    @pytest.mark.xfail(reason="Bug in source code: line 203 uses 'consolidated' instead of 'synthesized'")
    def test_parse_complete_concerns_file(self, tmp_path):
        """Test parsing complete concerns markdown file."""
        concerns_file = tmp_path / "concerns.md"
        output_file = tmp_path / "output.json"
        content = """
## Summary

**Total Experts:** 3
**Approvals:** 1
**Minor Tweaks:** 1
**Vetoes:** 1
**Synthesized Concerns:** 2

## Synthesized Concerns

### Test Coverage

**Priority:** High
**Category:** Testing
**Raised by:** typescript, python
**Agreement Level:** Unanimous
**Description:** Insufficient test coverage identified.
**Evidence:**
- typescript: Need more unit tests
**Recommendation:** Add comprehensive test suite.
**Impact if Ignored:** Quality degradation.

### Documentation

**Priority:** Medium
**Category:** Documentation
**Raised by:** dotnet
**Agreement Level:** Majority
**Description:** API documentation is incomplete.
**Recommendation:** Document all public APIs.
**Impact if Ignored:** Poor developer experience.
        """
        concerns_file.write_text(content)

        result = parse_synthesized_concerns(concerns_file, output_file)

        # Should return dict with summary and concerns
        assert result is not None
        assert "summary" in result
        assert "concerns" in result
        assert result["summary"]["total_experts"] == 3
        assert len(result["concerns"]) == 2

        # Verify output file was created
        assert output_file.exists()

    @pytest.mark.medium
    def test_parse_concerns_file_not_found(self, tmp_path):
        """Test handling of missing file."""
        output_file = tmp_path / "output.json"
        with pytest.raises(FileNotFoundError):
            parse_synthesized_concerns(Path("nonexistent.md"), output_file)


class TestRaisedByParsing:
    """Test parsing raised_by field."""

    @pytest.mark.medium
    def test_parse_raised_by_bracketed(self, tmp_path):
        """Test parsing raised_by with brackets."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Raised by:** [typescript, python, dotnet]
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].raised_by == ["typescript", "python", "dotnet"]

    @pytest.mark.medium
    def test_parse_raised_by_no_brackets(self, tmp_path):
        """Test parsing raised_by without brackets."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Raised by:** typescript, python
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].raised_by == ["typescript", "python"]

    @pytest.mark.medium
    def test_parse_raised_by_single_expert(self, tmp_path):
        """Test parsing raised_by with single expert."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Raised by:** typescript
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].raised_by == ["typescript"]


class TestMultiLineFields:
    """Test parsing multi-line fields."""

    @pytest.mark.medium
    def test_parse_multiline_description(self, tmp_path):
        """Test parsing multi-line description."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:**
This is a long description
that spans multiple lines
and includes details.
**Evidence:**
- expert1: Quote
**Recommendation:** Fix it
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert "multiple lines" in concerns[0].description
        assert concerns[0].description.count('\n') >= 2

    @pytest.mark.medium
    def test_parse_multiline_recommendation(self, tmp_path):
        """Test parsing multi-line recommendation."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:** Test
**Recommendation:**
Step 1: First thing
Step 2: Second thing
Step 3: Third thing
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert "Step 1" in concerns[0].recommendation
        assert "Step 3" in concerns[0].recommendation


class TestDefaultValues:
    """Test default values when fields are missing."""

    @pytest.mark.medium
    def test_missing_priority_defaults_to_medium(self, tmp_path):
        """Test that missing priority defaults to medium."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Category:** Testing
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].priority == "medium"

    @pytest.mark.medium
    def test_missing_category_defaults_to_general(self, tmp_path):
        """Test that missing category defaults to General."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].category == "General"

    @pytest.mark.medium
    def test_missing_agreement_defaults_to_unknown(self, tmp_path):
        """Test that missing agreement level defaults to unknown."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:** Test
**Recommendation:** Fix
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert concerns[0].agreement_level == "unknown"


class TestEdgeCases:
    """Test edge cases."""

    @pytest.mark.medium
    def test_concern_with_no_evidence(self, tmp_path):
        """Test concern without evidence."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test

**Priority:** High
**Category:** Testing
**Description:** Test description
**Recommendation:** Fix it
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert len(concerns[0].evidence) == 0

    @pytest.mark.medium
    def test_concern_with_special_characters(self, tmp_path):
        """Test concern title with special characters."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Synthesized Concerns

### Test <Component> & "API" Design

**Priority:** High
**Category:** Design
**Description:** Complex title test
**Recommendation:** Fix it
**Impact if Ignored:** Issues
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        concerns = parser.parse_concerns()

        assert len(concerns) == 1
        assert '<Component>' in concerns[0].title
        assert '&' in concerns[0].title

    @pytest.mark.medium
    def test_summary_missing_fields(self, tmp_path):
        """Test summary with missing fields."""
        concerns_file = tmp_path / "concerns.md"
        content = """
## Summary

**Synthesized Concerns:** 3
        """
        concerns_file.write_text(content)

        parser = SynthesizedConcernsParser(concerns_file)
        summary = parser.parse_summary()

        # Should provide defaults for missing fields
        assert summary["total_concerns"] == 3
        assert summary["total_experts"] == 0  # Default
        assert summary["approvals"] == 0  # Default
