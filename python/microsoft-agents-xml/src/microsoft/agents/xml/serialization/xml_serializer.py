"""
XML serialization using xsdata.

Provides high-level API for serializing Python dataclasses to XML.
"""

from io import StringIO
from typing import Any, Type

from xsdata.formats.dataclass.serializers import XmlSerializer as XsDataXmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


class XmlSerializer:
    """High-level XML serializer for agent-xml models."""

    def __init__(self, pretty_print: bool = True, xml_declaration: bool = True):
        """
        Initialize XML serializer.

        Args:
            pretty_print: Whether to format XML with indentation
            xml_declaration: Whether to include <?xml version="1.0"?> declaration
        """
        self.config = SerializerConfig(
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
            indent="  ",  # 2-space indentation
        )
        self.serializer = XsDataXmlSerializer(config=self.config)

    def serialize(self, obj: Any, encoding: str = "utf-8") -> str:
        """
        Serialize a Python dataclass object to XML string.

        Args:
            obj: The dataclass object to serialize
            encoding: Character encoding (default: utf-8)

        Returns:
            XML string representation

        Example:
            >>> serializer = XmlSerializer()
            >>> xml = serializer.serialize(user_message)
            >>> print(xml)
            <?xml version="1.0" encoding="utf-8"?>
            <user message-id="msg_123">
              <text>Hello world</text>
            </user>
        """
        return self.serializer.render(obj, encoding=encoding)

    def serialize_to_file(self, obj: Any, file_path: str, encoding: str = "utf-8") -> None:
        """
        Serialize a Python dataclass object to an XML file.

        Args:
            obj: The dataclass object to serialize
            file_path: Path to output XML file
            encoding: Character encoding (default: utf-8)
        """
        xml_string = self.serialize(obj, encoding=encoding)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(xml_string)

    def serialize_to_bytes(self, obj: Any, encoding: str = "utf-8") -> bytes:
        """
        Serialize a Python dataclass object to XML bytes.

        Args:
            obj: The dataclass object to serialize
            encoding: Character encoding (default: utf-8)

        Returns:
            XML as bytes
        """
        xml_string = self.serialize(obj, encoding=encoding)
        return xml_string.encode(encoding)
