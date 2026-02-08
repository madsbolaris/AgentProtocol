"""
XML Test Generator

Generates valid XML test files for content types based on TypeSpec models.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional
from xml.dom import minidom

from .typespec_parser import Model, Property
from .code_utils import to_kebab_case


class XmlTestGenerator:
    """Generates XML test files from TypeSpec models"""

    def __init__(self, models: list[Model]):
        """
        Initialize generator with TypeSpec models.

        Args:
            models: List of Model objects from TypeSpec parser
        """
        self.models = {m.name: m for m in models}
        self.id_counter = 0

    def generate_test_file(
        self,
        content_type: str,
        variant: str = "minimal",
        message_id_override: Optional[str] = None
    ) -> str:
        """
        Generate XML test file for a content type.

        Args:
            content_type: Name of the content type model
            variant: "minimal" or "maximal"
            message_id_override: Optional message ID override

        Returns:
            Formatted XML string
        """
        model = self.models.get(content_type)
        if not model:
            raise ValueError(f"Content type not found: {content_type}")

        # Increment counter
        self.id_counter += 1

        # Determine appropriate role for this content type
        role = self._infer_role(content_type)

        # Create message wrapper
        message = self._create_message_element(role, message_id_override)

        # Create content element
        content = self._create_content_element(model, variant)
        message.append(content)

        # Format and return
        return self._format_xml(message)

    def _infer_role(self, content_type: str) -> str:
        """
        Infer appropriate message role for content type.

        Args:
            content_type: Content type name

        Returns:
            Role name (system, user, agent, tool, channel, developer)
        """
        # Map content types to roles
        role_mapping = {
            "FunctionCallContent": "agent",
            "TextReasoningContent": "agent",
            "FunctionResultContent": "tool",
            "EventContent": "channel",
            "TraceContent": "channel",
            "ActionContent": "channel",
            "TypingIndicatorContent": "channel",
            "MessageReactionContent": "channel",
            "MessageDeleteContent": "channel",
            "MessageUpdateContent": "channel",
        }

        return role_mapping.get(content_type, "agent")

    def _create_message_element(
        self,
        role: str,
        message_id_override: Optional[str] = None
    ) -> ET.Element:
        """
        Create message wrapper element.

        Args:
            role: Message role (system, user, agent, etc.)
            message_id_override: Optional message ID override

        Returns:
            XML Element for message
        """
        elem = ET.Element(role)

        # Message ID
        if message_id_override:
            elem.set("message-id", message_id_override)
        else:
            elem.set("message-id", f"msg_{self.id_counter:04d}")

        # Created timestamp
        elem.set("created-at", "2026-02-07T10:00:00Z")

        # Role-specific attributes
        if role == "user":
            elem.set("user-id", f"user_test_{self.id_counter}")
            elem.set("author-name", "Test User")
        elif role == "agent":
            elem.set("agent-id", f"agent_test_{self.id_counter}")
        elif role == "tool":
            # Tool messages typically don't have additional attributes
            pass
        elif role == "channel":
            # Channel messages typically don't have user/agent IDs
            pass

        return elem

    def _create_content_element(self, model: Model, variant: str) -> ET.Element:
        """
        Create content element with properties.

        Args:
            model: Model definition
            variant: "minimal" or "maximal"

        Returns:
            XML Element for content
        """
        elem = ET.Element(model.xml_root)

        # Track if we have text content
        has_text_content = False
        text_content_value = None

        # Process each property
        for prop in model.properties:
            # Skip 'kind' property (discriminator, not serialized)
            if prop.name == "kind":
                continue

            # Skip optional properties in minimal variant
            if prop.optional and variant == "minimal":
                # Exception: include some important optional fields even in minimal
                if prop.name not in ["audience", "encryption"]:
                    continue

            # Skip if marked with @xmlIgnore
            if "@xmlIgnore" in prop.decorators:
                continue

            # Generate value for property
            value = self._generate_value(prop, variant)

            # Handle different XML serialization patterns
            if "@xmlAttribute" in prop.decorators:
                # Attribute
                attr_name = prop.decorator_args.get("@xmlAttribute", prop.name)
                # Convert camelCase to kebab-case for attributes
                attr_name = to_kebab_case(attr_name) if attr_name == prop.name else attr_name
                elem.set(attr_name, value)

            elif "@xmlText" in prop.decorators:
                # Text content
                has_text_content = True
                text_content_value = value

            elif "@xmlElement" in prop.decorators:
                # Child element
                child_name = prop.decorator_args.get("@xmlElement", prop.name)
                child_name = to_kebab_case(child_name) if child_name == prop.name else child_name
                child = ET.SubElement(elem, child_name)
                child.text = value

        # Set text content if any
        if has_text_content and text_content_value:
            elem.text = text_content_value

        return elem

    def _generate_value(self, prop: Property, variant: str) -> str:
        """
        Generate realistic test value for property.

        Args:
            prop: Property definition
            variant: "minimal" or "maximal"

        Returns:
            String value for property
        """
        # Check for contentType decorator
        content_type = prop.decorator_args.get("@contentType")

        if content_type == "json":
            if variant == "minimal":
                return '{"status": "success"}'
            else:
                return '{"status": "success", "count": 42, "message": "Test data"}'

        elif content_type == "text":
            if variant == "minimal":
                return "Sample text content."
            else:
                return "This is a comprehensive sample text with more detail for maximal variant testing."

        # Type-specific generation
        if prop.type == "string":
            return self._generate_string_value(prop, variant)

        elif prop.type in ["int32", "integer"]:
            return self._generate_int_value(prop)

        elif prop.type == "int64":
            return str(1048576)

        elif prop.type in ["float32", "float64", "float"]:
            return "0.95"

        elif prop.type == "boolean":
            return "true"

        elif prop.type == "utcDateTime":
            return "2026-02-07T10:00:00Z"

        # Default
        return f"test_{prop.name}"

    def _generate_string_value(self, prop: Property, variant: str) -> str:
        """Generate string value based on property name and variant"""
        name_lower = prop.name.lower()

        if "uri" in name_lower or "url" in name_lower:
            return "https://example.com/test-resource"

        elif "id" in name_lower:
            if "file" in name_lower:
                return "file_abc123"
            elif "vector" in name_lower or "store" in name_lower:
                return "vs_xyz789"
            elif "call" in name_lower:
                return "call_001"
            elif "message" in name_lower:
                return "msg_ref_001"
            elif "user" in name_lower:
                return "user_123"
            else:
                return f"{prop.name}_test_123"

        elif "name" in name_lower or "title" in name_lower:
            return f"Test {prop.name}"

        elif "type" in name_lower:
            return "test_type"

        elif "text" in name_lower or "message" in name_lower or "content" in name_lower:
            if variant == "minimal":
                return "Sample text"
            else:
                return "Comprehensive sample text for testing"

        elif "mime" in name_lower or "media" in name_lower:
            if "image" in name_lower:
                return "image/png"
            elif "audio" in name_lower:
                return "audio/mpeg"
            elif "video" in name_lower:
                return "video/mp4"
            else:
                return "application/octet-stream"

        elif "filename" in name_lower:
            return "test-file.pdf"

        elif "reason" in name_lower:
            return "Test reason for testing purposes"

        elif "category" in name_lower:
            return "test_category"

        elif "severity" in name_lower:
            return "medium"

        elif "status" in name_lower:
            return "active"

        else:
            return f"Sample {prop.name} value"

    def _generate_int_value(self, prop: Property) -> str:
        """Generate integer value based on property name"""
        name_lower = prop.name.lower()

        if "width" in name_lower:
            return "1920"
        elif "height" in name_lower:
            return "1080"
        elif "duration" in name_lower:
            return "120"
        elif "frame" in name_lower:
            return "30"
        elif "count" in name_lower:
            return "42"
        elif "size" in name_lower:
            return "1024"
        else:
            return "100"

    def _format_xml(self, element: ET.Element) -> str:
        """
        Format XML with proper indentation.

        Args:
            element: XML Element

        Returns:
            Formatted XML string
        """
        # Convert to string
        rough_string = ET.tostring(element, encoding='unicode')

        # Parse with minidom for pretty printing
        reparsed = minidom.parseString(rough_string)

        # Get pretty XML
        pretty = reparsed.toprettyxml(indent="  ")

        # Remove XML declaration
        lines = pretty.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]

        # Remove empty lines
        lines = [line for line in lines if line.strip()]

        return '\n'.join(lines) + '\n'
