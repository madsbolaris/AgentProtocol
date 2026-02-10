from microsoft.agents.protocol import AgentProtocolClient
import asyncio

async def main():
    # Create a client
    async with AgentProtocolClient.from_url("https://agents.example.com/v1") as client:
        # Create and execute a run
        run = {
            "agentId": "agent_001",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"type": "text", "text": "Hello! Can you help me?"}
                    ]
                }
            ]
        }

        # Wait for completion
        result = await client.runs.create_and_wait(run)

        print(f"Status: {result['status']}")
        print(f"Messages: {len(result['messages'])}")

asyncio.run(main())
