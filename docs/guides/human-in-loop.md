# Human-in-the-Loop (HITL) Patterns Guide

**Version**: 1.1

## Overview

This guide explains how to implement human-in-the-loop workflows where agents pause execution to request approval, confirmation, or input from users before proceeding with sensitive or critical operations.

**What You'll Learn:**

- Understand the 11-state run lifecycle with HITL support
- Implement tool approval workflows with `requires_action` state
- Implement input collection workflows with `input_required` state
- Implement authentication workflows with `auth_required` state
- Use webhook notifications as alternative to polling
- Build UI components for approval forms
- Handle timeouts, escalations, and conditional approvals
- Integrate with compliance and audit systems

## Prerequisites

- **API Access**: Agent Runtime API endpoint and credentials
- **Programming Language**: Examples in Python and JavaScript
- **HTTP Client**: requests (Python), fetch (JavaScript)
- **UI Framework (Optional)**: React, Vue, or vanilla HTML for approval forms

## Quick Start

The Agent Protocol supports three distinct human-in-the-loop patterns:

1. **Tool Approval** (`requires_action`): Review and approve tool calls before execution
   - Route: `POST /runs/{runId}/submit_tool_outputs`
   - Use case: Approve file deletions, financial transactions, API calls

2. **Input Collection** (`input_required`): Collect clarifications or additional data
   - Route: `POST /runs/{runId}/submit_input`
   - Use case: Disambiguate user intent, collect missing parameters, confirm actions

3. **Authentication** (`auth_required`): Collect user credentials for protected resources
   - Route: `POST /runs/{runId}/submit_auth`
   - Use case: OAuth flows for Microsoft Graph, Google APIs, enterprise systems

All three patterns follow the same lifecycle:

```text
in_progress → [interruption_state] → submit_* → in_progress → completed
```

You can use webhooks (`Run.webhook` field) to receive notifications when runs pause for human input, avoiding polling.

## Use Cases

Human-in-the-loop workflows are critical for:

1. **Financial Operations**
   - Expense approvals above threshold
   - Payment processing confirmations
   - Budget allocation requests
   - Wire transfer authorizations

2. **Content Management**
   - Social media post reviews
   - Email campaign approvals
   - Content moderation decisions
   - Marketing material sign-offs

3. **Data Operations**
   - Sensitive data access requests
   - Data deletion confirmations
   - Database modification approvals
   - Bulk operation validations

4. **Compliance & Governance**
   - Contract signing workflows
   - Legal document reviews
   - Privacy policy changes
   - Audit trail generation

5. **Multi-Stakeholder Decisions**
   - Sequential approvals (manager → director → VP)
   - Parallel approvals (legal + finance + security)
   - Conditional routing based on approval results

## Architecture

### State Machine Flow

Human-in-the-loop workflows use three distinct interruption states in the 11-state run lifecycle:

1. **Tool Approval** (`requires_action`): Human reviews and approves tool calls
2. **Input Collection** (`input_required`): Agent requests clarification or additional data
3. **Authentication** (`auth_required`): Agent needs user credentials for protected resources

#### Tool Approval Flow

```text
Client                    Agent Runtime              Tool/System
  |                            |                            |
  | POST /runs                 |                            |
  |--------------------------->|                            |
  |                            | status: in_progress        |
  |                            | Agent requests tool call   |
  |                            |                            |
  |                            | status: requires_action    |
  |<---------------------------| (FunctionCallContent)      |
  |                            |                            |
  | User reviews tool calls    |                            |
  | [UI Approval Form]         |                            |
  |                            |                            |
  | POST /runs/{runId}/        |                            |
  |   submit_tool_outputs      |                            |
  |--------------------------->|                            |
  |                            | status: in_progress        |
  |                            | Execute approved tools     |
  |                            |--------------------------->|
  |                            | Tool results               |
  |                            |<---------------------------|
  |                            | status: completed          |
  |<---------------------------|                            |
```

#### Input Collection Flow

```text
Client                    Agent Runtime
  |                            |
  | POST /runs                 |
  |--------------------------->|
  |                            | status: in_progress
  |                            | Agent needs clarification
  |                            |
  |                            | status: input_required
  |<---------------------------| (UserInputRequestContent)
  |                            |
  | User provides input        |
  | [UI Input Form]            |
  |                            |
  | POST /runs/{runId}/        |
  |   submit_input             |
  |--------------------------->|
  |                            | status: in_progress
  |                            | Continue with input
  |                            | status: completed
  |<---------------------------|
```

#### Authentication Flow

```text
Client                    Agent Runtime              External Service
  |                            |                            |
  | POST /runs                 |                            |
  |--------------------------->|                            |
  |                            | status: in_progress        |
  |                            | Tool needs auth            |
  |                            |                            |
  |                            | status: auth_required      |
  |<---------------------------| (OAuth URL, scopes)        |
  |                            |                            |
  | User authenticates         |                            |
  | OAuth flow                 |--------------------------->|
  |                            |                     token  |
  |                            |<---------------------------|
  | POST /runs/{runId}/        |                            |
  |   submit_auth              |                            |
  |--------------------------->|                            |
  |                            | status: in_progress        |
  |                            | Use token for API calls    |
  |                            |--------------------------->|
  |                            | status: completed          |
  |<---------------------------|                            |
```

### Run Status Lifecycle (11 States)

The complete run lifecycle includes three HITL interruption states:

```text
queued → in_progress → requires_action (tool approval)
                          ↓
          ┌───────────────┴────────────────┐
          ↓                                ↓
    submit_tool_outputs              cancel/timeout
          ↓                                ↓
    in_progress                      cancelled/failed
          ↓
          ├──→ input_required (input collection)
          │         ↓
          │    submit_input
          │         ↓
          │    in_progress
          │
          ├──→ auth_required (authentication)
          │         ↓
          │    submit_auth
          │         ↓
          │    in_progress
          │
          ├──→ cancelling (user cancellation)
          │         ↓
          │    cancelled
          │
          └──→ completed / failed / incomplete / timeout
```

### Key Components

1. **RunStatus States** ([typespec/execution.tsp](/typespec/execution.tsp))
   - `requires_action`: Run pauses for tool approval (FunctionCallContent in output)
   - `input_required`: Run pauses for user input (UserInputRequestContent in output)
   - `auth_required`: Run pauses for authentication (auth details in output)
   - All three can transition back to `in_progress` after submission

2. **Content Types** ([typespec/messages.tsp](/typespec/messages.tsp))
   - `FunctionCallContent`: Tool call requiring approval (callId, name, arguments)
   - `UserInputRequestContent`: Input request with prompt and options (requestId, prompt, inputType)
   - Authentication details: OAuth URLs, required scopes, service info

3. **Submission Routes** ([typespec/routes.tsp](/typespec/routes.tsp))
   - `POST /runs/{runId}/submit_tool_outputs`: Submit approved tool results
   - `POST /runs/{runId}/submit_input`: Submit user input value
   - `POST /runs/{runId}/submit_auth`: Submit authentication token

4. **Run.webhook Field**
   - Optional webhook URL for completion notifications
   - Alternative to polling for async workflows
   - Receives POST notification when run status changes

