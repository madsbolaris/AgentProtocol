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
class ThreadCopyRequest:
    """
    Thread Copy Request
@usage
Use Cases:
- "Try this approach instead" → Copy thread, continue with different strategy
- Testing agents: Same input conversation, multiple agent configurations
- Template threads: Copy starter thread for new conversations
- Conversation variations: Explore what-if scenarios
    """
    # Whether to include full message history in copied thread.

@usage

Use Cases:
- true: Branch from specific conversation point (A/B testing, variations)
- false: Reuse thread template/structure without history

    include_history: Optional[bool] = None
    # Metadata for the new copied thread.
OPTIONAL: Override or add metadata to distinguish copy from original

COMMON FIELDS:
- original_thread_id: Reference to source thread
- copy_reason: Why this thread was copied
- variant_name: For A/B testing variants

MERGE BEHAVIOR:
- Merges with original thread metadata
- New values override original values for same keys
    metadata: Optional[Dict[str, Any]] = None
