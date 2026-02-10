import { AgentProtocolClient } from '@microsoft/agents-protocol';

// Create a client
const client = new AgentProtocolClient({
  baseUrl: 'https://agents.example.com/v1'
});

// Create and execute a run
const run = {
  agentId: 'agent_001',
  input: [
    {
      role: 'user',
      contents: [
        { type: 'text', text: 'Hello! Can you help me?' }
      ]
    }
  ]
};

// Wait for completion
const result = await client.runs.createAndWait(run);

console.log(`Status: ${result.status}`);
console.log(`Messages: ${result.messages.length}`);
