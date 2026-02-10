"""
Enum Test Generator

Generates tests for enum value serialization.
Implements Phase 1 test category: Enum Value Tests
"""

from typing import List, Dict
from .typespec_parser import Model
from .code_utils import to_pascal_case, to_snake_case, to_kebab_case


class EnumInfo:
    """Information about an enum extracted from TypeSpec"""
    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values


def extract_enums_from_typespec(typespec_content: str) -> List[EnumInfo]:
    """
    Extract enum definitions from TypeSpec content.

    Args:
        typespec_content: Full TypeSpec file content

    Returns:
        List of EnumInfo objects
    """
    import re

    enums = []
    enum_pattern = r'enum\s+(\w+)\s*\{([^}]+)\}'

    for match in re.finditer(enum_pattern, typespec_content):
        enum_name = match.group(1)
        enum_body = match.group(2)

        # Extract enum values - only match identifiers at start of line (not in comments)
        # Pattern: optional whitespace, identifier, optional colon + string, optional comma
        values = []
        for line in enum_body.split('\n'):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('/**') or line.startswith('*'):
                continue
            # Match enum value at start of line
            value_match = re.match(r'^(\w+)(?:\s*:\s*"[^"]*")?[,\s]*', line)
            if value_match:
                values.append(value_match.group(1))

        if values:
            enums.append(EnumInfo(enum_name, values))

    return enums


def generate_csharp_enum_tests(enums: List[EnumInfo], output_file: str) -> str:
    """
    Generate C# test code for enum value validation.

    Args:
        enums: List of EnumInfo objects
        output_file: Path to output test file

    Returns:
        Generated C# test code
    """
    lines = []
    lines.append("using System;")
    lines.append("using System.Xml;")
    lines.append("using System.Xml.Serialization;")
    lines.append("using Microsoft.Agents.Xml.Generated.Models;")
    lines.append("using Xunit;")
    lines.append("")
    lines.append("namespace Microsoft.Agents.Xml.Tests;")
    lines.append("")
    lines.append("/// <summary>")
    lines.append("/// Auto-generated enum value tests.")
    lines.append("/// Tests that all enum values serialize and deserialize correctly.")
    lines.append("/// </summary>")
    lines.append("public class GeneratedEnumValueTests")
    lines.append("{")

    for enum_info in enums:
        lines.extend(_generate_enum_tests_csharp(enum_info))

    lines.append("}")

    code = "\n".join(lines)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(code)

    return code


def _generate_enum_tests_csharp(enum_info: EnumInfo) -> List[str]:
    """Generate tests for a single enum (C#)."""
    lines = []
    lines.append(f"    #region {enum_info.name} Enum Tests")
    lines.append("")

    # Deduplicate values to avoid duplicate test methods
    seen_test_names = set()

    # Test each enum value
    for value in enum_info.values:
        test_name = f"Test_{enum_info.name}_{to_pascal_case(value)}_Value"

        # Skip if we've already generated this test
        if test_name in seen_test_names:
            continue
        seen_test_names.add(test_name)

        lines.append(f"    [Fact]")
        lines.append(f"    public void {test_name}()")
        lines.append("    {")
        lines.append(f"        // Arrange: Get enum value")
        lines.append(f"        var enumValue = {enum_info.name}.{to_pascal_case(value)};")
        lines.append("")
        lines.append("        // Act: Serialize to string")
        lines.append(f"        var serialized = enumValue.ToString();")
        lines.append("")
        lines.append("        // Assert: Value serializes correctly")
        lines.append(f"        Assert.NotNull(serialized);")
        lines.append(f"        Assert.NotEmpty(serialized);")
        lines.append("")
        lines.append("        // Act: Parse back")
        lines.append(f"        var parsed = Enum.Parse<{enum_info.name}>(serialized);")
        lines.append("")
        lines.append("        // Assert: Round-trip successful")
        lines.append(f"        Assert.Equal(enumValue, parsed);")
        lines.append("    }")
        lines.append("")

    # Test all enum values are valid
    test_name = f"Test_{enum_info.name}_AllValuesAreValid"
    lines.append(f"    [Fact]")
    lines.append(f"    public void {test_name}()")
    lines.append("    {")
    lines.append(f"        // Arrange: Get all enum values")
    lines.append(f"        var allValues = Enum.GetValues<{enum_info.name}>();")
    lines.append("")
    lines.append("        // Assert: Each value can be serialized and deserialized")
    lines.append("        foreach (var value in allValues)")
    lines.append("        {")
    lines.append("            var serialized = value.ToString();")
    lines.append("            Assert.NotNull(serialized);")
    lines.append(f"            var parsed = Enum.Parse<{enum_info.name}>(serialized);")
    lines.append("            Assert.Equal(value, parsed);")
    lines.append("        }")
    lines.append("    }")
    lines.append("")

    lines.append("    #endregion")
    lines.append("")

    return lines


