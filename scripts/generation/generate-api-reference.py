#!/usr/bin/env python3
"""
Generate API reference documentation from TypeSpec files.

This script:
1. Parses TypeSpec files to extract routes, models, and enums
2. Generates markdown documentation for each endpoint
3. Preserves manual content sections (examples, best practices)
4. Uses template markers for merging auto-generated + manual content
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Example:
    """Documentation example."""
    title: str
    language: str  # http, json, typescript, etc.
    code: str


@dataclass
class StructuredDocs:
    """Structured documentation parsed from TypeSpec comments."""
    summary: str = ""  # Brief one-line description
    usage: str = ""  # @usage section
    examples: List[Example] = field(default_factory=list)  # @example blocks
    responses: Dict[str, str] = field(default_factory=dict)  # code -> description
    params: Dict[str, str] = field(default_factory=dict)  # param name -> description
    see_also: List[str] = field(default_factory=list)  # @see references
    raw_sections: Dict[str, str] = field(default_factory=dict)  # Free-form sections (PURPOSE, etc.)


@dataclass
class Parameter:
    """API parameter (path, query, header, body)."""
    name: str
    type: str
    location: str  # path, query, header, body
    required: bool
    description: str = ""


@dataclass
class Endpoint:
    """API endpoint definition."""
    method: str  # GET, POST, PUT, PATCH, DELETE
    path: str  # /agents/{agentId}
    operation_name: str  # getAgent
    summary: str = ""
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[str] = None  # Model name
    response_types: List[str] = field(default_factory=list)  # Model names
    decorators: List[str] = field(default_factory=list)
    doc_comment: str = ""
    structured_docs: Optional['StructuredDocs'] = None  # Parsed structured documentation


@dataclass
class Model:
    """TypeSpec model definition."""
    name: str
    description: str = ""
    properties: Dict[str, Tuple[str, str, bool]] = field(default_factory=dict)  # name -> (type, desc, required)
    extends: List[str] = field(default_factory=list)
    doc_comment: str = ""
    structured_docs: Optional['StructuredDocs'] = None  # Parsed structured documentation


@dataclass
class Enum:
    """TypeSpec enum definition."""
    name: str
    description: str = ""
    values: Dict[str, str] = field(default_factory=dict)  # value -> description


class TypeSpecParser:
    """Parse TypeSpec files to extract API definitions."""

    def __init__(self, typespec_dir: str):
        self.typespec_dir = Path(typespec_dir)
        self.endpoints: List[Endpoint] = []
        self.models: Dict[str, Model] = {}
        self.enums: Dict[str, Enum] = {}
        self.interfaces: Dict[str, str] = {}  # interface name -> base route

    def parse_all(self):
        """Parse all TypeSpec files."""
        print("📖 Parsing TypeSpec files...\n")

        # Parse routes first
        routes_file = self.typespec_dir / "routes.tsp"
        if routes_file.exists():
            self._parse_routes(routes_file)

        # Parse models from all files
        for tsp_file in self.typespec_dir.glob("*.tsp"):
            if tsp_file.name != "routes.tsp":
                self._parse_models_and_enums(tsp_file)

        print(f"✓ Parsed {len(self.endpoints)} endpoints")
        print(f"✓ Parsed {len(self.models)} models")
        print(f"✓ Parsed {len(self.enums)} enums\n")

    def _parse_routes(self, file_path: Path):
        """Parse routes.tsp to extract endpoint definitions."""
        content = file_path.read_text()
        lines = content.split('\n')

        current_interface = None
        current_base_route = None
        in_interface = False
        brace_depth = 0
        pending_decorators = []
        doc_comment = ""

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Track doc comments
            if stripped.startswith('/**') or stripped.startswith('*') or stripped.startswith('*/'):
                if stripped.startswith('/**'):
                    doc_comment = stripped
                elif doc_comment:
                    doc_comment += '\n' + stripped
                i += 1
                continue

            # Track @route decorator
            route_match = re.match(r'@route\("([^"]+)"\)', stripped)
            if route_match:
                current_base_route = route_match.group(1)
                i += 1
                continue

            # Track interface start
            interface_match = re.match(r'interface\s+(\w+)', stripped)
            if interface_match and current_base_route:
                current_interface = interface_match.group(1)
                self.interfaces[current_interface] = current_base_route
                in_interface = True
                brace_depth = stripped.count('{') - stripped.count('}')
                i += 1
                continue

            if not in_interface:
                doc_comment = ""
                i += 1
                continue

            # Track brace depth
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth <= 0:
                in_interface = False
                current_interface = None
                current_base_route = None
                pending_decorators = []
                doc_comment = ""
                i += 1
                continue

            # Collect decorators
            if stripped.startswith('@'):
                pending_decorators.append(stripped)
                i += 1
                continue

            # Check if this looks like an operation name (identifier followed by opening paren)
            # May be on this line or next lines
            if re.match(r'^\w+\s*\(', stripped) or (re.match(r'^\w+\s*$', stripped) and i + 1 < len(lines) and '(' in lines[i + 1]):
                # Collect full operation signature (may span multiple lines until semicolon)
                op_lines = []
                j = i
                while j < len(lines) and ';' not in lines[j]:
                    op_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    op_lines.append(lines[j])  # Include line with semicolon

                full_operation = '\n'.join(op_lines)

                # Try to parse operation
                endpoint = self._parse_operation(
                    full_operation,
                    pending_decorators,
                    current_base_route,
                    doc_comment,
                    lines,
                    i
                )
                if endpoint:
                    self.endpoints.append(endpoint)

                # Clear for next operation
                pending_decorators = []
                doc_comment = ""

                # Skip past the operation
                i = j + 1
                continue

            i += 1

    def _parse_operation(
        self,
        operation_text: str,
        decorators: List[str],
        base_route: str,
        doc_comment: str,
        all_lines: List[str],
        line_num: int
    ) -> Optional[Endpoint]:
        """Parse an operation signature to extract endpoint details."""
        # Flatten multi-line operation to single line for easier parsing
        flat_operation = ' '.join(operation_text.split('\n')).strip()

        # Extract HTTP method from decorators
        method = None
        segment = None

        for decorator in decorators:
            for http_method in ['get', 'post', 'put', 'patch', 'delete']:
                if decorator.startswith(f'@{http_method}'):
                    method = http_method.upper()
                    break

            segment_match = re.match(r'@segment\("([^"]+)"\)', decorator)
            if segment_match:
                segment = segment_match.group(1)

        if not method:
            return None

        # Extract operation name and parameters
        # Pattern: operationName(params): returnType;
        op_match = re.match(r'(\w+)\s*\((.*?)\)\s*:\s*(.+?);', flat_operation, re.DOTALL)
        if not op_match:
            return None

        operation_name = op_match.group(1)
        params_str = op_match.group(2)
        return_type_str = op_match.group(3).strip()

        # Build full path
        if segment:
            full_path = f"{base_route}/{segment}"
        else:
            # Check for @path parameters
            path_params = re.findall(r'@path\s+(\w+):', params_str)
            if path_params:
                # Filter out parameters already in base route
                new_params = [p for p in path_params if f'{{{p}}}' not in base_route]
                if new_params:
                    param_segments = '/'.join(f'{{{param}}}' for param in new_params)
                    full_path = f"{base_route}/{param_segments}"
                else:
                    full_path = base_route
            else:
                full_path = base_route

        # Parse parameters
        parameters = self._parse_parameters(params_str)

        # Parse return type (already extracted)
        response_types = []
        if return_type_str:
            # Handle union types: Type1 | Type2
            # Also handle array types: Type[] and comments like "// SSE stream"
            return_type_clean = re.sub(r'//.*$', '', return_type_str).strip()
            response_types = [t.strip() for t in return_type_clean.split('|')]

        # Parse doc comment for description (legacy format)
        description = self._parse_doc_comment(doc_comment)

        # Parse structured documentation
        structured_docs = self._parse_structured_doc_comment(doc_comment)

        endpoint = Endpoint(
            method=method,
            path=full_path,
            operation_name=operation_name,
            description=description,
            parameters=parameters,
            response_types=response_types,
            decorators=decorators,
            doc_comment=doc_comment,
            structured_docs=structured_docs
        )

        return endpoint

    def _parse_parameters(self, params_str: str) -> List[Parameter]:
        """Parse operation parameters."""
        parameters = []

        # Split by comma, but be careful with nested types
        param_parts = []
        current_param = ""
        depth = 0

        for char in params_str:
            if char in '<{[':
                depth += 1
            elif char in '>}]':
                depth -= 1
            elif char == ',' and depth == 0:
                param_parts.append(current_param.strip())
                current_param = ""
                continue
            current_param += char

        if current_param.strip():
            param_parts.append(current_param.strip())

        for param in param_parts:
            if not param:
                continue

            # Parse: @decorator paramName: Type, or @decorator paramName?: Type
            decorators = []
            while param.startswith('@'):
                decorator_match = re.match(r'@(\w+)(?:\([^)]*\))?\s+(.*)', param)
                if decorator_match:
                    decorators.append(decorator_match.group(1))
                    param = decorator_match.group(2)
                else:
                    break

            # Parse: paramName: Type or paramName?: Type
            param_match = re.match(r'(\w+)(\?)?:\s*(.+)', param)
            if not param_match:
                continue

            param_name = param_match.group(1)
            optional = param_match.group(2) == '?'
            param_type = param_match.group(3).strip()

            # Determine location from decorators
            location = 'query'  # default
            if 'path' in decorators:
                location = 'path'
            elif 'header' in decorators:
                location = 'header'
            elif 'body' in decorators:
                location = 'body'

            parameters.append(Parameter(
                name=param_name,
                type=param_type,
                location=location,
                required=not optional
            ))

        return parameters

    def _parse_doc_comment(self, doc_comment: str) -> str:
        """Extract user-facing description from doc comment, filtering out TypeSpec metadata."""
        if not doc_comment:
            return ""

        # Metadata tags to filter out (developer-facing design notes)
        metadata_tags = [
            'BASE:', 'SOURCE:', 'FROM:', 'ALIGNED WITH:', 'RATIONALE:',
            'ADDITION:', 'REPRESENTS:', 'PATTERN:', 'SIMPLIFIED:',
            'MESSAGING APP ANALOGY:', 'MESSAGING APP PATTERN:', 'MESSAGING APP PATTERNS:',
            'MAF PATTERN:', 'M365:', 'PURPOSE:',
            'USE CASES:', 'EXAMPLES:', 'ALIGNMENT WITH', 'DIFFERENCES FROM',
            'COMPATIBILITY NOTES:', 'A2A', 'MODIFICATIONS:', 'EXTENSIBILITY:',
            'SEMANTIC DISTINCTION:', 'CRITICAL SEMANTIC DISTINCTION:', 'NOTE:', 'USAGE:', 'RELATIONSHIP:',
            'CREATED:', 'DELETED:', 'BEHAVIORAL IMPACT:', 'INSPIRED BY:',
            'AVAILABLE IN:', 'ADDED:', 'REMOVED:', 'WHY:', 'DESIGN:'
        ]

        # Remove comment markers and extract lines
        lines = []
        in_user_content = True

        for line in doc_comment.split('\n'):
            line = line.strip()

            # Remove comment markers
            if line.startswith('/**'):
                line = line[3:].strip()
            elif line.startswith('*/'):
                line = line[2:].strip()
            elif line.startswith('*'):
                line = line[1:].strip()

            # Clean up trailing comment markers
            if line.endswith('*/'):
                line = line[:-2].strip()

            # Skip structured documentation tags
            if line.startswith('@usage') or line.startswith('@example') or line.startswith('@response') or line.startswith('@param') or line.startswith('@see'):
                in_user_content = False
                continue

            # Stop including lines once we hit metadata section
            if line and any(line.startswith(tag) or line.upper().startswith(tag.upper()) for tag in metadata_tags):
                in_user_content = False
                continue

            # Skip lines that are part of metadata sections (indented continuation lines)
            if not in_user_content and line and (line.startswith('-') or line.startswith('•')):
                continue

            # Resume user content after blank line (end of metadata block)
            if not line and not in_user_content:
                in_user_content = True
                continue

            if line and in_user_content:
                lines.append(line)

        return '\n'.join(lines).strip()

    def _parse_structured_doc_comment(self, doc_comment: str) -> StructuredDocs:
        """
        Parse structured documentation from TypeSpec comment.

        Extracts:
        - @usage sections
        - @example blocks (with titles and code)
        - @response codes and descriptions
        - @param descriptions
        - @see references
        - Free-form sections (PURPOSE, EXAMPLES, etc.) for backward compatibility
        """
        if not doc_comment:
            return StructuredDocs()

        docs = StructuredDocs()

        # Remove comment markers
        lines = []
        for line in doc_comment.split('\n'):
            line = line.strip()
            if line.startswith('/**'):
                line = line[3:].strip()
            elif line.startswith('*/'):
                line = line[2:].strip()
            elif line.startswith('*'):
                line = line[1:].strip()
            if line.endswith('*/'):
                line = line[:-2].strip()
            lines.append(line)

        content = '\n'.join(lines)

        # Extract summary (first non-empty line before any @tag or section)
        first_line = True
        for line in lines:
            if line and not line.startswith('@') and not line.endswith(':'):
                docs.summary = line
                break

        # Parse @usage tag
        usage_match = re.search(r'@usage\s*\n((?:(?!@\w+).*\n?)*)', content, re.MULTILINE)
        if usage_match:
            docs.usage = usage_match.group(1).strip()

        # Parse @example tags
        # Format: @example Title\n```language\ncode\n```
        example_pattern = r'@example\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        for match in re.finditer(example_pattern, content, re.DOTALL):
            title = match.group(1).strip()
            language = match.group(2) or 'http'
            code = match.group(3).strip()
            docs.examples.append(Example(title=title, language=language, code=code))

        # Parse @response tags
        # Format: @response CODE Description
        response_pattern = r'@response\s+(\d+)\s+([^\n]+)\n((?:(?!@\w+).*\n?)*)'
        for match in re.finditer(response_pattern, content, re.MULTILINE):
            code = match.group(1)
            short_desc = match.group(2).strip()
            long_desc = match.group(3).strip()
            full_desc = f"{short_desc}\n{long_desc}".strip() if long_desc else short_desc
            docs.responses[code] = full_desc

        # Parse @param tags
        param_pattern = r'@param\s+(\w+)\s+(.*?)(?=@\w+|\Z)'
        for match in re.finditer(param_pattern, content, re.DOTALL):
            param_name = match.group(1)
            param_desc = match.group(2).strip()
            docs.params[param_name] = param_desc

        # Parse @see tags
        see_pattern = r'@see\s+([^\n]+)'
        docs.see_also = [match.group(1).strip() for match in re.finditer(see_pattern, content)]

        # Parse free-form sections for backward compatibility
        # Sections like PURPOSE:, EXAMPLES:, USE CASES:, etc.
        section_pattern = r'([A-Z][A-Z\s]+):\s*\n((?:(?![A-Z][A-Z\s]+:).*\n?)*)'
        for match in re.finditer(section_pattern, content):
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            if section_content:
                docs.raw_sections[section_name] = section_content

        return docs

    def _parse_models_and_enums(self, file_path: Path):
        """Parse models and enums from TypeSpec file."""
        content = file_path.read_text()
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            # Parse model
            model_match = re.match(r'model\s+(\w+)', stripped)
            if model_match:
                model_name = model_match.group(1)
                model, end_line = self._parse_model(lines, i, model_name)
                if model:
                    self.models[model_name] = model
                i = end_line
                continue

            # Parse enum
            enum_match = re.match(r'enum\s+(\w+)', stripped)
            if enum_match:
                enum_name = enum_match.group(1)
                enum_obj, end_line = self._parse_enum(lines, i, enum_name)
                if enum_obj:
                    self.enums[enum_name] = enum_obj
                i = end_line
                continue

            i += 1

    def _parse_model(self, lines: List[str], start_line: int, model_name: str) -> Tuple[Optional[Model], int]:
        """Parse a model definition."""
        model = Model(name=model_name)

        # Parse model-level doc comment (look backwards from start_line)
        model_doc = self._get_doc_comment_before(lines, start_line)
        if model_doc:
            model.doc_comment = model_doc
            model.description = self._parse_doc_comment(model_doc)
            model.structured_docs = self._parse_structured_doc_comment(model_doc)

        # Look for extends
        if 'extends' in lines[start_line]:
            extends_match = re.search(r'extends\s+([\w,\s]+)', lines[start_line])
            if extends_match:
                model.extends = [e.strip() for e in extends_match.group(1).split(',')]

        # Find opening brace
        i = start_line
        while i < len(lines) and '{' not in lines[i]:
            i += 1

        if i >= len(lines):
            return None, start_line + 1

        # Parse properties
        brace_depth = lines[i].count('{') - lines[i].count('}')
        i += 1

        current_doc_comment = ""
        while i < len(lines) and brace_depth > 0:
            line = lines[i].strip()
            brace_depth += lines[i].count('{') - lines[i].count('}')

            # Collect doc comments
            if line.startswith('/**') or line.startswith('*') or line.startswith('*/'):
                if line.startswith('/**'):
                    current_doc_comment = line
                elif current_doc_comment:
                    current_doc_comment += '\n' + line
                if line.startswith('*/'):
                    # Doc comment complete
                    pass
                i += 1
                continue

            # Parse property: propertyName: Type;
            prop_match = re.match(r'(\w+)(\?)?:\s*([^;]+);', line)
            if prop_match:
                prop_name = prop_match.group(1)
                optional = prop_match.group(2) == '?'
                prop_type = prop_match.group(3).strip()

                # Extract description from doc comment
                prop_desc = ""
                if current_doc_comment:
                    prop_desc = self._parse_doc_comment(current_doc_comment)
                    # Take first sentence only (before ALIGNED WITH, etc.)
                    if '\n' in prop_desc:
                        first_line = prop_desc.split('\n')[0].strip()
                        if first_line:
                            prop_desc = first_line
                    current_doc_comment = ""

                model.properties[prop_name] = (prop_type, prop_desc, not optional)

            i += 1

        return model, i

    def _get_doc_comment_before(self, lines: List[str], line_num: int) -> str:
        """Get doc comment immediately before a line."""
        doc_lines = []
        i = line_num - 1

        # Skip empty lines and decorators
        while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith('@')):
            i -= 1

        # Collect doc comment lines (backwards)
        while i >= 0:
            stripped = lines[i].strip()
            if stripped.startswith('*/'):
                doc_lines.insert(0, stripped)
                i -= 1
                continue
            elif stripped.startswith('*') or stripped.startswith('/**'):
                doc_lines.insert(0, stripped)
                if stripped.startswith('/**'):
                    break
                i -= 1
                continue
            else:
                break

        return '\n'.join(doc_lines) if doc_lines else ""

    def _parse_enum(self, lines: List[str], start_line: int, enum_name: str) -> Tuple[Optional[Enum], int]:
        """Parse an enum definition."""
        enum_obj = Enum(name=enum_name)

        # Parse enum-level doc comment
        enum_doc = self._get_doc_comment_before(lines, start_line)
        if enum_doc:
            enum_obj.description = self._parse_doc_comment(enum_doc)

        # Find opening brace
        i = start_line
        while i < len(lines) and '{' not in lines[i]:
            i += 1

        if i >= len(lines):
            return None, start_line + 1

        # Parse values
        brace_depth = lines[i].count('{') - lines[i].count('}')
        i += 1

        current_doc_comment = ""
        while i < len(lines) and brace_depth > 0:
            line = lines[i].strip()
            brace_depth += lines[i].count('{') - lines[i].count('}')

            # Collect doc comments
            if line.startswith('/**') or line.startswith('*') or line.startswith('*/'):
                if line.startswith('/**'):
                    current_doc_comment = line
                elif current_doc_comment:
                    current_doc_comment += '\n' + line
                i += 1
                continue

            # Parse enum value
            value_match = re.match(r'(\w+)[:,]?', line)
            if value_match and not line.startswith('//'):
                value_name = value_match.group(1)

                # Extract description from doc comment
                value_desc = ""
                if current_doc_comment:
                    value_desc = self._parse_doc_comment(current_doc_comment)
                    # Take first sentence only
                    if '\n' in value_desc:
                        first_line = value_desc.split('\n')[0].strip()
                        if first_line:
                            value_desc = first_line
                    current_doc_comment = ""

                enum_obj.values[value_name] = value_desc

            i += 1

        return enum_obj, i


class MarkdownGenerator:
    """Generate markdown API reference from parsed TypeSpec."""

    def __init__(self, parser: TypeSpecParser, output_dir: str):
        self.parser = parser
        self.output_dir = Path(output_dir)

    def generate_all(self):
        """Generate all API reference markdown files."""
        print("📝 Generating API reference markdown...\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "operations").mkdir(exist_ok=True)

        # Group endpoints by resource and type
        endpoints_by_resource = defaultdict(list)
        for endpoint in self.parser.endpoints:
            # Extract resource from path: /agents/... -> agents
            resource = endpoint.path.split('/')[1] if len(endpoint.path.split('/')) > 1 else 'other'
            endpoints_by_resource[resource].append(endpoint)

        # Separate subscriptions from main resources
        subscriptions = {}
        main_resources = {}
        for resource, endpoints in endpoints_by_resource.items():
            subscription_eps = [ep for ep in endpoints if 'subscriptions' in ep.path]
            main_eps = [ep for ep in endpoints if 'subscriptions' not in ep.path]

            if subscription_eps:
                singular = resource.rstrip("s") if resource.endswith("s") else resource
                subscriptions[f"{singular}-subscriptions"] = subscription_eps
            if main_eps:
                main_resources[resource] = main_eps

        # Generate INDIVIDUAL operation files (1 file per endpoint)
        endpoint_count = 0
        for resource, endpoints in sorted(main_resources.items()):
            for endpoint in endpoints:
                self._generate_individual_endpoint_file(endpoint)
                endpoint_count += 1

        for resource, endpoints in sorted(subscriptions.items()):
            for endpoint in endpoints:
                self._generate_individual_endpoint_file(endpoint)
                endpoint_count += 1

        # Generate INDIVIDUAL model files (1 file per model)
        # All models including tools, content types, and agent models are now in models/ directory
        model_count = 0
        for model_name in sorted(self.parser.models.keys()):
            model = self.parser.models[model_name]
            self._generate_individual_model_file(model_name, model)
            model_count += 1

        # Grouped reference files removed - all models now individual files
        # self._generate_content_types_file()  # Removed: models now in models/ directory
        # self._generate_tools_file()  # Removed: models now in models/ directory
        # self._generate_agents_models_file()  # Removed: models now in models/ directory

        # Generate operations/README.md (operations.md removed - redundant with README)
        # self._generate_operations_summary(main_resources, subscriptions)  # Removed: redundant consolidated file
        self._generate_operations_readme(main_resources, subscriptions)

        # Generate README
        self._generate_readme(main_resources, subscriptions)

        print(f"✓ Generated {endpoint_count} individual endpoint files")
        print(f"✓ Generated {model_count} individual model files")
        print(f"✓ Generated README\n")

    def _generate_operations_file(self, resource: str, endpoints: List[Endpoint]):
        """Generate markdown for operations in operations/ subdirectory."""
        output_file = self.output_dir / "operations" / f"{resource}.md"

        lines = []
        lines.append(f"# {resource.title()} API")
        lines.append("")
        lines.append(f"Operations for managing {resource}.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Sort endpoints by path and method
        endpoints.sort(key=lambda e: (e.path, e.method))

        for endpoint in endpoints:
            lines.extend(self._format_endpoint(endpoint))
            lines.append("")

        lines.append("<!-- GENERATED_END -->")

        output_file.write_text('\n'.join(lines))

    def _generate_individual_endpoint_file(self, endpoint: Endpoint):
        """Generate markdown for a single endpoint in its own file."""
        # Create filename: post-threads-threadid-subscriptions.md
        filename = self._endpoint_to_filename(endpoint)
        output_file = self.output_dir / "operations" / filename

        lines = []

        # Title from endpoint
        lines.append(f"# {endpoint.method} {endpoint.path}")
        lines.append("")

        # Brief description if available
        if endpoint.description:
            lines.append(endpoint.description.split('\n')[0])  # First line only
            lines.append("")

        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Format the endpoint details
        lines.extend(self._format_endpoint(endpoint))

        lines.append("")
        lines.append("<!-- GENERATED_END -->")

        # Ensure the operations directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text('\n'.join(lines))

    def _endpoint_to_filename(self, endpoint: Endpoint) -> str:
        """Convert endpoint to filename: POST /threads/{id} -> post-threads-id.md"""
        key = f"{endpoint.method} {endpoint.path}".lower()
        key = re.sub(r'[{}/\s]', '-', key)
        key = re.sub(r'-+', '-', key)
        key = key.strip('-')
        return f"{key}.md"

    def _generate_individual_model_file(self, model_name: str, model: 'Model'):
        """Generate markdown for a single model in its own file."""
        filename = self._model_to_filename(model_name)
        output_file = self.output_dir / "models" / filename

        lines = []

        # Title from model name
        lines.append(f"# {model_name}")
        lines.append("")

        # Brief description if available
        if model.description:
            lines.append(model.description.split('\n')[0])  # First line only
            lines.append("")

        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Format the model details
        lines.extend(self._format_model(model))

        lines.append("<!-- GENERATED_END -->")

        # Ensure the models directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text('\n'.join(lines))

    def _model_to_filename(self, model_name: str) -> str:
        """Convert model name to filename: AgentCard -> agentcard.md"""
        # Convert to lowercase and add .md extension
        filename = model_name.lower() + ".md"
        return filename

    def _format_endpoint(self, endpoint: Endpoint) -> List[str]:
        """Format an endpoint as markdown."""
        lines = []

        # Header
        lines.append(f"## {endpoint.method} {endpoint.path}")
        lines.append("")

        # Use structured documentation if available
        if endpoint.structured_docs and endpoint.structured_docs.usage:
            # Summary (brief description)
            if endpoint.structured_docs.summary:
                lines.append(endpoint.structured_docs.summary)
                lines.append("")

            # Usage section
            lines.append("### Usage")
            lines.append("")
            lines.append(endpoint.structured_docs.usage)
            lines.append("")

        elif endpoint.description:
            # Extract main description and examples separately
            desc_parts = endpoint.description.split('EXAMPLES:')
            main_desc = desc_parts[0]
            examples = desc_parts[1] if len(desc_parts) > 1 else ""

            # Clean up main description (remove REQUEST/RESPONSE/PURPOSE sections)
            desc_lines = []
            skip_section = False
            for line in main_desc.split('\n'):
                if line.strip() in ['REQUEST:', 'RESPONSE:', 'PURPOSE:', 'BEHAVIOR:', 'VALIDATION:', 'FROM:', 'INSPIRED BY:', 'RATIONALE:', 'USE CASES:', 'FOUNDRY SDK ALIGNMENT:']:
                    skip_section = True
                    continue
                if skip_section and line.strip().startswith('-'):
                    continue
                if skip_section and not line.strip():
                    skip_section = False
                    continue
                if not skip_section and line.strip():
                    desc_lines.append(line)

            if desc_lines:
                # Take first paragraph only for brevity
                first_para = []
                for line in desc_lines:
                    if line.strip():
                        first_para.append(line)
                    elif first_para:
                        break
                if first_para:
                    lines.append(' '.join(first_para))
                    lines.append("")

        # Path parameters
        path_params = [p for p in endpoint.parameters if p.location == 'path']
        if path_params:
            lines.append("### Path Parameters")
            lines.append("")
            lines.append("| Parameter | Type | Required | Description |")
            lines.append("|-----------|------|----------|-------------|")
            for param in path_params:
                required = "Yes" if param.required else "No"
                lines.append(f"| `{param.name}` | `{param.type}` | {required} | {param.description} |")
            lines.append("")

        # Query parameters
        query_params = [p for p in endpoint.parameters if p.location == 'query']
        if query_params:
            lines.append("### Query Parameters")
            lines.append("")
            lines.append("| Parameter | Type | Required | Description |")
            lines.append("|-----------|------|----------|-------------|")
            for param in query_params:
                required = "Yes" if param.required else "No"
                lines.append(f"| `{param.name}` | `{param.type}` | {required} | {param.description} |")
            lines.append("")

        # Request body
        body_params = [p for p in endpoint.parameters if p.location == 'body']
        if body_params:
            lines.append("### Request Body")
            lines.append("")
            for param in body_params:
                lines.append(f"**Type:** `{param.type}`")
                lines.append("")
                if param.description:
                    lines.append(param.description)
                    lines.append("")

        # Response - use structured docs if available
        if endpoint.structured_docs and endpoint.structured_docs.responses:
            lines.append("### Responses")
            lines.append("")
            # Sort by status code
            for code in sorted(endpoint.structured_docs.responses.keys(), key=int):
                description = endpoint.structured_docs.responses[code]
                lines.append(f"**{code}**: {description}")
                lines.append("")
        elif endpoint.response_types:
            # Legacy format fallback
            lines.append("### Response")
            lines.append("")

            # Check for @statusCode decorator
            success_code = "200 OK"
            for decorator in endpoint.decorators:
                if decorator.startswith('@statusCode'):
                    code_match = re.search(r'@statusCode\((\d+)\)', decorator)
                    if code_match:
                        code = code_match.group(1)
                        if code == "201":
                            success_code = "201 Created"
                        elif code == "202":
                            success_code = "202 Accepted"
                        elif code == "204":
                            success_code = "204 No Content"

            for resp_type in endpoint.response_types:
                # Map error types to status codes with descriptions
                if 'Error' in resp_type:
                    status_code, description = self._map_error_to_status(resp_type, endpoint.method)
                    lines.append(f"- **{status_code}:** {description}")
                elif resp_type in ['void', '{}']:
                    # Void responses typically mean success with no body
                    if endpoint.method == 'DELETE':
                        lines.append(f"- **204 No Content:** Resource deleted successfully")
                    else:
                        lines.append(f"- **{success_code}:** Operation completed successfully")
                else:
                    # Success response with body
                    lines.append(f"- **{success_code}:** Returns `{resp_type}`")
            lines.append("")

        # Add examples from structured docs or legacy format
        if endpoint.structured_docs and endpoint.structured_docs.examples:
            lines.append("### Examples")
            lines.append("")
            for example in endpoint.structured_docs.examples:
                # Example title
                lines.append(f"#### {example.title}")
                lines.append("")
                # Code block
                lines.append(f"```{example.language}")
                lines.append(example.code)
                lines.append("```")
                lines.append("")
        elif endpoint.description and 'EXAMPLES:' in endpoint.description:
            # Legacy format fallback
            examples_part = endpoint.description.split('EXAMPLES:')[1]

            # Stop at next major section
            for stop_marker in ['RATIONALE:', 'DIFFERENCES', 'USE CASES:', 'NOTE:', 'IMPORTANT:', 'WARNING:']:
                if stop_marker in examples_part:
                    examples_part = examples_part.split(stop_marker)[0]

            lines.append("### Examples")
            lines.append("")
            # Clean up examples (remove excessive whitespace, normalize code blocks)
            example_lines = []
            in_code_block = False
            for line in examples_part.split('\n'):
                stripped = line.strip()
                if not stripped:
                    if in_code_block:
                        example_lines.append('')
                    continue
                if stripped.startswith('```'):
                    in_code_block = not in_code_block
                    example_lines.append('```json' if in_code_block else '```')
                else:
                    example_lines.append(stripped)

            if example_lines:
                lines.extend(example_lines)
                lines.append("")

        lines.append("---")
        return lines


    def _generate_content_types_file(self):
        """Generate content-types.md with all AIContent types."""
        output_file = self.output_dir / "content-types.md"

        lines = []
        lines.append("# Content Types")
        lines.append("")
        lines.append("Multi-modal content types supported by the Agent Runtime API.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Filter content type models
        content_models = {name: model for name, model in self.parser.models.items()
                         if 'Content' in name and name not in ['AIContent']}

        # Group by category
        categories = {
            'Text & Reasoning': ['TextContent', 'TextReasoningContent'],
            'Tool Execution': ['FunctionCallContent', 'FunctionResultContent', 'ErrorContent'],
            'Multi-Modal': ['ImageContent', 'AudioContent', 'VideoContent', 'FileContent', 'TranscriptContent'],
            'References': ['SearchResultContent', 'DocumentContent', 'UriContent', 'DataContent', 'HostedFileContent', 'HostedVectorStoreContent'],
            'Rich UI': ['AdaptiveCardContent', 'SuggestedActionsContent', 'UserInputRequestContent'],
            'Platform Events': ['EventContent', 'TraceContent', 'ActionContent'],
            'Presence': ['TypingIndicatorContent', 'MessageReactionContent', 'MessageDeleteContent', 'MessageUpdateContent'],
            'Moderation': ['RefusalContent', 'ContentFilterResultContent']
        }

        for category, model_names in categories.items():
            lines.append(f"## {category}")
            lines.append("")

            for model_name in model_names:
                if model_name in content_models:
                    model = content_models[model_name]
                    lines.extend(self._format_model(model))
                    lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))

    def _generate_tools_file(self):
        """Generate tools.md with tool-related models."""
        output_file = self.output_dir / "tools.md"

        lines = []
        lines.append("# Tools")
        lines.append("")
        lines.append("Tool definition and execution models.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Filter tool-related models
        tool_models = {name: model for name, model in self.parser.models.items()
                      if 'Tool' in name or name in ['Connection', 'Scopes', 'JSONSchema']}

        for model_name in sorted(tool_models.keys()):
            model = tool_models[model_name]
            lines.extend(self._format_model(model))
            lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))

    def _generate_readme(self, main_resources: dict, subscriptions: dict):
        """Generate README.md with index."""
        output_file = self.output_dir / "README.md"

        lines = []
        lines.append("# API Reference")
        lines.append("")
        lines.append("Complete API reference for the Agent Runtime API.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        lines.append("## Core Resources")
        lines.append("")
        for resource in sorted(main_resources.keys()):
            lines.append(f"- [{resource.title()}](operations/{resource}.md) - {resource.title()} operations")
        lines.append("")

        lines.append("## Subscriptions (Webhooks)")
        lines.append("")
        for resource in sorted(subscriptions.keys()):
            display_name = resource.replace('-', ' ').title()
            lines.append(f"- [{display_name}](operations/{resource}.md) - Webhook subscriptions")
        lines.append("")

        lines.append("## Data Models")
        lines.append("")
        lines.append("- [Models](models.md) - Core data models")
        lines.append("- [Content Types](content-types.md) - Multi-modal content")
        lines.append("- [Tools](tools.md) - Tool definitions")
        lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))


    def _map_error_to_status(self, error_type: str, method: str) -> Tuple[str, str]:
        """Map error type to HTTP status code and description."""
        error_mappings = {
            'NotFoundError': ('404 Not Found', 'Resource not found'),
            'BadRequestError': ('400 Bad Request', 'Invalid request parameters'),
            'ValidationError': ('400 Bad Request', 'Request validation failed'),
            'UnauthorizedError': ('401 Unauthorized', 'Authentication required'),
            'ForbiddenError': ('403 Forbidden', 'Access denied'),
            'ConflictError': ('409 Conflict', 'Resource conflict'),
            'TooManyRequestsError': ('429 Too Many Requests', 'Rate limit exceeded'),
            'InternalServerError': ('500 Internal Server Error', 'Server error'),
            'ServiceUnavailableError': ('503 Service Unavailable', 'Service temporarily unavailable'),
        }

        return error_mappings.get(error_type, ('500 Internal Server Error', f'Error: `{error_type}`'))

        lines.append("---")
        return lines

    def _generate_models_file(self):
        """Generate models reference file."""
        output_file = self.output_dir / "models.md"

        lines = []
        lines.append("# Data Models")
        lines.append("")
        lines.append("API data model definitions.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Sort models alphabetically
        for model_name in sorted(self.parser.models.keys()):
            model = self.parser.models[model_name]
            lines.extend(self._format_model(model))
            lines.append("")

        # Add enums
        lines.append("## Enums")
        lines.append("")
        for enum_name in sorted(self.parser.enums.keys()):
            enum_obj = self.parser.enums[enum_name]
            lines.extend(self._format_enum(enum_obj))
            lines.append("")

        lines.append("<!-- GENERATED_END -->")

        output_file.write_text('\n'.join(lines))

    def _format_model(self, model: Model) -> List[str]:
        """Format a model as markdown."""
        lines = []
        lines.append(f"## {model.name}")
        lines.append("")

        # Description
        if model.description:
            lines.append(model.description)
            lines.append("")

        # Usage section from structured docs
        if model.structured_docs and model.structured_docs.usage:
            lines.append("### Usage")
            lines.append("")
            lines.append(model.structured_docs.usage)
            lines.append("")

        # Extends
        if model.extends:
            lines.append(f"**Extends:** {', '.join(f'`{e}`' for e in model.extends)}")
            lines.append("")

        # Properties table
        if model.properties:
            lines.append("### Properties")
            lines.append("")
            lines.append("| Property | Type | Required | Description |")
            lines.append("|----------|------|----------|-------------|")
            for prop_name, (prop_type, prop_desc, required) in sorted(model.properties.items()):
                required_str = "Yes" if required else "No"
                lines.append(f"| `{prop_name}` | `{prop_type}` | {required_str} | {prop_desc} |")
            lines.append("")

        # Example section from structured docs
        if model.structured_docs and model.structured_docs.examples:
            lines.append("### Examples")
            lines.append("")
            for example in model.structured_docs.examples:
                if example.title != "Example 1":  # Only show title if not default
                    lines.append(f"#### {example.title}")
                    lines.append("")
                lines.append(f"```{example.language}")
                lines.append(example.code)
                lines.append("```")
                lines.append("")

        lines.append("---")
        return lines

    def _format_enum(self, enum_obj: Enum) -> List[str]:
        """Format an enum as markdown."""
        lines = []
        lines.append(f"### {enum_obj.name}")
        lines.append("")

        if enum_obj.description:
            lines.append(enum_obj.description)
            lines.append("")

        if enum_obj.values:
            lines.append("| Value | Description |")
            lines.append("|-------|-------------|")
            for value, desc in sorted(enum_obj.values.items()):
                lines.append(f"| `{value}` | {desc} |")
            lines.append("")

        return lines


    def _generate_agents_models_file(self):
        """Generate agents.md with agent model documentation (not operations)."""
        output_file = self.output_dir / "agents.md"

        lines = []
        lines.append("# Agents")
        lines.append("")
        lines.append("Agent configuration, discovery, and registration models.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # Agent-related models
        agent_models = ['AgentDefinition', 'PromptAgent', 'AgentCard', 'AgentModel', 'ModelOptions',
                       'ModelCapabilities', 'PropertySchema', 'PromptTemplate', 'GuardrailResult',
                       'ThreadWatch', 'AutoResponseConfig', 'WatchCondition', 'RemoteCondition']

        for model_name in agent_models:
            if model_name in self.parser.models:
                model = self.parser.models[model_name]
                lines.extend(self._format_model(model))
                lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))

    def _generate_operations_summary(self, main_resources: dict, subscriptions: dict):
        """Generate operations.md with consolidated view of all operations."""
        output_file = self.output_dir / "operations.md"

        lines = []
        lines.append("# API Operations")
        lines.append("")
        lines.append("Complete list of all REST API endpoints.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        # All resources
        for resource, endpoints in sorted(main_resources.items()):
            lines.append(f"## {resource.title()}")
            lines.append("")
            for endpoint in sorted(endpoints, key=lambda e: (e.path, e.method)):
                lines.extend(self._format_endpoint(endpoint))
                lines.append("")

        # Subscriptions
        for resource, endpoints in sorted(subscriptions.items()):
            display_name = resource.replace('-', ' ').title()
            lines.append(f"## {display_name}")
            lines.append("")
            for endpoint in sorted(endpoints, key=lambda e: (e.path, e.method)):
                lines.extend(self._format_endpoint(endpoint))
                lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))

    def _generate_operations_readme(self, main_resources: dict, subscriptions: dict):
        """Generate operations/README.md with index for operations."""
        output_file = self.output_dir / "operations" / "README.md"

        lines = []
        lines.append("# API Operations")
        lines.append("")
        lines.append("REST API endpoint documentation organized by resource type.")
        lines.append("")
        lines.append("<!-- GENERATED_START -->")
        lines.append("")

        lines.append("## Resources")
        lines.append("")
        for resource in sorted(main_resources.keys()):
            lines.append(f"- [{resource.title()}](./{resource}.md) - {resource.title()} operations")
        lines.append("")

        lines.append("## Webhook Subscriptions")
        lines.append("")
        for resource in sorted(subscriptions.keys()):
            display_name = resource.replace('-', ' ').title()
            lines.append(f"- [{display_name}](./{resource}.md) - Webhook subscriptions")
        lines.append("")

        lines.append("<!-- GENERATED_END -->")
        output_file.write_text('\n'.join(lines))


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    typespec_dir = project_root / "typespec"
    output_dir = project_root / ".generated" / "api-reference"

    # Parse TypeSpec
    parser = TypeSpecParser(str(typespec_dir))
    parser.parse_all()

    # Generate markdown
    generator = MarkdownGenerator(parser, str(output_dir))
    generator.generate_all()

    print(f"✅ Generated API reference in {output_dir}")
    print(f"docs/api-reference/ directory")


if __name__ == "__main__":
    main()

