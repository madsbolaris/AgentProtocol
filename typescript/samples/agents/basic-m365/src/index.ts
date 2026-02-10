import { AuthConfiguration, authorizeJWT, CloudAdapter, loadAuthConfigFromEnv, Request } from '@microsoft/agents-hosting'
import express, { Response } from 'express'
import { agentApp } from './agent'
import * as fs from 'fs'
import * as path from 'path'

const authConfig: AuthConfiguration = loadAuthConfigFromEnv()
const adapter = new CloudAdapter(authConfig)

const server = express()

// Add CORS middleware for development
server.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
  res.header('Access-Control-Allow-Headers', '*')
  res.header('Access-Control-Expose-Headers', '*')
  res.header('Access-Control-Max-Age', '3600')
  if (_req.method === 'OPTIONS') {
    return res.status(200).end()
  }
  next()
})

server.use(express.json())

// Only apply JWT authorization if credentials are configured
// For local development without authentication, this allows anonymous access
if (authConfig.clientId && authConfig.clientSecret) {
  server.use(authorizeJWT(authConfig))
  console.log('Running with authentication enabled')
} else {
  console.log('Running in anonymous mode (no authentication required)')
}

/**
 * Helper function to read port from centralized agent-config.json
 * Falls back to environment variable PORT, then default 3980
 */
function getPortFromConfig(): number | null {
  try {
    // Navigate up to repository root (3 levels up from EchoM365 directory)
    const configPath = path.join(__dirname, '..', '..', '..', '..', 'agent-config.json')

    if (!fs.existsSync(configPath)) {
      return null
    }

    const configContent = fs.readFileSync(configPath, 'utf-8')
    const config = JSON.parse(configContent)

    return config?.bots?.['typescript-basic-m365']?.port || null
  } catch (error) {
    // If config reading fails, return null to fall back to environment variable
    return null
  }
}

function generateRunId(): string {
  return `run_${Math.random().toString(36).substring(2, 15)}`
}

function generateMessageId(): string {
  return `msg_${Math.random().toString(36).substring(2, 15)}`
}

function generateThreadId(): string {
  return `thread_${Math.random().toString(36).substring(2, 15)}`
}

/**
 * Builds a Thread XML document from output messages
 */
function buildThreadXml(threadId: string, outputMessages: any[], createdAt: string, status: string = 'active'): string {
  const escapeXml = (unsafe: string): string => {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;')
  }

  let xml = `<?xml version="1.0" encoding="utf-8"?>\n`
  xml += `<thread thread-id="${threadId}" status="${status}" created-at="${createdAt}">\n`

  for (const msg of outputMessages) {
    const role = msg.role || 'agent'
    xml += `  <${role}`
    if (msg.messageId) {
      xml += ` message-id="${msg.messageId}"`
    }
    xml += `>\n`

    // Add contents
    if (msg.contents && Array.isArray(msg.contents)) {
      for (const content of msg.contents) {
        const kind = content.kind || 'text'
        if (kind === 'text') {
          xml += `    <text`
          if (content.audience) {
            xml += ` audience="${content.audience}"`
          }
          xml += `>${escapeXml(content.text || '')}</text>\n`
        } else if (kind === 'functionCall') {
          xml += `    <function-call call-id="${content.callId}" name="${content.name}">${escapeXml(content.arguments || '')}</function-call>\n`
        } else if (kind === 'functionResult') {
          xml += `    <function-result call-id="${content.callId}">${escapeXml(content.result || '')}</function-result>\n`
        }
      }
    }

    // If no contents or empty contents, make it self-closing
    if (!msg.contents || msg.contents.length === 0) {
      xml = xml.slice(0, -1) + '/>\n'
    } else {
      xml += `  </${role}>\n`
    }
  }

  xml += `</thread>\n`
  return xml
}

/**
 * Setup Agent Protocol routes
 * This implements the Agent Protocol endpoints for health checks and runs
 */