def generate_python_enum_tests(enums: List[EnumInfo], output_file: str) -> str:
    """
    Generate Python test code for enum value validation.

    Args:
        enums: List of EnumInfo objects
        output_file: Path to output test file

    Returns:
        Generated Python test code
    """
    lines = []
    lines.append('"""')
    lines.append("Auto-generated enum value tests.")
    lines.append("Tests that all enum values serialize and deserialize correctly.")
    lines.append('"""')
    lines.append("")
    lines.append("import pytest")
    lines.append("from enum import Enum")
    lines.append("from microsoft.agents.xml.models.messages import (")
    for enum_info in enums:
        lines.append(f"    {enum_info.name},")
    lines.append(")")
    lines.append("")
    lines.append("")

    for enum_info in enums:
        lines.extend(_generate_enum_tests_python(enum_info))

    code = "\n".join(lines)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(code)

    return code


def _generate_enum_tests_python(enum_info: EnumInfo) -> List[str]:
    """Generate tests for a single enum (Python)."""
    lines = []
    lines.append(f"# {enum_info.name} Enum Tests")
    lines.append("")

    # Deduplicate values to avoid duplicate test functions
    seen_test_names = set()

    # Test each enum value
    for value in enum_info.values:
        test_name = f"test_{to_snake_case(enum_info.name)}_{to_snake_case(value)}_value"

        # Skip if we've already generated this test
        if test_name in seen_test_names:
            continue
        seen_test_names.add(test_name)

        lines.append(f"def {test_name}():")
        lines.append(f'    """Test {enum_info.name}.{value} value serialization."""')
        lines.append(f"    # Arrange: Get enum value")
        lines.append(f"    enum_value = {enum_info.name}.{to_pascal_case(value).upper()}")
        lines.append("")
        lines.append("    # Act: Serialize to string")
        lines.append(f"    serialized = enum_value.value")
        lines.append("")
        lines.append("    # Assert: Value serializes correctly")
        lines.append(f"    assert serialized is not None")
        lines.append(f"    assert len(serialized) > 0")
        lines.append("")
        lines.append("    # Act: Parse back")
        lines.append(f"    parsed = {enum_info.name}(serialized)")
        lines.append("")
        lines.append("    # Assert: Round-trip successful")
        lines.append(f"    assert parsed == enum_value")
        lines.append("")
        lines.append("")

    # Test all enum values are valid
    test_name = f"test_{to_snake_case(enum_info.name)}_all_values_are_valid"
    lines.append(f"def {test_name}():")
    lines.append(f'    """Test all {enum_info.name} values are valid."""')
    lines.append(f"    # Arrange: Get all enum values")
    lines.append(f"    all_values = list({enum_info.name})")
    lines.append("")
    lines.append("    # Assert: Each value can be serialized and deserialized")
    lines.append("    for value in all_values:")
    lines.append("        serialized = value.value")
    lines.append("        assert serialized is not None")
    lines.append(f"        parsed = {enum_info.name}(serialized)")
    lines.append("        assert parsed == value")
    lines.append("")
    lines.append("")

    return lines
