import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { MessageDeserializer } from '@microsoft/agents-xml';
import { ChatMessage, TextContent } from '@microsoft/agents';
import { promises as fs } from 'fs';

// Load customer's conversation from XML
const xml = await fs.readFile('customer-issue-456.xml', 'utf-8');
const deserializer = new MessageDeserializer();
const messages = deserializer.deserializeMany(xml);

// Extract thread ID if it exists (for resuming context)
const threadId = extractThreadId(xml); // Parse thread-id attribute

// Replay through agent using Client SDK
const client = new AgentProtocolClient({ baseUrl: "http://localhost:5000" });

for (const message of messages) {
  // Use type guard instead of type assertion
  if (message.role === 'user') {
    console.log("\n--- User Message ---");

    // Use type guard for text content
    const textContent = message.contents.find((c): c is TextContent => c.kind === 'text');
    if (!textContent) continue;

    const userText = textContent.text;
    console.log(`User: ${userText}`);

    // Re-run through agent via Client SDK
    const conversation = threadId
      ? client.resumeConversation(threadId)
      : client.createConversation();

    const start = Date.now();
    const response = await conversation.send(userText);
    const elapsed = Date.now() - start;

    console.log(`Response time: ${elapsed}ms`);
    console.log(`Agent: ${response}`);
  }
}

console.log("\n✓ Replay complete - verify behavior matches expectations");

function extractThreadId(xml: string): string | undefined {
  // Simple regex or XML parsing
  return undefined; // Placeholder
}
