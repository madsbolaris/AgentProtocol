#!/usr/bin/env python3
"""
Auto-generate serialization tests from TypeSpec schema.

This script:
1. Parses TypeSpec schema to extract content types
2. Generates XML test files (minimal variant)
3. Generates C# xUnit test code
4. Generates Python pytest test code
5. Copies test data to Python test directory
6. Generates Phase 1 property validation tests (--phase1)
7. Generates Phase 1 enum value tests (--phase1)

Usage:
    # Generate missing tests (19-26)
    ./generate-tests.py

    # Regenerate all tests
    ./generate-tests.py --all

    # Generate Phase 1 property and enum tests
    ./generate-tests.py --phase1-only

    # Generate EchoM365 compliance tests
    ./generate-tests.py --compliance-only

    # Generate protocol validation tests
    ./generate-tests.py --validation-only

    # Check if generated tests match committed files (CI mode)
    ./generate-tests.py --check

    # Custom TypeSpec file
    ./generate-tests.py --typespec path/to/messages.tsp
"""

import argparse
import sys
import shutil
from pathlib import Path

# Add test_gen to path
sys.path.insert(0, str(Path(__file__).parent))

from test_gen import (
    parse_typespec,
    get_content_types,
    XmlTestGenerator,
    generate_csharp_tests,
    generate_python_tests,
    generate_echom365_compliance_tests,
    generate_python_echom365_compliance_tests,
    generate_run_execution_tests,
    generate_typescript_echom365_compliance_tests,
    generate_typescript_run_execution_tests,
    generate_csharp_property_tests,
    generate_python_property_tests,
    extract_enums_from_typespec,
    generate_csharp_enum_tests,
    generate_python_enum_tests,
    generate_typescript_roundtrip_tests,
    generate_typescript_property_tests,
    generate_typescript_enum_tests,
    generate_python_validation_tests,
    to_kebab_case,
)