## Implementation Patterns

### Pattern 1: Tool Approval Workflow

Tool approval workflows pause execution when the agent requests potentially dangerous or sensitive tool calls, allowing humans to review and approve before execution.

#### Step 1: Detect requires_action State

**Python:**

```python
import requests
import json

API_BASE = "https://agents.example.com/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_run_with_tool_approval(prompt: str, agent_config: dict):
    """Create run that may require tool approval"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent_config,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']
    status = result['status']

    print(f"Run {run_id} status: {status}")

    # Handle different states
    if status == 'requires_action':
        # Extract tool calls requiring approval
        tool_calls = [
            content for msg in result['output']
            for content in msg['contents']
            if content['kind'] == 'functionCall'
        ]

        if tool_calls:
            return handle_tool_approval(run_id, tool_calls)

    elif status == 'completed':
        return result

    else:
        # May still be in_progress, poll or wait
        return {"run_id": run_id, "status": status}

def handle_tool_approval(run_id: str, tool_calls: list):
    """Handle tool approval request"""
    print(f"\n{'='*60}")
    print(f"TOOL APPROVAL REQUIRED")
    print(f"{'='*60}")

    for tool_call in tool_calls:
        print(f"Call ID: {tool_call['callId']}")
        print(f"Tool: {tool_call['name']}")
        print(f"Arguments: {tool_call.get('arguments', '{}')}")
        print()

    print(f"{'='*60}\n")

    # Return for UI to handle
    return {
        "run_id": run_id,
        "status": "requires_action",
        "tool_calls": tool_calls
    }
```

**JavaScript:**

```javascript
async function createRunWithToolApproval(prompt, agentConfig) {
    const response = await fetch(`${API_BASE}/runs`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            agent: agentConfig,
            input: [{
                role: "user",
                contents: [{ kind: "text", text: prompt }]
            }]
        })
    });

    const result = await response.json();
    const { runId, status, output } = result;

    console.log(`Run ${runId} status: ${status}`);

    if (status === 'requires_action') {
        // Extract tool calls requiring approval
        const toolCalls = output
            .flatMap(msg => msg.contents)
            .filter(content => content.kind === 'functionCall');

        if (toolCalls.length > 0) {
            return {
                runId,
                status: 'requires_action',
                toolCalls
            };
        }
    }

    return result;
}
```

#### Step 2: Submit Tool Outputs

**Python:**

```python
def submit_tool_outputs(run_id: str, tool_outputs: list):
    """Submit tool execution results to resume run"""
    response = requests.post(
        f"{API_BASE}/runs/{run_id}/submit_tool_outputs",
        headers=headers,
        json={
            "tool_outputs": tool_outputs
        }
    )

    result = response.json()
    print(f"Run resumed with status: {result['status']}")

    # Run may complete or require more actions
    if result['status'] == 'requires_action':
        # Another tool approval needed
        return handle_tool_approval(run_id, extract_tool_calls(result))

    return result

# Example: Approve tool execution
approval_result = submit_tool_outputs(
    run_id="run_abc123",
    tool_outputs=[{
        "tool_call_id": "call_xyz789",
        "output": "File deleted successfully"
    }]
)

# Example: Reject with error
rejection_result = submit_tool_outputs(
    run_id="run_abc123",
    tool_outputs=[{
        "tool_call_id": "call_xyz789",
        "output": json.dumps({
            "error": "Permission denied",
            "reason": "User rejected file deletion"
        })
    }]
)
```

**JavaScript:**

```javascript
async function submitToolOutputs(runId, toolOutputs) {
    const response = await fetch(`${API_BASE}/runs/${runId}/submit_tool_outputs`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            tool_outputs: toolOutputs
        })
    });

    const result = await response.json();
    console.log(`Run resumed with status: ${result.status}`);

    return result;
}

// Example: Approve tool execution
await submitToolOutputs("run_abc123", [{
    tool_call_id: "call_xyz789",
    output: "File deleted successfully"
}]);

// Example: Reject with error
await submitToolOutputs("run_abc123", [{
    tool_call_id: "call_xyz789",
    output: JSON.stringify({
        error: "Permission denied",
        reason: "User rejected file deletion"
    })
}]);
```

### Pattern 2: Input Collection Workflow

Input collection workflows pause execution when the agent needs clarification, disambiguation, or additional information from the user.

#### Step 1: Detect input_required State

**Python:**

```python
def create_run_with_input_collection(prompt: str, agent_config: dict):
    """Create run that may require user input"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent_config,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']
    status = result['status']

    if status == 'input_required':
        # Extract input requests
        input_requests = [
            content for msg in result['output']
            for content in msg['contents']
            if content['kind'] == 'userInputRequest'
        ]

        if input_requests:
            return handle_input_request(run_id, input_requests[0])

    return {"run_id": run_id, "status": status}

def handle_input_request(run_id: str, request: dict):
    """Handle user input request"""
    print(f"\n{'='*60}")
    print(f"USER INPUT REQUIRED")
    print(f"{'='*60}")
    print(f"Request ID: {request['requestId']}")
    print(f"Prompt: {request['prompt']}")
    print(f"Type: {request.get('inputType', 'text')}")

    if request.get('choices'):
        print(f"Choices: {', '.join(request['choices'])}")

    print(f"{'='*60}\n")

    return {
        "run_id": run_id,
        "status": "input_required",
        "input_request": request
    }
```

#### Step 2: Submit User Input

**Python:**

```python
def submit_input(run_id: str, value: str):
    """Submit user input to resume run"""
    response = requests.post(
        f"{API_BASE}/runs/{run_id}/submit_input",
        headers=headers,
        json={"value": value}
    )

    result = response.json()
    print(f"Run resumed with status: {result['status']}")

    return result

# Example: Simple text input
result = submit_input("run_abc123", "Option 1")

# Example: Structured input
result = submit_input("run_abc123", json.dumps({
    "selection": "option_1",
    "additional_context": "Prefer expedited shipping"
}))
```

**JavaScript:**

```javascript
async function submitInput(runId, value) {
    const response = await fetch(`${API_BASE}/runs/${runId}/submit_input`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ value })
    });

    const result = await response.json();
    console.log(`Run resumed with status: ${result.status}`);

    return result;
}

// Example: Choice selection
await submitInput("run_abc123", "1");

// Example: Text clarification
await submitInput("run_abc123", "I meant the project from last quarter");
```

### Pattern 3: Authentication Workflow

Authentication workflows pause execution when the agent needs user credentials to access protected resources.

#### Step 1: Detect auth_required State

**Python:**

```python
def create_run_with_auth(prompt: str, agent_config: dict):
    """Create run that may require authentication"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent_config,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']
    status = result['status']

    if status == 'auth_required':
        # Extract auth requirements from run metadata or output
        auth_info = result.get('metadata', {}).get('required_auth', {})

        print(f"\n{'='*60}")
        print(f"AUTHENTICATION REQUIRED")
        print(f"{'='*60}")
        print(f"Service: {auth_info.get('service')}")
        print(f"Scopes: {auth_info.get('scopes')}")
        print(f"Auth URL: {auth_info.get('authUrl')}")
        print(f"{'='*60}\n")

        return {
            "run_id": run_id,
            "status": "auth_required",
            "auth_info": auth_info
        }

    return {"run_id": run_id, "status": status}
```

