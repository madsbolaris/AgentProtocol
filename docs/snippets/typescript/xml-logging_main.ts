import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { promises as fs } from 'fs';

// Create client with automatic logging enabled
const client = new AgentProtocolClient({
  baseUrl: "http://localhost:5000",
  enableLogging: true  // That's it! Auto-saves to logs/conversations/
});

// Have a conversation - it's automatically logged
const conversation = client.createConversation();
const response = await conversation.send("What's the weather in Seattle?");
console.log(`Agent: ${response}`);

// Done! Conversation automatically saved to:
// logs/conversations/{threadId}.xml

// Or manually save to a custom location
const xml = conversation.toString();
await fs.writeFile('my-conversation.xml', xml, 'utf-8');
console.log(`Saved conversation XML (${xml.length} bytes)`);
