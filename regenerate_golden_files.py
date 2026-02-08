#!/usr/bin/env python3
"""
Regenerate golden files for basic-m365 agent tests.
Reads XML input files, sends them to the .NET server, and saves responses.
"""

import json
import requests
from pathlib import Path
from xml.etree import ElementTree as ET

# Configuration
DOTNET_URL = "http://localhost:3981"
INPUT_DIR = Path("test-data/input")
OUTPUT_DIR = Path("test-data/results/basic-m365")
TEST_FILES = ["50-weather-query", "51-time-query", "52-multi-function", "53-no-function"]

def parse_xml_to_message(xml_content: str) -> dict:
    """Parse XML user message into Agent Protocol format."""
    root = ET.fromstring(xml_content)

    # Extract text from <text> element
    text_elem = root.find(".//text")
    text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

    return {
        "role": "user",
        "contents": [
            {
                "kind": "text",
                "text": text
            }
        ]
    }

def generate_golden_files():
    """Generate golden files for all test cases."""
    print("🚀 Regenerating golden files from .NET server...")
    print(f"   Server: {DOTNET_URL}")
    print(f"   Using LLM recordings for deterministic results\n")

    for test_name in TEST_FILES:
        input_file = INPUT_DIR / f"{test_name}.xml"

        if not input_file.exists():
            print(f"⚠️  Skipping {test_name}: input file not found")
            continue

        print(f"📝 Processing {test_name}...")

        # Read and parse input XML
        xml_content = input_file.read_text()
        message = parse_xml_to_message(xml_content)

        # Create run request
        request_data = {
            "agentId": "basic-m365-agent",
            "input": [message]
        }

        # Generate JSON golden file
        try:
            response = requests.post(
                f"{DOTNET_URL}/runs/wait?format=json",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()

            json_output = OUTPUT_DIR / "json" / f"{test_name}-result.json"
            json_output.parent.mkdir(parents=True, exist_ok=True)
            json_output.write_text(json.dumps(response.json(), indent=2))
            print(f"   ✅ Generated {json_output.relative_to('.')}")
        except Exception as e:
            print(f"   ❌ Failed to generate JSON: {e}")
            continue

        # Generate XML golden file
        try:
            response = requests.post(
                f"{DOTNET_URL}/runs/wait?format=xml",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()

            xml_output = OUTPUT_DIR / "xml" / f"{test_name}-result.xml"
            xml_output.parent.mkdir(parents=True, exist_ok=True)
            xml_output.write_text(response.text)
            print(f"   ✅ Generated {xml_output.relative_to('.')}")
        except Exception as e:
            print(f"   ❌ Failed to generate XML: {e}")

    print("\n✨ Golden file regeneration complete!")

if __name__ == "__main__":
    generate_golden_files()