#### Step 2: Submit Authentication

**Python:**

```python
def submit_auth(run_id: str, token: str, token_type: str = "Bearer"):
    """Submit authentication token to resume run"""
    response = requests.post(
        f"{API_BASE}/runs/{run_id}/submit_auth",
        headers=headers,
        json={
            "token": token,
            "tokenType": token_type
        }
    )

    result = response.json()
    print(f"Run resumed with status: {result['status']}")

    return result

# Example: OAuth token
oauth_token = perform_oauth_flow(auth_url, scopes)
result = submit_auth("run_abc123", oauth_token, "Bearer")
```

**JavaScript:**

```javascript
async function submitAuth(runId, token, tokenType = "Bearer") {
    const response = await fetch(`${API_BASE}/runs/${runId}/submit_auth`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token,
            tokenType
        })
    });

    const result = await response.json();
    console.log(`Run resumed with status: ${result.status}`);

    return result;
}

// Example: Microsoft Graph OAuth
const oauthToken = await performOAuthFlow(authUrl, scopes);
await submitAuth("run_abc123", oauthToken);
```

### Pattern 4: Webhook Notifications

Use webhooks to receive notifications when runs complete, avoiding polling.

**Python:**

```python
def create_run_with_webhook(prompt: str, agent_config: dict, webhook_url: str):
    """Create run with webhook notification"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent_config,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "webhook": webhook_url  # Notification on completion
        }
    )

    result = response.json()
    print(f"Run {result['runId']} created, webhook will be called on completion")

    return result

# Webhook endpoint (Flask example)
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/run-completion', methods=['POST'])
def handle_run_completion():
    data = request.json
    run_id = data['runId']
    status = data['status']

    print(f"Run {run_id} completed with status: {status}")

    # Fetch full run details
    run = get_run(run_id)

    # Handle based on status
    if status == 'requires_action':
        handle_tool_approval(run_id, extract_tool_calls(run))
    elif status == 'input_required':
        handle_input_request(run_id, extract_input_request(run))
    elif status == 'completed':
        process_results(run)

    return {"status": "ok"}
```

### Build Approval UI Components

#### React Tool Approval Component

```javascript
import React, { useState } from 'react';

function ToolApprovalForm({ toolCalls, onSubmit, onCancel }) {
    const [outputs, setOutputs] = useState({});
    const [loading, setLoading] = useState(false);

    const handleApprove = async (toolCall) => {
        setLoading(true);
        try {
            // Execute tool and get result
            const result = await executeToolSafely(toolCall);

            // Build tool output
            const toolOutputs = [{
                tool_call_id: toolCall.callId,
                output: typeof result === 'string' ? result : JSON.stringify(result)
            }];

            await onSubmit(toolOutputs);
        } catch (error) {
            console.error('Tool execution failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleReject = async (toolCall) => {
        const toolOutputs = [{
            tool_call_id: toolCall.callId,
            output: JSON.stringify({
                error: "User rejected tool execution",
                rejected: true
            })
        }];

        await onSubmit(toolOutputs);
    };

    return (
        <div className="tool-approval-form">
            <div className="approval-header">
                <h3>Tool Approval Required</h3>
            </div>

            {toolCalls.map(toolCall => (
                <div key={toolCall.callId} className="tool-call">
                    <h4>{toolCall.name}</h4>
                    <pre className="arguments">
                        {JSON.stringify(
                            typeof toolCall.arguments === 'string'
                                ? JSON.parse(toolCall.arguments)
                                : toolCall.arguments,
                            null,
                            2
                        )}
                    </pre>

                    <div className="actions">
                        <button
                            onClick={() => handleApprove(toolCall)}
                            disabled={loading}
                            className="btn-approve"
                        >
                            ✓ Approve & Execute
                        </button>
                        <button
                            onClick={() => handleReject(toolCall)}
                            disabled={loading}
                            className="btn-reject"
                        >
                            ✗ Reject
                        </button>
                    </div>
                </div>
            ))}

            {loading && <div className="loading-overlay">Processing...</div>}
        </div>
    );
}
```

#### React Input Collection Component

```javascript
function InputRequestForm({ inputRequest, onSubmit, onCancel }) {
    const [value, setValue] = useState(inputRequest.defaultValue || '');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await onSubmit(value);
        } catch (error) {
            console.error('Submission failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderInput = () => {
        switch (inputRequest.inputType) {
            case 'confirmation':
                return (
                    <div className="confirmation-buttons">
                        <button
                            onClick={() => { setValue('yes'); handleSubmit(); }}
                            disabled={loading}
                            className="btn-confirm"
                        >
                            Yes
                        </button>
                        <button
                            onClick={() => { setValue('no'); handleSubmit(); }}
                            disabled={loading}
                            className="btn-cancel"
                        >
                            No
                        </button>
                    </div>
                );

            case 'choice':
                return (
                    <div className="choice-input">
                        <select
                            value={value}
                            onChange={(e) => setValue(e.target.value)}
                            disabled={loading}
                        >
                            <option value="">-- Select --</option>
                            {inputRequest.choices.map(choice => (
                                <option key={choice} value={choice}>{choice}</option>
                            ))}
                        </select>
                        <button
                            onClick={handleSubmit}
                            disabled={!value || loading}
                        >
                            Submit
                        </button>
                    </div>
                );

            case 'text':
            default:
                return (
                    <div className="text-input">
                        <textarea
                            value={value}
                            onChange={(e) => setValue(e.target.value)}
                            placeholder="Enter your response..."
                            rows={4}
                            disabled={loading}
                        />
                        <button
                            onClick={handleSubmit}
                            disabled={(!value && inputRequest.required) || loading}
                        >
                            Submit
                        </button>
                    </div>
                );
        }
    };

    return (
        <div className="input-request-form">
            <div className="form-header">
                <h3>Input Required</h3>
                {inputRequest.required && (
                    <span className="required-badge">Required</span>
                )}
            </div>

            <div className="form-content">
                <p className="prompt">{inputRequest.prompt}</p>
                {renderInput()}
            </div>

            {loading && <div className="loading-overlay">Processing...</div>}
        </div>
    );
}
```

#### App Component with All HITL Patterns

