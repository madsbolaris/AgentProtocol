#!/usr/bin/env python3
"""
Generate golden datasets and LLM recordings for all agent samples.

This script:
1. Reads agent-config.json to discover all samples
2. For each sample, sends test inputs and captures outputs
3. Generates golden datasets in test-data/results/{sample}/
4. Always generates LLM recordings in test-data/llm-recordings/{sample}/

The golden datasets are language-agnostic and used for cross-platform validation
across .NET, Python, and TypeScript implementations.

LLM recording is ALWAYS enabled when generating golden datasets to ensure
deterministic testing. Recordings are saved to test-data/llm-recordings/.

Usage:
    # Generate golden files for all samples (always records LLM)
    python scripts/testgen/generate_golden_datasets.py

    # Generate for specific sample only
    python scripts/testgen/generate_golden_datasets.py --sample echom365

    # Specify custom inputs directory
    python scripts/testgen/generate_golden_datasets.py --inputs test-data/input/

Prerequisites:
- Agent bots must be running on configured ports
- Or use --start-bots to automatically start them (requires implementation)
"""

import json
import sys
import argparse
import httpx
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from lxml import etree
import hashlib
import time
import subprocess
import signal
import atexit
import os


class GoldenDatasetGenerator:
    """Generate golden datasets for agent samples."""

    def __init__(
        self,
        config_path: Path,
        inputs_dir: Path,
        results_dir: Path,
        llm_recordings_dir: Path,
        timeout: int = 30,
        repo_root: Optional[Path] = None
    ):
        """
        Initialize the generator.

        Args:
            config_path: Path to agent-config.json
            inputs_dir: Directory containing input test files
            results_dir: Directory to write results
            llm_recordings_dir: Directory to write LLM recordings
            timeout: HTTP request timeout in seconds
            repo_root: Repository root path

        Note: LLM recording is ALWAYS enabled when generating golden datasets.
        """
        self.config_path = config_path
        self.inputs_dir = inputs_dir
        self.results_dir = results_dir
        self.llm_recordings_dir = llm_recordings_dir
        self.timeout = timeout
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.config = self._load_config()
        self.running_processes = []

        # Register cleanup handler
        atexit.register(self._cleanup_processes)

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse agent-config.json."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        return json.loads(self.config_path.read_text())

    def _cleanup_processes(self):
        """Clean up any running bot processes."""
        for process in self.running_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

    def _find_dotnet_bot_directory(self, sample_name: str) -> Optional[Path]:
        """
        Find the .NET bot directory for a sample.

        Args:
            sample_name: Sample name (e.g., "echo-m365", "basic-m365")

        Returns:
            Path to the .NET bot directory, or None if not found
        """
        # Map sample names to directory names
        sample_dir_map = {
            "echo-m365": "EchoM365",
            "basic-m365": "BasicM365Agent",
            "emoji-chat": "EmojiChatBot"
        }

        dir_name = sample_dir_map.get(sample_name)
        if not dir_name:
            # Try to find by pattern
            samples_dir = self.repo_root / "dotnet" / "samples" / "agents-protocol-abstractions"
            if not samples_dir.exists():
                return None

            # Look for directory matching sample name (case-insensitive)
            for d in samples_dir.iterdir():
                if d.is_dir() and d.name.lower() == sample_name.replace("-", "").lower():
                    return d
            return None

        bot_dir = self.repo_root / "dotnet" / "samples" / "agents-protocol-abstractions" / dir_name
        return bot_dir if bot_dir.exists() else None

    def _start_dotnet_bot(self, sample_name: str, port: int) -> Optional[subprocess.Popen]:
        """
        Start the .NET bot for a sample.

        Args:
            sample_name: Sample name (e.g., "echo-m365")
            port: Port to run the bot on

        Returns:
            Process handle if successful, None otherwise
        """
        bot_dir = self._find_dotnet_bot_directory(sample_name)
        if not bot_dir:
            print(f"  ❌ Could not find .NET bot directory for {sample_name}")
            return None

        print(f"  → Starting .NET bot from: {bot_dir}")
        print(f"  → Bot will run on port: {port}")

        try:
            # Start dotnet run in the bot directory
            env = os.environ.copy()
            env["ASPNETCORE_URLS"] = f"http://localhost:{port}"

            # Disable LLM recordings playback (we want real data for golden datasets)
            env["USE_LLM_RECORDINGS"] = "false"

            # Always enable LLM recording (required for generating golden datasets)
            env["RECORD_LLM"] = "true"
            print(f"  → LLM recording enabled")

            process = subprocess.Popen(
                ["dotnet", "run"],
                cwd=bot_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )

            self.running_processes.append(process)

            # Wait for bot to be ready (check health endpoint)
            print(f"  → Waiting for bot to be ready...")
            max_retries = 30
            retry_delay = 1

            for i in range(max_retries):
                if self._check_bot_health("http://localhost", port):
                    print(f"  ✅ .NET bot is ready on port {port}")
                    return process

                time.sleep(retry_delay)

                # Check if process died
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    print(f"  ❌ Bot process died during startup")
                    print(f"  stdout: {stdout}")
                    print(f"  stderr: {stderr}")
                    return None

            print(f"  ⚠️  Bot did not become ready after {max_retries} seconds")
            return None

        except Exception as e:
            print(f"  ❌ Failed to start .NET bot: {e}")
            return None

    def _extract_sample_name(self, bot_key: str) -> str:
        """
        Extract sample name from bot key.

        Examples:
            "dotnet" -> "echo-m365"
            "python-basic-m365" -> "basic-m365"
            "typescript-emoji-chat" -> "emoji-chat"

        Args:
            bot_key: Bot key from config (e.g., "dotnet", "python-basic-m365")

        Returns:
            Sample name (e.g., "echo-m365", "basic-m365")
        """
        # Remove language prefix
        for lang in ["dotnet-", "python-", "typescript-"]:
            if bot_key.startswith(lang):
                return bot_key[len(lang):]

        # Default to echo-m365 for base language keys
        if bot_key in ["dotnet", "python", "typescript"]:
            return "echo-m365"

        return bot_key

    def _group_bots_by_sample(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group bot configurations by sample name.

        Returns:
            Dict mapping sample name to list of bot configs
            Example: {"echo-m365": [{lang: "dotnet", config: {...}}, ...]}
        """
        samples = {}

        for bot_key, bot_config in self.config.get("bots", {}).items():
            sample_name = self._extract_sample_name(bot_key)

            if sample_name not in samples:
                samples[sample_name] = []

            samples[sample_name].append({
                "key": bot_key,
                "language": bot_key.split("-")[0],  # Extract language prefix
                "config": bot_config
            })

        return samples

    def _check_bot_health(self, base_url: str, port: int) -> bool:
        """
        Check if a bot is running and healthy.

        Args:
            base_url: Bot base URL (e.g., "http://localhost")
            port: Bot port number

        Returns:
            True if bot is healthy, False otherwise
        """
        try:
            url = f"{base_url}:{port}/health"
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    def _xml_to_agent_message(self, xml_content: str) -> Dict[str, Any]:
        """
        Convert XML message to Agent Protocol JSON format.

        Args:
            xml_content: XML message content

        Returns:
            Agent Protocol message dict
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
        message_id = root.get("message-id")
        if message_id:
            message["messageId"] = message_id

        # Add other common attributes
        for attr in ["user-id", "agent-id", "created-at"]:
            value = root.get(attr)
            if value:
                # Convert kebab-case to camelCase
                key = "".join(word.capitalize() if i > 0 else word
                             for i, word in enumerate(attr.split("-")))
                message[key] = value

        # Extract text contents
        for text_elem in root.findall(".//text"):
            content = {
                "kind": "text",
                "text": text_elem.text or ""
            }
            if "audience" in text_elem.attrib:
                content["audience"] = text_elem.attrib["audience"]
            message["contents"].append(content)

        # Extract function call contents
        for call_elem in root.findall(".//function-call"):
            content = {
                "kind": "functionCall",
                "callId": call_elem.get("call-id", ""),
                "name": call_elem.get("name", "")
            }
            # Get arguments from child element
            args_elem = call_elem.find("arguments")
            if args_elem is not None and args_elem.text:
                content["arguments"] = args_elem.text
            message["contents"].append(content)

        # Extract function result contents
        for result_elem in root.findall(".//function-result"):
            content = {
                "kind": "functionResult",
                "callId": result_elem.get("call-id", ""),
                "name": result_elem.get("name", "")
            }
            # Get result from child element or text
            result_text_elem = result_elem.find("result")
            if result_text_elem is not None and result_text_elem.text:
                content["result"] = result_text_elem.text
            elif result_elem.text:
                content["result"] = result_elem.text
            message["contents"].append(content)

        # Extract image contents
        for img_elem in root.findall(".//image"):
            content = {
                "kind": "image",
                "uri": img_elem.get("uri", "")
            }
            if "alt-text" in img_elem.attrib:
                content["altText"] = img_elem.attrib["alt-text"]
            message["contents"].append(content)

        # Extract error contents
        for error_elem in root.findall(".//error"):
            content = {
                "kind": "error"
            }
            if "code" in error_elem.attrib:
                content["code"] = error_elem.attrib["code"]
            msg_elem = error_elem.find("message")
            if msg_elem is not None and msg_elem.text:
                content["message"] = msg_elem.text
            message["contents"].append(content)

        # If no contents, add empty text content
        if not message["contents"]:
            message["contents"].append({"kind": "text", "text": ""})

        return message

    def _send_message_to_bot(
        self,
        bot_url: str,
        message: Dict[str, Any],
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Send a message to a bot and get response.

        Args:
            bot_url: Full bot URL (base_url:port)
            message: Agent Protocol message
            format: Response format ("json" or "xml")

        Returns:
            Bot response as RunWaitResponse
        """
        # Create run request
        run_request = {
            "agentId": message.get("agentId", "agent"),
            "input": [message]
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{bot_url}/runs/wait",
                params={"format": format},
                json=run_request
            )
            response.raise_for_status()

            # Return based on format
            if format == "xml":
                return response.text
            else:
                return response.json()

    def _normalize_xml(self, xml_content: str) -> str:
        """
        Normalize XML for consistent comparison.

        Args:
            xml_content: Raw XML content

        Returns:
            Normalized XML string
        """
        # Parse and pretty-print to normalize
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        return etree.tostring(
            root,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        ).decode('utf-8')

    def _hash_content(self, content: str) -> str:
        """
        Generate SHA-256 hash of content.

        Args:
            content: String content to hash

        Returns:
            Hex-encoded hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_relative_path_from_input(self, input_file: Path) -> Path:
        """
        Get relative path of input file from input base directory.

        Args:
            input_file: Input file path

        Returns:
            Relative path from input base (e.g., evals/basic/01-test.xml -> basic)
        """
        # Determine if this is in evals or threads
        if "evals" in input_file.parts:
            base = self.inputs_dir / "evals"
        elif "threads" in input_file.parts:
            base = self.inputs_dir / "threads"
        else:
            # Fallback: try to get relative to inputs_dir
            try:
                return input_file.relative_to(self.inputs_dir).parent
            except ValueError:
                return Path(".")

        try:
            rel_path = input_file.relative_to(base)
            return rel_path.parent
        except ValueError:
            return Path(".")

    def _save_golden_file(
        self,
        output_dir: Path,
        filename: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        input_file: Optional[Path] = None
    ) -> None:
        """
        Save a golden file with metadata, preserving input directory structure.

        Args:
            output_dir: Base directory to save file
            filename: Output filename
            content: Content to save (string or dict)
            metadata: Optional metadata to include
            input_file: Optional input file path to preserve structure
        """
        # If input_file provided, preserve directory structure
        if input_file:
            rel_dir = self._get_relative_path_from_input(input_file)
            if rel_dir and rel_dir != Path("."):
                output_dir = output_dir / rel_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # For JSON content, save with structure
        if isinstance(content, dict):
            golden_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "content": content,
                "hash": self._hash_content(json.dumps(content, sort_keys=True)),
                "metadata": metadata or {}
            }
            output_file = output_dir / filename
            output_file.write_text(json.dumps(golden_data, indent=2) + "\n")

        # For XML content, save raw with metadata sidecar
        else:
            output_file = output_dir / filename
            output_file.write_text(content)

            # Save metadata sidecar
            if metadata:
                metadata_file = output_dir / f"{filename}.meta.json"
                meta_data = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "hash": self._hash_content(content),
                    "metadata": metadata
                }
                metadata_file.write_text(json.dumps(meta_data, indent=2) + "\n")

    def generate_for_sample(
        self,
        sample_name: str,
        bot_configs: List[Dict[str, Any]],
        input_files: List[Path]
    ) -> None:
        """
        Generate golden datasets for a specific sample.

        The .NET implementation is used as the canonical source for golden datasets.
        All other language implementations must conform to the .NET output.

        Args:
            sample_name: Sample name (e.g., "echo-m365")
            bot_configs: List of bot configurations for this sample
            input_files: List of input files to test
        """
        print(f"\n{'='*70}")
        print(f"Generating golden datasets for: {sample_name}")
        print(f"{'='*70}\n")

        # Clean up old results and recordings for this sample
        sample_results_dir = self.results_dir / sample_name
        sample_recordings_dir = self.llm_recordings_dir / sample_name

        if sample_results_dir.exists():
            print(f"🧹 Cleaning old results for {sample_name}...")
            import shutil
            for subdir in ["json", "xml"]:
                target_dir = sample_results_dir / subdir
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                    print(f"  ✅ Cleared: {target_dir}")

        if sample_recordings_dir.exists():
            print(f"🧹 Cleaning old LLM recordings for {sample_name}...")
            import shutil
            shutil.rmtree(sample_recordings_dir)
            print(f"  ✅ Cleared: {sample_recordings_dir}")

        print()

        # Find the .NET bot configuration
        dotnet_bot = None
        for bot in bot_configs:
            if bot["language"] == "dotnet":
                dotnet_bot = bot
                break

        if not dotnet_bot:
            print(f"❌ No .NET bot configuration found for {sample_name}")
            print("   The .NET implementation is required as the canonical source.")
            return

        config = dotnet_bot["config"]
        port = config["port"]
        bot_url = f"{config['baseUrl']}:{port}"

        print(f"Using .NET implementation as canonical source")
        print(f"  → {config['name']}")
        print(f"  → {bot_url}\n")

        # Check if bot is already running
        bot_process = None
        if not self._check_bot_health(config['baseUrl'], port):
            print(f"Bot not running, starting automatically...")
            bot_process = self._start_dotnet_bot(sample_name, port)
            if not bot_process:
                print(f"\n❌ Failed to start .NET bot for {sample_name}")
                return
            print()
        else:
            print(f"  ✅ .NET bot is already running\n")

        # Setup output directories
        sample_results_dir = self.results_dir / sample_name
        json_dir = sample_results_dir / "json"
        xml_dir = sample_results_dir / "xml"

        print(f"Generating golden files from .NET implementation...\n")

        success_count = 0
        error_count = 0

        for input_file in input_files:
            try:
                print(f"Processing: {input_file.name}")

                # Read XML input
                xml_content = input_file.read_text()

                # Convert to Agent Protocol message
                message = self._xml_to_agent_message(xml_content)

                # Send to bot and get JSON response
                print(f"  → Sending to {bot_url}...")
                json_response = self._send_message_to_bot(bot_url, message, format="json")

                # Save JSON golden file
                json_filename = f"{input_file.stem}-result.json"
                self._save_golden_file(
                    json_dir,
                    json_filename,
                    json_response,
                    metadata={
                        "input_file": input_file.name,
                        "sample": sample_name,
                        "generator": "dotnet",
                        "canonical": True
                    },
                    input_file=input_file
                )
                print(f"  ✅ Saved: {json_filename}")

                # Optionally get XML response
                # Note: Some bots may not support XML format parameter
                try:
                    xml_response = self._send_message_to_bot(bot_url, message, format="xml")
                    # xml_response should be raw XML text now
                    xml_content_out = xml_response

                    xml_filename = f"{input_file.stem}-result.xml"
                    self._save_golden_file(
                        xml_dir,
                        xml_filename,
                        self._normalize_xml(xml_content_out),
                        metadata={
                            "input_file": input_file.name,
                            "sample": sample_name,
                            "generator": "dotnet",
                            "canonical": True
                        },
                        input_file=input_file
                    )
                    print(f"  ✅ Saved XML: {xml_filename}")
                except Exception as e:
                    print(f"  ⚠️  XML format not supported or failed: {e}")

                success_count += 1

                # Small delay to avoid overwhelming the bot
                time.sleep(0.1)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                error_count += 1

        # Stop bot if we started it
        if bot_process:
            print(f"\nStopping .NET bot...")
            try:
                bot_process.terminate()
                bot_process.wait(timeout=5)
                print(f"  ✅ Bot stopped")
            except Exception as e:
                print(f"  ⚠️  Failed to stop bot cleanly: {e}")
                try:
                    bot_process.kill()
                except Exception:
                    pass

        print(f"\n{'='*70}")
        print(f"Summary for {sample_name}:")
        print(f"  ✅ Success: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  📁 Results: {sample_results_dir}")
        print(f"  🎯 Source: .NET (canonical implementation)")
        print(f"{'='*70}")

    def generate_all(self, sample_filter: Optional[str] = None, dry_run: bool = False) -> None:
        """
        Generate golden datasets for all samples.

        Args:
            sample_filter: Optional sample name to generate for (e.g., "echom365")
            dry_run: If True, show what would be generated without writing files
        """
        samples = self._group_bots_by_sample()

        if sample_filter:
            if sample_filter not in samples:
                print(f"❌ Sample '{sample_filter}' not found in config")
                print(f"Available samples: {', '.join(samples.keys())}")
                sys.exit(1)
            samples = {sample_filter: samples[sample_filter]}

        # Get all input files recursively (excludes invalid subdirectory)
        all_input_files = sorted(self.inputs_dir.rglob("*.xml"))
        input_files = [f for f in all_input_files if "invalid" not in f.parts]
        if not input_files:
            print(f"❌ No input files found in {self.inputs_dir}")
            sys.exit(1)

        print(f"Found {len(input_files)} input files in {self.inputs_dir}")

        # Dry-run mode: show what would be generated without writing files
        if dry_run:
            print(f"\n{'='*70}")
            print("🔍 DRY RUN - Preview of golden dataset generation")
            print(f"{'='*70}\n")

            for sample_name, bot_configs in samples.items():
                print(f"Sample: {sample_name}")
                dotnet_bot = next((b for b in bot_configs if b["language"] == "dotnet"), None)
                if dotnet_bot:
                    config = dotnet_bot["config"]
                    print(f"  → Would use .NET bot at: {config['baseUrl']}:{config['port']}")
                else:
                    print(f"  → ⚠️  No .NET bot found (required)")

                print(f"  → Would process {len(input_files)} input files")
                print(f"  → Would generate:")
                print(f"      - {len(input_files)} JSON golden files")
                print(f"      - {len(input_files)} XML golden files")
                print(f"      - LLM recordings")
                print(f"  → Output directories:")
                print(f"      - {self.results_dir / sample_name / 'json'}")
                print(f"      - {self.results_dir / sample_name / 'xml'}")
                print(f"      - {self.llm_recordings_dir / sample_name}")
                print()

            print("🔍 Dry run complete - no files were written")
            print("   Run without --dry-run to generate files")
            return

        # Generate for each sample
        for sample_name, bot_configs in samples.items():
            self.generate_for_sample(sample_name, bot_configs, input_files)

        print(f"\n{'='*70}")
        print("✅ Golden dataset generation complete!")
        print(f"{'='*70}")
        print(f"\nResults saved to: {self.results_dir}")
        print(f"LLM recordings saved to: {self.llm_recordings_dir}")
        print(f"\n🎯 Golden files generated from .NET (canonical implementation)")
        print("   All other language implementations must conform to these outputs.")
        print(f"📹 LLM interactions recorded for mock replay in tests")
        print("\nNext steps:")
        print("1. Review generated golden files")
        print("2. Run tests for Python and TypeScript implementations:")
        print("   SAMPLE_NAME=echom365 pytest python/microsoft-agents-protocol-xml/tests/")
        print("   SAMPLE_NAME=echom365 npm test")
        print("3. If tests fail, fix Python/TypeScript to match .NET output")
        print("4. Delete deprecated directories:")
        print(f"   ./scripts/cleanup_deprecated_results.sh")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate golden datasets for agent samples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for all samples (always records LLM)
  python scripts/testgen/generate_golden_datasets.py

  # Generate for specific sample
  python scripts/testgen/generate_golden_datasets.py --sample echom365

  # Use custom paths
  python scripts/testgen/generate_golden_datasets.py --inputs test-data/input --results test-data/results

