# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class AIContentBase:
    """
    Base model for all AI content types.
Provides common properties for audience filtering, encryption, and extensibility.
RATIONALE: DRY principle - common properties inherited by all 29+ content types
PROPERTIES:
- audience: Content-level audience filtering (e.g., reasoning visible to assistant only)
- encryption: Content-level encryption metadata
- additionalProperties: Client-side extensibility (not serialized to XML)
    """
    # Target audience filter (comma-separated roles).
Controls which roles should see this content:
- Omitted/null: Visible to all roles (default)
- "user": Human-only content (UI hints, summaries)
- "agent": Agent-only content (reasoning, internal context)
- "user,agent": Explicitly visible to both

EXAMPLES:
- <thinking audience="agent">reasoning here</thinking>
- <text audience="user">User-facing summary</text>
- <adaptive-card audience="user" />
    audience: Optional[str] = None
    # Encryption information (simplified as string for XML).
Contains encryption key reference and metadata.

RATIONALE: Simplified from complex EncryptionInfo object for XML compatibility
FORMAT: JSON string or key reference
    encryption: Optional[str] = None
    # Additional properties for extensibility.
NOT SERIALIZED: Client-side metadata, transient state.

EXAMPLES:
- Tracking IDs, correlation data
- Client-specific rendering hints
- Temporary computation results
    additional_properties: Optional[Dict[str, Any]] = None
