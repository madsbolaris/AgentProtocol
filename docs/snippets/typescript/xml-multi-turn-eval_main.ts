import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { MessageDeserializer } from '@microsoft/agents-xml';
import { ThreadValidator } from '@microsoft/agents-validation';
import { ChatMessage, TextContent } from '@microsoft/agents';
import { promises as fs } from 'fs';

class EvaluationRunner {
  private client: AgentProtocolClient;
  private deserializer = new MessageDeserializer();
  private validator = new ThreadValidator();

  constructor(agentEndpoint: string) {
    this.client = new AgentProtocolClient({ baseUrl: agentEndpoint });
  }

  async runMultiTurnEval(testFilePath: string): Promise<boolean> {
    // Load eval
    const xml = await fs.readFile(testFilePath, 'utf-8');
    const testMessages = this.deserializer.deserializeMany(xml);

    // Extract user messages using type guard
    const userMessages = testMessages.filter((m): m is ChatMessage & { role: 'user' } => m.role === 'user');

    // Use Client SDK with persistent conversation
    const conversation = this.client.createConversation();
    const start = Date.now();

    // Send each user message in sequence
    for (const userMsg of userMessages) {
      // Use type guard for text content
      const textContent = userMsg.contents.find((c): c is TextContent => c.kind === 'text');
      if (!textContent) continue;

      await conversation.send(textContent.text);
    }

    const elapsedMs = Date.now() - start;

    // Get messages from local cache (no HTTP call)
    const actualMessages = conversation.messages;

    // Validate against expected behavior
    const result = this.validator.validate(actualMessages, testMessages);

    // Check metrics
    if (elapsedMs > 2000) {
      console.log(`⚠ Performance threshold exceeded: ${elapsedMs}ms`);
    }

    return result.isValid;
  }
}

// Usage
const runner = new EvaluationRunner("http://localhost:5000");
await runner.runMultiTurnEval("test-cases/multi-turn-booking.xml");
