"""
Agent XML - Python implementation

XML serialization for Agent Protocol messages.
"""

__version__ = "0.1.0"

from microsoft.agents.xml.serialization.xml_serializer import XmlSerializer
from microsoft.agents.xml.serialization.xml_deserializer import XmlDeserializer
from microsoft.agents.xml.serialization.message_serializer import MessageSerializer
from microsoft.agents.xml.validation import (
    ValidationResult,
    ValidationError,
    ThreadValidator,
)

__all__ = [
    "XmlSerializer",
    "XmlDeserializer",
    "MessageSerializer",
    "ValidationResult",
    "ValidationError",
    "ThreadValidator",
    "__version__"
]
