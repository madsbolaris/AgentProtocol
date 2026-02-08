// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { createAgentProtocolRouter } from '@microsoft/agents-protocol';
import fs from 'fs';
import path from 'path';

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Health check
app.get('/', (req, res) => {
  res.send('Microsoft Agents SDK Sample');
});

// Bot Framework /api/messages endpoint (for Bot Framework Emulator compatibility)
app.post('/api/messages', (req, res) => {
  const activity = req.body;

  console.log('📨 Received Bot Framework activity:', {
    type: activity.type,
    text: activity.text
  });

  if (activity.type === 'message' && activity.text) {
    const responseActivity = {
      type: 'message',
      from: {
        id: 'echo-bot',
        name: 'Echo Bot'
      },
      recipient: activity.from,
      conversation: activity.conversation,
      text: `You said: ${activity.text}`,
      timestamp: new Date().toISOString(),
      channelId: activity.channelId || 'demo',
      serviceUrl: activity.serviceUrl || '',
      id: `msg-${Date.now()}`
    };

    console.log('✅ Sending response:', responseActivity.text);
    res.status(200).json(responseActivity);
  } else {
    res.status(200).json({ status: 'ok' });
  }
});

// Add Agent Protocol routes - THIS IS THE ONE LINE CHANGE!
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
    // Navigate up to repository root (3 levels up from echo-bot)
    const configPath = path.resolve(
      process.cwd(),
      '..', '..', '..',
      'agent-config.json'
    );

    if (!fs.existsSync(configPath)) {
      return null;
    }

    const json = fs.readFileSync(configPath, 'utf-8');
    const config = JSON.parse(json);

    return config?.bots?.typescript?.port?.toString() || null;
  } catch {
    return null;
  }
}

// Start server
const port = getPortFromConfig() || process.env.PORT || '3979';
app.listen(parseInt(port), () => {
  console.log('🤖 Echo Bot Server Started');
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
  console.log('✨ Ready to receive messages!');
  console.log('');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down Echo Bot...');
  process.exit(0);
});
