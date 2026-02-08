#!/usr/bin/env python3
"""
Generate golden result files for echo bot test inputs.

This script reads XML input files (standalone messages) and generates
the expected echo bot responses as both XML Thread documents and JSON RunWaitResponse.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from lxml import etree


def create_echo_response(input_xml: str) -> tuple[str, str]:
    """
    Create echo bot response from input message.

    The echo bot extracts text from the input message and echoes it back
    in an agent message wrapped in a Thread document.

    Args:
        input_xml: The input message XML

    Returns:
        Tuple of (xml_response, json_response)
    """
    # Parse input XML
    try:
        root = etree.fromstring(input_xml.encode('utf-8'))
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None, None

    # Extract text from input message
    text_content = []

    # Handle different message types
    if root.tag == "user":
        # User message - extract text content
        for text_elem in root.findall(".//text"):
            text = text_elem.text
            if text:
                text_content.append(text.strip())
    elif root.tag == "agent":
        # Agent message - extract text content
        for text_elem in root.findall(".//text"):
            text = text_elem.text
            if text:
                text_content.append(text.strip())
    elif root.tag == "tool":
        # Tool message - extract result content
        for result_elem in root.findall(".//result"):
            text = result_elem.text
            if text:
                text_content.append(text.strip())
        # Also check for error content
        for error_elem in root.findall(".//error"):
            msg_elem = error_elem.find("message")
            if msg_elem is not None and msg_elem.text:
                text_content.append(f"Error: {msg_elem.text.strip()}")
    elif root.tag == "channel":
        # Channel message - extract any text content
        for text_elem in root.findall(".//text"):
            text = text_elem.text
            if text:
                text_content.append(text.strip())

    # If no text found, create a generic response
    if not text_content:
        echo_text = f"Received {root.tag} message"
    else:
        combined_text = " ".join(text_content)
        echo_text = f"You said: {combined_text}"

    # Generate IDs and timestamps
    thread_id = f"thread_{uuid.uuid4().hex[:16]}"
    run_id = f"run_{uuid.uuid4().hex[:16]}"
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Create XML response (Thread document)
    xml_output = f"""<?xml version='1.0' encoding='utf-8'?>
<thread thread-id="{thread_id}" status="active" created-at="{created_at}">
  <agent>
    <text>{escape_xml(echo_text)}</text>
  </agent>
</thread>
"""

    # Create JSON response (RunWaitResponse)
    json_output = {
        "runId": run_id,
        "agentId": "echo-agent",
        "threadId": thread_id,
        "status": "completed",
        "input": [],
        "output": [
            {
                "role": "agent",
                "contents": [
                    {
                        "kind": "text",
                        "text": echo_text
                    }
                ]
            }
        ],
        "createdAt": created_at,
        "completedAt": created_at
    }

    return xml_output, json.dumps(json_output, indent=2)


def escape_xml(text: str) -> str:
    """Escape special characters for XML."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;"))


def main():
    """Generate golden files for all inputs without results."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "test-data" / "input"
    xml_results_dir = project_root / "test-data" / "results" / "echobot" / "xml"
    json_results_dir = project_root / "test-data" / "results" / "echobot" / "json"

    # Ensure result directories exist
    xml_results_dir.mkdir(parents=True, exist_ok=True)
    json_results_dir.mkdir(parents=True, exist_ok=True)

    # Find all input files without results
    files_to_process = []
    for xml_file in sorted(input_dir.glob("*.xml")):
        xml_result_file = xml_results_dir / f"{xml_file.stem}-result.xml"
        if not xml_result_file.exists():
            files_to_process.append(xml_file)

    print(f"Found {len(files_to_process)} input files without results\n")

    # Process each file
    success_count = 0
    error_count = 0

    for input_file in files_to_process:
        print(f"Processing: {input_file.name}")

        try:
            # Read input
            input_xml = input_file.read_text()

            # Generate responses
            xml_response, json_response = create_echo_response(input_xml)

            if xml_response is None:
                print(f"  ❌ Failed to generate response")
                error_count += 1
                continue

            # Write XML result
            xml_result_file = xml_results_dir / f"{input_file.stem}-result.xml"
            xml_result_file.write_text(xml_response)

            # Write JSON result
            json_result_file = json_results_dir / f"{input_file.stem}-result.json"
            json_result_file.write_text(json_response)

            print(f"  ✅ Generated: {xml_result_file.name} and {json_result_file.name}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📁 XML results: {xml_results_dir}")
    print(f"  📁 JSON results: {json_results_dir}")


if __name__ == "__main__":
    main()
