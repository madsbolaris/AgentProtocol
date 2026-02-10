"""
Property Test Code Generator

Generates C# and Python test code for property validation tests.
"""

from typing import List
from .typespec_parser import Model, Property
from .code_utils import to_pascal_case, to_snake_case, to_kebab_case, escape_python_keyword
from .property_test_generator import PropertyTestGenerator
from .test_utilities import is_complex_type, is_value_type, get_test_value_for_property


def generate_csharp_property_tests(models: List[Model], output_file: str) -> str:
    """
    Generate C# test code for property validation.

    Args:
        models: List of Model objects from TypeSpec parser
        output_file: Path to output test file

    Returns:
        Generated C# test code
    """
    content_types = [m for m in models if m.extends == "AIContentBase" and m.xml_root]
    test_generator = PropertyTestGenerator(models)

    lines = []
    lines.append("using System;")
    lines.append("using System.Xml;")
    lines.append("using System.Xml.Serialization;")
    lines.append("using System.Linq;")
    lines.append("using Microsoft.Agents.Xml.Core.Serialization;")
    lines.append("using Microsoft.Agents.Xml.Generated.Models;")
    lines.append("using Xunit;")
    lines.append("")
    lines.append("namespace Microsoft.Agents.Xml.Tests;")
    lines.append("")
    lines.append("/// <summary>")
    lines.append("/// Auto-generated property validation tests.")
    lines.append("/// Tests that every property serializes and deserializes correctly.")
    lines.append("/// </summary>")
    lines.append("public class GeneratedPropertyValidationTests")
    lines.append("{")

    # Generate tests for each content type
    for model in content_types:
        lines.extend(_generate_model_property_tests_csharp(model, test_generator))

    # Generate discriminator tests
    lines.append("    #region Discriminator Tests")
    lines.append("")
    for model in content_types:
        if model.kind:
            lines.extend(_generate_discriminator_test_csharp(model, test_generator))
    lines.append("    #endregion")
    lines.append("")

    # Generate required/optional tests
    lines.append("    #region Required vs Optional Tests")
    lines.append("")
    for model in content_types:
        lines.extend(_generate_required_optional_tests_csharp(model, test_generator))
    lines.append("    #endregion")
    lines.append("")

    lines.append("}")

    code = "\n".join(lines)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(code)

    return code


