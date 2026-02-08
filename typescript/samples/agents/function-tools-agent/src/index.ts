// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { createAgentProtocolRouter } from '@microsoft/agents-protocol';
import { config } from 'dotenv';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

// Load environment variables from .env file in repository root
const envPath = path.resolve(process.cwd(), '..', '..', '..', '..', '.env');
if (fs.existsSync(envPath)) {
  config({ path: envPath });
  console.log(`Loaded .env from: ${envPath}`);
}

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Initialize OpenAI client for Foundry
const foundryEndpoint = process.env.FOUNDRY_ENDPOINT;
const foundryApiKey = process.env.FOUNDRY_API_KEY;
const foundryModel = process.env.FOUNDRY_MODEL_DEPLOYMENT || 'gpt-5-nano';

if (!foundryEndpoint || !foundryApiKey) {
  throw new Error('FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables are required');
}

const openaiClient = new OpenAI({
  apiKey: foundryApiKey,
  baseURL: `${foundryEndpoint}/openai/v1`
});

// Conversation history storage (in-memory for demo)
const conversationHistory: Record<string, Array<OpenAI.Chat.ChatCompletionMessageParam>> = {};

// Function Tools
function getWeather(location: string): string {
  const conditions = ['sunny', 'cloudy', 'rainy', 'partly cloudy', 'stormy'];
  const condition = conditions[Math.floor(Math.random() * conditions.length)];
  const temperature = Math.floor(Math.random() * 25) + 10;
  return `🌤️ The weather in ${location} is ${condition} with a temperature of ${temperature}°C.`;
}

function getTime(): string {
  const now = new Date();
  return `🕐 The current UTC time is ${now.toISOString()}.`;
}

function extractLocation(message: string): string {
  const patterns = [' in ', ' at ', ' for '];
  for (const pattern of patterns) {
    const index = message.toLowerCase().indexOf(pattern);
    if (index >= 0) {
      const locationStart = index + pattern.length;
      const locationPart = message.substring(locationStart).trim().replace(/[?!.]/g, '');
      if (locationPart) {
        const words = locationPart.split(' ');
        return words[0].charAt(0).toUpperCase() + words[0].slice(1).toLowerCase();
      }
    }
  }
  return 'your location';
}

// Health check
app.get('/', (req, res) => {
  res.send('Microsoft Agents SDK - Basic M365 Agent Sample');
});

