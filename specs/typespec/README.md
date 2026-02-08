# TypeSpec API Contracts

This directory contains TypeSpec schema definitions for the Agent Runtime API.

## Overview

TypeSpec is a language for defining APIs and generating OpenAPI specifications, client SDKs, and documentation. These files define the **structure** of the API (models, endpoints, types) but not the **behavior** (state machines, validation rules, error semantics).

## File Organization

| File | Purpose |
|------|---------|
| **agents.tsp** | Agent definitions, agent cards, guardrails, handoff patterns |
| **common.tsp** | Shared types (Connection, Scope, Participant, SessionInfo) |
| **execution.tsp** | Run lifecycle models (Run, Thread, Session, RunStatus) |
| **memory.tsp** | Conversation memory patterns and configuration |
| **messages.tsp** | ChatMessage model and all AIContent types (text, image, audio, video, tool calls, etc.) |
| **routes.tsp** | REST API operations (GET/POST/DELETE endpoints) |
| **tools.tsp** | Tool definitions, parameters, lifecycle hooks |
| **usage.tsp** | Token usage tracking and completion metadata |

## Key Concepts

### Models (What)
TypeSpec defines data structures:
- `Thread` - conversation container
- `Run` - agent execution instance
- `ChatMessage` - message with role and content
- `AgentDefinition` - agent configuration
- `AIContent` - multi-modal content union type

### Operations (How to Call)
TypeSpec defines REST operations:
- `POST /runs` - start agent execution
- `GET /threads/{threadId}/messages` - retrieve messages
- `POST /runs/{runId}/cancel` - cancel running execution

### Behavioral Requirements (Separate)
For state machines, validation rules, and error semantics, see:
- [Specifications](../docs/specifications/) - behavioral requirements
- [Guides](../docs/guides/) - integration patterns

## Recent Features

### Streaming Tool Input/Output
- `FunctionCallContent` and `FunctionResultContent` support streaming via `sequenceNumber` and `isFinalChunk`
- Consistent with `AudioContent`/`VideoContent` streaming pattern
- Enables large file uploads and progressive result streaming

### Content Encryption
- `ContentAnnotations.encryption` supports end-to-end encryption for all content types
- Algorithms: AES-256-GCM, ChaCha20-Poly1305
- Universal support via annotations (text, reasoning, tool results, images, etc.)

### Run Cancellation
- `POST /runs/{runId}/cancel` endpoint for user-initiated cancellation
- `Run.cancelledAt` and `Run.cancellationReason` track cancellation
- Support for "stop generating" button UX

## Documentation

- **API Reference**: [api-reference/](../docs/api-reference/) - explains models and operations
- **Specifications**: [specifications/](../docs/specifications/) - behavioral requirements
- **Guides**: [guides/](../docs/guides/) - integration patterns

## Compiling TypeSpec

To generate OpenAPI specifications from TypeSpec:

```bash
# Install TypeSpec compiler
npm install -g @typespec/compiler

# Compile TypeSpec to OpenAPI
tsp compile .
```

## Cross-Framework Alignment

These TypeSpec definitions align with:
- **Microsoft Agent Framework (MAF)** - ChatMessage, Run, Thread models
- **OpenAI Agents SDK** - Tool system, streaming, voice pipelines
- **Azure Agent API** - Multi-modal content types (audio, video, file)
- **Google A2A Protocol** - Agent cards, discovery, task lifecycle
- **LangGraph** - State management, checkpointing, HITL patterns

See [specifications directory](../docs/specifications/) for detailed behavioral requirements.
