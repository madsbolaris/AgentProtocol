# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# Add protocol package to path for development (Agent Protocol extension)
import sys
from pathlib import Path

protocol_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol"
if protocol_path.exists():
    sys.path.insert(0, str(protocol_path))

# enable logging for Microsoft Agents library
# for more information, see README.md for Quickstart Agent
import logging
ms_agents_logger = logging.getLogger("microsoft.agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)

from .agent import AGENT_APP, CONNECTION_MANAGER
from .start_server import start_server

start_server(
    agent_application=AGENT_APP,
    auth_configuration=None,  # Run in anonymous mode for demo
)
