#!/usr/bin/env python3
"""
Auto-generate tests from TypeSpec schema.

This script parses TypeSpec and automatically generates comprehensive tests:
- Property validation tests (all properties of all content types)
- Enum value tests (all enum values)
- Serialization round-trip tests (XML/JSON)
- EchoM365 compliance tests (protocol conformance)
- Protocol validation tests (validation framework)

Usage:
    # Generate ALL test types (default)
    python3 generate_tests.py

    # Generate only specific test types
    python3 generate_tests.py --property --enum
    python3 generate_tests.py --compliance --validation

    # Regenerate all tests (force overwrite)
    python3 generate_tests.py --all

    # Check if generated tests match committed files (CI mode)
    python3 generate_tests.py --check

    # Custom TypeSpec file
    python3 generate_tests.py --typespec path/to/messages.tsp

Examples:
    # Typical usage: generate everything
    python3 scripts/testgen/generate_tests.py

    # Quick iteration: just property/enum tests
    python3 scripts/testgen/generate_tests.py --property --enum

    # CI validation: ensure generated code is up to date
    python3 scripts/testgen/generate_tests.py --check
"""

import argparse
import sys
import shutil
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib import (
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
        default="typespec/messages.tsp",
        help="Path to TypeSpec file (default: typespec/messages.tsp)"
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
    # Test type selection (if none specified, all are generated)
    parser.add_argument(
        "--property",
        action="store_true",
        help="Generate property validation tests"
    )
    parser.add_argument(
        "--enum",
        action="store_true",
        help="Generate enum value tests"
    )
    parser.add_argument(
        "--roundtrip",
        action="store_true",
        help="Generate serialization round-trip tests"
    )
    parser.add_argument(
        "--compliance",
        action="store_true",
        help="Generate EchoM365 compliance tests"
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Generate protocol validation tests"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )

    args = parser.parse_args()

    # Determine which test types to generate
    # If no specific test type flags given, generate ALL types
    no_flags_specified = not any([
        args.property, args.enum, args.roundtrip,
        args.compliance, args.validation
    ])

    # Set what to generate (default to all if no flags specified)
    should_generate_property = args.property or no_flags_specified
    should_generate_enum = args.enum or no_flags_specified
    should_generate_roundtrip = args.roundtrip or no_flags_specified
    should_generate_compliance = args.compliance or no_flags_specified
    should_generate_validation = args.validation or no_flags_specified

    # Resolve paths
    project_root = Path(__file__).parent.parent.parent
    typespec_file = project_root / args.typespec
    output_dir = project_root / args.output_dir

    print("=" * 70)
    print("🧪 Agent Protocol Test Generator")
    print("=" * 70)
    print()

    # Show what will be generated
    if no_flags_specified:
        print("📋 Generating ALL test types")
    else:
        print("📋 Generating:")
        if should_generate_property: print("   ✓ Property validation tests")
        if should_generate_enum: print("   ✓ Enum value tests")
        if should_generate_roundtrip: print("   ✓ Round-trip serialization tests")
        if should_generate_compliance: print("   ✓ EchoM365 compliance tests")
        if should_generate_validation: print("   ✓ Protocol validation tests")
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

    # Dry-run mode: show what would be generated without writing files
    if args.dry_run:
        print("=" * 70)
        print("🔍 DRY RUN - Preview of files that would be generated")
        print("=" * 70)
        print()

        files_to_generate = []

        # Compliance tests
        if should_generate_compliance:
            files_to_generate.append("dotnet/tests/Microsoft.Agents.Protocol.Tests/Compliance/EchoM365ComplianceTests.cs")
            files_to_generate.append("python/microsoft-agents-protocol/tests/compliance/test_echom365_compliance.py")
            files_to_generate.append("typescript/packages/agents-protocol/tests/compliance/echom365.test.ts")
            files_to_generate.append("dotnet/tests/Microsoft.Agents.Protocols.Tests/EchoM365.Compliance.Tests/RunExecutionComplianceTests.cs")
            files_to_generate.append("typescript/packages/agents-protocol/tests/compliance/runExecution.test.ts")

        # Validation tests
        if should_generate_validation:
            files_to_generate.append("python/microsoft-agents-protocol/tests/test_*_validation.py (multiple files)")

        # Property tests
        if should_generate_property:
            files_to_generate.append("dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedPropertyValidationTests.cs")
            files_to_generate.append("python/microsoft-agents-protocol-xml/tests/test_generated_property_validation.py")
            files_to_generate.append("typescript/packages/agents-xml/tests/generatedPropertyValidation.test.ts")

        # Enum tests
        if should_generate_enum:
            files_to_generate.append("dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedEnumValueTests.cs")
            files_to_generate.append("python/microsoft-agents-protocol-xml/tests/test_generated_enum_values.py")
            files_to_generate.append("typescript/packages/agents-xml/tests/generatedEnumValues.test.ts")

        # Round-trip tests
        if should_generate_roundtrip:
            if args.all:
                types_count = len(content_types)
            else:
                types_count = len([m for m in content_types if m.name in MISSING_CONTENT_TYPES])

            if types_count > 0:
                files_to_generate.append(f"test-data/input/*.xml ({types_count} XML files)")
                files_to_generate.append(f"test-data/output/*.xml ({types_count} XML files)")
                files_to_generate.append("dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/GeneratedRoundTripTests.cs")
                files_to_generate.append("python/microsoft-agents-protocol-xml/tests/test_generated_roundtrip.py")
                files_to_generate.append("typescript/packages/agents-xml/tests/generatedRoundTrip.test.ts")

        print(f"Would generate {len(files_to_generate)} files:")
        for file in files_to_generate:
            print(f"  - {file}")
        print()
        print("🔍 Dry run complete - no files were written")
        print("   Run without --dry-run to generate files")
        print()
        return 0

    # Generate compliance tests if requested
    if should_generate_compliance:
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
        typescript_compliance_test_file = project_root / "typescript/packages/agents-protocol/tests/compliance/echom365.test.ts"
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
        typescript_run_test_file = project_root / "typescript/packages/agents-protocol/tests/compliance/runExecution.test.ts"
        try:
            generate_typescript_run_execution_tests(str(typescript_run_test_file))
            print(f"✅ Generated TypeScript Run tests: {typescript_run_test_file.relative_to(project_root)}")
        except Exception as e:
            print(f"❌ Error generating TypeScript Run tests: {e}")

        print()

    # Generate protocol validation tests if requested
    if should_generate_validation:
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

    # Generate property validation tests if requested
    if should_generate_property:
        print("=" * 70)
        print("🧪 Generating Property Validation Tests")
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
        python_property_test_file = project_root / "python/microsoft-agents-protocol-xml/tests/test_generated_property_validation.py"
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
        typescript_property_test_file = project_root / "typescript/packages/agents-xml/tests/generatedPropertyValidation.test.ts"
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

    # Generate enum tests if requested
    if should_generate_enum:
        print("=" * 70)
        print("🧪 Generating Enum Value Tests")
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
        python_enum_test_file = project_root / "python/microsoft-agents-protocol-xml/tests/test_generated_enum_values.py"
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
        typescript_enum_test_file = project_root / "typescript/packages/agents-xml/tests/generatedEnumValues.test.ts"
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

    # Generate round-trip serialization tests if requested
    if should_generate_roundtrip:
        print("=" * 70)
        print("🧪 Generating Round-Trip Serialization Tests")
        print("=" * 70)
        print()

        # Determine which content types to generate tests for
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
        else:
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
            python_test_file = project_root / "python/microsoft-agents-protocol-xml/tests/test_generated_roundtrip.py"
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
            typescript_test_file = project_root / "typescript/packages/agents-xml/tests/generatedRoundTrip.test.ts"
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
            print("  3. Run Python tests: cd python/microsoft-agents-protocol-xml && pytest")
            print("  4. Run TypeScript tests: cd typescript/packages/agents-xml && npm test")
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
