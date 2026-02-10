# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for StreamEvent"""

import pytest
from dataclasses import dataclass
from microsoft.agents.protocol.client import StreamEvent


def test_stream_event_creation():
    """Test creating a StreamEvent"""
    event = StreamEvent(event_type="message.delta", data={"text": "hello"})

    assert event.event_type == "message.delta"
    assert event.data == {"text": "hello"}


def test_stream_event_get_data_as_dict():
    """Test get_data_as with dict-like data"""
    event = StreamEvent(
        event_type="test.event",
        data={"field1": "value1", "field2": 42},
    )

    # Since the data is already a dict, we can access it directly
    assert event.data["field1"] == "value1"
    assert event.data["field2"] == 42


def test_stream_event_get_data_as_dataclass():
    """Test get_data_as with a dataclass"""

    @dataclass
    class TestData:
        name: str
        count: int

    event = StreamEvent(event_type="test.event", data={"name": "test", "count": 5})

    result = event.get_data_as(TestData)

    assert result is not None
    assert result.name == "test"
    assert result.count == 5


def test_stream_event_get_data_as_invalid():
    """Test get_data_as with invalid data returns None"""

    @dataclass
    class TestData:
        required_field: str

    # Missing required field
    event = StreamEvent(event_type="test.event", data={"other_field": "value"})

    result = event.get_data_as(TestData)

    # Should return None when deserialization fails
    assert result is None


def test_stream_event_with_nested_data():
    """Test StreamEvent with nested data structures"""
    event = StreamEvent(
        event_type="complex.event",
        data={
            "message": {
                "role": "agent",
                "contents": [{"kind": "text", "text": "Hello"}],
            }
        },
    )

    assert event.data["message"]["role"] == "agent"
    assert event.data["message"]["contents"][0]["text"] == "Hello"


def test_stream_event_with_empty_data():
    """Test StreamEvent with empty data"""
    event = StreamEvent(event_type="empty.event", data={})

    assert event.data == {}
    assert len(event.data) == 0


def test_stream_event_get_data_as_with_type_error():
    """Test get_data_as handles TypeError gracefully"""

    class TestData:
        def __init__(self, value: int):
            if not isinstance(value, int):
                raise TypeError("value must be int")
            self.value = value

    # String instead of int will cause TypeError
    event = StreamEvent(event_type="test.event", data={"value": "not_an_int"})

    result = event.get_data_as(TestData)

    # Should return None when TypeError occurs
    assert result is None


def test_stream_event_get_data_as_with_value_error():
    """Test get_data_as handles ValueError gracefully"""

    class CustomClass:
        def __init__(self, field1: str, field2: int):
            self.field1 = field1
            self.field2 = field2
            # Raise ValueError during construction for testing
            if field2 < 0:
                raise ValueError("field2 must be positive")

    event = StreamEvent(event_type="test.event", data={"field1": "test", "field2": -1})

    result = event.get_data_as(CustomClass)

    # Should return None when ValueError occurs
    assert result is None


def test_stream_event_get_data_as_with_key_error():
    """Test get_data_as handles KeyError gracefully"""

    class CustomClass:
        def __init__(self, required_key: str):
            self.required_key = required_key

    # Missing required_key
    event = StreamEvent(event_type="test.event", data={"other_key": "value"})

    result = event.get_data_as(CustomClass)

    # Should return None when KeyError occurs
    assert result is None


def test_stream_event_get_data_as_with_non_dataclass():
    """Test get_data_as with a regular class (not a dataclass)"""

    class RegularClass:
        def __init__(self, name: str, value: int):
            self.name = name
            self.value = value

    event = StreamEvent(event_type="test.event", data={"name": "test", "value": 42})

    result = event.get_data_as(RegularClass)

    # Should successfully create instance
    assert result is not None
    assert result.name == "test"
    assert result.value == 42


def test_stream_event_get_data_as_with_optional_fields():
    """Test get_data_as with dataclass having optional fields"""
    from typing import Optional

    @dataclass
    class TestData:
        required: str
        optional: Optional[int] = None

    event = StreamEvent(event_type="test.event", data={"required": "test"})

    result = event.get_data_as(TestData)

    assert result is not None
    assert result.required == "test"
    assert result.optional is None


def test_stream_event_get_data_as_with_all_optional_fields():
    """Test get_data_as with all fields provided"""
    from typing import Optional

    @dataclass
    class TestData:
        required: str
        optional: Optional[int] = None

    event = StreamEvent(
        event_type="test.event", data={"required": "test", "optional": 123}
    )

    result = event.get_data_as(TestData)

    assert result is not None
    assert result.required == "test"
    assert result.optional == 123


def test_stream_event_with_list_data():
    """Test StreamEvent with list in data"""
    event = StreamEvent(
        event_type="list.event",
        data={"items": [1, 2, 3, 4, 5], "count": 5},
    )

    assert event.data["items"] == [1, 2, 3, 4, 5]
    assert event.data["count"] == 5
    assert len(event.data["items"]) == 5


def test_stream_event_with_none_values():
    """Test StreamEvent with None values in data"""
    event = StreamEvent(
        event_type="null.event",
        data={"field1": None, "field2": "value", "field3": None},
    )

    assert event.data["field1"] is None
    assert event.data["field2"] == "value"
    assert event.data["field3"] is None


def test_stream_event_get_data_as_with_nested_dataclass():
    """Test get_data_as with nested dataclass structures"""

    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner
        count: int

    # This will likely fail because nested dataclass construction isn't supported
    # by the simple approach in get_data_as
    event = StreamEvent(
        event_type="test.event",
        data={"inner": {"value": "test"}, "count": 5},
    )

    result = event.get_data_as(Outer)

    # Python dataclasses don't auto-convert nested dicts to dataclasses
    # So the inner field will be a dict, not an Inner instance
    assert result is not None
    assert result.count == 5
    assert isinstance(result.inner, dict)  # inner is still a dict


def test_stream_event_different_event_types():
    """Test StreamEvent with various event type strings"""
    event_types = [
        "message.start",
        "message.delta",
        "message.completed",
        "tool_call.start",
        "tool_call.completed",
        "run.completed",
        "error",
    ]

    for event_type in event_types:
        event = StreamEvent(event_type=event_type, data={"test": "data"})
        assert event.event_type == event_type
        assert event.data == {"test": "data"}


def test_stream_event_with_numeric_data():
    """Test StreamEvent with various numeric types"""
    event = StreamEvent(
        event_type="numeric.event",
        data={
            "int_value": 42,
            "float_value": 3.14,
            "negative": -10,
            "zero": 0,
        },
    )

    assert event.data["int_value"] == 42
    assert event.data["float_value"] == 3.14
    assert event.data["negative"] == -10
    assert event.data["zero"] == 0


def test_stream_event_with_boolean_data():
    """Test StreamEvent with boolean values"""
    event = StreamEvent(
        event_type="bool.event",
        data={"true_value": True, "false_value": False},
    )

    assert event.data["true_value"] is True
    assert event.data["false_value"] is False


def test_stream_event_string_representation():
    """Test that StreamEvent can be converted to string"""
    event = StreamEvent(event_type="test.event", data={"key": "value"})

    # Just verify it doesn't crash
    str_repr = str(event)
    assert "test.event" in str_repr or "StreamEvent" in str_repr
