/**
 * Simple Echo M365 for Agent Protocol Demo
 *
 * This is a minimal Bot Framework-compatible echo bot that:
 * - Listens on port 3978
 * - Responds to the Bot Framework Activity protocol
 * - Echoes back any message it receives
 *
 * No authentication or complex dependencies - just works!
 */

import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';

const app = express();
const PORT = 3978;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Health check endpoint
app.get('/', (req, res) => {
  res.send('Agent Framework Protocol SDK Sample');
});

// Main bot endpoint - receives Bot Framework Activities
app.post('/api/messages', (req, res) => {
  const activity = req.body;

  console.log('📨 Received activity:', {
    type: activity.type,
    text: activity.text,
    from: activity.from?.name || activity.from?.id,
    conversationId: activity.conversation?.id
  });

  // Handle different activity types
  if (activity.type === 'message' && activity.text) {
    // Echo the message back
    const responseActivity = {
      type: 'message',
      from: {
        id: 'echo-m365',
        name: 'Echo M365'
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
  }
  else if (activity.type === 'conversationUpdate') {
    // Welcome message for new members
    if (activity.membersAdded && activity.membersAdded.length > 0) {
      const welcomeActivity = {
        type: 'message',
        from: {
          id: 'echo-m365',
          name: 'Echo M365'
        },
        recipient: activity.from,
        conversation: activity.conversation,
        text: '👋 Welcome! I\'m a simple echo bot. Whatever you say, I\'ll repeat back to you!',
        timestamp: new Date().toISOString(),
        channelId: activity.channelId || 'demo',
        serviceUrl: activity.serviceUrl || '',
        id: `msg-${Date.now()}`
      };

      console.log('👋 Sending welcome message');
      res.status(200).json(welcomeActivity);
    } else {
      res.status(200).json({ status: 'ok' });
    }
  }
  else {
    // For other activity types, just acknowledge
    console.log(`ℹ️  Received activity type: ${activity.type}`);
    res.status(200).json({ status: 'ok' });
  }
});

// Error handling
app.use((err, req, res, next) => {
  console.error('❌ Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log('🤖 Echo M365 Server Started');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`📡 Listening on: http://localhost:${PORT}`);
  console.log(`💬 Bot endpoint: http://localhost:${PORT}/api/messages`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
  console.log('✨ Ready to receive messages!');
  console.log('💡 Tip: Refresh your browser demo to connect');
  console.log('');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n👋 Shutting down Echo M365...');
  process.exit(0);
});
