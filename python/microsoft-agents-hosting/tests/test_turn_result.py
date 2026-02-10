# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for TurnResult enum."""

from microsoft.agents.hosting import TurnResult


def test_turn_result_values():
    """Test that TurnResult has the expected values."""
    assert TurnResult.CONTINUE.value == "continue"
    assert TurnResult.CONSUMED.value == "consumed"
    assert TurnResult.REPLIED.value == "replied"


def test_turn_result_equality():
    """Test TurnResult equality."""
    assert TurnResult.CONTINUE == TurnResult.CONTINUE
    assert TurnResult.CONTINUE != TurnResult.CONSUMED
    assert TurnResult.CONSUMED != TurnResult.REPLIED