def _generate_model_property_tests_csharp(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate property tests for a single model (C#)."""
    lines = []
    lines.append(f"    #region {model.name} Property Tests")
    lines.append("")

    # Get testable properties (exclude kind, xmlIgnore, arrays, complex types)
    testable_props = [
        p for p in model.properties
        if p.name != "kind"
        and "@xmlIgnore" not in p.decorators
        and not p.type.startswith("List<")  # Skip arrays
        and not p.type.startswith("Array<")  # Skip arrays
        and p.type not in ["utcDateTime", "DateTime"]  # Skip dates for now
        and not is_complex_type(p.type)  # Skip complex types
    ]

    for prop in testable_props:
        test_name = f"Test_{model.name}_{to_pascal_case(prop.name)}_Property"
        test_value = get_test_value_for_property(prop)

        # Generate XML inline
        try:
            xml_content = test_generator.generate_property_test_xml(
                model.name,
                prop.name,
                test_value,
                test_id=f"{test_name}_msg"
            )
            # Escape XML for C# string literal
            xml_escaped = xml_content.replace('"', '""')
        except Exception as e:
            # Skip properties that can't be tested
            print(f"  ⚠️  Skipping {model.name}.{prop.name}: {e}")
            continue

        lines.append(f"    [Fact]")
        lines.append(f"    public void {test_name}()")
        lines.append("    {")
        lines.append(f"        // Arrange: XML with {prop.name} property set")
        lines.append(f'        var xml = @"{xml_escaped}";')
        lines.append(f"        var testValue = \"{test_value}\";")
        lines.append("")
        lines.append("        // Act: Deserialize")
        lines.append("        var serializer = new MessageSerializer();")
        lines.append("        var message = serializer.Deserialize(xml);")
        lines.append("")
        lines.append("        // Assert: Verify property value")
        lines.append(f"        Assert.NotNull(message);")
        lines.append(f"        var content = Assert.IsType<{model.name}>(message.Contents.FirstOrDefault());")

        # Only assert NotNull for reference types, not value types
        if not is_value_type(prop.type):
            lines.append(f"        Assert.NotNull(content.{to_pascal_case(prop.name)});")

        # Type-specific assertions
        if prop.type in ["int32", "integer", "int64"]:
            lines.append(f"        Assert.True(int.TryParse(testValue, out var expectedValue));")
            lines.append(f"        Assert.Equal(expectedValue, content.{to_pascal_case(prop.name)});")
        elif prop.type in ["float32", "float64", "float"]:
            lines.append(f"        Assert.True(double.TryParse(testValue, out var expectedValue));")
            lines.append(f"        Assert.Equal(expectedValue, content.{to_pascal_case(prop.name)}, 2);")
        elif prop.type == "boolean":
            lines.append(f"        Assert.True(bool.TryParse(testValue, out var expectedValue));")
            lines.append(f"        Assert.Equal(expectedValue, content.{to_pascal_case(prop.name)});")
        else:
            lines.append(f"        Assert.Equal(testValue, content.{to_pascal_case(prop.name)});")

        lines.append("    }")
        lines.append("")

    lines.append("    #endregion")
    lines.append("")

    return lines


def _generate_discriminator_test_csharp(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate discriminator test for a model (C#)."""
    lines = []
    test_name = f"Test_{model.name}_Discriminator"

    # Generate XML inline
    try:
        xml_content = test_generator.generate_discriminator_test_xml(
            model.name,
            test_id=f"{test_name}_msg"
        )
        # Escape XML for C# string literal
        xml_escaped = xml_content.replace('"', '""')
    except Exception as e:
        # Skip if can't generate
        print(f"  ⚠️  Skipping discriminator test for {model.name}: {e}")
        return []

    lines.append(f"    [Fact]")
    lines.append(f"    public void {test_name}()")
    lines.append("    {")
    lines.append(f"        // Arrange: XML with {model.kind} discriminator")
    lines.append(f'        var xml = @"{xml_escaped}";')
    lines.append("")
    lines.append("        // Act: Deserialize")
    lines.append("        var serializer = new MessageSerializer();")
    lines.append("        var message = serializer.Deserialize(xml);")
    lines.append("")
    lines.append("        // Assert: Verify correct type is instantiated")
    lines.append(f"        Assert.NotNull(message);")
    lines.append(f"        var content = Assert.IsType<{model.name}>(message.Contents.FirstOrDefault());")
    lines.append(f"        Assert.Equal(\"{model.kind}\", content.Kind);")
    lines.append("    }")
    lines.append("")

    return lines


def _generate_required_optional_tests_csharp(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate required/optional field tests for a model (C#)."""
    lines = []

    required_props = [p for p in model.properties if not p.optional and p.name != "kind" and "@xmlIgnore" not in p.decorators]
    optional_props = [p for p in model.properties if p.optional and "@xmlIgnore" not in p.decorators]

    # Test optional fields can be omitted
    if optional_props:
        test_name = f"Test_{model.name}_OptionalFieldsCanBeOmitted"

        # Generate XML inline with optional fields omitted
        try:
            omitted_field_names = [p.name for p in optional_props[:3]]
            xml_content = test_generator.generate_optional_field_test_xml(
                model.name,
                omitted_field_names,
                test_id=f"{test_name}_msg"
            )
            # Escape XML for C# string literal
            xml_escaped = xml_content.replace('"', '""')
        except Exception as e:
            # Skip if can't generate
            print(f"  ⚠️  Skipping optional field test for {model.name}: {e}")
            return lines

        lines.append(f"    [Fact]")
        lines.append(f"    public void {test_name}()")
        lines.append("    {")
        lines.append(f"        // Arrange: XML omitting optional fields: {', '.join(omitted_field_names)}")
        lines.append(f'        var xml = @"{xml_escaped}";')
        lines.append("")
        lines.append("        // Act: Deserialize (should succeed)")
        lines.append("        var serializer = new MessageSerializer();")
        lines.append("        var message = serializer.Deserialize(xml);")
        lines.append("")
        lines.append("        // Assert: Message deserializes successfully")
        lines.append(f"        Assert.NotNull(message);")
        lines.append(f"        var content = Assert.IsType<{model.name}>(message.Contents.FirstOrDefault());")
        lines.append(f"        Assert.NotNull(content);")
        lines.append("    }")
        lines.append("")

    return lines


def generate_python_property_tests(models: List[Model], output_file: str) -> str:
    """
    Generate Python test code for property validation.

    Args:
        models: List of Model objects from TypeSpec parser
        output_file: Path to output test file

    Returns:
        Generated Python test code
    """
    content_types = [m for m in models if m.extends == "AIContentBase" and m.xml_root]
    test_generator = PropertyTestGenerator(models)

    lines = []
    lines.append('"""')
    lines.append("Auto-generated property validation tests.")
    lines.append("Tests that every property serializes and deserializes correctly.")
    lines.append('"""')
    lines.append("")
    lines.append("import pytest")
    lines.append("from microsoft.agents.xml.serialization import MessageSerializer")
    lines.append("from microsoft.agents.xml.models.messages import (")
    for model in content_types:
        lines.append(f"    {model.name},")
    lines.append(")")
    lines.append("")
    lines.append("")

    # Generate tests for each content type
    for model in content_types:
        lines.extend(_generate_model_property_tests_python(model, test_generator))

    # Generate discriminator tests
    lines.append("# Discriminator Tests")
    lines.append("")
    for model in content_types:
        if model.kind:
            lines.extend(_generate_discriminator_test_python(model, test_generator))

    # Generate required/optional tests
    lines.append("# Required vs Optional Tests")
    lines.append("")
    for model in content_types:
        lines.extend(_generate_required_optional_tests_python(model, test_generator))

    code = "\n".join(lines)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(code)

    return code


def _generate_model_property_tests_python(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate property tests for a single model (Python)."""
    lines = []
    lines.append(f"# {model.name} Property Tests")
    lines.append("")

    # Get testable properties
    testable_props = [
        p for p in model.properties
        if p.name != "kind" and "@xmlIgnore" not in p.decorators
    ]

    for prop in testable_props:
        test_name = f"test_{to_snake_case(model.name)}_{to_snake_case(prop.name)}_property"
        test_value = get_test_value_for_property(prop)

        # Generate XML inline
        try:
            xml_content = test_generator.generate_property_test_xml(
                model.name,
                prop.name,
                test_value,
                test_id=f"{test_name}_msg"
            )
            # Escape for Python triple-quoted string
            xml_escaped = xml_content.replace('"""', r'\"\"\"')
        except Exception as e:
            # Skip properties that can't be tested
            print(f"  ⚠️  Skipping {model.name}.{prop.name}: {e}")
            continue

        lines.append(f"def {test_name}():")
        lines.append(f'    """Test {model.name}.{prop.name} property serialization."""')
        lines.append(f"    # Arrange: XML with {prop.name} property set")
        lines.append(f'    xml = """{xml_escaped}"""')
        lines.append(f'    test_value = "{test_value}"')
        lines.append("")
        lines.append("    # Act: Deserialize")
        lines.append("    serializer = MessageSerializer()")
        lines.append("    message = serializer.deserialize(xml)")
        lines.append("")
        # Get Python-safe property name
        python_prop_name = escape_python_keyword(to_snake_case(prop.name))

        lines.append("    # Assert: Verify property value")
        lines.append("    assert message is not None")
        lines.append("    assert len(message.contents) > 0")
        lines.append(f"    content = message.contents[0]")
        lines.append(f"    assert isinstance(content, {model.name})")
        lines.append(f"    assert content.{python_prop_name} is not None")

        # Type-specific assertions
        if prop.type in ["int32", "integer", "int64"]:
            lines.append(f"    assert content.{python_prop_name} == int(test_value)")
        elif prop.type in ["float32", "float64", "float"]:
            lines.append(f"    assert abs(content.{python_prop_name} - float(test_value)) < 0.01")
        elif prop.type == "boolean":
            lines.append(f"    assert content.{python_prop_name} == (test_value.lower() == 'true')")
        else:
            lines.append(f"    assert content.{python_prop_name} == test_value")

        lines.append("")
        lines.append("")

    return lines


def _generate_discriminator_test_python(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate discriminator test for a model (Python)."""
    lines = []
    test_name = f"test_{to_snake_case(model.name)}_discriminator"

    # Generate XML inline
    try:
        xml_content = test_generator.generate_discriminator_test_xml(
            model.name,
            test_id=f"{test_name}_msg"
        )
        # Escape for Python triple-quoted string
        xml_escaped = xml_content.replace('"""', r'\"\"\"')
    except Exception as e:
        # Skip if can't generate
        print(f"  ⚠️  Skipping discriminator test for {model.name}: {e}")
        return []

    lines.append(f"def {test_name}():")
    lines.append(f'    """Test {model.name} discriminator field."""')
    lines.append(f"    # Arrange: XML with {model.kind} discriminator")
    lines.append(f'    xml = """{xml_escaped}"""')
    lines.append("")
    lines.append("    # Act: Deserialize")
    lines.append("    serializer = MessageSerializer()")
    lines.append("    message = serializer.deserialize(xml)")
    lines.append("")
    lines.append("    # Assert: Verify correct type is instantiated")
    lines.append("    assert message is not None")
    lines.append("    assert len(message.contents) > 0")
    lines.append(f"    content = message.contents[0]")
    lines.append(f"    assert isinstance(content, {model.name})")
    lines.append(f'    assert content.kind == "{model.kind}"')
    lines.append("")
    lines.append("")

    return lines


def _generate_required_optional_tests_python(model: Model, test_generator: PropertyTestGenerator) -> List[str]:
    """Generate required/optional field tests for a model (Python)."""
    lines = []

    optional_props = [p for p in model.properties if p.optional and "@xmlIgnore" not in p.decorators]

    # Test optional fields can be omitted
    if optional_props:
        test_name = f"test_{to_snake_case(model.name)}_optional_fields_can_be_omitted"

        # Generate XML inline with optional fields omitted
        try:
            omitted_field_names = [p.name for p in optional_props[:3]]
            xml_content = test_generator.generate_optional_field_test_xml(
                model.name,
                omitted_field_names,
                test_id=f"{test_name}_msg"
            )
            # Escape for Python triple-quoted string
            xml_escaped = xml_content.replace('"""', r'\"\"\"')
        except Exception as e:
            # Skip if can't generate
            print(f"  ⚠️  Skipping optional field test for {model.name}: {e}")
            return lines

        lines.append(f"def {test_name}():")
        lines.append(f'    """Test {model.name} optional fields can be omitted."""')
        lines.append(f"    # Arrange: XML omitting optional fields: {', '.join(omitted_field_names)}")
        lines.append(f'    xml = """{xml_escaped}"""')
        lines.append("")
        lines.append("    # Act: Deserialize (should succeed)")
        lines.append("    serializer = MessageSerializer()")
        lines.append("    message = serializer.deserialize(xml)")
        lines.append("")
        lines.append("    # Assert: Message deserializes successfully")
        lines.append("    assert message is not None")
        lines.append("    assert len(message.contents) > 0")
        lines.append(f"    content = message.contents[0]")
        lines.append(f"    assert isinstance(content, {model.name})")
        lines.append("")
        lines.append("")

    return lines