# Content types that are currently missing tests (need to generate)
MISSING_CONTENT_TYPES = [
    "HostedFileContent",
    "HostedVectorStoreContent",
    "TypingIndicatorContent",
    "MessageReactionContent",
    "MessageDeleteContent",
    "MessageUpdateContent",
    "RefusalContent",
    "ContentFilterResultContent",
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate serialization tests from TypeSpec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--typespec",
        type=str,
        default="specs/typespec/messages.tsp",
        help="Path to TypeSpec file (default: specs/typespec/messages.tsp)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="test-data",
        help="Output directory for shared test data (default: test-data)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Regenerate ALL tests (not just missing ones)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if generated tests match committed files (CI mode)"
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=19,
        help="Starting test number (default: 19)"
    )
    parser.add_argument(
        "--compliance",
        action="store_true",
        help="Generate EchoM365 compliance tests"
    )
    parser.add_argument(
        "--compliance-only",
        action="store_true",
        help="Generate ONLY compliance tests (skip serialization tests)"
    )
    parser.add_argument(
        "--phase1",
        action="store_true",
        help="Generate Phase 1 property validation and enum tests"
    )
    parser.add_argument(
        "--phase1-only",
        action="store_true",
        help="Generate ONLY Phase 1 tests (skip serialization tests)"
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Generate protocol validation tests"
    )
    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Generate ONLY validation tests (skip serialization tests)"
    )

    args = parser.parse_args()

    # Resolve paths
    project_root = Path(__file__).parent.parent.parent
    typespec_file = project_root / args.typespec
    output_dir = project_root / args.output_dir

    print("=" * 70)
    print("🧪 Agent Framework Test Generator")
    print("=" * 70)
    print()

    # Verify TypeSpec file exists
    if not typespec_file.exists():
        print(f"❌ Error: TypeSpec file not found: {typespec_file}")
        sys.exit(1)

    # Parse TypeSpec
    print(f"📖 Parsing TypeSpec: {typespec_file.relative_to(project_root)}")
    try:
        models = parse_typespec(str(typespec_file))
        content_types = get_content_types(models)
    except Exception as e:
        print(f"❌ Error parsing TypeSpec: {e}")
        sys.exit(1)

    print(f"✅ Found {len(content_types)} content types")
    print()

    # Generate compliance tests if requested
    if args.compliance or args.compliance_only:
        print("=" * 70)
        print("🧪 Generating EchoM365 Compliance Tests")
        print("=" * 70)
        print()

        # Generate C# EchoM365 compliance tests
        # NOTE: Following new structure - compliance tests go in Protocol package
        compliance_test_file = project_root / "dotnet/tests/Microsoft.Agents.Protocol.Tests/Compliance/EchoM365ComplianceTests.cs"
        compliance_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            generate_echom365_compliance_tests(models, str(compliance_test_file))
            print(f"✅ Generated C# tests: {compliance_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating C# compliance tests: {e}")

        # Generate Python EchoM365 compliance tests
        # NOTE: Following new structure - compliance tests go in Protocol package
        python_compliance_test_file = project_root / "python/microsoft-agents-protocol/tests/compliance/test_echom365_compliance.py"
        python_compliance_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            generate_python_echom365_compliance_tests(models, str(python_compliance_test_file))
            print(f"✅ Generated Python tests: {python_compliance_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating Python compliance tests: {e}")

        # Generate TypeScript EchoM365 compliance tests
        # NOTE: Following new structure - compliance tests go in Protocol package
        typescript_compliance_test_file = project_root / "javascript/packages/agents-protocol/tests/compliance/echom365.test.ts"
        typescript_compliance_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            generate_typescript_echom365_compliance_tests(models, str(typescript_compliance_test_file))
            print(f"✅ Generated TypeScript tests: {typescript_compliance_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating TypeScript compliance tests: {e}")

        # Generate Run execution tests
        run_test_file = project_root / "dotnet/tests/Microsoft.Agents.Protocols.Tests/EchoM365.Compliance.Tests/RunExecutionComplianceTests.cs"
        try:
            generate_run_execution_tests(str(run_test_file))
            print(f"✅ Generated C# Run tests: {run_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating C# Run tests: {e}")

        # Generate TypeScript Run execution tests
        typescript_run_test_file = project_root / "javascript/packages/agents-protocol/tests/compliance/runExecution.test.ts"
        try:
            generate_typescript_run_execution_tests(str(typescript_run_test_file))
            print(f"✅ Generated TypeScript Run tests: {typescript_run_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating TypeScript Run tests: {e}")

        print()

        if args.compliance_only:
            print("=" * 70)
            print("✅ Compliance test generation complete!")
            print("=" * 70)
            print()
            print("Next steps:")
            print("  1. Review generated tests in dotnet/tests/Microsoft.Agents.Protocols.Tests/")
            print("  2. Create test project if needed: dotnet new xunit")
            print("  3. Run tests: cd dotnet/tests && dotnet test")
            print()
            return 0

    # Generate protocol validation tests if requested
    if args.validation or args.validation_only:
        print("=" * 70)
        print("🧪 Generating Protocol Validation Tests")
        print("=" * 70)
        print()

        # Generate Python validation tests
        python_validation_dir = project_root / "python/microsoft-agents-protocol/tests"
        try:
            print("🐍 Generating Python validation tests...")
            generated_files = generate_python_validation_tests(str(python_validation_dir))
            for file in generated_files:
                rel_path = Path(file).relative_to(project_root)
                print(f"  ✓ {rel_path}")
            print(f"\n  Generated {len(generated_files)} Python validation test files")
        except Exception as e:
            print(f"  ❌ Error generating Python validation tests: {e}")
            import traceback
            traceback.print_exc()

        print()

        if args.validation_only:
            print("=" * 70)
            print("✅ Validation test generation complete!")
            print("=" * 70)
            print()
            print("Generated validation tests for:")
            print("  ✓ Python: python/microsoft-agents-protocol/tests/validation/")
            print()
            print("Test categories:")
            print("  ✓ Core validation (ValidationResult)")
            print("  ✓ Content validation (FunctionCall, Text, Image, Error, FunctionResult)")
            print("  ✓ Message validation (User, Tool)")
            print("  ✓ Thread validation")
            print()
            print("Next steps:")
            print("  1. Run Python tests: cd python/microsoft-agents-protocol && pytest")
            print("  2. Review test coverage and add more validators as needed")
            print("  3. Port validation tests to TypeScript (future work)")
            print()
            return 0

    # Generate Phase 1 property validation tests if requested
    if args.phase1 or args.phase1_only:
        print("=" * 70)
        print("🧪 Generating Phase 1 Property Validation Tests")
        print("=" * 70)
        print()

        # Generate C# property validation tests
        property_test_file = project_root / "dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedPropertyValidationTests.cs"
        property_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("🔷 Generating C# property validation tests...")
            generate_csharp_property_tests(models, str(property_test_file))
            print(f"  ✓ {property_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating C# property tests: {e}")
            import traceback
            traceback.print_exc()

        # Generate Python property validation tests
        python_property_test_file = project_root / "python/microsoft-agents-xml/tests/test_generated_property_validation.py"
        python_property_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("🐍 Generating Python property validation tests...")
            generate_python_property_tests(models, str(python_property_test_file))
            print(f"  ✓ {python_property_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating Python property tests: {e}")
            import traceback
            traceback.print_exc()

        # Generate TypeScript property validation tests
        typescript_property_test_file = project_root / "javascript/packages/agents-xml/tests/generatedPropertyValidation.test.ts"
        typescript_property_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("📘 Generating TypeScript property validation tests...")
            generate_typescript_property_tests(models, str(typescript_property_test_file))
            print(f"  ✓ {typescript_property_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating TypeScript property tests: {e}")
            import traceback
            traceback.print_exc()

        print()

        # Extract and generate enum tests
        print("=" * 70)
        print("🧪 Generating Phase 1 Enum Value Tests")
        print("=" * 70)
        print()

        # Read TypeSpec content for enum extraction
        typespec_content = typespec_file.read_text()
        enums = extract_enums_from_typespec(typespec_content)
        print(f"✅ Found {len(enums)} enums")
        print()

        # Generate C# enum tests
        enum_test_file = project_root / "dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedEnumValueTests.cs"
        enum_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("🔷 Generating C# enum value tests...")
            generate_csharp_enum_tests(enums, str(enum_test_file))
            print(f"  ✓ {enum_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating C# enum tests: {e}")
            import traceback
            traceback.print_exc()

        # Generate Python enum tests
        python_enum_test_file = project_root / "python/microsoft-agents-xml/tests/test_generated_enum_values.py"
        python_enum_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("🐍 Generating Python enum value tests...")
            generate_python_enum_tests(enums, str(python_enum_test_file))
            print(f"  ✓ {python_enum_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating Python enum tests: {e}")
            import traceback
            traceback.print_exc()

        # Generate TypeScript enum tests
        typescript_enum_test_file = project_root / "javascript/packages/agents-xml/tests/generatedEnumValues.test.ts"
        typescript_enum_test_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            print("📘 Generating TypeScript enum value tests...")
            generate_typescript_enum_tests(enums, str(typescript_enum_test_file))
            print(f"  ✓ {typescript_enum_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"  ❌ Error generating TypeScript enum tests: {e}")
            import traceback
            traceback.print_exc()

        print()

        if args.phase1_only:
            print("=" * 70)
            print("✅ Phase 1 test generation complete!")
            print("=" * 70)
            print()
            print("Generated tests for all languages:")
            print()
            print("Property Validation Tests:")
            print(f"  🔷 C#: {property_test_file.relative_to(project_root)}")
            print(f"  🐍 Python: {python_property_test_file.relative_to(project_root)}")
            print(f"  📘 TypeScript: {typescript_property_test_file.relative_to(project_root)}")
            print()
            print("Enum Value Tests:")
            print(f"  🔷 C#: {enum_test_file.relative_to(project_root)}")
            print(f"  🐍 Python: {python_enum_test_file.relative_to(project_root)}")
            print(f"  📘 TypeScript: {typescript_enum_test_file.relative_to(project_root)}")
            print()
            print("Test coverage includes:")
            print("  ✓ Individual property serialization/deserialization")
            print("  ✓ All enum values")
            print("  ✓ Required vs optional fields")
            print("  ✓ Discriminator values")
            print()
            print("Next steps:")
            print("  1. Run C# tests: cd dotnet && dotnet test")
            print("  2. Run Python tests: cd python/microsoft-agents-xml && pytest")
            print("  3. Run TypeScript tests: cd javascript/packages/agents-xml && npm test")
            print("  4. Review test coverage and failures")
            print("  5. Commit changes")
            print()
            return 0

    # Filter to missing types or all types (serialization tests)
    if args.all:
        types_to_generate = content_types
        print("🔄 Regenerating ALL content type tests...")
    else:
        # Filter to only missing types
        types_to_generate = [
            m for m in content_types
            if m.name in MISSING_CONTENT_TYPES
        ]
        print(f"📝 Generating {len(types_to_generate)} missing tests:")
        for model in types_to_generate:
            print(f"   - {model.name}")

    if not types_to_generate:
        print("✅ No tests to generate (all content types already have tests)")
        return

    print()

    # Generate XML test files
    print("📝 Generating XML test files...")
    input_dir = output_dir / "input"
    output_test_dir = output_dir / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_test_dir.mkdir(parents=True, exist_ok=True)

    xml_gen = XmlTestGenerator(types_to_generate)
    generated_files = []

    for i, model in enumerate(types_to_generate, start=args.start_number):
        filename = f"{i:02d}-{to_kebab_case(model.name)}.xml"

        # Generate minimal variant (input)
        try:
            xml_content = xml_gen.generate_test_file(model.name, variant="minimal")

            input_file = input_dir / filename
            input_file.write_text(xml_content)

            # For now, output = input (will be updated after first test run)
            output_file = output_test_dir / filename
            output_file.write_text(xml_content)

            generated_files.append(filename)
            print(f"  ✓ {filename}")
        except Exception as e:
            print(f"  ❌ {filename}: {e}")
            continue

    print()

    # Generate C# test code
    print("🔷 Generating C# round-trip tests...")
    csharp_test_file = project_root / "dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedRoundTripTests.cs"
    try:
        generate_csharp_tests(
            types_to_generate,
            str(csharp_test_file),
            start_number=args.start_number
        )
        print(f"  ✓ {csharp_test_file.relative_to(project_root)}")
    except Exception as e:
        print(f"  ❌ Error generating C# tests: {e}")

    print()

    # Generate Python test code
    print("🐍 Generating Python round-trip tests...")
    python_test_file = project_root / "python/microsoft-agents-xml/tests/test_generated_roundtrip.py"
    python_test_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        generate_python_tests(
            types_to_generate,
            str(python_test_file),
            start_number=args.start_number
        )
        print(f"  ✓ {python_test_file.relative_to(project_root)}")
    except Exception as e:
        print(f"  ❌ Error generating Python tests: {e}")

    print()

    # Generate TypeScript test code
    print("📘 Generating TypeScript round-trip tests...")
    typescript_test_file = project_root / "javascript/packages/agents-xml/tests/generatedRoundTrip.test.ts"
    typescript_test_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        generate_typescript_roundtrip_tests(
            types_to_generate,
            str(typescript_test_file),
            start_number=args.start_number
        )
        print(f"  ✓ {typescript_test_file.relative_to(project_root)}")
    except Exception as e:
        print(f"  ❌ Error generating TypeScript tests: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)
    print("✅ Round-trip test generation complete!")
    print("=" * 70)
    print()
    print(f"Generated {len(generated_files)} XML test files in test-data/input/")
    for file in generated_files:
        print(f"  - {file}")
    print()
    print("Generated test code for all languages:")
    print(f"  🔷 C#: {csharp_test_file.relative_to(project_root)}")
    print(f"  🐍 Python: {python_test_file.relative_to(project_root)}")
    print(f"  📘 TypeScript: {typescript_test_file.relative_to(project_root)}")
    print()
    print("Next steps:")
    print("  1. Review shared test data in test-data/")
    print("  2. Run C# tests: cd dotnet && dotnet test")
    print("  3. Run Python tests: cd python/microsoft-agents-xml && pytest")
    print("  4. Run TypeScript tests: cd javascript/packages/agents-xml && npm test")
    print("  5. Commit changes")
    print()

    # Check mode
    if args.check:
        print("🔍 Checking if generated tests match committed files...")
        # TODO: Implement check logic
        print("  ⚠️  Check mode not yet implemented")

    return 0


if __name__ == "__main__":
    sys.exit(main())
