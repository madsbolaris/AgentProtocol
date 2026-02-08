# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Configuration options for Agent Protocol client"""

from dataclasses import dataclass, field
from typing import Optional
import aiohttp


@dataclass
class AgentProtocolClientOptions:
    """Configuration options for Agent Protocol client"""

    base_url: str
    """Base URL for the Agent Protocol API"""

    api_key: Optional[str] = None
    """Optional API key for authentication"""

    session: Optional[aiohttp.ClientSession] = None
    """Optional aiohttp session to use for requests. If not provided, a new session will be created"""

    timeout_seconds: int = 30
    """Request timeout in seconds (default: 30)"""

    max_retries: int = 3
    """Maximum number of retry attempts for failed requests (default: 3)"""
