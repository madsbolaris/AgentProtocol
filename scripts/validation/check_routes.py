#!/usr/bin/env python3
"""
Check if API routes/endpoints used in documentation exist in TypeSpec.

This script:
1. Extracts all @route definitions from TypeSpec files
2. Searches documentation for API endpoint references
3. Reports endpoints used in docs that don't exist in TypeSpec
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class RouteChecker:
    """Check if documentation routes exist in TypeSpec."""

    def __init__(self, typespec_dir: str, docs_dirs: List[str]):
        self.typespec_dir = Path(typespec_dir)
        self.docs_dirs = [Path(d) for d in docs_dirs]

        # TypeSpec routes
        self.routes: Set[str] = set()  # e.g., "/agents", "/threads/{threadId}"
        self.route_methods: Dict[str, Set[str]] = defaultdict(set)  # route -> {GET, POST, ...}

        # Issues found
        self.issues: List[Dict] = []

    def parse_typespec(self):
        """Parse TypeSpec files to extract all route definitions."""
        print("📖 Parsing TypeSpec routes...\n")

        for tsp_file in self.typespec_dir.glob("**/*.tsp"):
            content = tsp_file.read_text()
            self._parse_typespec_file(content)

        print(f"✓ Found {len(self.routes)} routes in TypeSpec")
        if self.routes:
            print(f"  Examples: {', '.join(sorted(list(self.routes))[:10])}\n")
        else:
            print("  ⚠️  No routes found - TypeSpec might not define routes explicitly\n")

    def _parse_typespec_file(self, content: str):
        """Parse a single TypeSpec file to extract routes."""
        # Line-by-line parsing to track interface context
        lines = content.split('\n')
        current_base_route = None
        in_interface = False
        brace_depth = 0
        pending_decorators = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track @route decorator
            route_match = re.match(r'@route\("([^"]+)"\)', stripped)
            if route_match:
                current_base_route = route_match.group(1)
                continue

            # Track interface start
            if 'interface' in stripped and current_base_route and '{' in stripped:
                in_interface = True
                brace_depth = stripped.count('{') - stripped.count('}')
                self.routes.add(current_base_route)
                continue

            if not in_interface:
                continue

            # Track brace depth to know when interface ends
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth <= 0:
                in_interface = False
                current_base_route = None
                pending_decorators = []
                continue

            # Collect decorators
            if stripped.startswith('@'):
                pending_decorators.append(stripped)
                continue

            # Check if this line starts an operation (has function name with parenthesis)
            if '(' in stripped and any(d.startswith(f'@{method}') for d in pending_decorators for method in ['get', 'post', 'put', 'patch', 'delete']):
                # Extract method
                method = None
                segment = None

                for decorator in pending_decorators:
                    # Check for HTTP method
                    for http_method in ['get', 'post', 'put', 'patch', 'delete']:
                        if decorator.startswith(f'@{http_method}'):
                            method = http_method.upper()
                            break

                    # Check for @segment
                    segment_match = re.match(r'@segment\("([^"]+)"\)', decorator)
                    if segment_match:
                        segment = segment_match.group(1)

                if method:
                    if segment:
                        # Build full route with @segment
                        full_route = f"{current_base_route}/{segment}"
                        self.routes.add(full_route)
                        self.route_methods[full_route].add(method)
                    else:
                        # No @segment, check for @path parameters in operation signature
                        # Pattern: functionName(@path paramName: type)
                        path_params = re.findall(r'@path\s+(\w+):', stripped)
                        if path_params:
                            # Filter out parameters already in base route
                            # E.g., /agents/{agentId}/subscriptions with @path agentId, @path subscriptionId
                            # Should only add subscriptionId
                            new_params = [p for p in path_params if f'{{{p}}}' not in current_base_route]
                            if new_params:
                                # Build route with new path parameters
                                # E.g., @get get(@path runId: string) -> /runs/{runId}
                                param_segments = '/'.join(f'{{{param}}}' for param in new_params)
                                full_route = f"{current_base_route}/{param_segments}"
                                self.routes.add(full_route)
                                self.route_methods[full_route].add(method)
                            else:
                                # All parameters already in base route
                                self.route_methods[current_base_route].add(method)
                        else:
                            # Operation uses base route directly
                            self.route_methods[current_base_route].add(method)

                # Clear pending decorators
                pending_decorators = []

    def check_docs(self):
        """Check documentation for undefined routes."""
        print("🔍 Checking documentation for undefined routes...\n")

        # Common patterns for API endpoints in docs
        patterns = [
            # Full HTTP request format: GET /path or POST /path/{param}
            (r'(?:GET|POST|PUT|PATCH|DELETE)\s+(\/[\w\-\/\{\}]+)', 'HTTP_METHOD'),
            # Code examples: f"{API_BASE}/path"  or "{API_BASE}/path/{param}"
            (r'["\'](?:\{API_BASE\}|\/api)?(\/[\w\-\/\{\}]+)["\']', 'CODE_ENDPOINT'),
            # Markdown headers: ## GET /path or ### POST /path
            (r'##\s+(?:GET|POST|PUT|PATCH|DELETE)\s+(\/[\w\-\/\{\}]+)', 'HEADER_ENDPOINT'),
        ]

        # Find all markdown files
        md_files = []
        for docs_dir in self.docs_dirs:
            if docs_dir.exists():
                md_files.extend(docs_dir.glob("**/*.md"))

        for md_file in md_files:
            # Skip .workspace directory
            if '.workspace' in str(md_file):
                continue
            self._check_file(md_file, patterns)

        # Remove duplicates
        seen = set()
        unique_issues = []
        for issue in self.issues:
            key = (issue['endpoint'], issue['type'])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        self.issues = unique_issues

    def _check_file(self, file_path: Path, patterns: List[tuple]):
        """Check a single file for undefined routes."""
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return

        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, content):
                endpoint = match.group(1)

                # Normalize endpoint (remove query params, anchors, trailing slashes)
                endpoint = endpoint.split('?')[0].split('#')[0].rstrip('/')

                # Skip if endpoint exists in TypeSpec
                if self._endpoint_exists(endpoint):
                    continue

                # Skip common non-API paths
                skip_patterns = [
                    '/docs', '/specifications', '/guides', '/typespec',
                    '/examples', '/api-reference', '/Users', '/home',
                    '/var', '/etc', '/tmp', '/opt'
                ]
                if any(skip in endpoint for skip in skip_patterns):
                    continue

                # Skip example webhook URLs (client-side, not our API)
                webhook_patterns = [
                    '/webhooks/', '/webhook',  # Client webhook endpoints
                    '/ws/',  # WebSocket URLs
                    '/admin/',  # Example admin endpoints
                ]
                if any(pattern in endpoint for pattern in webhook_patterns):
                    continue

                # Skip example external/remote API endpoints (not our API)
                external_patterns = [
                    '/public-api/', '/content-filter', '/tools/', '/authorize',
                    '/check', '/search', '/data', '/upload', '/download',
                    '/token',  # OAuth token endpoint examples
                    '/evaluate', '/hook', '/watch',  # Remote condition/hook endpoint examples
                ]
                # Only skip if they look like external examples (not our API routes)
                if any(pattern in endpoint for pattern in external_patterns) and not endpoint.startswith('/agents') and not endpoint.startswith('/runs') and not endpoint.startswith('/threads'):
                    continue

                # Skip generic placeholders
                if endpoint in ['/resources', '/resource', '/api', '/service']:
                    continue

                # Skip message endpoint examples (these may be valid but incomplete in docs)
                if endpoint in ['/messages', '/messages/{messageId}']:
                    continue

                # Skip webhook management examples
                if 'subscriptions' in endpoint and ('/deliveries' in endpoint or '/test' in endpoint):
                    continue

                # Skip generic resourceId placeholders
                if '{resourceId}' in endpoint:
                    continue

                # Skip very short paths (likely not real endpoints)
                if len(endpoint) < 4:
                    continue

                # Get line number and context
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                # Skip if in comment explaining something was removed
                skip_words = ['removed', 'deprecated', 'old', 'example', 'sample']
                if any(word in line_content.lower() for word in skip_words):
                    continue

                # Report issue
                self.issues.append({
                    'file': str(file_path.relative_to(self.typespec_dir.parent)),
                    'line': line_num,
                    'endpoint': endpoint,
                    'pattern_type': pattern_type,
                    'type': 'UNDEFINED_ROUTE',
                    'severity': 'ERROR',
                    'message': f'Endpoint "{endpoint}" not found in TypeSpec routes',
                    'line_content': line_content[:100]
                })

    def _endpoint_exists(self, endpoint: str) -> bool:
        """Check if endpoint exists in TypeSpec routes."""
        # Direct match
        if endpoint in self.routes:
            return True

        # Check with parameter placeholders
        # e.g., /threads/thread-123 might match /threads/{threadId}
        for route in self.routes:
            if self._matches_route_pattern(endpoint, route):
                return True

        return False

    def _matches_route_pattern(self, endpoint: str, route_pattern: str) -> bool:
        """Check if endpoint matches a route pattern with parameters."""
        # Convert route pattern to regex
        # /threads/{threadId} -> /threads/[^/]+
        pattern = route_pattern
        pattern = re.sub(r'\{[^}]+\}', '[^/]+', pattern)
        pattern = f'^{pattern}$'

        return bool(re.match(pattern, endpoint))

    def report_issues(self):
        """Report all issues found."""
        if not self.issues:
            print("✅ All documented endpoints exist in TypeSpec!\n")
            return

        # Group by endpoint
        endpoints_count = defaultdict(list)
        for issue in self.issues:
            endpoints_count[issue['endpoint']].append(issue)

        print(f"❌ Found {len(endpoints_count)} undefined endpoints used in documentation:\n")

        # Report by frequency
        print("UNDEFINED ENDPOINTS (sorted by frequency):")
        print("=" * 80)

        sorted_endpoints = sorted(endpoints_count.items(), key=lambda x: len(x[1]), reverse=True)

        for endpoint, occurrences in sorted_endpoints[:30]:  # Top 30
            print(f"\n\"{endpoint}\" - {len(occurrences)} occurrences")
            print(f"  Not found in TypeSpec routes")

            # Show first few locations
            for issue in occurrences[:3]:
                print(f"  - {issue['file']}:{issue['line']}")

            if len(occurrences) > 3:
                print(f"  ... and {len(occurrences) - 3} more occurrences")

        if len(sorted_endpoints) > 30:
            print(f"\n  ... and {len(sorted_endpoints) - 30} more undefined endpoints")

        # Summary by file
        print("\n\nSUMMARY BY FILE:")
        print("=" * 80)
        files_count = defaultdict(int)
        for issue in self.issues:
            files_count[issue['file']] += 1

        for file_path, count in sorted(files_count.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"{count:3d} undefined endpoints: {file_path}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    typespec_dir = project_root / "typespec"
    docs_dirs = [
        project_root / "api-reference",
        project_root / "guides",
        project_root / "specifications",
    ]

    # Parse TypeSpec
    checker = RouteChecker(str(typespec_dir), [str(d) for d in docs_dirs])
    checker.parse_typespec()

    # Check documentation
    checker.check_docs()
    checker.report_issues()

    # Exit with error if undefined routes found
    if checker.issues:
        print(f"\n❌ Found {len(set(i['endpoint'] for i in checker.issues))} undefined endpoints")
        print("These endpoints are used in documentation but not defined in TypeSpec")
        exit(1)
    else:
        print("\n✅ All documented endpoints exist in TypeSpec")
        exit(0)


if __name__ == "__main__":
    main()
