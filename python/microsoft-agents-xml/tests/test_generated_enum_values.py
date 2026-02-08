"""
Auto-generated enum value tests.
Tests that all enum values serialize and deserialize correctly.
"""

import pytest
from enum import Enum
from microsoft.agents.xml.models.messages import (
    ChatRole,
)


# ChatRole Enum Tests

def test_chat_role_system_value():
    """Test ChatRole.system value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.SYSTEM

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_developer_value():
    """Test ChatRole.developer value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.DEVELOPER

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_agent_value():
    """Test ChatRole.agent value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.AGENT

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_user_value():
    """Test ChatRole.user value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.USER

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_tool_value():
    """Test ChatRole.tool value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.TOOL

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_channel_value():
    """Test ChatRole.channel value serialization."""
    # Arrange: Get enum value
    enum_value = ChatRole.CHANNEL

    # Act: Serialize to string
    serialized = enum_value.value

    # Assert: Value serializes correctly
    assert serialized is not None
    assert len(serialized) > 0

    # Act: Parse back
    parsed = ChatRole(serialized)

    # Assert: Round-trip successful
    assert parsed == enum_value


def test_chat_role_all_values_are_valid():
    """Test all ChatRole values are valid."""
    # Arrange: Get all enum values
    all_values = list(ChatRole)

    # Assert: Each value can be serialized and deserialized
    for value in all_values:
        serialized = value.value
        assert serialized is not None
        parsed = ChatRole(serialized)
        assert parsed == value

