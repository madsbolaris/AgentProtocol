import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { promises as fs } from 'fs';

// Have a conversation via Client SDK
const client = new AgentProtocolClient({ baseUrl: "http://localhost:5000" });
const conversation = client.createConversation();
await conversation.send("Book a flight to Seattle");
await conversation.send("The first one");

// Export conversation instantly with toString()
const xml = conversation.toString();

// Save or send to developer
await fs.writeFile('customer-issue-456.xml', xml, 'utf-8');
console.log("Exported conversation to customer-issue-456.xml");
