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
class RunOptions:
    """
    Run Options
FROM: Azure Agent API (RunOptions) + OpenAI Agents SDK (RunOptions/RunConfig)
    """
    # Continuation token for resuming background responses.
FROM: MAF (AgentRunOptions.ContinuationToken)
    continuation_token: Optional[str] = None
