# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Type definitions for Emoji Chat Bot."""

from dataclasses import dataclass, field


@dataclass
class AddEmojiResult:
    """Result returned by add_emoji_to_message function."""

    success: bool
    message_id: str
    emoji: str
    message: str


@dataclass
class EmojiSuggestion:
    """Result returned by suggest_emoji function."""

    message_text: str
    suggested_emojis: list[str] = field(default_factory=list)
