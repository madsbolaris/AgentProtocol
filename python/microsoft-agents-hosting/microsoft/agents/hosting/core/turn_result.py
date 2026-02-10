# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Turn result enum for controlling message flow."""

from enum import Enum


class TurnResult(Enum):
    """
    Represents the result of processing a turn in an agent conversation.
    Provides explicit control flow for message handling.
    """

    CONTINUE = "continue"
    """Continue processing - pass to next handler or LLM."""

    CONSUMED = "consumed"
    """Message has been consumed - stop processing, no response needed."""

    REPLIED = "replied"
    """A response has already been sent - stop processing."""
