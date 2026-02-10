"""
Test Generation Package for Agent Framework

Auto-generates serialization tests and compliance tests from TypeSpec schema definitions.
"""

from .typespec_parser import parse_typespec, Model, Property, get_content_types
from .xml_generator import XmlTestGenerator
from .test_code_generator import generate_csharp_tests, generate_python_tests
from .compliance_test_generator import (
    generate_echom365_compliance_tests,
    generate_python_echom365_compliance_tests,
    generate_run_execution_tests,
    generate_typescript_echom365_compliance_tests,
    generate_typescript_run_execution_tests
)
from .code_utils import to_kebab_case, to_pascal_case, to_camel_case, to_snake_case
from .property_test_generator import PropertyTestGenerator
from .property_test_code_generator import (
    generate_csharp_property_tests,
    generate_python_property_tests
)
from .enum_test_generator import (
    extract_enums_from_typespec,
    generate_csharp_enum_tests,
    generate_python_enum_tests,
    EnumInfo
)
from .typescript_test_generator import (
    generate_typescript_roundtrip_tests,
    generate_typescript_property_tests,
    generate_typescript_enum_tests
)
from .test_utilities import (
    is_complex_type,
    is_value_type,
    get_test_value_for_property,
    is_testable_property
)
from .validation_test_generator import (
    ValidationTestGenerator,
    generate_python_validation_tests
)

__all__ = [
    'parse_typespec',
    'Model',
    'Property',
    'get_content_types',
    'to_kebab_case',
    'to_pascal_case',
    'to_camel_case',
    'to_snake_case',
    'XmlTestGenerator',
    'generate_csharp_tests',
    'generate_python_tests',
    'generate_echom365_compliance_tests',
    'generate_python_echom365_compliance_tests',
    'generate_run_execution_tests',
    'generate_typescript_echom365_compliance_tests',
    'generate_typescript_run_execution_tests',
    'PropertyTestGenerator',
    'generate_csharp_property_tests',
    'generate_python_property_tests',
    'extract_enums_from_typespec',
    'generate_csharp_enum_tests',
    'generate_python_enum_tests',
    'EnumInfo',
    'generate_typescript_roundtrip_tests',
    'generate_typescript_property_tests',
    'generate_typescript_enum_tests',
    'is_complex_type',
    'is_value_type',
    'get_test_value_for_property',
    'is_testable_property',
    'ValidationTestGenerator',
    'generate_python_validation_tests',
]