```javascript
function App() {
    const [runState, setRunState] = useState(null);

    const handleToolOutputs = async (toolOutputs) => {
        const result = await submitToolOutputs(runState.runId, toolOutputs);
        updateRunState(result);
    };

    const handleInputSubmit = async (value) => {
        const result = await submitInput(runState.runId, value);
        updateRunState(result);
    };

    const handleAuthSubmit = async (token) => {
        const result = await submitAuth(runState.runId, token);
        updateRunState(result);
    };

    const updateRunState = (result) => {
        if (result.status === 'completed') {
            console.log('Run completed!', result);
            setRunState(null);
        } else if (result.status === 'requires_action') {
            setRunState({
                runId: result.runId,
                status: 'requires_action',
                toolCalls: extractToolCalls(result)
            });
        } else if (result.status === 'input_required') {
            setRunState({
                runId: result.runId,
                status: 'input_required',
                inputRequest: extractInputRequest(result)
            });
        } else if (result.status === 'auth_required') {
            setRunState({
                runId: result.runId,
                status: 'auth_required',
                authInfo: extractAuthInfo(result)
            });
        }
    };

    return (
        <div>
            {runState?.status === 'requires_action' && (
                <ToolApprovalForm
                    toolCalls={runState.toolCalls}
                    onSubmit={handleToolOutputs}
                    onCancel={() => cancelRun(runState.runId)}
                />
            )}

            {runState?.status === 'input_required' && (
                <InputRequestForm
                    inputRequest={runState.inputRequest}
                    onSubmit={handleInputSubmit}
                    onCancel={() => cancelRun(runState.runId)}
                />
            )}

            {runState?.status === 'auth_required' && (
                <AuthForm
                    authInfo={runState.authInfo}
                    onSubmit={handleAuthSubmit}
                    onCancel={() => cancelRun(runState.runId)}
                />
            )}
        </div>
    );
}

// Helper functions
function extractToolCalls(result) {
    return result.output
        .flatMap(msg => msg.contents)
        .filter(content => content.kind === 'functionCall');
}

function extractInputRequest(result) {
    const requests = result.output
        .flatMap(msg => msg.contents)
        .filter(content => content.kind === 'userInputRequest');
    return requests[0];
}

function extractAuthInfo(result) {
    return result.metadata?.required_auth || {};
}
```

#### HTML + Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>Approval Form</title>
    <style>
        .approval-modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            max-width: 500px;
            width: 90%;
        }

        .approval-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .required-badge {
            background: #ff6b6b;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }

        .prompt {
            font-size: 16px;
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .btn-approve {
            background: #51cf66;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }

        .btn-reject {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }

        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div id="approval-container"></div>

    <script>
        function renderApprovalForm(inputRequest, runId) {
            const container = document.getElementById('approval-container');

            const modal = document.createElement('div');
            modal.className = 'approval-modal';
            modal.innerHTML = `
                <div class="approval-header">
                    <h3>Approval Required</h3>
                    ${inputRequest.required ? '<span class="required-badge">Required</span>' : ''}
                </div>
                <div class="approval-content">
                    <p class="prompt">${inputRequest.prompt}</p>
                    <div id="input-area"></div>
                </div>
            `;

            const inputArea = modal.querySelector('#input-area');

            if (inputRequest.inputType === 'confirmation') {
                inputArea.innerHTML = `
                    <button class="btn-approve" onclick="handleApproval(true)">✓ Approve</button>
                    <button class="btn-reject" onclick="handleApproval(false)">✗ Reject</button>
                `;
            } else if (inputRequest.inputType === 'choice') {
                const select = document.createElement('select');
                select.innerHTML = '<option value="">-- Select --</option>';
                inputRequest.choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.value = choice;
                    option.textContent = choice;
                    select.appendChild(option);
                });
                inputArea.appendChild(select);

                const submitBtn = document.createElement('button');
                submitBtn.textContent = 'Submit';
                submitBtn.onclick = () => handleApproval(select.value);
                inputArea.appendChild(submitBtn);
            } else {
                const textarea = document.createElement('textarea');
                textarea.rows = 4;
                textarea.placeholder = 'Enter your response...';
                inputArea.appendChild(textarea);

                const submitBtn = document.createElement('button');
                submitBtn.textContent = 'Submit';
                submitBtn.onclick = () => handleApproval(textarea.value);
                inputArea.appendChild(submitBtn);
            }

            container.appendChild(modal);
        }

        async function handleApproval(response) {
            const result = await submitUserInput(currentRunId, currentRequestId, response);
            document.getElementById('approval-container').innerHTML = '';

            if (result.status === 'completed') {
                alert('Request completed!');
            }
        }
    </script>
</body>
</html>
```

## Examples

### Example 1: Tool Approval for Delete Operations

This example demonstrates using `requires_action` state for dangerous file operations.

```python
def file_deletion_workflow(file_paths: list[str]):
    """
    Delete files with human approval using requires_action state
    """
    agent = {
        "type": "prompt",
        "model": "gpt-4o",
        "instructions": "You are a file management agent. Use delete_file tool to delete files.",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file from the filesystem",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path to delete"},
                            "reason": {"type": "string", "description": "Reason for deletion"}
                        },
                        "required": ["path"]
                    }
                }
            }
        ]
    }

    # Create run that will request file deletion
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": f"Delete these files: {', '.join(file_paths)}"
                }]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']

    # Wait for requires_action state
    while result['status'] in ['queued', 'in_progress']:
        time.sleep(1)
        result = requests.get(f"{API_BASE}/runs/{run_id}", headers=headers).json()

    if result['status'] == 'requires_action':
        # Extract tool calls
        tool_calls = [
            c for msg in result['output']
            for c in msg['contents']
            if c['kind'] == 'functionCall'
        ]

        print(f"\n{'='*60}")
        print(f"TOOL APPROVAL REQUIRED")
        print(f"{'='*60}")

        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call['name'] == 'delete_file':
                args = json.loads(tool_call['arguments']) if isinstance(tool_call['arguments'], str) else tool_call['arguments']
                file_path = args['path']

                print(f"Tool: delete_file")
                print(f"Path: {file_path}")
                print(f"Reason: {args.get('reason', 'N/A')}")

                # Get human approval
                approved = input(f"Approve deletion? (yes/no): ").lower() == 'yes'

                if approved:
                    # Actually delete the file
                    try:
                        os.remove(file_path)
                        output = f"File {file_path} deleted successfully"
                    except Exception as e:
                        output = json.dumps({"error": str(e)})
                else:
                    output = json.dumps({"error": "User rejected deletion", "approved": False})

                tool_outputs.append({
                    "tool_call_id": tool_call['callId'],
                    "output": output
                })

        # Submit tool outputs
        response = requests.post(
            f"{API_BASE}/runs/{run_id}/submit_tool_outputs",
            headers=headers,
            json={"tool_outputs": tool_outputs}
        )
        result = response.json()

    return result

