# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Structured streaming events"""

import json
from dataclasses import dataclass
from typing import Dict, Any, TypeVar, Type, Optional

T = TypeVar("T")


@dataclass
class StreamEvent:
    """
    Server-Sent Event from a streaming run.
    """

    event_type: str
    """Event type (e.g., 'message.start', 'message.delta', 'tool_call.start')"""

    data: Dict[str, Any]
    """Event data as dictionary"""

    def get_data_as(self, cls: Type[T]) -> Optional[T]:
        """
        Deserialize data to specific type.

        Args:
            cls: Target class to deserialize to

        Returns:
            Deserialized object or None if deserialization fails
        """
        try:
            # For dataclasses, try to construct from dict
            if hasattr(cls, "__dataclass_fields__"):
                return cls(**self.data)

            # For other types, try JSON serialization approach
            json_str = json.dumps(self.data)
            return json.loads(json_str, object_hook=lambda d: cls(**d))
        except (TypeError, ValueError, KeyError):
            return None