function setupAgentProtocolRoutes(app: express.Application): void {
  // Health check endpoint
  app.get('/health', (_req: express.Request, res: express.Response) => {
    res.status(200).json({ status: 'OK' })
  })

  // Agent card endpoint
  app.get('/agent-card', (_req: express.Request, res: express.Response) => {
    const agentCard = {
      agentId: 'basic-m365',
      name: 'Basic M365 Agent',
      description: 'A basic agent that can check weather and tell time',
      version: '1.0.0',
      outputModes: ['text'],
      inputModes: ['text']
    }
    res.status(200).json(agentCard)
  })

  // Create run endpoint
  app.post('/runs', async (req: express.Request, res: express.Response) => {
    // Get format query parameter (default to json)
    const format = req.query.format || 'json'

    try {
      const { agentId = 'agent', threadId = generateThreadId(), input = [] } = req.body
      const runId = generateRunId()

      // TODO: Process through agent
      // Only process user messages
      const output = input
        .filter((msg: any) => msg.role === 'user')
        .map((msg: any) => ({
          role: 'assistant',
          contents: [{ kind: 'text', text: `Echo: ${msg?.contents?.[0]?.text || ''}` }]
        }))

      const createdAt = new Date().toISOString()
      const completedAt = new Date().toISOString()

      const run = {
        runId,
        agentId,
        threadId,
        status: 'completed',
        // NOTE: input field omitted per TypeSpec @visibility("create") rule
        // input should only appear in request bodies, not responses
        output,
        createdAt,
        completedAt
      }

      // Return XML or JSON based on format parameter
      if (format === 'xml') {
        const xml = buildThreadXml(threadId, output, createdAt)
        res.status(201).type('application/xml').send(xml)
      } else {
        res.status(201).json(run)
      }
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  })

  // Create and wait endpoint
  app.post('/runs/wait', async (req: express.Request, res: express.Response) => {
    // Get format query parameter (default to json)
    const format = req.query.format || 'json'

    try {
      const { agentId = 'agent', threadId = generateThreadId(), input = [] } = req.body
      const runId = generateRunId()

      // Process through agent - convert each input message to activity and collect responses
      const output: any[] = []

      for (const msg of input) {
        if (msg.role === 'user') {
          const activity = {
            type: 'message',
            text: msg?.contents?.[0]?.text || '',
            from: { id: 'user' },
            recipient: { id: 'bot' },
            conversation: { id: threadId },
            channelId: 'agent-protocol',
            serviceUrl: 'https://agent-protocol',
            channelData: { role: 'user' },
            removeRecipientMention: () => msg?.contents?.[0]?.text || ''
          }

          // Create a mock turn context to capture responses
          const mockContext = {
            activity,
            sendActivity: async (activityOrText: any) => {
              const responseActivity = typeof activityOrText === 'string'
                ? { text: activityOrText, value: null }
                : activityOrText

              // If there's a value field (Agent Protocol format), use it
              if (responseActivity.value) {
                output.push(responseActivity.value)
              } else if (responseActivity.text) {
                // Otherwise convert text to Agent Protocol format
                output.push({
                  role: 'assistant',
                  contents: [{ kind: 'text', text: responseActivity.text }]
                })
              }
              return { id: 'mock-id' }
            },
            sendActivities: async (activities: any[]) => {
              for (const act of activities) {
                const responseActivity = typeof act === 'string' ? { text: act, value: null } : act
                if (responseActivity.value) {
                  output.push(responseActivity.value)
                } else if (responseActivity.text) {
                  output.push({
                    role: 'assistant',
                    contents: [{ kind: 'text', text: responseActivity.text }]
                  })
                }
              }
              return activities.map(() => ({ id: 'mock-id' }))
            }
          }

          // Run the agent with mock context
          await agentApp.run(mockContext as any)
        }
      }

      const createdAt = new Date().toISOString()
      const completedAt = new Date().toISOString()

      const run = {
        runId,
        agentId,
        threadId,
        status: 'completed',
        // NOTE: input field omitted per TypeSpec @visibility("create") rule
        // input should only appear in request bodies, not responses
        output,
        createdAt,
        completedAt
      }

      // Return XML or JSON based on format parameter
      if (format === 'xml') {
        const xml = buildThreadXml(threadId, output, createdAt)
        res.status(200).type('application/xml').send(xml)
      } else {
        res.status(200).json(run)
      }
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  })

  // Create and stream endpoint
  app.post('/runs/stream', async (req: express.Request, res: express.Response) => {
    try {
      const { agentId = 'agent', threadId = generateThreadId(), input = [] } = req.body
      const runId = generateRunId()

      // Set up SSE response headers
      res.setHeader('Content-Type', 'text/event-stream')
      res.setHeader('Cache-Control', 'no-cache')
      res.setHeader('Connection', 'keep-alive')

      const createdAt = new Date().toISOString()

      // Helper to send SSE event
      const sendEvent = (event: string, data: any) => {
        res.write(`event: ${event}\n`)
        res.write(`data: ${JSON.stringify({ event, data })}\n\n`)
      }

      // Event: run.started
      sendEvent('run.started', {
        runId,
        agentId,
        threadId,
        status: 'in_progress',
        createdAt
      })

      // Process through agent - convert each input message to activity and collect responses
      const output: any[] = []

      for (const msg of input) {
        if (msg.role === 'user') {
          const activity = {
            type: 'message',
            text: msg?.contents?.[0]?.text || '',
            from: { id: 'user' },
            recipient: { id: 'bot' },
            conversation: { id: threadId },
            channelId: 'agent-protocol',
            serviceUrl: 'https://agent-protocol',
            channelData: { role: 'user' },
            removeRecipientMention: () => msg?.contents?.[0]?.text || ''
          }

          // Create a mock turn context to capture responses
          const mockContext = {
            activity,
            sendActivity: async (activityOrText: any) => {
              const responseActivity = typeof activityOrText === 'string'
                ? { text: activityOrText, value: null }
                : activityOrText

              // If there's a value field (Agent Protocol format), use it
              if (responseActivity.value) {
                output.push(responseActivity.value)
              } else if (responseActivity.text) {
                // Otherwise convert text to Agent Protocol format
                output.push({
                  role: 'assistant',
                  contents: [{ kind: 'text', text: responseActivity.text }]
                })
              }
              return { id: 'mock-id' }
            },
            sendActivities: async (activities: any[]) => {
              for (const act of activities) {
                const responseActivity = typeof act === 'string' ? { text: act, value: null } : act
                if (responseActivity.value) {
                  output.push(responseActivity.value)
                } else if (responseActivity.text) {
                  output.push({
                    role: 'assistant',
                    contents: [{ kind: 'text', text: responseActivity.text }]
                  })
                }
              }
              return activities.map(() => ({ id: 'mock-id' }))
            }
          }

          // Run the agent with mock context
          await agentApp.run(mockContext as any)
        }
      }

      // Get the response text for streaming
      let fullOutputText = ''
      if (output.length > 0) {
        const lastMessage = output[output.length - 1]
        if (lastMessage?.contents?.[0]?.text) {
          fullOutputText = lastMessage.contents[0].text
        }
      }

      // Stream the output text in chunks (word-by-word for visual effect)
      if (fullOutputText) {
        const words = fullOutputText.split(' ').filter(w => w.length > 0)

        for (let i = 0; i < words.length; i++) {
          let chunk = words[i]
          if (i > 0) chunk = ' ' + chunk // Add space before word (except first)

          // Event: message.delta with delta containing the text chunk
          sendEvent('message.delta', {
            runId,
            agentId,
            threadId,
            delta: {
              role: 'assistant',
              contents: [{ kind: 'text', text: chunk }]
            }
          })

          // Small delay to simulate streaming effect
          await new Promise(resolve => setTimeout(resolve, 30))
        }
      }

      const completedAt = new Date().toISOString()

      // Event: run.completed
      sendEvent('run.completed', {
        runId,
        agentId,
        threadId,
        status: 'completed',
        output,
        createdAt,
        completedAt
      })

      res.end()
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  })
}

server.get('/', (_req: express.Request, res: express.Response) => {
  res.send('Microsoft Agents SDK Sample')
})

// ==================================================================================
// LEGACY ENDPOINT - DO NOT MODIFY
// This is the Bot Framework /api/messages endpoint for backwards compatibility.
// It should work as-is with M365 Agents SDK bots sending plain text/Activity responses.
// For Agent Protocol functionality, use the Agent Protocol extension routes below.
// ==================================================================================
server.post('/api/messages', async (req: Request, res: Response) => {
  try {
    // In anonymous mode, handle messages directly without full Bot Framework auth
    if (!authConfig.clientId || !authConfig.clientSecret) {
      const activity = req.body
      const responses: string[] = []

      // Add missing methods to activity object
      if (activity && !activity.removeRecipientMention) {
        activity.removeRecipientMention = () => activity.text
      }

      // Create a mock turn context to capture responses
      const mockContext = {
        activity,
        sendActivity: async (activityOrText: any) => {
          const responseActivity = typeof activityOrText === 'string'
            ? { text: activityOrText, value: null }
            : activityOrText

          // If there's a value field (Agent Protocol format), extract text from it
          if (responseActivity.value) {
            const agentMessage = responseActivity.value
            if (agentMessage.contents && Array.isArray(agentMessage.contents)) {
              for (const content of agentMessage.contents) {
                if (content.kind === 'text' && content.text) {
                  responses.push(content.text)
                }
              }
            }
          } else if (responseActivity.text) {
            responses.push(responseActivity.text)
          }
          return { id: 'mock-id' }
        },
        sendActivities: async (activities: any[]) => {
          for (const act of activities) {
            const responseActivity = typeof act === 'string' ? { text: act, value: null } : act
            if (responseActivity.value) {
              const agentMessage = responseActivity.value
              if (agentMessage.contents && Array.isArray(agentMessage.contents)) {
                for (const content of agentMessage.contents) {
                  if (content.kind === 'text' && content.text) {
                    responses.push(content.text)
                  }
                }
              }
            } else if (responseActivity.text) {
              responses.push(responseActivity.text)
            }
          }
          return activities.map(() => ({ id: 'mock-id' }))
        }
      }

      // Run the agent with mock context
      await agentApp.run(mockContext as any)

      // Return the first response
      const responseText = responses[0] || 'OK'
      res.status(200).json({
        type: 'message',
        text: responseText,
        from: { id: 'bot' },
        recipient: activity?.from || { id: 'user' },
        conversation: activity?.conversation || { id: 'default' }
      })
    } else {
      // Use full Bot Framework adapter for authenticated requests
      await adapter.process(req, res, async (context: any) => {
        await agentApp.run(context)
      })
    }
  } catch (error: any) {
    console.error('Error processing message:', error)
    res.status(500).json({ error: error.message })
  }
})

// AGENT PROTOCOL EXTENSION: Modern Agent Protocol routes
// These routes (/health, /agent-card, /runs/wait, etc.) are added by setupAgentProtocolRoutes.
setupAgentProtocolRoutes(server)

// Read port from centralized agent-config.json
const port = getPortFromConfig() || process.env.PORT || 3983

server.listen(port, () => {
  console.log(`\nServer listening to port ${port} for appId ${authConfig.clientId} debug ${process.env.DEBUG}`)
}).on('error', (err) => {
  console.error(err)
  process.exit(1)
})
