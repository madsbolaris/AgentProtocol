// Test OpenAI client initialization
const OpenAI = require('openai');

console.log('Testing OpenAI client...');

const endpoint = process.env.FOUNDRY_ENDPOINT;
const apiKey = process.env.FOUNDRY_API_KEY;

console.log(`Endpoint: ${endpoint ? endpoint.substring(0, 30) + '...' : 'NOT SET'}`);
console.log(`API Key: ${apiKey ? '***' + apiKey.substring(apiKey.length - 4) : 'NOT SET'}`);

if (!endpoint || !apiKey) {
  console.log('❌ Missing credentials');
  process.exit(1);
}

const client = new OpenAI({
  apiKey: apiKey,
  baseURL: `${endpoint}/openai/v1/`
});

console.log('✅ Client created');
console.log(`Client type: ${typeof client}`);
console.log(`Client is null: ${client === null}`);
console.log(`Client is undefined: ${client === undefined}`);
console.log(`Has chat property: ${client.hasOwnProperty('chat')}`);
