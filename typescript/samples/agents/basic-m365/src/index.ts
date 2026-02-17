// Copyright (c) Microsoft. All rights reserved.

// Sample that shows how to create an Agent Protocol agent that is hosted using the M365 Agent SDK.
// The agent can then be consumed from various M365 channels.
// Agent Protocol routes are added via mapAgentProtocol() - the TypeScript equivalent of .NET's app.MapAgentProtocol()
// See the README.md for more information.

import express, { Request, Response } from 'express'
import { CloudAdapter, getAuthConfigWithDefaults, AuthConfiguration } from '@microsoft/agents-hosting'
import { mapAgentProtocol } from '@microsoft/agents-protocol-hosting'
import { agentApp } from './agent'

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
    agentApp.run(context)
  )
)

// AGENT PROTOCOL EXTENSION: Add Agent Protocol routes
// Pass agentApp so Agent Protocol routes use the actual agent with LLM capabilities
mapAgentProtocol(server, agentApp)

// Get port from environment variable or use default
const port = parseInt(process.env.PORT || '3983', 10)

server.listen(port, () => {
  console.log(`\nServer listening on port ${port} for appId ${authConfig.clientId}`)
  console.log('Legacy M365 endpoint: POST /api/messages')
  console.log('Agent Protocol routes: GET /health, GET /agent-card')
}).on('error', console.error)