# Example usage
result = file_deletion_workflow([
    "/tmp/old_data.csv",
    "/tmp/cache.json"
])
```

### Example 2: Content Moderation Workflow

```python
def content_moderation_workflow(content: str, platform: str):
    """
    Multi-step content review with approve/reject/edit options
    """
    agent = {
        "name": "ContentModerationAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": """
        You are a content moderation agent. Review content for:
        - Policy violations (hate speech, harassment, spam)
        - Brand safety (inappropriate language, off-brand messaging)
        - Legal compliance (copyright, privacy)

        For flagged content, request human review with specific concerns.
        """,
        "tools": [{
            "name": "request_content_review",
            "description": "Request human review of content",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "concerns": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "suggested_action": {"type": "string", "enum": ["approve", "reject", "edit"]}
                }
            }
        }]
    }

    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": f"Review this {platform} post: {content}"
                }]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']

    # Handle moderation workflow
    if result['status'] == 'input_required':
        input_request = [
            c for msg in result['output']
            for c in msg['contents']
            if c['type'] == 'userInputRequest'
        ][0]

        print(f"\nContent Review Required:")
        print(f"Original: {content}")
        print(f"Concerns: {input_request.get('additionalProperties', {}).get('concerns', [])}")
        print(f"Severity: {input_request.get('additionalProperties', {}).get('severity', 'unknown')}")

        # Present moderation UI
        action = input("Action (approve/reject/edit): ").lower()

        response_data = {"action": action}

        if action == "edit":
            edited_content = input("Enter edited version: ")
            response_data["edited_content"] = edited_content
        elif action == "reject":
            reason = input("Rejection reason: ")
            response_data["reason"] = reason

        response = requests.post(
            f"{API_BASE}/runs/{runId}/submit_input",
            headers=headers,
            json={
                "request_id": input_request['requestId'],
                "response": response_data
            }
        )
        result = response.json()

    return result

# Example scenarios
print("=== Safe content (auto-approve) ===")
result = content_moderation_workflow(
    "Excited to announce our new product launch! Check it out at our website.",
    "LinkedIn"
)

print("\n=== Borderline content (needs review) ===")
result = content_moderation_workflow(
    "Our competitors' products are terrible. Switch to us for quality!",
    "Twitter"
)

print("\n=== Problematic content (needs rejection/editing) ===")
result = content_moderation_workflow(
    "URGENT! Limited time offer! Click now or miss out forever!!!",
    "Email"
)
```

### Example 3: Sensitive Data Access

```python
def sensitive_data_access_workflow(user_id: str, data_type: str, justification: str):
    """
    Secure data access with justification and approval
    """
    agent = {
        "name": "DataAccessAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": """
        You manage access to sensitive data (PII, financial, health records).

        For any sensitive data access:
        1. Validate user has legitimate need
        2. Request access justification
        3. Get approval from data owner or compliance
        4. Log access for audit trail

        Use request_data_access_approval tool for sensitive data.
        """,
        "tools": [{
            "name": "request_data_access_approval",
            "description": "Request approval for sensitive data access",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "data_type": {"type": "string"},
                    "justification": {"type": "string"},
                    "data_classification": {
                        "type": "string",
                        "enum": ["public", "internal", "confidential", "restricted"]
                    }
                },
                "required": ["user_id", "data_type", "justification", "data_classification"]
            }
        }]
    }

    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": f"User {user_id} requests access to {data_type}. Justification: {justification}"
                }]
            }]
        }
    )

    result = response.json()
    run_id = result['runId']

    if result['status'] == 'input_required':
        input_request = [
            c for msg in result['output']
            for c in msg['contents']
            if c['type'] == 'userInputRequest'
        ][0]

        print(f"\n{'='*60}")
        print(f"SENSITIVE DATA ACCESS REQUEST")
        print(f"{'='*60}")
        print(f"User: {user_id}")
        print(f"Data Type: {data_type}")
        print(f"Justification: {justification}")
        print(f"Classification: {input_request.get('additionalProperties', {}).get('data_classification')}")
        print(f"{'='*60}\n")

        # Approval decision
        approved = input("Approve access? (yes/no): ").lower() == 'yes'

        response_data = {
            "approved": approved,
            "approver": "compliance@company.com",
            "timestamp": datetime.now().isoformat()
        }

        if approved:
            duration = input("Access duration (hours): ")
            response_data["access_duration_hours"] = int(duration)
            response_data["access_conditions"] = input("Any conditions? (optional): ")
        else:
            response_data["denial_reason"] = input("Denial reason: ")

        response = requests.post(
            f"{API_BASE}/runs/{runId}/submit_input",
            headers=headers,
            json={
                "request_id": input_request['requestId'],
                "response": response_data
            }
        )
        result = response.json()

    return result

# Example scenarios
print("=== Public data (auto-grant) ===")
result = sensitive_data_access_workflow(
    "alice@company.com",
    "product_catalog",
    "Need to update product descriptions"
)

print("\n=== Confidential data (approval required) ===")
result = sensitive_data_access_workflow(
    "bob@company.com",
    "customer_payment_info",
    "Investigating payment dispute for ticket #12345"
)

print("\n=== Restricted data (strict approval) ===")
result = sensitive_data_access_workflow(
    "charlie@company.com",
    "employee_health_records",
    "HR benefits audit Q4 2025"
)
```

### Example 4: Multi-Stakeholder Approval

```python
def multi_stakeholder_approval_workflow(contract_id: str, contract_value: float):
    """
    Sequential approval chain: Legal → Finance → Executive
    """
    approvers = []

    # Determine required approvers based on value
    if contract_value > 10000:
        approvers.append("legal")
    if contract_value > 50000:
        approvers.append("finance")
    if contract_value > 100000:
        approvers.append("executive")

    print(f"Contract {contract_id} (${contract_value:,.2f})")
    print(f"Required approvals: {' → '.join(approvers)}")

    for approver_role in approvers:
        print(f"\n{'='*60}")
        print(f"Requesting {approver_role.upper()} approval...")
        print(f"{'='*60}")

        # Simulate approval request
        input_request = {
            "requestId": f"contract_{contract_id}_{approver_role}",
            "prompt": f"Review and approve contract {contract_id} (${contract_value:,.2f})?",
            "inputType": "confirmation",
            "required": True,
            "additionalProperties": {
                "approver_role": approver_role,
                "contract_id": contract_id,
                "contract_value": contract_value
            }
        }

        # Get approval
        approved = input(f"{approver_role.capitalize()} approves? (yes/no): ").lower() == 'yes'

        if not approved:
            reason = input("Rejection reason: ")
            print(f"\n❌ Contract rejected by {approver_role}: {reason}")
            return {
                "status": "rejected",
                "rejected_by": approver_role,
                "reason": reason
            }

        comments = input(f"{approver_role.capitalize()} comments (optional): ")
        print(f"✓ {approver_role.capitalize()} approved")

        if comments:
            print(f"  Comments: {comments}")

    print(f"\n✓ Contract {contract_id} FULLY APPROVED")
    return {
        "status": "approved",
        "approvers": approvers,
        "final_approval_time": datetime.now().isoformat()
    }

# Example scenarios
print("=== Small contract (legal only) ===")
result = multi_stakeholder_approval_workflow("CNT-2025-001", 25000)

print("\n=== Medium contract (legal + finance) ===")
result = multi_stakeholder_approval_workflow("CNT-2025-002", 75000)

