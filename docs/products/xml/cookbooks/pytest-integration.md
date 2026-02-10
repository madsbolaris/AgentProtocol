# pytest Integration

Use XML serialization and validation in pytest test suites.

## Overview

This cookbook shows how to integrate XML message validation into pytest tests, including test data organization and EvalXML preprocessing.

---

## Test Structure

```
tests/
├── test_data/
│   ├── input/          # Input XML files
│   └── expected/       # Expected output XML files
├── conftest.py         # Shared fixtures
└── test_messages.py    # Message tests
```

---

## Installation

```bash
pip install microsoft-agents-xml pytest pytest-asyncio
```

---

## Complete Test Example

### conftest.py - Shared Fixtures

```python
"""Shared pytest fixtures for XML tests."""

import pytest
from pathlib import Path
from microsoft.agents.xml import MessageSerializer, ThreadValidator
from microsoft.agents.xml.eval_xml_preprocessor import preprocess

@pytest.fixture
def test_data_dir():
    """Get path to test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def serializer():
    """Create XML message serializer."""
    return MessageSerializer()

@pytest.fixture
def validator():
    """Create XML thread validator."""
    return ThreadValidator()

@pytest.fixture
def sample_xml(test_data_dir):
    """Load sample XML from test data."""
    input_dir = test_data_dir / "input"
    xml_file = input_dir / "basic_message.xml"
    return xml_file.read_text()

@pytest.fixture
def evalxml_preprocessor():
    """Create EvalXML preprocessor."""
    return lambda xml: preprocess(xml)
```

### test_messages.py - Message Tests

```python
"""Tests for XML message serialization and validation."""

import pytest
from pathlib import Path
from microsoft.agents.models import UserMessage, TextContent, AgentMessage
from microsoft.agents.xml import MessageSerializer
from microsoft.agents.validation import ThreadValidator

class TestMessageSerialization:
    """Test XML message serialization."""
    
    def test_serialize_user_message(self, serializer):
        """Test serializing a user message to XML."""
        # Arrange
        message = UserMessage(
            role="user",
            content=[TextContent(text="Hello, agent!")]
        )
        
        # Act
        xml = serializer.serialize(message)
        
        # Assert
        assert xml is not None
        assert "<?xml" in xml
        assert "<user-message" in xml
        assert "Hello, agent!" in xml
    
    def test_serialize_agent_message(self, serializer):
        """Test serializing an agent message to XML."""
        # Arrange
        message = AgentMessage(
            role="agent",
            content=[TextContent(text="Hello, user!")]
        )
        
        # Act
        xml = serializer.serialize(message)
        
        # Assert
        assert xml is not None
        assert "<agent-message" in xml
        assert "Hello, user!" in xml
    
    def test_roundtrip_serialization(self, serializer):
        """Test serialize and deserialize roundtrip."""
        # Arrange
        original = UserMessage(
            role="user",
            content=[TextContent(text="Test message")]
        )
        
        # Act
        xml = serializer.serialize(original)
        deserialized = serializer.deserialize(xml)
        
        # Assert
        assert deserialized.role == original.role
        assert len(deserialized.content) == len(original.content)
        assert deserialized.content[0].text == original.content[0].text

class TestXMLValidation:
    """Test XML validation against schema."""
    
    def test_validate_valid_xml(self, validator, sample_xml):
        """Test validating a valid XML message."""
        # Act
        errors = validator.validate(sample_xml)
        
        # Assert
        assert len(errors) == 0, "Valid XML should have no errors"
    
    def test_validate_invalid_xml(self, validator):
        """Test validating an invalid XML message."""
        # Arrange
        invalid_xml = "<invalid>Not a valid message</invalid>"
        
        # Act
        errors = validator.validate(invalid_xml)
        
        # Assert
        assert len(errors) > 0, "Invalid XML should have errors"
        assert any("schema" in str(e).lower() for e in errors)
    
    def test_validate_with_test_data(self, validator, test_data_dir):
        """Test validation using test data files."""
        # Arrange
        input_dir = test_data_dir / "input"
        xml_files = list(input_dir.glob("*.xml"))
        
        # Act & Assert
        for xml_file in xml_files:
            xml = xml_file.read_text()
            errors = validator.validate(xml)
            assert len(errors) == 0, f"{xml_file.name} should be valid"

class TestEvalXMLPreprocessing:
    """Test EvalXML preprocessing."""
    
    def test_preprocess_assert_block(self, evalxml_preprocessor):
        """Test CDATA wrapping of assertion blocks."""
        # Arrange
        input_xml = '<assert>x == 5</assert>'
        
        # Act
        result = evalxml_preprocessor(input_xml)
        
        # Assert
        assert result == '<assert><![CDATA[x == 5]]></assert>'
    
    def test_preprocess_metric_comparison(self, evalxml_preprocessor):
        """Test CDATA wrapping protects comparison operators."""
        # Arrange
        input_xml = '<metric>x > 5 && y < 10</metric>'
        
        # Act
        result = evalxml_preprocessor(input_xml)
        
        # Assert
        assert '<![CDATA[' in result
        assert 'x > 5 && y < 10' in result
    
    def test_preprocess_evalxml_file(self, evalxml_preprocessor, test_data_dir):
        """Test preprocessing complete EvalXML files."""
        # Arrange
        evalxml_file = test_data_dir / "input" / "test_case.evalxml"
        if not evalxml_file.exists():
            pytest.skip("EvalXML test file not found")
        
        input_xml = evalxml_file.read_text()
        
        # Act
        result = evalxml_preprocessor(input_xml)
        
        # Assert
        assert '<![CDATA[' in result
        assert ']]>' in result

class TestIntegrationWithTestData:
    """Integration tests using test data files."""
    
    @pytest.fixture
    def test_cases(self, test_data_dir):
        """Load all test cases from test data."""
        input_dir = test_data_dir / "input"
        expected_dir = test_data_dir / "expected"
        
        test_cases = []
        for input_file in input_dir.glob("*.xml"):
            expected_file = expected_dir / input_file.name
            if expected_file.exists():
                test_cases.append({
                    "name": input_file.stem,
                    "input": input_file.read_text(),
                    "expected": expected_file.read_text()
                })
        
        return test_cases
    
    def test_all_cases(self, test_cases, serializer, validator):
        """Test all cases from test data."""
        for case in test_cases:
            # Validate input
            errors = validator.validate(case["input"])
            assert len(errors) == 0, f"Input for {case['name']} should be valid"
            
            # Validate expected
            errors = validator.validate(case["expected"])
            assert len(errors) == 0, f"Expected for {case['name']} should be valid"

# Run with: pytest tests/ -v
```

