# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ChannelInfo:
    """
    Channel Information
@usage
Use Cases:
- Teams Integration: channelId="msteams", externalConversationId="19:meeting@thread.v2"
- Slack Integration: channelId="slack", externalConversationId="C123456", workspaceId="T123456"
- Discord Integration: channelId="discord", externalConversationId="123456789012345678"
- Web Chat: channelId="webchat" (no external ID needed)
    """
    # Channel identifier (platform type).

STANDARD VALUES:
- "msteams": Microsoft Teams
- "slack": Slack
- "discord": Discord
- "webchat": Web chat widget
- "sms": SMS/text messaging
- "email": Email
- "whatsapp": WhatsApp
- "directline": Bot Framework Direct Line
- "custom": Custom channel integration

PATTERN: Like Bot Framework Activity.channelId
    channel_id: str
    # External conversation ID from the channel.
OPTIONAL: Channel's native conversation/thread identifier

EXAMPLES:
- Teams: "19:meeting_abc@thread.v2" (conversation ID)
- Slack: "C123456" (channel ID)
- Discord: "123456789012345678" (channel ID)

PURPOSE: Correlation and bidirectional sync
    external_conversation_id: Optional[str] = None
    # External tenant/workspace/server ID.
OPTIONAL: Multi-tenant or workspace-scoped channels

EXAMPLES:
- Teams: Tenant ID (Entra tenant)
- Slack: "T123456" (workspace ID)
- Discord: Server ID

PURPOSE: Isolate conversations by tenant/workspace
    external_tenant_id: Optional[str] = None
    # Channel-specific service URL.
OPTIONAL: Base URL for channel-specific APIs

EXAMPLES:
- Teams: "https://smba.trafficmanager.net/amer/" (Bot Framework service URL)
- Slack: "https://slack.com/api" (Slack API URL)

PURPOSE: Dynamic routing for different channel regions/deployments
    service_url: Optional[str] = None
    # Channel-specific metadata.
FLEXIBLE: Additional channel-specific context

EXAMPLES:
- Teams: { "meetingId": "...", "channelId": "..." }
- Slack: { "teamName": "...", "channelName": "..." }
- Discord: { "guildName": "...", "channelName": "..." }
    metadata: Optional[Dict[str, Any]] = None
