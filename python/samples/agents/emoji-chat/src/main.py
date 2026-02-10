# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# Add packages to path for development
import sys
from pathlib import Path

# Add microsoft-agents-hosting to path
hosting_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-hosting"
if hosting_path.exists():
    sys.path.insert(0, str(hosting_path))

# Add microsoft-agents-protocol to path
protocol_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol"
if protocol_path.exists():
    sys.path.insert(0, str(protocol_path))

# Add microsoft-agents-protocol-abstractions to path (needed for models)
abstractions_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol-abstractions"
if abstractions_path.exists():
    sys.path.insert(0, str(abstractions_path))

# Now import and run the emoji chat bot
from .emoji_chat_bot import main

if __name__ == "__main__":
    main()
