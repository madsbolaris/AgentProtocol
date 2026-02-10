"""
Property Test Generator

Generates comprehensive property validation tests for all content types.
Implements Phase 1 test categories:
1. Property Validation Tests - Verify every property serializes/deserializes correctly
2. Enum Value Tests - Test all enum values serialize correctly
3. Required vs Optional Tests - Test required/optional field handling
4. Discriminator Tests - Test polymorphic serialization with discriminators
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from xml.dom import minidom

from .typespec_parser import Model, Property
from .code_utils import to_kebab_case, to_pascal_case, to_snake_case, to_camel_case


class PropertyTestGenerator:
    """Generates property validation tests from TypeSpec models"""

    def __init__(self, models: List[Model]):
        """
        Initialize generator with TypeSpec models.

        Args:
            models: List of Model objects from TypeSpec parser
        """
        self.models = {m.name: m for m in models}
        self.id_counter = 0

    def generate_property_test_xml(
        self,
        content_type: str,
        property_name: str,
        property_value: str,
        test_id: Optional[str] = None
    ) -> str:
        """
        Generate XML test file focusing on a specific property.

        Args:
            content_type: Name of the content type model
            property_name: Property to test
            property_value: Value for the property
            test_id: Optional test identifier

        Returns:
            Formatted XML string
        """
        model = self.models.get(content_type)
        if not model:
            raise ValueError(f"Content type not found: {content_type}")

        self.id_counter += 1
        role = self._infer_role(content_type)
        message = self._create_message_element(role, test_id)

        # Create minimal content with just required properties + the test property
        content = self._create_content_with_property(model, property_name, property_value)
        message.append(content)

        return self._format_xml(message)

    def generate_required_field_test_xml(
        self,
        content_type: str,
        omitted_required_field: str,
        test_id: Optional[str] = None
    ) -> str:
        """
        Generate XML test file that omits a required field (should fail validation).

        Args:
            content_type: Name of the content type model
            omitted_required_field: Required field to omit
            test_id: Optional test identifier

        Returns:
            Formatted XML string (invalid, for negative testing)
        """
        model = self.models.get(content_type)
        if not model:
            raise ValueError(f"Content type not found: {content_type}")

        self.id_counter += 1
        role = self._infer_role(content_type)
        message = self._create_message_element(role, test_id)

        # Create content omitting the required field
        content = self._create_content_omitting_field(model, omitted_required_field)
        message.append(content)

        return self._format_xml(message)

    def generate_optional_field_test_xml(
        self,
        content_type: str,
        omitted_optional_fields: List[str],
        test_id: Optional[str] = None
    ) -> str:
        """
        Generate XML test file that omits optional fields (should succeed).

        Args:
            content_type: Name of the content type model
            omitted_optional_fields: Optional fields to omit
            test_id: Optional test identifier

        Returns:
            Formatted XML string
        """
        model = self.models.get(content_type)
        if not model:
            raise ValueError(f"Content type not found: {content_type}")

        self.id_counter += 1
        role = self._infer_role(content_type)
        message = self._create_message_element(role, test_id)

        # Create content omitting the optional fields
        content = self._create_content_omitting_fields(model, omitted_optional_fields)
        message.append(content)

        return self._format_xml(message)

    def generate_discriminator_test_xml(
        self,
        content_type: str,
        test_id: Optional[str] = None
    ) -> str:
        """
        Generate XML test file that focuses on discriminator (kind) field.

        Args:
            content_type: Name of the content type model
            test_id: Optional test identifier

        Returns:
            Formatted XML string
        """
        model = self.models.get(content_type)
        if not model:
            raise ValueError(f"Content type not found: {content_type}")

        if not model.kind:
            raise ValueError(f"Content type {content_type} has no discriminator")

        self.id_counter += 1
        role = self._infer_role(content_type)
        message = self._create_message_element(role, test_id)

        # Create minimal content - discriminator is automatically added by kind value
        content = self._create_minimal_content(model)
        message.append(content)

        return self._format_xml(message)

    def _infer_role(self, content_type: str) -> str:
        """Infer appropriate message role for content type."""
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
        """Create message wrapper element."""
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

        return elem

    def _create_content_with_property(
        self,
        model: Model,
        test_property: str,
        test_value: str
    ) -> ET.Element:
        """Create content element with specific property set."""
        elem = ET.Element(model.xml_root)

        has_text_content = False
        text_content_value = None

        for prop in model.properties:
            # Skip 'kind' property (discriminator)
            if prop.name == "kind":
                continue

            # Skip if marked with @xmlIgnore
            if "@xmlIgnore" in prop.decorators:
                continue

            # Determine if we should include this property
            is_test_property = prop.name == test_property
            is_required = not prop.optional

            # Include if: required OR is the test property
            if not is_required and not is_test_property:
                continue

            # Use test value for test property, minimal values for others
            value = test_value if is_test_property else self._generate_minimal_value(prop)

            # Handle different XML serialization patterns
            if "@xmlAttribute" in prop.decorators:
                attr_name = prop.decorator_args.get("@xmlAttribute", prop.name)
                attr_name = to_kebab_case(attr_name) if attr_name == prop.name else attr_name
                elem.set(attr_name, value)

            elif "@xmlText" in prop.decorators:
                has_text_content = True
                text_content_value = value

            elif "@xmlElement" in prop.decorators:
                child_name = prop.decorator_args.get("@xmlElement", prop.name)
                child_name = to_kebab_case(child_name) if child_name == prop.name else child_name
                child = ET.SubElement(elem, child_name)
                child.text = value

        if has_text_content and text_content_value:
            elem.text = text_content_value

        return elem

    def _create_content_omitting_field(
        self,
        model: Model,
        omitted_field: str
    ) -> ET.Element:
        """Create content element omitting a specific field."""
        elem = ET.Element(model.xml_root)

        has_text_content = False
        text_content_value = None

        for prop in model.properties:
            # Skip 'kind' property
            if prop.name == "kind":
                continue

            # Skip the omitted field
            if prop.name == omitted_field:
                continue

            # Skip if marked with @xmlIgnore
            if "@xmlIgnore" in prop.decorators:
                continue

            # Only include required properties (for minimal test)
            if prop.optional:
                continue

            value = self._generate_minimal_value(prop)

            # Handle different XML serialization patterns
            if "@xmlAttribute" in prop.decorators:
                attr_name = prop.decorator_args.get("@xmlAttribute", prop.name)
                attr_name = to_kebab_case(attr_name) if attr_name == prop.name else attr_name
                elem.set(attr_name, value)

            elif "@xmlText" in prop.decorators:
                has_text_content = True
                text_content_value = value

            elif "@xmlElement" in prop.decorators:
                child_name = prop.decorator_args.get("@xmlElement", prop.name)
                child_name = to_kebab_case(child_name) if child_name == prop.name else child_name
                child = ET.SubElement(elem, child_name)
                child.text = value

        if has_text_content and text_content_value:
            elem.text = text_content_value

        return elem

    def _create_content_omitting_fields(
        self,
        model: Model,
        omitted_fields: List[str]
    ) -> ET.Element:
        """Create content element omitting multiple fields."""
        elem = ET.Element(model.xml_root)

        has_text_content = False
        text_content_value = None

        for prop in model.properties:
            # Skip 'kind' property
            if prop.name == "kind":
                continue

            # Skip omitted fields
            if prop.name in omitted_fields:
                continue

            # Skip if marked with @xmlIgnore
            if "@xmlIgnore" in prop.decorators:
                continue

            # Only include required properties
            if prop.optional:
                continue

            value = self._generate_minimal_value(prop)

            # Handle different XML serialization patterns
            if "@xmlAttribute" in prop.decorators:
                attr_name = prop.decorator_args.get("@xmlAttribute", prop.name)
                attr_name = to_kebab_case(attr_name) if attr_name == prop.name else attr_name
                elem.set(attr_name, value)

            elif "@xmlText" in prop.decorators:
                has_text_content = True
                text_content_value = value

            elif "@xmlElement" in prop.decorators:
                child_name = prop.decorator_args.get("@xmlElement", prop.name)
                child_name = to_kebab_case(child_name) if child_name == prop.name else child_name
                child = ET.SubElement(elem, child_name)
                child.text = value

        if has_text_content and text_content_value:
            elem.text = text_content_value

        return elem

    def _create_minimal_content(self, model: Model) -> ET.Element:
        """Create minimal content element with only required properties."""
        elem = ET.Element(model.xml_root)

        has_text_content = False
        text_content_value = None

        for prop in model.properties:
            # Skip 'kind' property
            if prop.name == "kind":
                continue

            # Skip if marked with @xmlIgnore
            if "@xmlIgnore" in prop.decorators:
                continue

            # Only include required properties
            if prop.optional:
                continue

            value = self._generate_minimal_value(prop)

            # Handle different XML serialization patterns
            if "@xmlAttribute" in prop.decorators:
                attr_name = prop.decorator_args.get("@xmlAttribute", prop.name)
                attr_name = to_kebab_case(attr_name) if attr_name == prop.name else attr_name
                elem.set(attr_name, value)

            elif "@xmlText" in prop.decorators:
                has_text_content = True
                text_content_value = value

            elif "@xmlElement" in prop.decorators:
                child_name = prop.decorator_args.get("@xmlElement", prop.name)
                child_name = to_kebab_case(child_name) if child_name == prop.name else child_name
                child = ET.SubElement(elem, child_name)
                child.text = value

        if has_text_content and text_content_value:
            elem.text = text_content_value

        return elem

    def _generate_minimal_value(self, prop: Property) -> str:
        """Generate minimal test value for property."""
        if prop.type == "string":
            return "test"
        elif prop.type in ["int32", "integer"]:
            return "1"
        elif prop.type == "int64":
            return "1000"
        elif prop.type in ["float32", "float64", "float"]:
            return "0.5"
        elif prop.type == "boolean":
            return "true"
        elif prop.type == "utcDateTime":
            return "2026-02-07T10:00:00Z"
        else:
            return "test_value"

    def _format_xml(self, element: ET.Element) -> str:
        """Format XML with proper indentation."""
        rough_string = ET.tostring(element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent="  ")

        # Remove XML declaration
        lines = pretty.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]

        # Remove empty lines
        lines = [line for line in lines if line.strip()]

        return '\n'.join(lines) + '\n'
