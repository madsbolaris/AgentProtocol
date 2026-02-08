#!/usr/bin/env python3
"""
Generate JSON golden files for echo bot integration tests.

This script:
1. Reads XML input files from test-data/input/
2. Sends each to the echo bot with ?format=json
3. Saves JSON responses to test-data/results/echom365/json/

Prerequisites:
- Echo bot must be running on http://localhost:3978
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import httpx
from lxml import etree


def read_xml_file(xml_path: Path) -> str:
    """Read XML file content."""
    return xml_path.read_text()


def xml_to_agent_protocol_message(xml_content: str) -> Dict[str, Any]:
    """
    Convert XML message to Agent Protocol JSON format.

    This is a simplified conversion for testing purposes.
    """
    root = etree.fromstring(xml_content.encode('utf-8'))

    # Extract role from root element tag
    role = root.tag

    # Build message
    message = {
        "role": role,
        "contents": []
    }

    # Add message-id if present
    if "message-id" in root.attrib:
        message["messageId"] = root.attrib["message-id"]

    # Extract text contents
    for text_elem in root.findall(".//text"):
        content = {
            "kind": "text",
            "text": text_elem.text or ""
        }
        if "audience" in text_elem.attrib:
            content["audience"] = text_elem.attrib["audience"]
        message["contents"].append(content)

    # If no text contents, add empty one
    if not message["contents"]:
        message["contents"].append({"kind": "text", "text": ""})

    return message


def generate_json_golden_file(
    input_file: Path,
    output_dir: Path,
    base_url: str = "http://localhost:3978"
) -> None:
    """Generate a JSON golden file from an XML input file."""

    print(f"Processing {input_file.name}...")

    try:
        # Read XML input
        xml_content = read_xml_file(input_file)

        # Convert to Agent Protocol message
        message = xml_to_agent_protocol_message(xml_content)

        # Create run request
        run_request = {
            "agentId": "echo-agent",
            "input": [message]
        }

        # Send request to echo bot with format=json
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{base_url}/runs/wait",
                params={"format": "json"},
                json=run_request
            )
            response.raise_for_status()

            # Get JSON response
            result = response.json()

            # Generate output filename
            output_file = output_dir / f"{input_file.stem}-result.json"

            # Save JSON with pretty printing
            output_file.write_text(json.dumps(result, indent=2) + "\n")

            print(f"  ✅ Generated {output_file.name}")

    except Exception as e:
        print(f"  ❌ Error: {e}")


def main():
    """Main entry point."""
    # Setup paths
    repo_root = Path(__file__).parent.parent
    input_dir = repo_root / "test-data" / "input"
    output_dir = repo_root / "test-data" / "results" / "echom365" / "json"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if echo bot is running
    try:
        with httpx.Client(timeout=5.0) as client:
            health = client.get("http://localhost:3978/health")
            health.raise_for_status()
            print("✅ Echo bot is running\n")
    except Exception as e:
        print("❌ Echo bot is not running!")
        print(f"   Error: {e}")
        print("\nPlease start the echo bot first:")
        print("  cd python/samples/agents/echo-bot")
        print("  python src/main.py")
        sys.exit(1)

    # Get all XML input files
    xml_files = sorted(input_dir.glob("*.xml"))

    if not xml_files:
        print(f"❌ No XML files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(xml_files)} input files\n")

    # Generate golden files
    for xml_file in xml_files:
        generate_json_golden_file(xml_file, output_dir)

    print(f"\n✅ Generated {len(xml_files)} JSON golden files in {output_dir}")


if __name__ == "__main__":
    main()
