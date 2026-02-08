# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class AIContentBase(ABC):
    """
    Base class for all content types.
    Contains the discriminator property 'kind' and optional audience.
    """

    # Target audience for this content (user, agent, or both)
    audience: Optional[Literal['user', 'agent']] = None

    @property
    @abstractmethod
    def kind(self) -> str:
        """Content type discriminator."""
        ...
