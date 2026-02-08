# Echo Bot - TypeScript

This is a simple echo bot that demonstrates the Agent Protocol implementation in TypeScript.

## Key Feature

This sample shows the **one-line change** to add Agent Protocol support to your Express app:

```typescript
import { createAgentProtocolRouter } from '@microsoft/agents-protocol';

// Add Agent Protocol routes - just like .NET's app.MapAgentProtocol()!
app.use(createAgentProtocolRouter());
```

This single line adds all the Agent Protocol endpoints:
- `GET /health` - Health check
- `POST /runs` - Create a run
- `POST /runs/wait` - Create and wait for completion
- `POST /runs/stream` - Create and stream results
- `GET /runs/:runId/stream` - Stream a specific run

## Running the Sample

```bash
# Install dependencies
npm install

# Build
npm run build

# Run
npm start
```

The bot will start on port 3979 (or the port specified in `agent-config.json`).

## Comparison to .NET

**C# (.NET):**
```csharp
app.MapAgentProtocol();
```

**TypeScript:**
```typescript
app.use(createAgentProtocolRouter());
```

Both provide the same Agent Protocol endpoints with minimal code!
