#!/usr/bin/env python3
"""
Helper script to send Telegram messages from within Claude Code SDK agents.

Usage: python3 send_telegram_message.py "Your message here"
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import ssl
from pathlib import Path

def load_env():
    """Load environment variables from .env file."""
    env_vars = {}
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        print(f"ERROR: .env file not found at {env_file}", file=sys.stderr)
        return env_vars

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"ERROR loading .env: {e}", file=sys.stderr)

    return env_vars

def send_message(text):
    """Send a message via Telegram."""
    env_vars = load_env()
    bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
    chat_id = env_vars.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("ERROR: Telegram credentials not configured", file=sys.stderr)
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data)
        ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                print("Message sent successfully")
                return True
            else:
                print(f"Telegram API error: {result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"Error sending message: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 send_telegram_message.py \"Your message here\"", file=sys.stderr)
        return 1

    message = ' '.join(sys.argv[1:])
    success = send_message(message)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
