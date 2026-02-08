# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from enum import Enum
from typing import Literal


class ThreadCleanup(str, Enum):
    """
    Thread Cleanup Strategy
@usage
Use Cases:
- keep: Chat conversations, multi-turn interactions
- delete: Extraction tasks, one-shot queries, stateless APIs
    """
    KEEP = "keep"
    DELETE = "delete"


ThreadCleanupType = Literal["keep", "delete"]
