#!/usr/bin/env python3
"""
Convert existing XML golden files to JSON format golden files.

This script reads XML result files and converts them to JSON RunWaitResponse format.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from lxml import etree


def xml_thread_to_json_run(xml_content: str, input_file: Path) -> dict:
    """Convert XML Thread to JSON RunWaitResponse format."""
    root = etree.fromstring(xml_content.encode('utf-8'))

    # Extract thread attributes
    thread_id = root.get("thread-id", f"thread_{uuid.uuid4().hex[:16]}")
    status = root.get("status", "active")
    created_at = root.get("created-at", datetime.utcnow().isoformat() + "Z")

    # Extract output messages from thread children
    output_messages = []
    for msg_elem in root:
        role = msg_elem.tag
        message = {
            "role": role,
            "contents": []
        }

        # Add message-id if present
        if "message-id" in msg_elem.attrib:
            message["messageId"] = msg_elem.attrib["message-id"]

        # Extract contents
        for content_elem in msg_elem:
            if content_elem.tag == "text":
                content = {
                    "kind": "text",
                    "text": content_elem.text or ""
                }
                if "audience" in content_elem.attrib:
                    content["audience"] = content_elem.attrib["audience"]
                message["contents"].append(content)

        # Only add if has contents
        if message["contents"]:
            output_messages.append(message)

    # Create RunWaitResponse
    run_id = f"run_{uuid.uuid4().hex[:16]}"
    run_response = {
        "runId": run_id,
        "agentId": "echo-agent",
        "threadId": thread_id,
        "status": "completed",
        "input": [],  # Input not preserved in XML results
        "output": output_messages,
        "createdAt": created_at,
        "completedAt": created_at
    }

    return run_response


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    xml_dir = repo_root / "test-data" / "results" / "echobot" / "xml"
    json_dir = repo_root / "test-data" / "results" / "echobot" / "json"

    # Ensure output directory exists
    json_dir.mkdir(parents=True, exist_ok=True)

    # Get all XML result files
    xml_files = sorted(xml_dir.glob("*-result.xml"))

    if not xml_files:
        print(f"❌ No XML result files found in {xml_dir}")
        return

    print(f"Found {len(xml_files)} XML result files\n")

    # Convert each XML file to JSON
    for xml_file in xml_files:
        try:
            print(f"Converting {xml_file.name}...")

            # Read XML content
            xml_content = xml_file.read_text()

            # Convert to JSON format
            json_data = xml_thread_to_json_run(xml_content, xml_file)

            # Generate output filename
            json_filename = xml_file.name.replace(".xml", ".json")
            json_file_path = json_dir / json_filename

            # Write JSON with pretty printing
            json_file_path.write_text(json.dumps(json_data, indent=2) + "\n")

            print(f"  ✅ Generated {json_filename}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n✅ Converted {len(xml_files)} files to JSON format in {json_dir}")


if __name__ == "__main__":
    main()
