# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for stub modules to achieve 100% coverage."""

import pytest


def test_middleware_module_import():
    """Test that middleware module can be imported."""
    from microsoft.agents.hosting import middleware

    assert middleware is not None
    # Verify __all__ is defined
    assert hasattr(middleware, "__all__")
    assert middleware.__all__ == []


def test_observability_module_import():
    """Test that observability module can be imported."""
    from microsoft.agents.hosting import observability

    assert observability is not None
    # Verify __all__ is defined
    assert hasattr(observability, "__all__")
    assert observability.__all__ == []


def test_testing_module_import():
    """Test that testing module can be imported."""
    from microsoft.agents.hosting import testing

    assert testing is not None
    # Verify __all__ is defined
    assert hasattr(testing, "__all__")
    assert testing.__all__ == []


def test_all_stub_modules_accessible():
    """Test that all stub modules are accessible from the main package."""
    from microsoft.agents.hosting import middleware, observability, testing

    # All should be importable without errors
    assert middleware is not None
    assert observability is not None
    assert testing is not None