print("\n=== Large contract (legal + finance + executive) ===")
result = multi_stakeholder_approval_workflow("CNT-2025-003", 250000)
```

### Example 5: Conditional Auto-Approval

```python
def conditional_approval_workflow(
    transaction_type: str,
    amount: float,
    user_tier: str,
    previous_approvals: int
):
    """
    Auto-approve under certain conditions, otherwise require approval
    """
    # Define auto-approval rules
    auto_approve = False

    if user_tier == "premium" and amount < 1000:
        auto_approve = True
    elif user_tier == "standard" and amount < 500:
        auto_approve = True
    elif previous_approvals > 10 and amount < 200:
        auto_approve = True  # Trusted user

    if auto_approve:
        print(f"✓ AUTO-APPROVED: {transaction_type} ${amount}")
        print(f"  Reason: {user_tier} user, amount under threshold")
        return {
            "status": "approved",
            "approval_type": "automatic",
            "timestamp": datetime.now().isoformat()
        }

    # Manual approval required
    print(f"\n{'='*60}")
    print(f"MANUAL APPROVAL REQUIRED")
    print(f"{'='*60}")
    print(f"Transaction: {transaction_type}")
    print(f"Amount: ${amount}")
    print(f"User Tier: {user_tier}")
    print(f"Previous Approvals: {previous_approvals}")
    print(f"{'='*60}\n")

    approved = input("Approve? (yes/no): ").lower() == 'yes'

    if approved:
        return {
            "status": "approved",
            "approval_type": "manual",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "rejected",
            "reason": input("Rejection reason: "),
            "timestamp": datetime.now().isoformat()
        }

# Example scenarios
print("=== Premium user, small amount (auto-approve) ===")
result = conditional_approval_workflow("Refund", 450, "premium", 5)

print("\n=== Standard user, large amount (manual approval) ===")
result = conditional_approval_workflow("Refund", 850, "standard", 3)

print("\n=== Trusted user, small amount (auto-approve) ===")
result = conditional_approval_workflow("Refund", 150, "standard", 25)
```

### Example 6: Timeout Handling with Escalation

```python
import time
from datetime import datetime, timedelta

def approval_with_timeout(
    run_id: str,
    request_id: str,
    timeout_seconds: int = 300,  # 5 minutes
    escalate_to: str = "supervisor@company.com"
):
    """
    Request approval with timeout and automatic escalation
    """
    print(f"Approval requested (timeout: {timeout_seconds}s)")
    start_time = datetime.now()

    # Simulate waiting for approval
    time.sleep(2)  # In real app, this would be event-driven

    elapsed = (datetime.now() - start_time).total_seconds()

    if elapsed > timeout_seconds:
        print(f"\n⏰ TIMEOUT: No response after {timeout_seconds}s")
        print(f"Escalating to {escalate_to}...")

        # Create escalation request
        escalation_request = {
            "requestId": f"{request_id}_escalated",
            "prompt": f"ESCALATED: Original request timed out. Please review urgently.",
            "inputType": "confirmation",
            "required": True,
            "additionalProperties": {
                "original_request_id": request_id,
                "escalated_from": "primary_approver@company.com",
                "escalated_to": escalate_to,
                "escalation_reason": "timeout",
                "timeout_seconds": timeout_seconds
            }
        }

        # Submit escalated request
        response = requests.post(
            f"{API_BASE}/runs/{runId}/submit_input",
            headers=headers,
            json={
                "request_id": request_id,
                "response": {
                    "status": "escalated",
                    "escalated_to": escalate_to,
                    "new_request": escalation_request
                }
            }
        )

        return response.json()

    # Normal approval flow
    approved = input("Approve? (yes/no): ").lower() == 'yes'

    response = requests.post(
        f"{API_BASE}/runs/{runId}/submit_input",
        headers=headers,
        json={
            "request_id": request_id,
            "response": {
                "approved": approved,
                "response_time_seconds": elapsed
            }
        }
    )

    return response.json()

# Example: Email approval with 5-minute timeout
print("=== Email campaign approval (5-min timeout) ===")
result = approval_with_timeout(
    "run_abc123",
    "req_email_campaign_001",
    timeout_seconds=300,
    escalate_to="marketing_director@company.com"
)
```

## Troubleshooting

### Issue 1: Run Not Entering `input_required` State

**Problem**: Run completes without requesting approval

**Solutions:**
```python
# Ensure agent is configured to request approval
agent = {
    "instructions": """
    When approval is needed, you MUST create a UserInputRequestContent.
    Do not proceed without explicit approval.
    """,
    "tools": [{
        "name": "request_approval",
        "description": "Request user approval before proceeding",
        # ... tool definition
    }]
}

# Verify tool is being called
if result['status'] == 'requires_action':
    tool_calls = [c for msg in result['output'] for c in msg['contents'] if c['type'] == 'functionCall']
    print(f"Tool calls: {[t['name'] for t in tool_calls]}")
```

### Issue 2: Missing `UserInputRequestContent`

**Problem**: `input_required` state but no input request content

**Solutions:**
```python
# Check all message contents
for msg in result['output']:
    for content in msg['contents']:
        print(f"Content type: {content['type']}")
        if content['type'] == 'userInputRequest':
            print(f"Found request: {content['requestId']}")

# Ensure tool result creates UserInputRequestContent
tool_result = {
    "callId": tool_call['callId'],
    "result": json.dumps({
        "type": "userInputRequest",
        "requestId": f"approval_{run_id}",
        "prompt": "Please approve this action",
        "inputType": "confirmation",
        "required": True
    })
}
```

### Issue 3: Input Submission Rejected

**Problem**: `submit_user_input` returns error

**Solutions:**
```python
# Verify request_id matches exactly
input_request = extract_input_request(result)
print(f"Request ID: {input_request['requestId']}")

# Ensure response format matches inputType
if input_request['inputType'] == 'confirmation':
    response_data = {"approved": True}  # Boolean
elif input_request['inputType'] == 'choice':
    response_data = input_request['choices'][0]  # Must be from choices
elif input_request['inputType'] == 'text':
    response_data = "User's text response"  # String

# Check run is still in input_required state
current_status = requests.get(f"{API_BASE}/runs/{run_id}", headers=headers).json()
print(f"Current status: {current_status['status']}")
```

### Issue 4: Timeout Not Handled

**Problem**: Approval hangs indefinitely

**Solutions:**
```python
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

# Set alarm for timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)  # 5 minutes

try:
    # Wait for approval
    approval = wait_for_user_input(request_id)
except TimeoutException:
    # Handle timeout
    print("Approval timed out, escalating...")
    escalate_request(request_id)
finally:
    signal.alarm(0)  # Cancel alarm
```

### Issue 5: Audit Trail Missing

**Problem**: Approvals not logged for compliance

**Solutions:**
```python
def submit_user_input_with_audit(run_id: str, request_id: str, response: dict):
    """Submit input with full audit trail"""
    # Enrich response with audit metadata
    audit_response = {
        **response,
        "audit": {
            "approver_id": get_current_user_id(),
            "approver_ip": get_client_ip(),
            "timestamp": datetime.now().isoformat(),
            "user_agent": get_user_agent(),
            "session_id": get_session_id()
        }
    }

    # Submit
    result = requests.post(
        f"{API_BASE}/runs/{runId}/submit_input",
        headers=headers,
        json={
            "request_id": request_id,
            "response": audit_response
        }
    )

    # Log to audit system
    log_approval_event({
        "run_id": run_id,
        "request_id": request_id,
        "approved": response.get("approved"),
        "approver": audit_response["audit"]["approver_id"],
        "timestamp": audit_response["audit"]["timestamp"]
    })

    return result.json()