// Bot Framework /api/messages endpoint
app.post('/api/messages', async (req, res) => {
  const activity = req.body;

  console.log('📨 Received Bot Framework activity:', {
    type: activity.type,
    text: activity.text
  });

  // Extract role from channelData (default to "user" if not present)
  const role = activity.channelData?.role || 'user';

  // Only respond to user messages
  if (activity.type === 'message' && activity.text && role === 'user') {
    try {
      const userMessage = activity.text;
      const conversationId = activity.conversation.id;

      // Initialize conversation history if needed
      if (!conversationHistory[conversationId]) {
        conversationHistory[conversationId] = [
          {
            role: 'system',
            content: 'You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users.'
          }
        ];
      }

      // Add user message to history
      conversationHistory[conversationId].push({
        role: 'user',
        content: userMessage
      });

      // Define available functions
      const tools: OpenAI.Chat.ChatCompletionTool[] = [
        {
          type: 'function',
          function: {
            name: 'getWeather',
            description: 'Get the weather for a given location.',
            parameters: {
              type: 'object',
              properties: {
                location: {
                  type: 'string',
                  description: 'The location to get the weather for.'
                }
              },
              required: ['location']
            }
          }
        },
        {
          type: 'function',
          function: {
            name: 'getTime',
            description: 'Get the current UTC time.',
            parameters: {
              type: 'object',
              properties: {}
            }
          }
        }
      ];

      // Call LLM with function calling in a loop
      let responseText = '';
      const maxIterations = 5;
      let iteration = 0;

      while (iteration < maxIterations) {
        iteration++;

        // Get completion from LLM
        const completion = await openaiClient.chat.completions.create({
          model: foundryModel,
          messages: conversationHistory[conversationId],
          tools: tools,
          tool_choice: 'auto'
        });

        const choice = completion.choices[0];
        const message = choice.message;

        // Check if the model wants to call functions
        if (choice.finish_reason === 'tool_calls' && message.tool_calls) {
          // Add assistant message with tool calls to history
          conversationHistory[conversationId].push(message);

          // Execute each tool call
          for (const toolCall of message.tool_calls) {
            const functionName = toolCall.function.name;
            const functionArgs = JSON.parse(toolCall.function.arguments);

            let functionResult: string;
            if (functionName === 'getWeather') {
              const location = functionArgs.location || 'unknown';
              functionResult = getWeather(location);
            } else if (functionName === 'getTime') {
              functionResult = getTime();
            } else {
              functionResult = 'Unknown function';
            }

            // Add function result to conversation history
            conversationHistory[conversationId].push({
              role: 'tool',
              tool_call_id: toolCall.id,
              content: functionResult
            });
          }
        } else {
          // Model provided a final response
          responseText = message.content || "I apologize, but I wasn't able to complete your request.";
          conversationHistory[conversationId].push({
            role: 'assistant',
            content: responseText
          });
          break;
        }
      }

      if (!responseText) {
        responseText = "I apologize, but I wasn't able to complete your request.";
      }

      const responseActivity = {
        type: 'message',
        from: {
          id: 'basic-m365-bot',
          name: 'Basic M365 Agent'
        },
        recipient: activity.from,
        conversation: activity.conversation,
        text: responseText,
        timestamp: new Date().toISOString(),
        channelId: activity.channelId || 'demo',
        serviceUrl: activity.serviceUrl || '',
        id: `msg-${Date.now()}`
      };

      console.log('✅ Sending response:', responseActivity.text);
      res.status(200).json(responseActivity);
    } catch (error) {
      console.error('❌ Error processing message:', error);
      res.status(500).json({ error: 'Failed to process message' });
    }
  } else if (activity.type === 'conversationUpdate' && activity.membersAdded) {
    // Welcome message
    const welcomeText =
      "Hello! I'm a Basic M365 Agent. " +
      "I can help you with weather and time information. " +
      "Try asking: 'What's the weather in Seattle?' or 'What time is it?'";

    const responseActivity = {
      type: 'message',
      from: {
        id: 'basic-m365-bot',
        name: 'Function Tools Bot'
      },
      recipient: activity.from,
      conversation: activity.conversation,
      text: welcomeText,
      timestamp: new Date().toISOString(),
      channelId: activity.channelId || 'demo',
      serviceUrl: activity.serviceUrl || '',
      id: `msg-${Date.now()}`
    };

    console.log('✅ Sending welcome message');
    res.status(200).json(responseActivity);
  } else {
    res.status(200).json({ status: 'ok' });
  }
});

// Add Agent Protocol routes
// TypeScript equivalent of: app.MapAgentProtocol();
app.use(createAgentProtocolRouter());

// Error handling
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('❌ Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Read port from centralized agent-config.json
function getPortFromConfig(): string | null {
  try {
    // Navigate up to repository root (4 levels up from function-tools-agent)
    const configPath = path.resolve(
      process.cwd(),
      '..', '..', '..', '..',
      'agent-config.json'
    );

    if (!fs.existsSync(configPath)) {
      return null;
    }

    const json = fs.readFileSync(configPath, 'utf-8');
    const config = JSON.parse(json);

    return config?.bots?.['typescript-basic-m365']?.port?.toString() || null;
  } catch {
    return null;
  }
}

// Start server
const port = getPortFromConfig() || process.env.PORT || '3983';
app.listen(parseInt(port), () => {
  console.log('🤖 Function Tools Agent Server Started');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📡 Listening on: http://localhost:${port}`);
  console.log(`💬 Bot endpoint: http://localhost:${port}/api/messages`);
  console.log(`🔄 Agent Protocol endpoints:`);
  console.log(`   GET  http://localhost:${port}/health`);
  console.log(`   POST http://localhost:${port}/runs`);
  console.log(`   POST http://localhost:${port}/runs/wait`);
  console.log(`   POST http://localhost:${port}/runs/stream`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
  console.log('💡 Available function tools:');
  console.log('   🌤️  getWeather(location) - Get weather information');
  console.log('   🕐  getTime() - Get current UTC time');
  console.log('');
  console.log('Try sending a message like: "What\'s the weather in Seattle?"');
});
