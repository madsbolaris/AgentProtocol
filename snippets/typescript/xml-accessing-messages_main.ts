import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

const client = new AgentProtocolClient({ baseUrl: "http://localhost:5000" });
const conversation = client.createConversation();
await conversation.send("Hello!");
await conversation.send("How are you?");

// Access cached messages (no HTTP call)
const messages = conversation.messages;
console.log(`Conversation has ${messages.length} messages`);

// Or convert to XML instantly
const xml = conversation.toString();
console.log(xml);
