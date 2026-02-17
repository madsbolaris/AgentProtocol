// Copyright (c) Microsoft. All rights reserved.

// Sample that shows how to create an Agent Protocol agent that is hosted using the M365 Agent SDK.
// The agent can then be consumed from various M365 channels.
// Agent Protocol routes are added via mapAgentProtocol() - the TypeScript equivalent of .NET's app.MapAgentProtocol()
// See the README.md for more information.

import express, { Request, Response } from 'express'
import { AgentApplication, MemoryStorage, TurnContext, TurnState, AuthConfiguration, CloudAdapter, getAuthConfigWithDefaults } from '@microsoft/agents-hosting'
import { mapAgentProtocol } from '@microsoft/agents-protocol-hosting'

// Create the M365 agent (original code from M365 Agents SDK)
const echo = new AgentApplication<TurnState>({ storage: new MemoryStorage() })
echo.onConversationUpdate('membersAdded', async (context: TurnContext) => {
  await context.sendActivity('Welcome to the Echo sample, send a message to see the echo feature in action.')
})
echo.onActivity('message', async (context: TurnContext, state: TurnState) => {
  let counter: number = state.getValue('conversation.counter') || 0
  await context.sendActivity(`[${counter++}]You said: ${context.activity.text}`)
  state.setValue('conversation.counter', counter)
})

// Set up Express server
const authConfig: AuthConfiguration = getAuthConfigWithDefaults()
const adapter = new CloudAdapter()
const server = express()
server.use(express.json())

// ==================================================================================
// LEGACY ENDPOINT - DO NOT MODIFY
// This is the Bot Framework /api/messages endpoint for backwards compatibility.
// It receives incoming messages from Azure Bot Service or other M365 channels.
// For Agent Protocol functionality, use the routes added by mapAgentProtocol below.
// ==================================================================================
server.post('/api/messages', (req: Request, res: Response) =>
  adapter.process(req, res, (context) =>
    echo.run(context)
  )
)

// AGENT PROTOCOL EXTENSION: Add Agent Protocol routes
mapAgentProtocol(server)

// Get port from environment variable or use default
const port = parseInt(process.env.PORT || '3980', 10)

server.listen(port, () => {
  console.log(`\nServer listening on port ${port} for appId ${authConfig.clientId}`)
  console.log('Legacy M365 endpoint: POST /api/messages')
  console.log('Agent Protocol routes: GET /health, GET /agent-card')
}).on('error', console.error)
