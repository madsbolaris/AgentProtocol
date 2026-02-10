import winston from 'winston';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

class ProductionAgentService {
  private client: AgentProtocolClient;
  private logger = winston.createLogger({
    transports: [new winston.transports.Console()]
  });

  constructor(endpoint: string) {
    // Enable automatic logging to files
    this.client = new AgentProtocolClient({
      baseUrl: endpoint,
      enableLogging: true,
      logDirectory: "logs/production"
    });
  }

  async chat(userInput: string, threadId?: string): Promise<string> {
    const conversation = threadId
      ? this.client.resumeConversation(threadId)
      : this.client.createConversation();

    const response = await conversation.send(userInput);

    // Structured logging with message count
    this.logger.info('Conversation turn completed', {
      threadId: conversation.threadId,
      messageCount: conversation.messages.length
    });

    // Optionally stream XML to centralized storage
    await this.sendToObservabilityPlatform(
      conversation.threadId!,
      conversation.toString()
    );

    return response;
  }

  private async sendToObservabilityPlatform(threadId: string, xml: string): Promise<void> {
    // Send to Datadog, New Relic, etc.
  }
}

// Usage
const service = new ProductionAgentService("http://localhost:5000");
await service.chat("Hello, how can you help?");
