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
class ToolOutput:
    """
    Tool Output
@usage
Use Cases:
- Tool approval: Human reviews delete_file before execution
- External execution: Tools executed by external system, results fed back
- Modified execution: Human modifies tool arguments before running
    """
    # Tool call ID this output corresponds to.
MUST: Match callId from FunctionCallContent in required_action.tool_calls
    tool_call_id: str
    # Tool execution result.
FLEXIBLE: String output or structured data (serialized to string)

EXAMPLES:
- Simple: "File deleted successfully"
- JSON: "{\"status\":\"success\",\"files_deleted\":3}"
- Error: "Permission denied: /protected/file.txt"
    output: str
