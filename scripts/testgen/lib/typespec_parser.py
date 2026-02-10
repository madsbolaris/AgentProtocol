"""
TypeSpec Parser

Parses TypeSpec schema files to extract model definitions, properties, and decorators.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path


@dataclass
class Property:
    """Represents a property in a TypeSpec model"""
    name: str
    type: str
    optional: bool
    decorators: List[str] = field(default_factory=list)
    decorator_args: dict = field(default_factory=dict)


@dataclass
class Model:
    """Represents a TypeSpec model definition"""
    name: str
    kind: Optional[str]  # Discriminator value
    extends: Optional[str]
    properties: List[Property]
    xml_root: Optional[str]
    xml_ignore: bool = False


def parse_typespec(file_path: str) -> List[Model]:
    """
    Parse TypeSpec file and extract all model definitions.

    Args:
        file_path: Path to TypeSpec file

    Returns:
        List of Model objects
    """
    content = Path(file_path).read_text()

    # Extract all models
    models = []

    # Pattern 1: Models with extends and xml_root
    # Matches: @xmlRoot("name") model ModelName extends Base { ... }
    model_with_base_pattern = r'(?:@xmlRoot\("([^"]+)"\)\s*)?model\s+(\w+)\s+extends\s+(\w+)\s*\{([^}]+)\}'

    for match in re.finditer(model_with_base_pattern, content, re.DOTALL):
        xml_root, name, base, body = match.groups()

        # Parse properties
        properties = parse_properties(body)

        # Extract kind (discriminator)
        kind = extract_kind(body)

        models.append(Model(
            name=name,
            kind=kind,
            extends=base,
            properties=properties,
            xml_root=xml_root if xml_root else None,
            xml_ignore=False
        ))

    # Pattern 2: Standalone models without extends (like ChatMessage)
    # Matches: model ChatMessage { ... }
    standalone_model_pattern = r'model\s+(\w+)\s*\{([^}]+)\}'

    for match in re.finditer(standalone_model_pattern, content, re.DOTALL):
        name, body = match.groups()

        # Skip if already found (from pattern 1)
        if any(m.name == name for m in models):
            continue

        # Parse properties
        properties = parse_properties(body)

        models.append(Model(
            name=name,
            kind=None,
            extends=None,
            properties=properties,
            xml_root=None,
            xml_ignore=False
        ))

    return models


def parse_properties(body: str) -> List[Property]:
    """
    Parse property definitions from model body.

    Args:
        body: Model body text

    Returns:
        List of Property objects
    """
    properties = []

    # Split by lines and process
    lines = body.split('\n')
    current_decorators = []

    for line in lines:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('//') or line.startswith('/**') or line.startswith('*'):
            continue

        # Check if line is a decorator
        if line.startswith('@'):
            decorator_match = re.match(r'@(\w+)(?:\(([^)]*)\))?', line)
            if decorator_match:
                decorator_name = decorator_match.group(1)
                decorator_arg = decorator_match.group(2)

                # Store decorator with argument
                if decorator_arg:
                    # Remove quotes from argument
                    decorator_arg = decorator_arg.strip('"').strip("'")
                    current_decorators.append((f"@{decorator_name}", decorator_arg))
                else:
                    current_decorators.append((f"@{decorator_name}", None))
            continue

        # Parse property: name: type or name?: type
        prop_match = re.search(r'(\w+)(\?)?:\s*(.+?)(?:;|=)', line)
        if prop_match:
            name, optional, prop_type = prop_match.groups()

            # Clean up type
            prop_type = prop_type.strip()

            # Build decorator dict
            decorator_list = [d[0] for d in current_decorators]
            decorator_args = {d[0]: d[1] for d in current_decorators if d[1]}

            properties.append(Property(
                name=name,
                type=prop_type,
                optional=bool(optional),
                decorators=decorator_list,
                decorator_args=decorator_args
            ))

            # Reset decorators for next property
            current_decorators = []

    return properties


def extract_kind(body: str) -> Optional[str]:
    """
    Extract discriminator value (kind) from model body.

    Args:
        body: Model body text

    Returns:
        Kind value or None
    """
    match = re.search(r'kind:\s*"([^"]+)"', body)
    return match.group(1) if match else None


def get_content_types(models: List[Model]) -> List[Model]:
    """
    Filter models to only content types (extending AIContentBase).

    Args:
        models: List of all models

    Returns:
        List of content type models
    """
    return [m for m in models if m.extends == "AIContentBase"]


if __name__ == "__main__":
    # Test the parser
    import sys

    if len(sys.argv) < 2:
        print("Usage: python typespec_parser.py <typespec-file>")
        sys.exit(1)

    models = parse_typespec(sys.argv[1])
    content_types = get_content_types(models)

    print(f"Found {len(models)} models, {len(content_types)} content types:")
    for model in content_types:
        print(f"  - {model.name} (kind={model.kind}, xml_root={model.xml_root})")
        print(f"    Properties: {len(model.properties)}")
