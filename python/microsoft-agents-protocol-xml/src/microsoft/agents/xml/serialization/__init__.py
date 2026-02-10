"""
XML serialization and deserialization runtime.
"""

from microsoft.agents.xml.serialization.xml_serializer import XmlSerializer
from microsoft.agents.xml.serialization.xml_deserializer import XmlDeserializer
from microsoft.agents.xml.serialization.message_serializer import MessageSerializer

__all__ = ["XmlSerializer", "XmlDeserializer", "MessageSerializer"]
