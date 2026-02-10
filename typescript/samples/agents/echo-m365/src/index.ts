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
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
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

    return config?.bots?.typescript?.port || null
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
        }
      }
    }

    xml += `  </${role}>\n`
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
      const { agentId = 'agent', input = [] } = req.body
      const runId = generateRunId()

      res.setHeader('Content-Type', 'text/event-stream')
      res.setHeader('Cache-Control', 'no-cache')
      res.setHeader('Connection', 'keep-alive')

      // Send run.started event
      res.write(`event: run.started\n`)
      res.write(`data: ${JSON.stringify({ runId, agentId, status: 'in_progress' })}\n\n`)

      // TODO: Process through agent and stream results
      // Only process first user message
      const firstMsg = input.find((msg: any) => msg.role === 'user')
      const text = firstMsg?.contents?.[0]?.text || ''

      const messageId = generateMessageId()

      // Send message.created event
      res.write(`event: message.created\n`)
      res.write(`data: ${JSON.stringify({ runId, messageId, role: 'assistant' })}\n\n`)

      // Stream the text in chunks
      const words = text.split(' ')
      for (let i = 0; i < words.length; i++) {
        res.write(`event: message.updated\n`)
        res.write(`data: ${JSON.stringify({
          runId,
          messageId,
          contents: [{ kind: 'text', text: words.slice(0, i + 1).join(' ') }]
        })}\n\n`)
        await new Promise<void>(resolve => global.setTimeout(resolve, 50))
      }

      // Send message.completed event
      res.write(`event: message.completed\n`)
      res.write(`data: ${JSON.stringify({ runId, messageId })}\n\n`)

      // Send run.completed event
      res.write(`event: run.completed\n`)
      res.write(`data: ${JSON.stringify({ runId, status: 'completed' })}\n\n`)

      res.end()
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  })
}

server.get('/', (_req: express.Request, res: express.Response) => {
  res.send('Microsoft Agents SDK Sample')
})

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
          const text = typeof activityOrText === 'string' ? activityOrText : activityOrText.text
          responses.push(text)
          return { id: 'mock-id' }
        },
        sendActivities: async (activities: any[]) => {
          activities.forEach(act => {
            const text = typeof act === 'string' ? act : act.text
            if (text) responses.push(text)
          })
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

// Add Agent Protocol routes
setupAgentProtocolRoutes(server)

// Read port from centralized agent-config.json
const port = getPortFromConfig() || process.env.PORT || 3980

server.listen(port, () => {
  console.log(`\nServer listening to port ${port} for appId ${authConfig.clientId} debug ${process.env.DEBUG}`)
}).on('error', (err) => {
  console.error(err)
  process.exit(1)
})
