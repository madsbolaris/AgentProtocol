"""
Message serializer for XML messages.

Provides a unified interface for serializing and deserializing chat messages.
"""

from typing import Any, Type, Union
from pathlib import Path

from microsoft.agents.xml.serialization.xml_serializer import XmlSerializer
from microsoft.agents.xml.serialization.xml_deserializer import XmlDeserializer


class MessageSerializer:
    """
    High-level message serializer combining serialization and deserialization.

    This class provides a unified API similar to the C# MessageSerializer,
    making it easier to work with XML messages in tests and application code.
    """

    def __init__(self, pretty_print: bool = True, xml_declaration: bool = True):
        """
        Initialize message serializer.

        Args:
            pretty_print: Whether to format XML with indentation
            xml_declaration: Whether to include <?xml version="1.0"?> declaration
        """
        self.serializer = XmlSerializer(
            pretty_print=pretty_print,
            xml_declaration=xml_declaration
        )
        self.deserializer = XmlDeserializer()

    def serialize(self, obj: Any) -> str:
        """
        Serialize a message object to XML string.

        Args:
            obj: The message object to serialize

        Returns:
            XML string representation
        """
        return self.serializer.serialize(obj)

    def deserialize(self, xml: Union[str, bytes, Path], target_type: Type[Any] = None) -> Any:
        """
        Deserialize XML to a message object.

        Args:
            xml: XML string, bytes, or file path
            target_type: The target type to deserialize to. If None, auto-detects from root element.

        Returns:
            Deserialized message object
        """
        if target_type is None:
            # Auto-detect message type from root element
            from lxml import etree

            # Parse XML to get root element
            if isinstance(xml, (str, bytes)):
                root = etree.fromstring(xml.encode('utf-8') if isinstance(xml, str) else xml)
            else:
                root = etree.parse(xml).getroot()

            # Map root element name to message type
            from microsoft.agents.xml.models.messages import (
                SystemMessage, DeveloperMessage, UserMessage, AgentMessage,
                ToolMessage, ChannelMessage
            )

            element_to_type = {
                'system': SystemMessage,
                'developer': DeveloperMessage,
                'user': UserMessage,
                'agent': AgentMessage,
                'tool': ToolMessage,
                'channel': ChannelMessage,
            }

            root_name = root.tag
            target_type = element_to_type.get(root_name)

            if target_type is None:
                raise ValueError(f"Unknown message type: {root_name}")

        return self.deserializer.deserialize(xml, target_type)

    def serialize_to_file(self, obj: Any, file_path: Union[str, Path]) -> None:
        """
        Serialize a message object to an XML file.

        Args:
            obj: The message object to serialize
            file_path: Path to write the XML file
        """
        self.serializer.serialize_to_file(obj, file_path)

    def deserialize_from_file(self, file_path: Union[str, Path], target_type: Type[Any]) -> Any:
        """
        Deserialize XML from a file to a message object.

        Args:
            file_path: Path to the XML file
            target_type: The target type to deserialize to

        Returns:
            Deserialized message object
        """
        return self.deserializer.deserialize_from_file(file_path, target_type)
