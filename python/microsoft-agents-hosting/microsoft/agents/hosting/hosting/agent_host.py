# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Agent host implementation."""

import logging
from typing import Any, Optional

from ..core import (
    IStateStore,
    IQueueAdapter,
    ConcurrencyConfig,
    RetryConfig,
    TelemetryConfig,
    LoggingConfig,
    SandboxConfig,
)
from ..builder.agent_builder import AgentConfiguration
from .out_of_band_publisher import OutOfBandPublisher


class AgentHost:
    """Agent host for running agents."""

    def __init__(
        self,
        agents: list[AgentConfiguration],
        services: dict[type, Any],
        production_defaults: bool,
        concurrency_config: ConcurrencyConfig,
        retry_config: RetryConfig,
        telemetry_config: Optional[TelemetryConfig],
        logging_config: LoggingConfig,
        sandbox_config: SandboxConfig,
        state_store: IStateStore,
        queue_adapter: Optional[IQueueAdapter],
    ):
        """
        Initialize the agent host.

        Args:
            agents: List of agent configurations.
            services: Service container.
            production_defaults: Whether production defaults are enabled.
            concurrency_config: Concurrency configuration.
            retry_config: Retry configuration.
            telemetry_config: Telemetry configuration.
            logging_config: Logging configuration.
            sandbox_config: Sandbox configuration.
            state_store: State store implementation.
            queue_adapter: Queue adapter implementation.
        """
        self._agents = agents
        self._services = services
        self._production_defaults = production_defaults
        self._concurrency_config = concurrency_config
        self._retry_config = retry_config
        self._telemetry_config = telemetry_config
        self._logging_config = logging_config
        self._sandbox_config = sandbox_config
        self._state_store = state_store
        self._queue_adapter = queue_adapter
        self._logger = logging.getLogger(__name__)
        self._publisher = OutOfBandPublisher(queue_adapter)

    def get_publisher(self) -> OutOfBandPublisher:
        """
        Get the out-of-band message publisher.

        Returns:
            The out-of-band publisher instance.

        Example:
            ```python
            publisher = agent_host.get_publisher()
            await publisher.send_to_thread_async("thread_123", "Hello!")
            ```
        """
        return self._publisher

    async def process_message(self, message: str, thread_id: Optional[str] = None) -> Any:
        """
        Process a message (for testing).

        Args:
            message: The message to process.
            thread_id: Optional thread ID.

        Returns:
            The response.
        """
        # Simple implementation for testing
        if not self._agents:
            return {"text": "No agents configured"}

        # TODO: Implement full message processing with LLM
        return {"text": f"Echo: {message}"}

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Run the agent host server.

        Args:
            host: Host to bind to.
            port: Port to bind to.

        Example:
            ```python
            agent_host = AgentHostBuilder().add_default_agent(...).build()
            agent_host.run()
            ```
        """
        import asyncio

        asyncio.run(self.run_async(host, port))

    async def run_async(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Run the agent host server asynchronously.

        Args:
            host: Host to bind to.
            port: Port to bind to.
        """
        self._logger.info(f"Starting agent host on {host}:{port}")
        self._logger.info(f"Agents configured: {len(self._agents)}")
        self._logger.info(f"Production defaults: {self._production_defaults}")

        # Simple HTTP server implementation for development/testing
        from aiohttp import web
        import json

        async def health_handler(request):
            """Health check endpoint."""
            from datetime import datetime
            return web.json_response({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agents": len(self._agents)
            })

        async def message_handler(request):
            """Handle incoming messages."""
            try:
                data = await request.json()
                message = data.get("text", "")
                thread_id = data.get("thread_id")

                response = await self.process_message(message, thread_id)
                return web.json_response(response)
            except Exception as e:
                self._logger.error(f"Error processing message: {e}")
                return web.json_response({"error": str(e)}, status=500)

        app = web.Application()
        app.router.add_get('/health', health_handler)
        app.router.add_post('/api/messages', message_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)

        try:
            await site.start()
            self._logger.info("Agent host is running. Press Ctrl+C to stop.")

            # Keep running until interrupted
            import asyncio
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            self._logger.info("Shutting down agent host...")
        finally:
            await runner.cleanup()
            await self._state_store.close_async()
            if self._queue_adapter:
                await self._queue_adapter.close_async()
