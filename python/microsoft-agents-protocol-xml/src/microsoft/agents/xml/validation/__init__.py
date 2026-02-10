"""
Validation module for agent-xml.

Provides validation for messages, threads, and conversation flows.
"""

from microsoft.agents.xml.validation.validation_result import ValidationResult, ValidationError
from microsoft.agents.xml.validation.thread_validator import ThreadValidator

__all__ = [
    "ValidationResult",
    "ValidationError",
    "ThreadValidator",
]
