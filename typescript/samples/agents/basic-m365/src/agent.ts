// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// ============================================================================
// LEGACY SAMPLE - M365 Agents SDK + Agent Protocol
// ============================================================================
// This sample demonstrates how to take a LEGACY M365 Agents SDK application
// with LLM integration and make it speak Agent Protocol. It uses the older
// SDK architecture with AgentApplication and the protocol adapter layer.
//
// For NEW applications, see the emoji-chat sample which demonstrates the
// modern approach using ONLY the @microsoft/agents-protocol-hosting package.
// ============================================================================

import { TurnState, MemoryStorage, TurnContext, AgentApplication } from '@microsoft/agents-hosting'
import OpenAI from 'openai'
import * as path from 'path'
import { TestingChatClient } from './TestingChatClient'

interface ConversationState {
  messages: OpenAI.Chat.ChatCompletionMessageParam[];
}
type ApplicationTurnState = TurnState<ConversationState>

// 🔧 FIX: Track storage access for cleanup to prevent memory leaks
const storageAccessTimes = new Map<string, number>()
const STORAGE_MAX_AGE_MS = 60 * 60 * 1000 // 1 hour
let lastCleanup = Date.now()

function cleanupOldStorage(storage: MemoryStorage): void {
  const now = Date.now()

  // Only cleanup every 5 minutes
  if (now - lastCleanup < 5 * 60 * 1000) {
    return
  }

  lastCleanup = now
  const cutoff = now - STORAGE_MAX_AGE_MS

  // Find keys to delete
  const keysToDelete: string[] = []
  for (const [key, accessTime] of storageAccessTimes.entries()) {
    if (accessTime < cutoff) {
      keysToDelete.push(key)
    }
  }

  // Delete old keys
  if (keysToDelete.length > 0) {
    storage.delete(keysToDelete).then(() => {
      keysToDelete.forEach(key => storageAccessTimes.delete(key))
      console.log(`Cleaned up ${keysToDelete.length} old conversation states`)
    }).catch(err => {
      console.error('Error during storage cleanup:', err)
    })
  }
}

// LLM Client setup
let testingClient: TestingChatClient | null = null
let model: string = 'gpt-4'

// ============================================================================
// ENVIRONMENT VARIABLES - Set automatically by scripts/ci/start_samples.py
// ============================================================================
// These environment variables are loaded from .env file at repo root:
//   - FOUNDRY_ENDPOINT: LLM endpoint URL
//   - FOUNDRY_API_KEY: API key for authentication
//   - FOUNDRY_MODEL_DEPLOYMENT: Model name (default: gpt-4)
//   - USE_LLM_RECORDINGS: Set to "true" for test mode (replays recordings)
//   - RECORD_LLM: Set to "true" to record LLM interactions
//
// Developers should NEVER manually set these variables.
// Use: python3 scripts/ci/start_samples.py basic-m365 --lang typescript --ui
// ============================================================================

function initLLM() {
  console.log('🔧 Initializing LLM...')

  // Check mode from environment variables
  const useRecordings = process.env.USE_LLM_RECORDINGS?.toLowerCase() === 'true'
  const recordLlm = process.env.RECORD_LLM?.toLowerCase() === 'true'

  const playbackMode = useRecordings
  const recordMode = recordLlm

  // Find recordings directory
  const recordingsDir = path.join(__dirname, '..', '..', '..', '..', '..', '..', 'test-data', 'llm-recordings', 'basic-m365')

  // Create real OpenAI client if needed (for normal or recording mode)
  let realClient: OpenAI | null = null
  if (!playbackMode) {
    const endpoint = process.env.FOUNDRY_ENDPOINT
    const apiKey = process.env.FOUNDRY_API_KEY

    if (!endpoint || !apiKey) {
      console.log('⚠️  FOUNDRY_ENDPOINT or FOUNDRY_API_KEY not set. LLM features disabled.')
      console.log('   Set these environment variables to enable LLM functionality.')
      return
    }

    model = process.env.FOUNDRY_MODEL_DEPLOYMENT || 'gpt-4'

    try {
      realClient = new OpenAI({
        apiKey: apiKey,
        baseURL: `${endpoint}/openai/v1/`
      })
    } catch (error) {
      console.error('❌ Error creating OpenAI client:', error)
      return
    }
  } else {
    model = 'gpt-5-nano'
  }

  // Create TestingChatClient wrapper
  testingClient = new TestingChatClient(
    realClient,
    recordingsDir,
    model,
    recordMode,
    playbackMode
  )
}

// Initialize on module load
initLLM()


// Define storage and application
const storage = new MemoryStorage()
export const agentApp = new AgentApplication<ApplicationTurnState>({
  storage
})

// Function tools
async function getWeatherAsync(location: string): Promise<string> {
  // Simulate async API call
  await new Promise(resolve => setTimeout(resolve, 100))

  const conditions = ['sunny', 'cloudy', 'rainy', 'partly cloudy', 'stormy']
  const condition = conditions[Math.floor(Math.random() * conditions.length)]
  const temperature = Math.floor(Math.random() * 25) + 10

  return `🌤️ The weather in ${location} is ${condition} with a temperature of ${temperature}°C.`
}

function getCurrentTime(): string {
  const now = new Date()
  return `🕐 The current UTC time is ${now.toISOString().replace('T', ' ').substring(0, 19)}.`
}