---

## Test Data Organization

### Input XML Files

Create `test_data/input/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <user-message>
    <text>Hello, agent!</text>
  </user-message>
</thread>
```

### Expected Output Files

Create `test_data/expected/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <agent-message>
    <text>Hello, user!</text>
  </agent-message>
</thread>
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Class

```bash
pytest tests/test_messages.py::TestMessageSerialization -v
```

### Run With Coverage

```bash
pytest tests/ --cov=microsoft.agents.xml --cov-report=html
```

### Generate Test Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

---

## Advanced Patterns

### Parametrized Tests

```python
@pytest.mark.parametrize("input_file,expected_file", [
    ("basic_message.xml", "basic_response.xml"),
    ("multimodal.xml", "multimodal_response.xml"),
    ("tool_call.xml", "tool_result.xml"),
])
def test_message_transformation(input_file, expected_file, test_data_dir):
    """Test message transformations with parametrized inputs."""
    input_xml = (test_data_dir / "input" / input_file).read_text()
    expected_xml = (test_data_dir / "expected" / expected_file).read_text()
    
    # Process input
    validator = ThreadValidator()
    errors = validator.validate(input_xml)
    
    assert len(errors) == 0
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_serialization(serializer):
    """Test async serialization."""
    message = UserMessage(
        role="user",
        content=[TextContent(text="Async test")]
    )
    
    xml = await serializer.serialize_async(message)
    assert xml is not None
```

---

## See Also

- [Jest Integration](jest-integration.md)
- [xUnit Integration](xunit-integration.md)
- [How-To: Validation](../how-to-guides/validation.md)
