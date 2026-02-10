"""
Mock implementations for testing LLM-powered agents.

This package provides:
- MockLLMClient: Replays recorded LLM responses
- LLMRecorder: Records and replays LLM API interactions

Use the generate_golden_datasets.py or generate_eval_datasets.py scripts
with --record-llm flag to generate recordings.
"""

from .mock_llm_client import MockLLMClient
from .llm_recorder import LLMRecorder

__all__ = [
    "MockLLMClient",
    "LLMRecorder",
]
