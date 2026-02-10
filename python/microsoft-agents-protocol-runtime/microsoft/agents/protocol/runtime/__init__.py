# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Microsoft Agents Protocol Runtime Utilities.

Runtime utilities for Microsoft Agents Protocol including tool schema
generation, execution, and validation.
"""

from microsoft.agents.protocol.runtime.tools.schema_generator import ToolSchemaGenerator
from microsoft.agents.protocol.runtime.tools.executor import ToolExecutor

__all__ = ["ToolSchemaGenerator", "ToolExecutor"]
