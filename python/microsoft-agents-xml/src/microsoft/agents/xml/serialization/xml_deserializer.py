"""
XML deserialization using xsdata.

Provides high-level API for deserializing XML to Python dataclasses.
"""

from pathlib import Path
from typing import Type, TypeVar

from xsdata.formats.dataclass.parsers import XmlParser as XsDataXmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

T = TypeVar("T")


class XmlDeserializer:
    """High-level XML deserializer for agent-xml models."""

    def __init__(self):
        """Initialize XML deserializer."""
        self.config = ParserConfig()
        self.parser = XsDataXmlParser(config=self.config)

    def deserialize(self, xml: str, target_class: Type[T]) -> T:
        """
        Deserialize XML string to a Python dataclass object.

        Args:
            xml: XML string to deserialize
            target_class: The target dataclass type

        Returns:
            Instance of target_class populated with XML data

        Example:
            >>> deserializer = XmlDeserializer()
            >>> user_msg = deserializer.deserialize(xml_string, UserMessage)
            >>> print(user_msg.message_id)
            msg_123
        """
        return self.parser.from_string(xml, target_class)

    def deserialize_from_file(self, file_path: str | Path, target_class: Type[T]) -> T:
        """
        Deserialize XML file to a Python dataclass object.

        Args:
            file_path: Path to XML file
            target_class: The target dataclass type

        Returns:
            Instance of target_class populated with XML data
        """
        xml_content = Path(file_path).read_text(encoding="utf-8")
        return self.deserialize(xml_content, target_class)

    def deserialize_from_bytes(self, xml_bytes: bytes, target_class: Type[T]) -> T:
        """
        Deserialize XML bytes to a Python dataclass object.

        Args:
            xml_bytes: XML as bytes
            target_class: The target dataclass type

        Returns:
            Instance of target_class populated with XML data
        """
        return self.parser.from_bytes(xml_bytes, target_class)
