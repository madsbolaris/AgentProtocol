"""
Shared utilities for OpenAI prompt caching optimization.
"""
from typing import Optional
from hashlib import sha256
import json


def generate_cache_key(
    agent_name: str,
    conversation_id: str,
    static_content_hash: Optional[str] = None
) -> str:
    """
    Generate a stable cache key for OpenAI prompt caching.

    Args:
        agent_name: Name of the agent (e.g., "emoji-chat", "basic-m365")
        conversation_id: Unique conversation identifier
        static_content_hash: Optional hash of static prompt content

    Returns:
        Cache key string for OpenAI's prompt_cache_key parameter
    """
    components = [agent_name, conversation_id]
    if static_content_hash:
        components.append(static_content_hash)

    return sha256(":".join(components).encode()).hexdigest()[:16]


def compute_static_content_hash(
    system_prompt: str,
    tool_definitions: Optional[list] = None
) -> str:
    """
    Compute stable hash of static prompt content.

    Used to detect when static content changes and cache should be invalidated.

    Args:
        system_prompt: The system prompt string
        tool_definitions: Optional list of tool definitions

    Returns:
        16-character hash of the static content
    """
    content = system_prompt
    if tool_definitions:
        # Normalize tool definitions for stable hashing
        content += json.dumps(tool_definitions, sort_keys=True)

    return sha256(content.encode()).hexdigest()[:16]


def should_use_caching(messages: list, tools: Optional[list] = None) -> bool:
    """
    Determine if request should use caching.

    OpenAI caching requires >1024 tokens for automatic activation.
    Returns True if messages + tools likely exceed threshold.

    Args:
        messages: List of message dictionaries
        tools: Optional list of tool definitions

    Returns:
        True if estimated tokens > 1024, False otherwise
    """
    # Rough estimate: 1 token ≈ 4 characters
    total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)

    if tools:
        total_chars += len(json.dumps(tools))

    # Use caching if estimated tokens > 1024
    return (total_chars / 4) > 1024
