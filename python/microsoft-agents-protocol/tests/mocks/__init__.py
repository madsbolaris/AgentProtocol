"""
Mock implementations for testing LLM-powered agents.

This package provides:
- MockLLMClient: Replays recorded LLM responses

Note: LLM recording is now done by the .NET BasicM365Agent bot.
Use the generate_golden_datasets.py script with --record-llm flag.
"""

from .mock_llm_client import MockLLMClient

__all__ = [
    "MockLLMClient",
]
