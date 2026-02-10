# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Out-of-band message publisher for sending messages outside normal request flow."""

from typing import Optional, Any
import logging


class OutOfBandPublisher:
    """
    Publisher for sending out-of-band messages to threads.

    Out-of-band messages are sent from background tasks, webhooks,
    or scheduled jobs - not in response to user messages.
    """

    def __init__(self, queue_adapter: Optional[Any] = None):
        """
        Initialize the out-of-band publisher.

        Args:
            queue_adapter: Queue adapter for enqueuing messages.
        """
        self._queue_adapter = queue_adapter
        self._logger = logging.getLogger(__name__)

    async def send_to_thread_async(
        self,
        thread_id: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Send a message to a specific thread.

        Args:
            thread_id: The thread ID to send to.
            content: The message content.
            metadata: Optional metadata.

        Example:
            ```python
            publisher = agent_host.get_publisher()
            await publisher.send_to_thread_async(
                "thread_abc123",
                "This is your daily reminder!"
            )
            ```
        """
        message = {
            "thread_id": thread_id,
            "content": content,
            "metadata": metadata or {},
            "type": "out_of_band",
        }

        if self._queue_adapter:
            await self._queue_adapter.enqueue_async(message)
        else:
            self._logger.warning(
                f"No queue adapter configured, message not sent: {content}"
            )

    async def send_to_multiple_threads_async(
        self,
        thread_ids: list[str],
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Send a message to multiple threads.

        Args:
            thread_ids: List of thread IDs to send to.
            content: The message content.
            metadata: Optional metadata.

        Example:
            ```python
            await publisher.send_to_multiple_threads_async(
                ["thread_1", "thread_2", "thread_3"],
                "System maintenance in 10 minutes"
            )
            ```
        """
        for thread_id in thread_ids:
            await self.send_to_thread_async(thread_id, content, metadata)
