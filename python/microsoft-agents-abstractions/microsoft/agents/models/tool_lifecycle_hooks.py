# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .lifecycle_hook import LifecycleHook


@dataclass
class ToolLifecycleHooks:
    # Executed before tool invocation.
EXAMPLES:
- Validate parameters
- Check permissions
- Log invocation
- Apply input guardrails
    before_execute: Optional[LifecycleHook] = None
    # Executed after successful tool invocation.
EXAMPLES:
- Validate output
- Persist result to memory
- Log completion
- Apply output guardrails
    after_execute: Optional[LifecycleHook] = None
    # Executed when tool invocation fails.
EXAMPLES:
- Log error
- Send alert
- Fallback behavior
    on_error: Optional[LifecycleHook] = None