Note: LLM recording is ALWAYS enabled. Recordings are saved to test-data/llm-recordings/.
        """
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to agent-config.json (default: ./agent-config.json)"
    )
    parser.add_argument(
        "--inputs",
        type=Path,
        default=None,
        help="Directory containing input test files (default: test-data/input)"
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=None,
        help="Directory to write results (default: test-data/results)"
    )
    parser.add_argument(
        "--llm-recordings",
        type=Path,
        default=None,
        help="Directory to write LLM recordings (default: test-data/llm-recordings)"
    )
    parser.add_argument(
        "--sample",
        type=str,
        help="Generate only for specific sample (e.g., 'echom365', 'basic-m365')"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP request timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files or starting bots"
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent
    config_path = args.config or repo_root / "agent-config.json"
    inputs_dir = args.inputs or repo_root / "test-data" / "input"
    results_dir = args.results or repo_root / "test-data" / "results"
    llm_recordings_dir = args.llm_recordings or repo_root / "test-data" / "llm-recordings"

    # Create generator
    generator = GoldenDatasetGenerator(
        config_path=config_path,
        inputs_dir=inputs_dir,
        results_dir=results_dir,
        llm_recordings_dir=llm_recordings_dir,
        timeout=args.timeout,
        repo_root=repo_root
    )

    # Generate
    generator.generate_all(sample_filter=args.sample, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
