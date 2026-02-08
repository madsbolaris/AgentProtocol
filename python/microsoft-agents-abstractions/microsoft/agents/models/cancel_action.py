# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from enum import Enum
from typing import Literal


class CancelAction(str, Enum):
    """
    Cancel Action
@usage
Use Cases:
- interrupt: User stops generation, wants to see partial output
- rollback: Clean up failed/unwanted run completely (like "undo")
    """
    INTERRUPT = "interrupt"
    ROLLBACK = "rollback"


CancelActionType = Literal["interrupt", "rollback"]