```

## Blocking Hooks for Human-in-the-Loop

While `input_required` state provides explicit approval workflows, **blocking hooks** offer an alternative HITL pattern where you can automatically block execution based on policy conditions, requiring human intervention to proceed.

**Key Differences:**

| Pattern | `input_required` State | Blocking Hooks |
|---------|----------------------|----------------|
| **Trigger** | Agent explicitly requests input | Automatic policy evaluation |
| **Control** | Agent decides when to ask | System enforces policies |
| **Flexibility** | Dynamic approval prompts | Pre-configured rules |
| **Use Case** | Contextual approvals | Policy enforcement, compliance |

### Hook Types for Blocking

#### 1. BlockHook - Simple Policy Enforcement

**Purpose**: Unconditionally block execution when condition is met

**Use Case**: Simple content filtering, keyword blocking, policy violations

**Example - Block Prohibited Content**:

```python
# Configure agent with BlockHook
agent_config = {
    "name": "Content Agent",
    "model": "gpt-4o",
    "instructions": "Generate marketing content",
    "hooks": [{
        "kind": "block",
        "condition": {
            "kind": "content",
            "keywords": ["prohibited", "banned", "illegal"],
            "caseSensitive": False
        },
        "reason": "Content contains prohibited keywords",
        "eventTypes": ["content.created", "message.created"]
    }]
}

# Create run
response = requests.post(
    f"{API_BASE}/runs",
    headers=headers,
    json={
        "agent": agent_config,
        "input": [{
            "role": "user",
            "contents": [{"kind": "text", "text": "Write about our prohibited product"}]
        }]
    }
)

result = response.json()

# If content contains prohibited keywords:
# result["status"] == "failed"
# result["error"]["code"] == "hook_blocked"
# result["error"]["message"] == "Content contains prohibited keywords"
```

**Example - Block Based on User Role**:

```python
# Block execution for unauthorized users
agent_config = {
    "name": "Sensitive Data Agent",
    "model": "gpt-4o",
    "instructions": "Access sensitive customer data",
    "hooks": [{
        "kind": "block",
        "condition": {
            "kind": "expression",
            "language": "cel",
            "expression": "!user.roles.contains('admin') && !user.roles.contains('compliance')"
        },
        "reason": "User lacks required permissions",
        "eventTypes": ["run.started"]
    }]
}

# Run fails immediately if user not admin/compliance
```

#### 2. RemoteHook - Custom Approval Logic

**Purpose**: Call external service for approval decision

**Use Case**: Complex approval workflows, human review, ML-based moderation

**Example - Content Moderation with Human Review**:

```python
# Remote hook endpoint (Flask example)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/review-content', methods=['POST'])
def review_content():
    """Remote hook endpoint for content review"""
    event = request.json

    # Extract content
    if event['event']['type'] == 'content.created':
        content = event['event']['data']['content']

        # Automated checks
        toxicity_score = check_toxicity(content)

        if toxicity_score > 0.8:
            # Block immediately for high toxicity
            return jsonify({
                "kind": "block",
                "reason": "Content flagged as highly toxic",
                "errorCode": "TOXICITY_THRESHOLD_EXCEEDED"
            })

        elif toxicity_score > 0.5:
            # Require human review
            review_id = create_review_ticket(content, toxicity_score)

            return jsonify({
                "kind": "block",
                "reason": f"Content requires human review (ticket #{review_id})",
                "errorCode": "MANUAL_REVIEW_REQUIRED"
            })

        else:
            # Allow
            return jsonify({
                "kind": "allow"
            })

    return jsonify({"kind": "allow"})

def check_toxicity(content: str) -> float:
    """Check content toxicity (0.0-1.0)"""
    # Call moderation API
    response = requests.post(
        "https://moderation-api.example.com/analyze",
        json={"text": content}
    )
    return response.json()["toxicity_score"]

def create_review_ticket(content: str, score: float) -> str:
    """Create ticket for human review"""
    response = requests.post(
        "https://review-system.example.com/tickets",
        json={
            "content": content,
            "toxicity_score": score,
            "priority": "high" if score > 0.7 else "medium",
            "status": "pending_review"
        }
    )
    return response.json()["ticket_id"]
```

**Agent Configuration**:

```python
agent_config = {
    "name": "Social Media Agent",
    "model": "gpt-4o",
    "instructions": "Generate social media posts",
    "hooks": [{
        "kind": "remote",
        "endpoint": "https://hooks.example.com/review-content",
        "connection": {
            "kind": "key",
            "key": "hook_secret_key_123",
            "headerName": "X-Hook-Secret"
        },
        "eventTypes": ["content.created"],
        "mode": "blocking",
        "timeout": 5000  # 5 seconds
    }]
}

# Client workflow
response = requests.post(
    f"{API_BASE}/runs",
    headers=headers,
    json={
        "agent": agent_config,
        "input": [{
            "role": "user",
            "contents": [{"kind": "text", "text": "Generate a tweet"}]
        }]
    }
)

result = response.json()

if result["status"] == "failed" and result["error"]["code"] == "hook_blocked":
    # Check if manual review required
    if "MANUAL_REVIEW_REQUIRED" in result["error"]["message"]:
        ticket_id = extract_ticket_id(result["error"]["message"])
        print(f"Content sent for human review: Ticket #{ticket_id}")
        print("Run will remain blocked until review completed")
```

### Real-World Examples

#### Example 1: Financial Transaction Approval with Hooks

```python
def financial_transaction_with_hooks(amount: float, recipient: str):
    """
    Use RemoteHook for real-time approval of financial transactions
    """

    # Remote hook checks approval requirements
    @app.route('/approve-transaction', methods=['POST'])
    def approve_transaction():
        event = request.json

        # Extract transaction details
        run_data = event['event']['data']
        transaction = extract_transaction_details(run_data)

        # Auto-approve small amounts
        if transaction['amount'] < 100:
            return jsonify({"kind": "allow"})

        # Require approval for large amounts
        approval_request_id = create_approval_request(
            amount=transaction['amount'],
            recipient=transaction['recipient'],
            requester=event['context']['userId']
        )

        # Block and wait for approval
        return jsonify({
            "kind": "block",
            "reason": f"Transaction requires approval (request #{approval_request_id})",
            "errorCode": "APPROVAL_REQUIRED"
        })

    # Agent with RemoteHook
    agent = {
        "name": "Payment Agent",
        "model": "gpt-4o",
        "instructions": "Process payment transactions",
        "hooks": [{
            "kind": "remote",
            "endpoint": "https://hooks.example.com/approve-transaction",
            "eventTypes": ["run.started"],
            "mode": "blocking",
            "timeout": 30000  # 30 seconds
        }],
        "tools": [{
            "name": "process_payment",
            "description": "Process payment transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "recipient": {"type": "string"}
                }
            }
        }]
    }

    # Run is blocked until approval granted
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": f"Send ${amount} to {recipient}"
                }]
            }]
        }
    )

    result = response.json()

    if result["status"] == "failed":
        print(f"Transaction blocked: {result['error']['message']}")
        # Notify user that approval is pending
        # Run can be resumed after approval via webhook/polling
