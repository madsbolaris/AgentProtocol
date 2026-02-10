import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { MessageDeserializer } from '@microsoft/agents-xml';
import { ThreadValidator } from '@microsoft/agents-validation';
import { ChatMessage, TextContent } from '@microsoft/agents';
import { promises as fs } from 'fs';
import { glob } from 'glob';

class EvaluationRunner {
  private client: AgentProtocolClient;
  private deserializer = new MessageDeserializer();
  private validator = new ThreadValidator();

  constructor(agentEndpoint: string) {
    this.client = new AgentProtocolClient({ baseUrl: agentEndpoint });
  }

  async runEvaluation(testFilePath: string): Promise<boolean> {
    try {
      // Load evaluation test case from XML
      const evalXml = await fs.readFile(testFilePath, 'utf-8');
      const testMessages = this.deserializer.deserializeMany(evalXml);

      // Extract the user input from the test case using type guard
      const userMessage = testMessages.find((m): m is ChatMessage & { role: 'user' } => m.role === 'user');
      if (!userMessage) {
        throw new Error('No user message found in test case');
      }

      const expectedMessages = testMessages.filter(m => m.role !== 'user');

      // Send to agent via Client SDK
      const conversation = this.client.createConversation();

      // Use type guard for text content
      const textContent = userMessage.contents.find((c): c is TextContent => c.kind === 'text');
      if (!textContent) {
        throw new Error('No text content found in user message');
      }

      await conversation.send(textContent.text);

      // Get messages from local cache (no HTTP call)
      const actualMessages = conversation.messages;

      // Validate actual vs expected behavior
      const validationResult = this.validator.validate(actualMessages, expectedMessages);

      if (validationResult.isValid) {
        console.log(`✓ Test passed: ${testFilePath}`);
        return true;
      } else {
        console.log(`✗ Test failed: ${testFilePath}`);
        validationResult.errors.forEach(error => {
          console.log(`  - ${error.message}`);
        });
        return false;
      }
    } catch (error) {
      console.error(`Evaluation failed: ${testFilePath}`, error);
      return false;
    }
  }
}

// Usage: Run all evals
const runner = new EvaluationRunner("http://localhost:5000");
const testFiles = await glob("test-cases/*.xml");
for (const testFile of testFiles) {
  await runner.runEvaluation(testFile);
}
