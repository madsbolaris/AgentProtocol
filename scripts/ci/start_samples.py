#!/usr/bin/env python3
"""
Start agent samples and chat UI for testing.

Supports:
- echo-m365 (Python, .NET, TypeScript)
- basic-m365 (Python, .NET, TypeScript)
- emoji-chat (Python, .NET, TypeScript)

Optionally starts the chat UI for interaction.

Environment:
- Automatically loads .env file from repo root
- No manual environment variable setup required
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or run: pip install -r scripts/requirements.txt")
    sys.exit(1)


class SampleManager:
    """Manage agent sample processes and chat UI."""

    def __init__(self, repo_root: Path, config: Dict):
        self.repo_root = repo_root
        self.config = config
        self.processes: List[subprocess.Popen] = []
        self.log_dir = repo_root / ".logs"
        self.log_dir.mkdir(exist_ok=True)

        # Register cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals."""
        print()
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Stop all running processes."""
        if self.processes:
            print("\nStopping all processes...")
            for proc in self.processes:
                try:
                    proc.terminate()
                except:
                    pass

            # Wait for graceful shutdown
            time.sleep(2)

            # Force kill if needed
            for proc in self.processes:
                try:
                    if proc.poll() is None:
                        proc.kill()
                except:
                    pass

            print("All processes stopped.")

    def _get_sample_config(self, sample: str, language: str) -> Optional[Dict]:
        """Get configuration for a sample."""
        # Map sample names to config keys
        key_map = {
            "echo-m365": {
                "python": "python",
                "dotnet": "dotnet",
                "typescript": "typescript"
            },
            "basic-m365": {
                "python": "python-basic-m365",
                "dotnet": "dotnet-basic-m365",
                "typescript": "typescript-basic-m365"
            },
            "emoji-chat": {
                "python": "python-emoji-chat",
                "dotnet": "dotnet-emoji-chat",
                "typescript": "typescript-emoji-chat"
            }
        }

        if sample not in key_map or language not in key_map[sample]:
            return None

        bot_key = key_map[sample][language]
        return self.config.get("bots", {}).get(bot_key)

    def _get_sample_dir(self, sample: str, language: str) -> Optional[Path]:
        """Get sample directory path."""
        sample_map = {
            "python": {
                "echo-m365": "python/samples/agents/echo-m365",
                "basic-m365": "python/samples/agents/basic-m365",
                "emoji-chat": "python/samples/agents/emoji-chat"
            },
            "dotnet": {
                "echo-m365": "dotnet/samples/agents/EchoM365",
                "basic-m365": "dotnet/samples/agents/BasicM365Agent",
                "emoji-chat": "dotnet/samples/agents/EmojiChatBot"
            },
            "typescript": {
                "echo-m365": "typescript/samples/agents/echo-m365",
                "basic-m365": "typescript/samples/agents/basic-m365",
                "emoji-chat": "typescript/samples/agents/emoji-chat"
            }
        }

        if language not in sample_map or sample not in sample_map[language]:
            return None

        sample_dir = self.repo_root / sample_map[language][sample]
        return sample_dir if sample_dir.exists() else None

    def start_agent(self, sample: str, language: str) -> bool:
        """Start an agent sample."""
        bot_config = self._get_sample_config(sample, language)
        sample_dir = self._get_sample_dir(sample, language)

        if not bot_config:
            print(f"⚠️  Configuration not found for {sample} ({language})")
            return False

        if not sample_dir:
            print(f"⚠️  Sample directory not found for {sample} ({language})")
            return False

        port = bot_config["port"]
        name = bot_config["name"]

        print(f"Starting {name} on port {port}...")

        # Build command based on language
        if language == "python":
            cmd = [sys.executable, "-m", "src.main"]
        elif language == "dotnet":
            cmd = ["dotnet", "run"]
        elif language == "typescript":
            cmd = ["npm", "start"]
        else:
            return False

        # Set environment
        env = {"PORT": str(port), **subprocess.os.environ.copy()}

        # For Python, add protocol packages to PYTHONPATH to support namespace packages
        if language == "python":
            protocol_pkg = self.repo_root / "python" / "microsoft-agents-protocol"
            existing_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = f"{protocol_pkg}:{existing_path}" if existing_path else str(protocol_pkg)

        # Start process
        log_file = self.log_dir / f"{sample}-{language}.log"
        with open(log_file, 'w') as log:
            proc = subprocess.Popen(
                cmd,
                cwd=sample_dir,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

        self.processes.append(proc)
        print(f"  Started with PID {proc.pid}, logging to {log_file}")
        return True

    def start_chat_ui(self) -> bool:
        """Start the chat UI (demos/agent-demo.html)."""
        demos_dir = self.repo_root / "demos"
        start_script = demos_dir / "start-demo.js"

        if not start_script.exists():
            print("⚠️  Chat UI not found")
            print(f"   Expected: {start_script}")
            return False

        print(f"\nStarting Chat UI from {demos_dir}...")

        # Start demo server with Node.js
        log_file = self.log_dir / "chat-ui.log"
        with open(log_file, 'w') as log:
            proc = subprocess.Popen(
                ["node", "start-demo.js"],
                cwd=demos_dir,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

        self.processes.append(proc)
        print(f"  Chat UI started with PID {proc.pid}")
        print(f"  Access at: http://localhost:3000")
        print(f"  Log: {log_file}")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start agent samples with optional chat UI")
    parser.add_argument(
        "sample",
        choices=["echo-m365", "basic-m365", "emoji-chat", "all"],
        help="Sample to start (or 'all')"
    )
    parser.add_argument(
        "--lang",
        choices=["python", "dotnet", "typescript", "all"],
        default="all",
        help="Language to start (default: all)"
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Also start the chat UI"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for processes (return immediately)"
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    # Load .env file from repo root if it exists
    env_file = repo_root / ".env"
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}")
        load_dotenv(env_file)

        # Verify LLM configuration
        if os.getenv("FOUNDRY_ENDPOINT"):
            print(f"   ✓ LLM configured: {os.getenv('FOUNDRY_MODEL_DEPLOYMENT', 'gpt-5-nano')}")
        elif os.getenv("USE_LLM_RECORDINGS") == "true":
            print("   ✓ Using LLM recordings (test mode)")
        else:
            print("   ⚠️  No LLM credentials found in .env")
            print("      Samples requiring LLM may fail")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("   Create one from .env.example for LLM support")

    # Load config
    config_file = repo_root / "agent-config.json"
    if not config_file.exists():
        print(f"❌ Error: agent-config.json not found at {config_file}")
        sys.exit(1)

    config = json.loads(config_file.read_text())

    # Create manager
    manager = SampleManager(repo_root, config)

    print("╔" + "=" * 56 + "╗")
    print("║          Starting Agent Samples                        ║")
    print("╚" + "=" * 56 + "╝")
    print()

    # Determine what to start
    samples = ["echo-m365", "basic-m365", "emoji-chat"] if args.sample == "all" else [args.sample]
    languages = ["python", "dotnet", "typescript"] if args.lang == "all" else [args.lang]

    # Start agents
    started_count = 0
    for sample in samples:
        for lang in languages:
            if manager.start_agent(sample, lang):
                started_count += 1
            time.sleep(0.5)  # Stagger starts

    # Start chat UI if requested
    if args.ui:
        print()
        manager.start_chat_ui()

    print()
    print(f"✅ Started {started_count} agent(s)")
    print(f"📂 Logs: {manager.log_dir}/")
    print()

    if not args.no_wait:
        print("Press Ctrl+C to stop all processes")
        print()
        try:
            # Keep running
            while True:
                time.sleep(1)
                # Check if any process died
                for proc in manager.processes:
                    if proc.poll() is not None:
                        print(f"\n⚠️  Process {proc.pid} exited")
        except KeyboardInterrupt:
            pass

    manager.cleanup()


if __name__ == "__main__":
    main()
