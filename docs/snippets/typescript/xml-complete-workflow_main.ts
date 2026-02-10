import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { MessageDeserializer } from '@microsoft/agents-xml';
import { ThreadValidator } from '@microsoft/agents-validation';
import { ChatMessage, TextContent } from '@microsoft/agents';
import { promises as fs } from 'fs';

class ProductionAgentService {
  private client: AgentProtocolClient;
  private deserializer = new MessageDeserializer();
  private validator = new ThreadValidator();

  constructor(endpoint: string) {
    // Enable automatic logging
    this.client = new AgentProtocolClient({
      baseUrl: endpoint,
      enableLogging: true,
      logDirectory: "logs/production"
    });
  }

  // 1. Have conversations via Client SDK (auto-logged)
  async chat(userInput: string, threadId?: string): Promise<string> {
    const conversation = threadId
      ? this.client.resumeConversation(threadId)
      : this.client.createConversation();

    return await conversation.send(userInput);
  }

  // 2. Export conversation XML instantly
  exportConversation(threadId: string): string {
    const conversation = this.client.resumeConversation(threadId);
    return conversation.toString();  // Instant XML export
  }

  // 3. Run tests from XML eval files
  async runTest(evalFile: string): Promise<boolean> {
    const xml = await fs.readFile(evalFile, 'utf-8');
    const testMessages = this.deserializer.deserializeMany(xml);

    // Use type guard
    const userMsg = testMessages.find((m): m is ChatMessage & { role: 'user' } => m.role === 'user');
    if (!userMsg) return false;

    const conversation = this.client.createConversation();

    // Use type guard for text content
    const textContent = userMsg.contents.find((c): c is TextContent => c.kind === 'text');
    if (!textContent) return false;

    await conversation.send(textContent.text);

    // Use local message cache (no HTTP call)
    const actual = conversation.messages;

    return this.validator.validate(actual, testMessages).isValid;
  }

  // 4. Replay logged conversations for debugging
  async replay(logFile: string): Promise<void> {
    const xml = await fs.readFile(logFile, 'utf-8');
    const messages = this.deserializer.deserializeMany(xml);

    const conversation = this.client.createConversation();

    for (const msg of messages) {
      if (msg.role === 'user') {
        // Use type guard
        const textContent = msg.contents.find((c): c is TextContent => c.kind === 'text');
        if (!textContent) continue;

        const text = textContent.text;
        const response = await conversation.send(text);
        console.log(`User: ${text}\nAgent: ${response}\n`);
      }
    }
  }
}

// Usage
const service = new ProductionAgentService("http://localhost:5000");
await service.chat("Hello");
