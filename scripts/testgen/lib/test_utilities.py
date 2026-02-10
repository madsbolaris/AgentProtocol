"""
Test Generation Utilities

Shared helper functions for test code generation across all test generators.
Consolidates common logic for type checking and test value generation.
"""

from .typespec_parser import Property


def is_complex_type(type_name: str) -> bool:
    """
    Check if a type is complex (not a simple primitive).

    Complex types include objects, arrays, dates, etc. that can't be
    easily tested as simple string values.

    Args:
        type_name: TypeSpec type name (e.g., "string", "int32", "MyModel")

    Returns:
        True if the type is complex, False if it's a simple primitive

    Examples:
        >>> is_complex_type("string")
        False
        >>> is_complex_type("MyCustomModel")
        True
    """
    simple_types = [
        "string", "int32", "int64", "integer",
        "float32", "float64", "float",
        "boolean", "bytes"
    ]
    return type_name not in simple_types


def is_value_type(type_name: str) -> bool:
    """
    Check if a C# type is a value type (struct).

    Value types in C# can never be null, so Assert.NotNull should be
    skipped for these types to avoid xUnit warnings.

    Args:
        type_name: C# or TypeSpec type name

    Returns:
        True if the type is a C# value type

    Note:
        This is primarily used for C# test generation to avoid
        Assert.NotNull on value types like int, bool, DateTime, etc.

    Examples:
        >>> is_value_type("int")
        True
        >>> is_value_type("string")
        False
    """
    value_types = [
        "int", "long", "float", "double", "bool", "DateTime",
        "int32", "int64", "float32", "float64", "boolean"
    ]
    return type_name in value_types


def get_test_value_for_property(prop: Property) -> str:
    """
    Get an appropriate test value for a property based on its type and name.

    Generates context-aware test values that make sense for the property:
    - ID fields: "test_id_123"
    - URL/URI fields: "https://example.com"
    - Email fields: "test@example.com"
    - Numbers: "42" or "3.14"
    - Booleans: "true"
    - Default strings: "test_value"

    Args:
        prop: Property object from TypeSpec parser

    Returns:
        String representation of an appropriate test value

    Examples:
        >>> prop = Property(name="userId", type="string", ...)
        >>> get_test_value_for_property(prop)
        'test_id_123'

        >>> prop = Property(name="count", type="int32", ...)
        >>> get_test_value_for_property(prop)
        '42'
    """
    if prop.type == "string":
        if "id" in prop.name.lower():
            return "test_id_123"
        elif "url" in prop.name.lower() or "uri" in prop.name.lower():
            return "https://example.com"
        elif "email" in prop.name.lower():
            return "test@example.com"
        elif "name" in prop.name.lower():
            return "Test Name"
        return "test_value"
    elif prop.type in ["int32", "integer", "int64"]:
        return "42"
    elif prop.type in ["float32", "float64", "float"]:
        return "3.14"
    elif prop.type == "boolean":
        return "true"
    return "test_value"


def is_testable_property(prop: Property) -> bool:
    """
    Check if a property should be included in generated property tests.

    Properties are excluded from testing if they:
    - Are discriminator fields (name == "kind")
    - Have @xmlIgnore decorator
    - Are arrays/lists
    - Are complex types (not primitives)
    - Are DateTime types (for now, until datetime handling is improved)

    Args:
        prop: Property object from TypeSpec parser

    Returns:
        True if the property should be tested, False otherwise

    Examples:
        >>> prop = Property(name="text", type="string", ...)
        >>> is_testable_property(prop)
        True

        >>> prop = Property(name="kind", type="string", ...)
        >>> is_testable_property(prop)
        False
    """
    if prop.name == "kind":
        return False
    if "@xmlIgnore" in prop.decorators:
        return False
    if prop.type.startswith("List<") or prop.type.startswith("Array<"):
        return False
    if prop.type in ["utcDateTime", "DateTime"]:
        return False
    if is_complex_type(prop.type):
        return False
    return True


if __name__ == "__main__":
    # Run doctests
    import doctest
    doctest.testmod()
