import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Enable CORS for all routes
app.use(cors());

// Serve static files from the current directory
app.use(express.static(__dirname));

// Serve agent-config.json from the repository root
app.get('/agent-config.json', (req, res) => {
  res.sendFile(path.join(__dirname, '..', '..', 'agent-config.json'));
});

// Serve the main demo page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'agent-demo.html'));
});

app.listen(PORT, () => {
  console.log(`\n🚀 Agent Protocol Demo Server`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`  Demo UI:  http://localhost:${PORT}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  console.log(`Available bots (from agent-config.json):`);
  console.log(`  • EchoM365 (.NET) - http://localhost:3978`);
  console.log(`  • EchoM365 (Python) - http://localhost:3979`);
  console.log(`  • EchoM365 (TypeScript) - http://localhost:3980`);
  console.log(`  • EmojiChatBot (.NET) - http://localhost:3984`);
  console.log(`  • Quick Emoji Bot (Node.js) - http://localhost:3984`);
  console.log(`\n💡 Make sure at least one bot is running before testing!\n`);
});
