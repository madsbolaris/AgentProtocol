# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os.path as path
import re
import sys
import traceback
from dotenv import load_dotenv

from os import environ
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env
import asyncio
from datetime import datetime, timedelta

load_dotenv()

# 🔧 FIX: Create storage with cleanup to prevent unbounded memory growth
STORAGE = MemoryStorage()

# Track storage access times for cleanup
_storage_access_times = {}
_storage_max_age = timedelta(hours=1)  # Clean up conversations older than 1 hour
_last_cleanup = datetime.now()

async def _cleanup_old_storage():
    """Remove old conversation data from storage to prevent memory leaks."""
    global _last_cleanup, _storage_access_times

    now = datetime.now()
    # Only cleanup every 5 minutes
    if now - _last_cleanup < timedelta(minutes=5):
        return

    _last_cleanup = now
    cutoff = now - _storage_max_age

    # Find keys to delete
    keys_to_delete = [
        key for key, access_time in _storage_access_times.items()
        if access_time < cutoff
    ]

    if keys_to_delete:
        try:
            await STORAGE.delete(keys_to_delete)
            for key in keys_to_delete:
                del _storage_access_times[key]
            print(f"Cleaned up {len(keys_to_delete)} old conversation states")
        except Exception as e:
            print(f"Error during storage cleanup: {e}")

def _track_storage_access(key: str):
    """Track when storage keys are accessed."""
    _storage_access_times[key] = datetime.now()

# Force anonymous mode - no authentication for local development
CONNECTION_MANAGER = None
ADAPTER = CloudAdapter()
AUTHORIZATION = None

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION
)


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity(
        "Welcome to the empty agent! "
        "This agent is designed to be a starting point for your own agent development."
    )
    return True


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    # 🔧 Periodically clean up old storage to prevent memory leaks
    await _cleanup_old_storage()

    # Track this conversation's access time
    if hasattr(context.activity, "conversation") and context.activity.conversation:
        conv_id = context.activity.conversation.id
        if conv_id:
            _track_storage_access(conv_id)

    # Extract role from channelData (default to "user" if not present)
    role = "user"
    if hasattr(context.activity, "channel_data") and isinstance(context.activity.channel_data, dict):
        role = context.activity.channel_data.get("role", "user")

    # Only respond to user messages
    if role != "user":
        return

    await context.send_activity(f"you said: {context.activity.text}")


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