// Convert OpenAI chat message to Agent Protocol message format
function convertChatMessageToAgentProtocol(chatMessage: OpenAI.Chat.ChatCompletionMessageParam): any {
  const message: any = {}

  // Determine role
  const role = chatMessage.role
  if (role === 'tool') {
    message.role = 'tool'
  } else {
    message.role = 'assistant'
  }

  // Convert contents
  const contents: any[] = []

  if (role === 'assistant' && 'tool_calls' in chatMessage && chatMessage.tool_calls) {
    // Tool call message
    for (const toolCall of chatMessage.tool_calls) {
      contents.push({
        kind: 'functionCall',
        callId: toolCall.id,
        name: toolCall.function.name,
        arguments: toolCall.function.arguments
      })
    }
  } else if (role === 'tool') {
    // Tool result
    const toolMsg = chatMessage as OpenAI.Chat.ChatCompletionToolMessageParam
    contents.push({
      kind: 'functionResult',
      callId: toolMsg.tool_call_id,
      result: toolMsg.content
    })
  } else if (role === 'assistant' && 'content' in chatMessage) {
    // Text response
    const text = chatMessage.content || ''
    contents.push({
      kind: 'text',
      text: text
    })
  } else {
    // Fallback: treat as text
    const text = ('content' in chatMessage) ? chatMessage.content : ''
    contents.push({
      kind: 'text',
      text: text || ''
    })
  }

  message.contents = contents
  return message
}

agentApp.onConversationUpdate('membersAdded', async (context: TurnContext, state: ApplicationTurnState) => {
  await context.sendActivity(
    "Hello! I'm a Basic M365 Agent. I can help you with weather and time information. " +
    "Try asking: 'What's the weather in Seattle?' or 'What time is it?'"
  )
})

// Listen for ANY message to be received
agentApp.onActivity('message', async (context: TurnContext, state: ApplicationTurnState) => {
  // 🔧 Periodically clean up old storage to prevent memory leaks
  cleanupOldStorage(storage)

  // Track this conversation's access time
  if (context.activity.conversation?.id) {
    storageAccessTimes.set(context.activity.conversation.id, Date.now())
  }

  // Extract role from channelData (default to "user" if not present)
  const role = (context.activity.channelData as any)?.role ?? 'user'

  // Only respond to user messages
  if (role !== 'user') {
    return
  }

  const userMessage = context.activity.text || ''

  // If LLM is not configured, provide helpful message
  if (!testingClient) {
    console.log('⚠️ LLM not configured')
    await context.sendActivity(
      `Hello! I'm a Basic M365 Agent with LLM capabilities.\n\n` +
      `To enable AI features, please start this sample using:\n` +
      `python3 scripts/ci/start_samples.py basic-m365 --lang typescript`
    )
    return
  }

  // Initialize conversation history if needed
  if (!state.conversation.messages) {
    state.conversation.messages = [
      {
        role: 'system',
        content: 'You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users.'
      }
    ]
  }

  // Add user message to history
  state.conversation.messages.push({
    role: 'user',
    content: userMessage
  })

  // Track the starting index to capture new messages generated during this turn
  const startingHistoryCount = state.conversation.messages.length

  // Define available functions
  const tools: OpenAI.Chat.ChatCompletionTool[] = [
    {
      type: 'function',
      function: {
        name: 'get_weather',
        description: 'Get the weather for a given location',
        parameters: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'The location to get the weather for'
            }
          },
          required: ['location']
        }
      }
    },
    {
      type: 'function',
      function: {
        name: 'get_current_time',
        description: 'Get the current UTC time',
        parameters: {
          type: 'object',
          properties: {}
        }
      }
    }
  ]

  // Call LLM with function calling in a loop
  let response = ''
  const maxIterations = 5  // Prevent infinite loops
  let iteration = 0

  while (iteration < maxIterations) {
    iteration++

    try {
      // Get completion from LLM (transparently handles recording/playback)
      const completion = await testingClient.createCompletion(
        state.conversation.messages,
        tools
      )

      // Check if the model wants to call functions
      if (completion.choices[0].finish_reason === 'tool_calls' && completion.choices[0].message.tool_calls) {
        const toolCalls = completion.choices[0].message.tool_calls

        // Add assistant message with tool calls to history
        state.conversation.messages.push({
          role: 'assistant',
          content: null,
          tool_calls: toolCalls.map(tc => ({
            id: tc.id,
            type: 'function' as const,
            function: {
              name: tc.function.name,
              arguments: tc.function.arguments
            }
          }))
        })

        // Execute each tool call
        for (const toolCall of toolCalls) {
          const functionName = toolCall.function.name
          const functionArgs = JSON.parse(toolCall.function.arguments)

          let functionResult: string
          if (functionName === 'get_weather') {
            const location = functionArgs.location || 'unknown'
            functionResult = await getWeatherAsync(location)
          } else if (functionName === 'get_current_time') {
            functionResult = getCurrentTime()
          } else {
            functionResult = 'Unknown function'
          }

          // Add function result to conversation history
          state.conversation.messages.push({
            role: 'tool',
            tool_call_id: toolCall.id,
            content: functionResult
          })
        }
      } else {
        // Model provided a final response
        response = completion.choices[0].message.content || ''
        state.conversation.messages.push({
          role: 'assistant',
          content: response
        })
        break
      }
    } catch (error) {
      console.error('Error during LLM call:', error)
      response = 'I apologize, but I encountered an error while processing your request.'
      break
    }
  }

  if (!response) {
    response = "I apologize, but I wasn't able to complete your request."
  }

  // Send all messages generated during this turn as separate activities
  for (let i = startingHistoryCount; i < state.conversation.messages.length; i++) {
    const chatMessage = state.conversation.messages[i]
    const agentMessage = convertChatMessageToAgentProtocol(chatMessage)

    // Create an activity with the Agent Protocol message in the Value field
    const activity: any = {
      type: 'message',
      text: '',
      value: agentMessage
    }
    await context.sendActivity(activity)
  }
})
