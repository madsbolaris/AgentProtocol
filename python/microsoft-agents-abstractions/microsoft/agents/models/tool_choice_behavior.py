# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from typing import Union

from .auto_tool_choice import AutoToolChoice
from .required_tool_choice import RequiredToolChoice
from .none_tool_choice import NoneToolChoice
from .specific_tool_choice import SpecificToolChoice


# Tool Choice Behavior
FROM: Azure Agent API (ToolChoiceBehavior)
CONTROLS: How agent uses tools
MESSAGING APP ANALOGY:
- "auto": Bot decides when to use commands
- "required": Bot must use a command
- "none": Bot cannot use commands (text-only response)
- "specific": Force specific command (like /help shortcut)
ToolChoiceBehavior = Union[AutoToolChoice, RequiredToolChoice, NoneToolChoice, SpecificToolChoice]