```

#### Example 2: PII Detection and Blocking

```python
def pii_detection_with_hooks():
    """
    Block execution if PII detected in content
    """

    agent = {
        "name": "Customer Service Agent",
        "model": "gpt-4o",
        "instructions": "Help customers with support questions",
        "hooks": [
            {
                "kind": "remote",
                "endpoint": "https://hooks.example.com/detect-pii",
                "eventTypes": ["content.created", "message.created"],
                "mode": "blocking",
                "timeout": 3000
            }
        ]
    }

    # Remote hook for PII detection
    @app.route('/detect-pii', methods=['POST'])
    def detect_pii():
        event = request.json
        content = extract_content(event)

        # Check for PII patterns
        pii_types = detect_pii_patterns(content)

        if pii_types:
            return jsonify({
                "kind": "block",
                "reason": f"Content contains PII: {', '.join(pii_types)}",
                "errorCode": "PII_DETECTED"
            })

        return jsonify({"kind": "allow"})

    def detect_pii_patterns(content: str) -> list:
        """Detect PII in content"""
        pii_found = []

        # SSN pattern
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', content):
            pii_found.append("SSN")

        # Credit card pattern
        if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', content):
            pii_found.append("Credit Card")

        # Email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            pii_found.append("Email")

        return pii_found
```

#### Example 3: Compliance Checking

```python
def compliance_checking_with_hooks():
    """
    Block execution if content violates compliance policies
    """

    agent = {
        "name": "Legal Document Agent",
        "model": "gpt-4o",
        "instructions": "Generate legal documents",
        "hooks": [{
            "kind": "remote",
            "endpoint": "https://hooks.example.com/compliance-check",
            "eventTypes": ["message.created"],
            "mode": "blocking",
            "timeout": 10000  # 10 seconds for thorough check
        }]
    }

    @app.route('/compliance-check', methods=['POST'])
    def compliance_check():
        event = request.json
        content = extract_content(event)

        # Run compliance checks
        violations = []

        # Check for required disclaimers
        if not contains_required_disclaimers(content):
            violations.append("Missing required legal disclaimers")

        # Check for prohibited statements
        if contains_prohibited_statements(content):
            violations.append("Contains prohibited legal statements")

        # Check for regulatory compliance
        if not meets_regulatory_requirements(content):
            violations.append("Does not meet regulatory requirements")

        if violations:
            return jsonify({
                "kind": "block",
                "reason": "Compliance violations detected",
                "errorCode": "COMPLIANCE_VIOLATION",
                "metadata": {
                    "violations": violations,
                    "review_required": True
                }
            })

        return jsonify({"kind": "allow"})

    # Run with compliance checking
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": "Generate a service agreement"
                }]
            }]
        }
    )

    result = response.json()

    if result["status"] == "failed":
        error = result["error"]
        if error["code"] == "hook_blocked":
            violations = error.get("metadata", {}).get("violations", [])
            print(f"Compliance check failed:")
            for violation in violations:
                print(f"  - {violation}")
            print("Document requires legal review before finalization")
```

### When to Use Blocking Hooks vs input_required

**Use Blocking Hooks When:**

- Policy enforcement is consistent and rule-based
- You want automatic rejection without agent decision-making
- Approval logic can be pre-configured
- You need to block based on content analysis (PII, toxicity, compliance)
- Multiple runs need same approval logic

**Use input_required State When:**

- Agent needs to request approval contextually
- Approval prompts should be dynamic based on agent reasoning
- You need rich approval UI with multiple options
- Approval is part of agent's workflow logic
- Human needs to provide additional information beyond yes/no

**Combine Both When:**

- Start with blocking hooks for automated policy checks
- Use input_required for contextual approvals that pass automated checks
- Example: Block PII automatically, then request human approval for high-value transactions

```python
# Combined approach
agent = {
    "name": "Transaction Agent",
    "model": "gpt-4o",
    "instructions": """
    Process transactions. For amounts over $1000, request explicit approval.
    """,
    "hooks": [
        {
            # Automatic PII blocking
            "kind": "remote",
            "endpoint": "https://hooks.example.com/pii-check",
            "eventTypes": ["content.created"],
            "mode": "blocking"
        },
        {
            # Automatic compliance check
            "kind": "remote",
            "endpoint": "https://hooks.example.com/compliance",
            "eventTypes": ["run.started"],
            "mode": "blocking"
        }
    ],
    "tools": [{
        "name": "request_approval",
        "description": "Request human approval for high-value transaction",
        # Agent calls this for amounts > $1000
    }]
}

# Flow:
# 1. Hooks automatically check PII and compliance
# 2. If hooks pass, agent proceeds
# 3. Agent evaluates transaction amount
# 4. If > $1000, agent requests approval via input_required state
# 5. Human approves/rejects in UI
```

### Best Practices

1. **Set Appropriate Timeouts**:

   ```python
   {
       "kind": "remote",
       "timeout": 5000,  # 5 seconds for fast checks
       # Use longer timeouts for human review scenarios
   }
   ```

2. **Provide Clear Block Reasons**:

   ```python
   {
       "kind": "block",
       "reason": "Content contains credit card number (PII violation)",
       "errorCode": "PII_CREDIT_CARD"  # Machine-readable code
   }
   ```

3. **Use Fallback Behavior Appropriately**:

   - Early events (`run.started`): Fail closed (block on hook failure)
   - Late events (`message.completed`): Fail open (allow on hook failure)

4. **Log All Blocking Decisions**:

   ```python
   @app.route('/approval-hook', methods=['POST'])
   def approval_hook():
       event = request.json
       decision = evaluate_policy(event)

       # Always log blocking decisions for audit
       log_decision({
           "runId": event['context']['runId'],
           "decision": decision['kind'],
           "reason": decision.get('reason'),
           "timestamp": datetime.now().isoformat()
       })

       return jsonify(decision)
   ```

5. **Handle Hook Failures Gracefully**:

   ```python
   # Client-side handling
   if result["status"] == "failed":
       if result["error"]["code"] == "hook_blocked":
           # Policy violation - inform user
           display_policy_violation(result["error"])
       elif result["error"]["code"] == "hook_timeout":
           # Approval system unavailable - retry or escalate
           retry_with_fallback()
   ```

## Next Steps

Now that you understand HITL patterns:

1. **[Proactive Messaging](./proactive-messaging.md)** - Combine HITL with event-driven workflows
2. **[Multi-Agent](./multi-agent.md)** - Coordinate approvals across multiple agents
3. **[Webhooks](./webhooks.md)** - Real-time approval notifications
4. **[Voice Integration](./voice-integration.md)** - Voice-based approvals

## Related Documentation

- **[Execution Types](/typespec/execution.tsp)** - RunStatus and 11-state lifecycle transitions
- **[Message Types](/typespec/messages.tsp)** - UserInputRequestContent, FunctionCallContent specifications
- **[Routes](/typespec/routes.tsp)** - submit_tool_outputs, submit_input, submit_auth endpoints
- **[Webhooks Guide](./webhooks.md)** - Real-time notifications for run completion
