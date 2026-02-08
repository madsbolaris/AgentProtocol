# Testing Agents Guide

**Version**: 1.0
**Last Updated**: 2026-02-07

## Overview

Testing agent systems requires specialized approaches that account for non-deterministic LLM behavior, tool execution patterns, state transitions, and multi-agent coordination. This guide provides comprehensive strategies for testing agents at unit, integration, and system levels.

**What You'll Learn:**

- Unit testing agent behavior with deterministic fixtures
- Mocking tool calls and LLM responses
- Integration testing multi-agent systems
- Testing HITL patterns (requires_action, input_required, auth_required)
- Testing auto-response with ThreadWatch
- Validation strategies for run state transitions
- Test fixtures and factories for agent testing
- CI/CD integration patterns
- Performance and load testing for agent systems

**Key Concepts:**

- **Unit Testing**: Test individual agent components in isolation
- **Integration Testing**: Test agent interactions with tools, threads, and other agents
- **System Testing**: Test complete workflows end-to-end
- **Mock Objects**: Simulate LLM responses and external dependencies
- **Fixtures**: Reusable test data and agent configurations
- **State Validation**: Verify run lifecycle transitions
- **Deterministic Testing**: Achieve reproducible results despite non-determinism

## Prerequisites

- **Testing Framework**: pytest (Python) or Jest/Vitest (JavaScript/TypeScript)
- **Mocking Library**: unittest.mock (Python) or jest.mock (JavaScript)
- **HTTP Mocking**: responses (Python) or nock (JavaScript)
- **Agent Runtime API**: Access to test environment

## Use Cases

Testing is critical for:

### Agent Behavior Validation
- Verify agent follows instructions correctly
- Test tool selection and parameter generation
- Validate response quality and format
- Ensure consistent behavior across runs

### Tool Execution Testing
- Mock external API calls
- Test error handling in tool execution
- Validate tool parameter parsing
- Test parallel tool execution

### State Transition Testing
- Verify run lifecycle correctness (11 states)
- Test interruption states (requires_action, input_required, auth_required)
- Validate state recovery after failures
- Test timeout and cancellation behavior

### Multi-Agent Coordination
- Test agent handoffs
- Validate ThreadWatch activation
- Test auto-response conditions
- Verify agent collaboration patterns

### Human-in-the-Loop Testing
- Test approval workflows
- Validate input collection
- Test authentication flows
- Verify timeout and escalation

### Performance and Reliability
- Load testing with multiple concurrent runs
- Latency benchmarking
- Token usage validation
- Rate limit handling

## Architecture

### Testing Pyramid

```
         ┌─────────────────┐
         │  System Tests   │  ← E2E workflows
         │   (10% tests)   │
         ├─────────────────┤
         │Integration Tests│  ← Agent + tools + state
         │   (30% tests)   │
         ├─────────────────┤
         │   Unit Tests    │  ← Individual components
         │   (60% tests)   │
         └─────────────────┘
```

### Test Layers

**Layer 1: Unit Tests**
- Test individual functions and components
- Mock all external dependencies
- Fast execution (<10ms per test)
- Focus on logic and validation

**Layer 2: Integration Tests**
- Test agent-tool interactions
- Test state transitions
- Test multi-agent coordination
- Use in-memory or test databases

**Layer 3: System Tests**
- Test complete workflows
- Test against real API (test environment)
- Test webhook delivery
- Validate end-to-end scenarios

### Test Environment Architecture

```
┌─────────────────────────────────────────────────────────┐
│ TEST ENVIRONMENT                                        │
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │  Test Runner │     │  Mock Server │                 │
│  │   (pytest/   │────>│  (responses/ │                 │
│  │    Jest)     │     │     nock)    │                 │
│  └──────────────┘     └──────────────┘                 │
│         │                     │                         │
│         │                     │                         │
│         ▼                     ▼                         │
│  ┌──────────────────────────────────┐                  │
│  │   Agent Runtime API (Test Env)   │                  │
│  │  - In-memory state               │                  │
│  │  - Test fixtures                 │                  │
│  │  - Deterministic mode            │                  │
│  └──────────────────────────────────┘                  │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────────────────────┐                  │
│  │   Mock LLM Provider              │                  │
│  │  - Pre-configured responses      │                  │
│  │  - Deterministic behavior        │                  │
│  │  - Tool call simulation          │                  │
│  └──────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Implementation

### Pattern 1: Unit Testing Agent Configuration

Test agent configurations in isolation without invoking the LLM.

#### Python Implementation with pytest

```python
import pytest
import json
from typing import Dict, Any, List

# Test fixtures
@pytest.fixture
def basic_agent_config() -> Dict[str, Any]:
    """Basic agent configuration fixture."""
    return {
        "kind": "prompt",
        "name": "TestAgent",
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant.",
        "tools": []
    }

@pytest.fixture
def agent_with_tools() -> Dict[str, Any]:
    """Agent with tool definitions."""
    return {
        "kind": "prompt",
        "name": "ToolAgent",
        "model": "gpt-4o",
        "instructions": "You have access to tools.",
        "tools": [
            {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }

# Unit tests for agent configuration
class TestAgentConfiguration:
    """Test suite for agent configuration validation."""

    def test_basic_agent_structure(self, basic_agent_config):
        """Verify basic agent has required fields."""
        assert "kind" in basic_agent_config
        assert "name" in basic_agent_config
        assert "model" in basic_agent_config
        assert "instructions" in basic_agent_config
        assert basic_agent_config["kind"] == "prompt"

    def test_agent_name_validation(self, basic_agent_config):
        """Test agent name is non-empty string."""
        assert isinstance(basic_agent_config["name"], str)
        assert len(basic_agent_config["name"]) > 0

    def test_agent_tools_structure(self, agent_with_tools):
        """Verify tool definitions are properly structured."""
        tools = agent_with_tools["tools"]
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Validate first tool
        tool = tools[0]
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool

        # Validate JSON Schema
        params = tool["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        assert "required" in params

    def test_tool_parameter_schema(self, agent_with_tools):
        """Test tool parameters follow JSON Schema Draft 7."""
        tool = agent_with_tools["tools"][0]
        params = tool["parameters"]

        # Check required fields
        assert "type" in params
        assert "properties" in params

        # Check property definitions
        query_prop = params["properties"]["query"]
        assert query_prop["type"] == "string"
        assert "description" in query_prop

    def test_agent_instructions_not_empty(self, basic_agent_config):
        """Ensure instructions are provided."""
        instructions = basic_agent_config["instructions"]
        assert isinstance(instructions, str)
        assert len(instructions.strip()) > 0

    def test_agent_model_valid(self, basic_agent_config):
        """Test model identifier is valid."""
        model = basic_agent_config["model"]
        assert isinstance(model, str)
        # Check against known model names
        valid_models = ["gpt-4o", "gpt-4-turbo", "claude-3-opus", "claude-sonnet-4-5"]
        assert any(m in model for m in valid_models)
```

#### JavaScript Implementation with Jest

```javascript
// test/unit/agentConfiguration.test.js

describe('Agent Configuration', () => {
  // Fixtures
  const basicAgentConfig = {
    kind: 'prompt',
    name: 'TestAgent',
    model: 'gpt-4o',
    instructions: 'You are a helpful assistant.',
    tools: []
  };

  const agentWithTools = {
    kind: 'prompt',
    name: 'ToolAgent',
    model: 'gpt-4o',
    instructions: 'You have access to tools.',
    tools: [{
      name: 'search_web',
      description: 'Search the web for information',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query'
          }
        },
        required: ['query']
      }
    }]
  };

  describe('Basic Structure', () => {
    test('has required fields', () => {
      expect(basicAgentConfig).toHaveProperty('kind');
      expect(basicAgentConfig).toHaveProperty('name');
      expect(basicAgentConfig).toHaveProperty('model');
      expect(basicAgentConfig).toHaveProperty('instructions');
    });

    test('kind is prompt', () => {
      expect(basicAgentConfig.kind).toBe('prompt');
    });

    test('name is non-empty string', () => {
      expect(typeof basicAgentConfig.name).toBe('string');
      expect(basicAgentConfig.name.length).toBeGreaterThan(0);
    });
  });

  describe('Tool Definitions', () => {
    test('tools is an array', () => {
      expect(Array.isArray(agentWithTools.tools)).toBe(true);
    });

    test('tool has required properties', () => {
      const tool = agentWithTools.tools[0];
      expect(tool).toHaveProperty('name');
      expect(tool).toHaveProperty('description');
      expect(tool).toHaveProperty('parameters');
    });

    test('tool parameters follow JSON Schema', () => {
      const params = agentWithTools.tools[0].parameters;
      expect(params.type).toBe('object');
      expect(params).toHaveProperty('properties');
      expect(params).toHaveProperty('required');
    });

    test('tool property has type and description', () => {
      const queryProp = agentWithTools.tools[0].parameters.properties.query;
      expect(queryProp.type).toBe('string');
      expect(queryProp).toHaveProperty('description');
    });
  });

  describe('Validation', () => {
    test('instructions are not empty', () => {
      expect(typeof basicAgentConfig.instructions).toBe('string');
      expect(basicAgentConfig.instructions.trim().length).toBeGreaterThan(0);
    });

    test('model is valid identifier', () => {
      const validModels = ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus', 'claude-sonnet-4-5'];
      const isValid = validModels.some(m => basicAgentConfig.model.includes(m));
      expect(isValid).toBe(true);
    });
  });
});
```

### Pattern 2: Mocking Tool Execution

Mock tool calls to avoid external dependencies and achieve deterministic test results.

#### Python Implementation

```python
import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
import json

# Mock tool execution
class MockToolExecutor:
    """Mock tool executor for testing."""

    def __init__(self):
        self.calls = []

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute mock tool."""
        self.calls.append({
            "tool": tool_name,
            "arguments": arguments
        })

        # Return mock results based on tool
        if tool_name == "search_web":
            return {
                "results": [
                    {"title": "Test Result 1", "url": "https://example.com/1"},
                    {"title": "Test Result 2", "url": "https://example.com/2"}
                ]
            }
        elif tool_name == "get_weather":
            return {
                "temperature": 72,
                "conditions": "Sunny",
                "humidity": 45
            }
        elif tool_name == "calculate":
            # Simulate calculation
            operation = arguments.get("operation")
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)

            if operation == "add":
                return {"result": a + b}
            elif operation == "multiply":
                return {"result": a * b}

        return {"error": "Tool not implemented"}

# Test cases
class TestToolExecution:
    """Test suite for tool execution."""

    @pytest.fixture
    def tool_executor(self):
        """Mock tool executor fixture."""
        return MockToolExecutor()

    def test_search_web_tool(self, tool_executor):
        """Test search_web tool execution."""
        result = tool_executor.execute("search_web", {"query": "test query"})

        assert "results" in result
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "Test Result 1"

        # Verify call was recorded
        assert len(tool_executor.calls) == 1
        assert tool_executor.calls[0]["tool"] == "search_web"
        assert tool_executor.calls[0]["arguments"]["query"] == "test query"

    def test_get_weather_tool(self, tool_executor):
        """Test get_weather tool execution."""
        result = tool_executor.execute("get_weather", {"location": "San Francisco"})

        assert "temperature" in result
        assert "conditions" in result
        assert result["temperature"] == 72
        assert result["conditions"] == "Sunny"

    def test_calculate_tool_addition(self, tool_executor):
        """Test calculate tool with addition."""
        result = tool_executor.execute("calculate", {
            "operation": "add",
            "a": 5,
            "b": 3
        })

        assert result["result"] == 8

    def test_calculate_tool_multiplication(self, tool_executor):
        """Test calculate tool with multiplication."""
        result = tool_executor.execute("calculate", {
            "operation": "multiply",
            "a": 4,
            "b": 6
        })

        assert result["result"] == 24

    def test_unknown_tool(self, tool_executor):
        """Test execution of unknown tool."""
        result = tool_executor.execute("unknown_tool", {})

        assert "error" in result

    def test_multiple_tool_calls(self, tool_executor):
        """Test multiple sequential tool calls."""
        tool_executor.execute("search_web", {"query": "first"})
        tool_executor.execute("get_weather", {"location": "NY"})
        tool_executor.execute("search_web", {"query": "second"})

        assert len(tool_executor.calls) == 3
        assert tool_executor.calls[0]["tool"] == "search_web"
        assert tool_executor.calls[1]["tool"] == "get_weather"
        assert tool_executor.calls[2]["tool"] == "search_web"


# Mock API responses for external calls
class TestToolAPIIntegration:
    """Test tool integration with external APIs."""

    @responses.activate
    def test_api_tool_with_mock_response(self):
        """Test tool that calls external API with mocked response."""
        # Mock external API
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"data": "mock_value"},
            status=200
        )

        # Execute tool (would make HTTP request)
        import requests
        response = requests.get("https://api.example.com/data")

        assert response.status_code == 200
        assert response.json()["data"] == "mock_value"

    @responses.activate
    def test_api_tool_error_handling(self):
        """Test tool behavior on API error."""
        # Mock API error
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={"error": "Not found"},
            status=404
        )

        import requests
        response = requests.get("https://api.example.com/data")

        assert response.status_code == 404
        assert "error" in response.json()

    @responses.activate
    def test_api_tool_timeout(self):
        """Test tool behavior on API timeout."""
        # Mock API timeout
        responses.add(
            responses.GET,
            "https://api.example.com/slow",
            body=requests.exceptions.Timeout("Connection timeout")
        )

        import requests
        with pytest.raises(requests.exceptions.Timeout):
            requests.get("https://api.example.com/slow", timeout=1)


# Patch tool execution for run tests
class TestRunWithMockedTools:
    """Test runs with mocked tool execution."""

    @patch('requests.post')
    def test_run_with_tool_call(self, mock_post):
        """Test run that triggers tool call."""
        # Mock /runs endpoint
        mock_post.return_value.json.return_value = {
            "runId": "run_123",
            "status": "requires_action",
            "output": [{
                "role": "assistant",
                "contents": [{
                    "kind": "functionCall",
                    "callId": "call_1",
                    "name": "search_web",
                    "arguments": {"query": "test"}
                }]
            }]
        }

        # Simulate run creation
        import requests
        response = requests.post(
            "https://api.example.com/v1/runs",
            json={"agentId": "agent_1", "input": []}
        )

        result = response.json()

        assert result["status"] == "requires_action"
        assert len(result["output"][0]["contents"]) == 1

        tool_call = result["output"][0]["contents"][0]
        assert tool_call["kind"] == "functionCall"
        assert tool_call["name"] == "search_web"
```

#### JavaScript Implementation

```javascript
// test/unit/toolExecution.test.js

import { jest } from '@jest/globals';
import nock from 'nock';

// Mock tool executor
class MockToolExecutor {
  constructor() {
    this.calls = [];
  }

  execute(toolName, arguments) {
    this.calls.push({ tool: toolName, arguments });

    // Return mock results
    switch (toolName) {
      case 'search_web':
        return {
          results: [
            { title: 'Test Result 1', url: 'https://example.com/1' },
            { title: 'Test Result 2', url: 'https://example.com/2' }
          ]
        };

      case 'get_weather':
        return {
          temperature: 72,
          conditions: 'Sunny',
          humidity: 45
        };

      case 'calculate':
        const { operation, a = 0, b = 0 } = arguments;
        if (operation === 'add') return { result: a + b };
        if (operation === 'multiply') return { result: a * b };
        break;
    }

    return { error: 'Tool not implemented' };
  }
}

describe('Tool Execution', () => {
  let toolExecutor;

  beforeEach(() => {
    toolExecutor = new MockToolExecutor();
  });

  describe('Individual Tools', () => {
    test('search_web returns mock results', () => {
      const result = toolExecutor.execute('search_web', { query: 'test query' });

      expect(result.results).toHaveLength(2);
      expect(result.results[0].title).toBe('Test Result 1');

      // Verify call recorded
      expect(toolExecutor.calls).toHaveLength(1);
      expect(toolExecutor.calls[0].tool).toBe('search_web');
    });

    test('get_weather returns mock weather data', () => {
      const result = toolExecutor.execute('get_weather', { location: 'San Francisco' });

      expect(result.temperature).toBe(72);
      expect(result.conditions).toBe('Sunny');
    });

    test('calculate performs addition', () => {
      const result = toolExecutor.execute('calculate', {
        operation: 'add',
        a: 5,
        b: 3
      });

      expect(result.result).toBe(8);
    });

    test('unknown tool returns error', () => {
      const result = toolExecutor.execute('unknown_tool', {});

      expect(result).toHaveProperty('error');
    });
  });

  describe('Multiple Tool Calls', () => {
    test('tracks multiple sequential calls', () => {
      toolExecutor.execute('search_web', { query: 'first' });
      toolExecutor.execute('get_weather', { location: 'NY' });
      toolExecutor.execute('search_web', { query: 'second' });

      expect(toolExecutor.calls).toHaveLength(3);
      expect(toolExecutor.calls[0].tool).toBe('search_web');
      expect(toolExecutor.calls[1].tool).toBe('get_weather');
      expect(toolExecutor.calls[2].tool).toBe('search_web');
    });
  });
});

describe('Tool API Integration', () => {
  afterEach(() => {
    nock.cleanAll();
  });

  test('mocks external API call', async () => {
    // Mock external API
    nock('https://api.example.com')
      .get('/data')
      .reply(200, { data: 'mock_value' });

    // Execute tool (makes HTTP request)
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data).toBe('mock_value');
  });

  test('handles API errors', async () => {
    // Mock API error
    nock('https://api.example.com')
      .get('/data')
      .reply(404, { error: 'Not found' });

    const response = await fetch('https://api.example.com/data');
    const data = await response.json();

    expect(response.status).toBe(404);
    expect(data).toHaveProperty('error');
  });

  test('handles API timeout', async () => {
    // Mock timeout
    nock('https://api.example.com')
      .get('/slow')
      .delayConnection(2000)
      .reply(200, { data: 'slow' });

    // Simulate timeout with AbortController
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 1000);

    await expect(
      fetch('https://api.example.com/slow', { signal: controller.signal })
    ).rejects.toThrow();

    clearTimeout(timeout);
  });
});

describe('Run with Mocked Tools', () => {
  test('run triggers tool call', async () => {
    // Mock /runs endpoint
    nock('https://api.example.com')
      .post('/v1/runs')
      .reply(200, {
        runId: 'run_123',
        status: 'requires_action',
        output: [{
          role: 'assistant',
          contents: [{
            kind: 'functionCall',
            callId: 'call_1',
            name: 'search_web',
            arguments: { query: 'test' }
          }]
        }]
      });

    // Create run
    const response = await fetch('https://api.example.com/v1/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agentId: 'agent_1', input: [] })
    });

    const result = await response.json();

    expect(result.status).toBe('requires_action');
    expect(result.output[0].contents[0].kind).toBe('functionCall');
    expect(result.output[0].contents[0].name).toBe('search_web');
  });
});
```

### Pattern 3: Testing Run State Transitions

Verify run lifecycle transitions through the 11 states.

#### Python Implementation

```python
import pytest
from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Run states from TypeSpec
class RunStatus(str, Enum):
    """Run status enum - 11 states."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    INPUT_REQUIRED = "input_required"
    AUTH_REQUIRED = "auth_required"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    TIMEOUT = "timeout"


@dataclass
class RunStateTransition:
    """Represents a state transition."""
    from_state: RunStatus
    to_state: RunStatus
    timestamp: datetime
    reason: str = ""


class RunStateMachine:
    """Simulates run state machine for testing."""

    # Valid state transitions
    VALID_TRANSITIONS = {
        RunStatus.QUEUED: [RunStatus.IN_PROGRESS, RunStatus.CANCELLED, RunStatus.FAILED],
        RunStatus.IN_PROGRESS: [
            RunStatus.REQUIRES_ACTION,
            RunStatus.INPUT_REQUIRED,
            RunStatus.AUTH_REQUIRED,
            RunStatus.COMPLETED,
            RunStatus.FAILED,
            RunStatus.INCOMPLETE,
            RunStatus.TIMEOUT,
            RunStatus.CANCELLING
        ],
        RunStatus.REQUIRES_ACTION: [
            RunStatus.IN_PROGRESS,
            RunStatus.TIMEOUT,
            RunStatus.CANCELLED,
            RunStatus.FAILED
        ],
        RunStatus.INPUT_REQUIRED: [
            RunStatus.IN_PROGRESS,
            RunStatus.TIMEOUT,
            RunStatus.CANCELLED,
            RunStatus.FAILED
        ],
        RunStatus.AUTH_REQUIRED: [
            RunStatus.IN_PROGRESS,
            RunStatus.TIMEOUT,
            RunStatus.CANCELLED,
            RunStatus.FAILED
        ],
        RunStatus.CANCELLING: [RunStatus.CANCELLED, RunStatus.COMPLETED],
        # Terminal states have no transitions
        RunStatus.CANCELLED: [],
        RunStatus.FAILED: [],
        RunStatus.COMPLETED: [],
        RunStatus.INCOMPLETE: [],
        RunStatus.TIMEOUT: [],
    }

    def __init__(self):
        self.current_state = RunStatus.QUEUED
        self.transitions: List[RunStateTransition] = []

    def transition_to(self, new_state: RunStatus, reason: str = "") -> bool:
        """Attempt state transition."""
        if new_state in self.VALID_TRANSITIONS[self.current_state]:
            transition = RunStateTransition(
                from_state=self.current_state,
                to_state=new_state,
                timestamp=datetime.now(),
                reason=reason
            )
            self.transitions.append(transition)
            self.current_state = new_state
            return True
        return False

    def is_terminal(self) -> bool:
        """Check if current state is terminal."""
        return len(self.VALID_TRANSITIONS[self.current_state]) == 0


# Test cases
class TestRunStateTransitions:
    """Test suite for run state transitions."""

    def test_initial_state_is_queued(self):
        """Verify run starts in queued state."""
        machine = RunStateMachine()
        assert machine.current_state == RunStatus.QUEUED

    def test_queued_to_in_progress(self):
        """Test transition from queued to in_progress."""
        machine = RunStateMachine()
        success = machine.transition_to(RunStatus.IN_PROGRESS)

        assert success is True
        assert machine.current_state == RunStatus.IN_PROGRESS
        assert len(machine.transitions) == 1

    def test_in_progress_to_requires_action(self):
        """Test transition to requires_action (tool call)."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        success = machine.transition_to(
            RunStatus.REQUIRES_ACTION,
            reason="Tool call requested"
        )

        assert success is True
        assert machine.current_state == RunStatus.REQUIRES_ACTION

    def test_requires_action_to_in_progress(self):
        """Test transition back from requires_action after tool submission."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.REQUIRES_ACTION)
        success = machine.transition_to(
            RunStatus.IN_PROGRESS,
            reason="Tool outputs submitted"
        )

        assert success is True
        assert machine.current_state == RunStatus.IN_PROGRESS

    def test_in_progress_to_input_required(self):
        """Test transition to input_required (HITL)."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        success = machine.transition_to(
            RunStatus.INPUT_REQUIRED,
            reason="User input requested"
        )

        assert success is True
        assert machine.current_state == RunStatus.INPUT_REQUIRED

    def test_input_required_to_in_progress(self):
        """Test transition back from input_required after user input."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.INPUT_REQUIRED)
        success = machine.transition_to(
            RunStatus.IN_PROGRESS,
            reason="User input submitted"
        )

        assert success is True
        assert machine.current_state == RunStatus.IN_PROGRESS

    def test_in_progress_to_auth_required(self):
        """Test transition to auth_required."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        success = machine.transition_to(
            RunStatus.AUTH_REQUIRED,
            reason="OAuth token required"
        )

        assert success is True
        assert machine.current_state == RunStatus.AUTH_REQUIRED

    def test_auth_required_to_in_progress(self):
        """Test transition back from auth_required after auth."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.AUTH_REQUIRED)
        success = machine.transition_to(
            RunStatus.IN_PROGRESS,
            reason="Auth token submitted"
        )

        assert success is True
        assert machine.current_state == RunStatus.IN_PROGRESS

    def test_in_progress_to_completed(self):
        """Test successful completion."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        success = machine.transition_to(
            RunStatus.COMPLETED,
            reason="Run completed successfully"
        )

        assert success is True
        assert machine.current_state == RunStatus.COMPLETED
        assert machine.is_terminal() is True

    def test_in_progress_to_failed(self):
        """Test failure transition."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        success = machine.transition_to(
            RunStatus.FAILED,
            reason="Runtime error"
        )

        assert success is True
        assert machine.current_state == RunStatus.FAILED
        assert machine.is_terminal() is True

    def test_requires_action_to_timeout(self):
        """Test timeout during tool execution wait."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.REQUIRES_ACTION)
        success = machine.transition_to(
            RunStatus.TIMEOUT,
            reason="No tool outputs within timeout"
        )

        assert success is True
        assert machine.current_state == RunStatus.TIMEOUT
        assert machine.is_terminal() is True

    def test_invalid_transition(self):
        """Test invalid state transition is rejected."""
        machine = RunStateMachine()
        # Cannot go directly from queued to completed
        success = machine.transition_to(RunStatus.COMPLETED)

        assert success is False
        assert machine.current_state == RunStatus.QUEUED  # State unchanged

    def test_terminal_state_no_transitions(self):
        """Test terminal states cannot transition."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.COMPLETED)

        # Try to transition from completed (should fail)
        success = machine.transition_to(RunStatus.IN_PROGRESS)

        assert success is False
        assert machine.current_state == RunStatus.COMPLETED

    def test_cancellation_flow(self):
        """Test cancellation workflow."""
        machine = RunStateMachine()
        machine.transition_to(RunStatus.IN_PROGRESS)

        # User requests cancellation
        success1 = machine.transition_to(
            RunStatus.CANCELLING,
            reason="User requested cancellation"
        )

        # Cancellation completes
        success2 = machine.transition_to(
            RunStatus.CANCELLED,
            reason="Cancellation complete"
        )

        assert success1 is True
        assert success2 is True
        assert machine.current_state == RunStatus.CANCELLED
        assert machine.is_terminal() is True

    def test_multiple_tool_cycles(self):
        """Test multiple requires_action cycles."""
        machine = RunStateMachine()

        # Cycle 1
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.REQUIRES_ACTION, reason="Tool call 1")
        machine.transition_to(RunStatus.IN_PROGRESS, reason="Tool result 1")

        # Cycle 2
        machine.transition_to(RunStatus.REQUIRES_ACTION, reason="Tool call 2")
        machine.transition_to(RunStatus.IN_PROGRESS, reason="Tool result 2")

        # Complete
        machine.transition_to(RunStatus.COMPLETED)

        # Verify transition history
        assert len(machine.transitions) == 6
        assert machine.transitions[1].to_state == RunStatus.REQUIRES_ACTION
        assert machine.transitions[3].to_state == RunStatus.REQUIRES_ACTION

    def test_transition_history(self):
        """Test transition history is recorded."""
        machine = RunStateMachine()

        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.REQUIRES_ACTION)
        machine.transition_to(RunStatus.IN_PROGRESS)
        machine.transition_to(RunStatus.COMPLETED)

        assert len(machine.transitions) == 4

        # Verify sequence
        assert machine.transitions[0].from_state == RunStatus.QUEUED
        assert machine.transitions[0].to_state == RunStatus.IN_PROGRESS

        assert machine.transitions[1].from_state == RunStatus.IN_PROGRESS
        assert machine.transitions[1].to_state == RunStatus.REQUIRES_ACTION

        assert machine.transitions[2].from_state == RunStatus.REQUIRES_ACTION
        assert machine.transitions[2].to_state == RunStatus.IN_PROGRESS

        assert machine.transitions[3].from_state == RunStatus.IN_PROGRESS
        assert machine.transitions[3].to_state == RunStatus.COMPLETED


# Integration test with API
class TestRunStateAPI:
    """Test run state transitions via API."""

    @pytest.fixture
    def api_client(self):
        """Mock API client."""
        class MockClient:
            def __init__(self):
                self.machine = RunStateMachine()

            def get_run(self, run_id: str) -> Dict[str, Any]:
                return {
                    "runId": run_id,
                    "status": self.machine.current_state.value,
                    "transitions": [
                        {
                            "from": t.from_state.value,
                            "to": t.to_state.value,
                            "timestamp": t.timestamp.isoformat(),
                            "reason": t.reason
                        }
                        for t in self.machine.transitions
                    ]
                }

            def submit_tool_outputs(self, run_id: str, outputs: List[Dict]):
                if self.machine.current_state == RunStatus.REQUIRES_ACTION:
                    self.machine.transition_to(
                        RunStatus.IN_PROGRESS,
                        reason="Tool outputs submitted"
                    )
                    return self.get_run(run_id)
                raise ValueError("Run not in requires_action state")

        return MockClient()

    def test_api_state_query(self, api_client):
        """Test querying run state via API."""
        api_client.machine.transition_to(RunStatus.IN_PROGRESS)
        run = api_client.get_run("run_123")

        assert run["status"] == "in_progress"
        assert len(run["transitions"]) == 1

    def test_api_submit_tool_outputs(self, api_client):
        """Test submitting tool outputs via API."""
        api_client.machine.transition_to(RunStatus.IN_PROGRESS)
        api_client.machine.transition_to(RunStatus.REQUIRES_ACTION)

        # Submit tool outputs
        run = api_client.submit_tool_outputs("run_123", [
            {"callId": "call_1", "result": "test"}
        ])

        assert run["status"] == "in_progress"
        assert len(run["transitions"]) == 3  # queued → in_progress → requires_action → in_progress
```

#### JavaScript Implementation

```javascript
// test/integration/runStates.test.js

// Run states enum
const RunStatus = {
  QUEUED: 'queued',
  IN_PROGRESS: 'in_progress',
  REQUIRES_ACTION: 'requires_action',
  INPUT_REQUIRED: 'input_required',
  AUTH_REQUIRED: 'auth_required',
  CANCELLING: 'cancelling',
  CANCELLED: 'cancelled',
  FAILED: 'failed',
  COMPLETED: 'completed',
  INCOMPLETE: 'incomplete',
  TIMEOUT: 'timeout'
};

// State machine
class RunStateMachine {
  static VALID_TRANSITIONS = {
    [RunStatus.QUEUED]: [RunStatus.IN_PROGRESS, RunStatus.CANCELLED, RunStatus.FAILED],
    [RunStatus.IN_PROGRESS]: [
      RunStatus.REQUIRES_ACTION,
      RunStatus.INPUT_REQUIRED,
      RunStatus.AUTH_REQUIRED,
      RunStatus.COMPLETED,
      RunStatus.FAILED,
      RunStatus.INCOMPLETE,
      RunStatus.TIMEOUT,
      RunStatus.CANCELLING
    ],
    [RunStatus.REQUIRES_ACTION]: [
      RunStatus.IN_PROGRESS,
      RunStatus.TIMEOUT,
      RunStatus.CANCELLED,
      RunStatus.FAILED
    ],
    [RunStatus.INPUT_REQUIRED]: [
      RunStatus.IN_PROGRESS,
      RunStatus.TIMEOUT,
      RunStatus.CANCELLED,
      RunStatus.FAILED
    ],
    [RunStatus.AUTH_REQUIRED]: [
      RunStatus.IN_PROGRESS,
      RunStatus.TIMEOUT,
      RunStatus.CANCELLED,
      RunStatus.FAILED
    ],
    [RunStatus.CANCELLING]: [RunStatus.CANCELLED, RunStatus.COMPLETED],
    [RunStatus.CANCELLED]: [],
    [RunStatus.FAILED]: [],
    [RunStatus.COMPLETED]: [],
    [RunStatus.INCOMPLETE]: [],
    [RunStatus.TIMEOUT]: []
  };

  constructor() {
    this.currentState = RunStatus.QUEUED;
    this.transitions = [];
  }

  transitionTo(newState, reason = '') {
    if (RunStateMachine.VALID_TRANSITIONS[this.currentState].includes(newState)) {
      this.transitions.push({
        fromState: this.currentState,
        toState: newState,
        timestamp: new Date(),
        reason
      });
      this.currentState = newState;
      return true;
    }
    return false;
  }

  isTerminal() {
    return RunStateMachine.VALID_TRANSITIONS[this.currentState].length === 0;
  }
}

describe('Run State Transitions', () => {
  describe('Basic Transitions', () => {
    test('initial state is queued', () => {
      const machine = new RunStateMachine();
      expect(machine.currentState).toBe(RunStatus.QUEUED);
    });

    test('transitions from queued to in_progress', () => {
      const machine = new RunStateMachine();
      const success = machine.transitionTo(RunStatus.IN_PROGRESS);

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.IN_PROGRESS);
      expect(machine.transitions).toHaveLength(1);
    });

    test('transitions to completed', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      const success = machine.transitionTo(RunStatus.COMPLETED);

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.COMPLETED);
      expect(machine.isTerminal()).toBe(true);
    });
  });

  describe('Tool Execution States', () => {
    test('transitions to requires_action for tool call', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      const success = machine.transitionTo(
        RunStatus.REQUIRES_ACTION,
        'Tool call requested'
      );

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.REQUIRES_ACTION);
    });

    test('transitions back to in_progress after tool submission', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      machine.transitionTo(RunStatus.REQUIRES_ACTION);
      const success = machine.transitionTo(
        RunStatus.IN_PROGRESS,
        'Tool outputs submitted'
      );

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.IN_PROGRESS);
    });

    test('supports multiple tool cycles', () => {
      const machine = new RunStateMachine();

      // Cycle 1
      machine.transitionTo(RunStatus.IN_PROGRESS);
      machine.transitionTo(RunStatus.REQUIRES_ACTION, 'Tool call 1');
      machine.transitionTo(RunStatus.IN_PROGRESS, 'Tool result 1');

      // Cycle 2
      machine.transitionTo(RunStatus.REQUIRES_ACTION, 'Tool call 2');
      machine.transitionTo(RunStatus.IN_PROGRESS, 'Tool result 2');

      // Complete
      machine.transitionTo(RunStatus.COMPLETED);

      expect(machine.transitions).toHaveLength(6);
    });
  });

  describe('HITL States', () => {
    test('transitions to input_required', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      const success = machine.transitionTo(
        RunStatus.INPUT_REQUIRED,
        'User input requested'
      );

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.INPUT_REQUIRED);
    });

    test('transitions to auth_required', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      const success = machine.transitionTo(
        RunStatus.AUTH_REQUIRED,
        'OAuth token required'
      );

      expect(success).toBe(true);
      expect(machine.currentState).toBe(RunStatus.AUTH_REQUIRED);
    });
  });

  describe('Invalid Transitions', () => {
    test('rejects invalid transition', () => {
      const machine = new RunStateMachine();
      // Cannot go directly from queued to completed
      const success = machine.transitionTo(RunStatus.COMPLETED);

      expect(success).toBe(false);
      expect(machine.currentState).toBe(RunStatus.QUEUED);
    });

    test('terminal states cannot transition', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);
      machine.transitionTo(RunStatus.COMPLETED);

      const success = machine.transitionTo(RunStatus.IN_PROGRESS);

      expect(success).toBe(false);
      expect(machine.currentState).toBe(RunStatus.COMPLETED);
    });
  });

  describe('Cancellation', () => {
    test('handles cancellation flow', () => {
      const machine = new RunStateMachine();
      machine.transitionTo(RunStatus.IN_PROGRESS);

      const success1 = machine.transitionTo(
        RunStatus.CANCELLING,
        'User requested cancellation'
      );
      const success2 = machine.transitionTo(
        RunStatus.CANCELLED,
        'Cancellation complete'
      );

      expect(success1).toBe(true);
      expect(success2).toBe(true);
      expect(machine.currentState).toBe(RunStatus.CANCELLED);
      expect(machine.isTerminal()).toBe(true);
    });
  });

  describe('Transition History', () => {
    test('records transition history', () => {
      const machine = new RunStateMachine();

      machine.transitionTo(RunStatus.IN_PROGRESS);
      machine.transitionTo(RunStatus.REQUIRES_ACTION);
      machine.transitionTo(RunStatus.IN_PROGRESS);
      machine.transitionTo(RunStatus.COMPLETED);

      expect(machine.transitions).toHaveLength(4);

      // Verify sequence
      expect(machine.transitions[0].fromState).toBe(RunStatus.QUEUED);
      expect(machine.transitions[0].toState).toBe(RunStatus.IN_PROGRESS);

      expect(machine.transitions[3].fromState).toBe(RunStatus.IN_PROGRESS);
      expect(machine.transitions[3].toState).toBe(RunStatus.COMPLETED);
    });
  });
});
```

### Pattern 4: Testing HITL Patterns

Test human-in-the-loop workflows including tool approval, input collection, and authentication.

#### Python Implementation

```python
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch
import time

class HITLTestHelper:
    """Helper for testing HITL patterns."""

    @staticmethod
    def create_tool_approval_run() -> Dict[str, Any]:
        """Create run requiring tool approval."""
        return {
            "runId": "run_hitl_001",
            "status": "requires_action",
            "output": [{
                "role": "assistant",
                "contents": [{
                    "kind": "functionCall",
                    "callId": "call_delete_001",
                    "name": "delete_file",
                    "arguments": {"path": "/important/data.csv"}
                }]
            }]
        }

    @staticmethod
    def create_input_required_run() -> Dict[str, Any]:
        """Create run requiring user input."""
        return {
            "runId": "run_hitl_002",
            "status": "input_required",
            "output": [{
                "role": "assistant",
                "contents": [{
                    "kind": "userInputRequest",
                    "requestId": "input_001",
                    "prompt": "Which option do you prefer?",
                    "inputType": "choice",
                    "choices": ["Option A", "Option B", "Option C"]
                }]
            }]
        }

    @staticmethod
    def create_auth_required_run() -> Dict[str, Any]:
        """Create run requiring authentication."""
        return {
            "runId": "run_hitl_003",
            "status": "auth_required",
            "requiredAuth": {
                "provider": "gmail",
                "scopes": ["https://www.googleapis.com/auth/gmail.send"],
                "authUrl": "https://accounts.google.com/o/oauth2/v2/auth?..."
            }
        }


class TestToolApprovalWorkflow:
    """Test tool approval (requires_action) workflow."""

    def test_run_enters_requires_action(self):
        """Test run enters requires_action state."""
        run = HITLTestHelper.create_tool_approval_run()

        assert run["status"] == "requires_action"
        assert len(run["output"]) == 1

    def test_extract_tool_calls(self):
        """Test extracting tool calls from run output."""
        run = HITLTestHelper.create_tool_approval_run()

        # Extract tool calls
        tool_calls = [
            content
            for msg in run["output"]
            for content in msg["contents"]
            if content["kind"] == "functionCall"
        ]

        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "delete_file"
        assert tool_calls[0]["callId"] == "call_delete_001"

    def test_approve_tool_execution(self):
        """Test approving tool execution."""
        run = HITLTestHelper.create_tool_approval_run()
        tool_call = run["output"][0]["contents"][0]

        # Simulate approval
        approval = {
            "tool_outputs": [{
                "callId": tool_call["callId"],
                "result": "File deleted successfully"
            }]
        }

        assert approval["tool_outputs"][0]["callId"] == "call_delete_001"
        assert "result" in approval["tool_outputs"][0]

    def test_reject_tool_execution(self):
        """Test rejecting tool execution."""
        run = HITLTestHelper.create_tool_approval_run()
        tool_call = run["output"][0]["contents"][0]

        # Simulate rejection
        rejection = {
            "tool_outputs": [{
                "callId": tool_call["callId"],
                "exception": {
                    "type": "error",
                    "code": "USER_REJECTED",
                    "message": "User rejected file deletion"
                }
            }]
        }

        assert "exception" in rejection["tool_outputs"][0]
        assert rejection["tool_outputs"][0]["exception"]["code"] == "USER_REJECTED"

    @patch('requests.post')
    def test_submit_tool_outputs_api(self, mock_post):
        """Test submitting tool outputs via API."""
        # Mock API response
        mock_post.return_value.json.return_value = {
            "runId": "run_hitl_001",
            "status": "in_progress"
        }
        mock_post.return_value.status_code = 200

        # Submit tool outputs
        import requests
        response = requests.post(
            "https://api.example.com/runs/run_hitl_001/submit_tool_outputs",
            json={
                "tool_outputs": [{
                    "callId": "call_delete_001",
                    "result": "File deleted"
                }]
            }
        )

        result = response.json()
        assert result["status"] == "in_progress"
        assert mock_post.called


class TestInputCollectionWorkflow:
    """Test input collection (input_required) workflow."""

    def test_run_enters_input_required(self):
        """Test run enters input_required state."""
        run = HITLTestHelper.create_input_required_run()

        assert run["status"] == "input_required"

    def test_extract_input_request(self):
        """Test extracting input request from run output."""
        run = HITLTestHelper.create_input_required_run()

        # Extract input request
        input_requests = [
            content
            for msg in run["output"]
            for content in msg["contents"]
            if content["kind"] == "userInputRequest"
        ]

        assert len(input_requests) == 1
        request = input_requests[0]
        assert request["requestId"] == "input_001"
        assert request["inputType"] == "choice"
        assert len(request["choices"]) == 3

    def test_submit_choice_input(self):
        """Test submitting choice input."""
        run = HITLTestHelper.create_input_required_run()
        request = run["output"][0]["contents"][0]

        # User selects Option B
        submission = {
            "requestId": request["requestId"],
            "value": "Option B"
        }

        assert submission["value"] in request["choices"]

    def test_submit_text_input(self):
        """Test submitting text input."""
        # Modify run to expect text
        run = HITLTestHelper.create_input_required_run()
        run["output"][0]["contents"][0]["inputType"] = "text"
        run["output"][0]["contents"][0]["prompt"] = "Please clarify your request"
        del run["output"][0]["contents"][0]["choices"]

        submission = {
            "requestId": "input_001",
            "value": "I want the report from last quarter"
        }

        assert isinstance(submission["value"], str)

    @patch('requests.post')
    def test_submit_input_api(self, mock_post):
        """Test submitting input via API."""
        mock_post.return_value.json.return_value = {
            "runId": "run_hitl_002",
            "status": "in_progress"
        }
        mock_post.return_value.status_code = 200

        import requests
        response = requests.post(
            "https://api.example.com/runs/run_hitl_002/submit_input",
            json={"value": "Option B"}
        )

        result = response.json()
        assert result["status"] == "in_progress"


class TestAuthenticationWorkflow:
    """Test authentication (auth_required) workflow."""

    def test_run_enters_auth_required(self):
        """Test run enters auth_required state."""
        run = HITLTestHelper.create_auth_required_run()

        assert run["status"] == "auth_required"
        assert "requiredAuth" in run

    def test_extract_auth_requirements(self):
        """Test extracting auth requirements."""
        run = HITLTestHelper.create_auth_required_run()
        auth = run["requiredAuth"]

        assert auth["provider"] == "gmail"
        assert "gmail.send" in auth["scopes"][0]
        assert "authUrl" in auth

    def test_submit_oauth_token(self):
        """Test submitting OAuth token."""
        run = HITLTestHelper.create_auth_required_run()

        # Simulate OAuth flow completion
        submission = {
            "token": "ya29.a0AfH6SMBx...",
            "tokenType": "Bearer"
        }

        assert submission["tokenType"] == "Bearer"
        assert len(submission["token"]) > 0

    @patch('requests.post')
    def test_submit_auth_api(self, mock_post):
        """Test submitting auth via API."""
        mock_post.return_value.json.return_value = {
            "runId": "run_hitl_003",
            "status": "in_progress",
            "connectionId": "conn_gmail_001"
        }
        mock_post.return_value.status_code = 200

        import requests
        response = requests.post(
            "https://api.example.com/runs/run_hitl_003/submit_auth",
            json={
                "token": "ya29.a0AfH6SMBx...",
                "tokenType": "Bearer"
            }
        )

        result = response.json()
        assert result["status"] == "in_progress"
        assert "connectionId" in result


class TestHITLTimeout:
    """Test HITL timeout behavior."""

    def test_timeout_during_tool_approval(self):
        """Test run times out waiting for tool approval."""
        run = HITLTestHelper.create_tool_approval_run()
        run_id = run["runId"]

        # Simulate timeout (no submission within timeout period)
        time_elapsed = 601  # 10 minutes + 1 second

        if time_elapsed > 600:
            run["status"] = "timeout"
            run["error"] = {
                "code": "tool_response_timeout",
                "message": "No tool outputs submitted within 10 minutes"
            }

        assert run["status"] == "timeout"
        assert run["error"]["code"] == "tool_response_timeout"

    def test_timeout_during_input_collection(self):
        """Test run times out waiting for user input."""
        run = HITLTestHelper.create_input_required_run()
        time_elapsed = 601

        if time_elapsed > 600:
            run["status"] = "timeout"
            run["error"] = {
                "code": "input_response_timeout",
                "message": "No user input submitted within 10 minutes"
            }

        assert run["status"] == "timeout"


class TestHITLEscalation:
    """Test HITL escalation patterns."""

    def test_escalate_after_timeout(self):
        """Test escalating approval request after timeout."""
        run = HITLTestHelper.create_tool_approval_run()

        # Simulate timeout
        run["status"] = "timeout"

        # Create escalation
        escalation = {
            "originalRunId": run["runId"],
            "escalatedTo": "manager@example.com",
            "reason": "Original approver did not respond within timeout",
            "urgency": "high"
        }

        assert escalation["originalRunId"] == "run_hitl_001"
        assert escalation["urgency"] == "high"

    def test_conditional_escalation(self):
        """Test conditional escalation based on approval value."""
        run = HITLTestHelper.create_tool_approval_run()
        tool_call = run["output"][0]["contents"][0]

        # Extract deletion path
        import json
        args = json.loads(tool_call["arguments"]) if isinstance(
            tool_call["arguments"], str
        ) else tool_call["arguments"]

        path = args["path"]

        # Escalate if critical path
        requires_escalation = any(
            critical in path
            for critical in ["/production/", "/important/", "/system/"]
        )

        assert requires_escalation is True  # /important/ is in path
```

Continuing with Pattern 4 JavaScript implementation and the remaining patterns...


#### JavaScript Implementation (continued)

```javascript
// test/integration/hitl.test.js

class HITLTestHelper {
  static createToolApprovalRun() {
    return {
      runId: 'run_hitl_001',
      status: 'requires_action',
      output: [{
        role: 'assistant',
        contents: [{
          kind: 'functionCall',
          callId: 'call_delete_001',
          name: 'delete_file',
          arguments: { path: '/important/data.csv' }
        }]
      }]
    };
  }

  static createInputRequiredRun() {
    return {
      runId: 'run_hitl_002',
      status: 'input_required',
      output: [{
        role: 'assistant',
        contents: [{
          kind: 'userInputRequest',
          requestId: 'input_001',
          prompt: 'Which option do you prefer?',
          inputType: 'choice',
          choices: ['Option A', 'Option B', 'Option C']
        }]
      }]
    };
  }

  static createAuthRequiredRun() {
    return {
      runId: 'run_hitl_003',
      status: 'auth_required',
      requiredAuth: {
        provider: 'gmail',
        scopes: ['https://www.googleapis.com/auth/gmail.send'],
        authUrl: 'https://accounts.google.com/o/oauth2/v2/auth?...'
      }
    };
  }
}

describe('Tool Approval Workflow', () => {
  test('run enters requires_action state', () => {
    const run = HITLTestHelper.createToolApprovalRun();

    expect(run.status).toBe('requires_action');
    expect(run.output).toHaveLength(1);
  });

  test('extracts tool calls', () => {
    const run = HITLTestHelper.createToolApprovalRun();

    const toolCalls = run.output
      .flatMap(msg => msg.contents)
      .filter(content => content.kind === 'functionCall');

    expect(toolCalls).toHaveLength(1);
    expect(toolCalls[0].name).toBe('delete_file');
    expect(toolCalls[0].callId).toBe('call_delete_001');
  });

  test('approves tool execution', () => {
    const run = HITLTestHelper.createToolApprovalRun();
    const toolCall = run.output[0].contents[0];

    const approval = {
      tool_outputs: [{
        callId: toolCall.callId,
        result: 'File deleted successfully'
      }]
    };

    expect(approval.tool_outputs[0].callId).toBe('call_delete_001');
    expect(approval.tool_outputs[0]).toHaveProperty('result');
  });

  test('rejects tool execution', () => {
    const run = HITLTestHelper.createToolApprovalRun();
    const toolCall = run.output[0].contents[0];

    const rejection = {
      tool_outputs: [{
        callId: toolCall.callId,
        exception: {
          type: 'error',
          code: 'USER_REJECTED',
          message: 'User rejected file deletion'
        }
      }]
    };

    expect(rejection.tool_outputs[0]).toHaveProperty('exception');
    expect(rejection.tool_outputs[0].exception.code).toBe('USER_REJECTED');
  });
});

describe('Input Collection Workflow', () => {
  test('run enters input_required state', () => {
    const run = HITLTestHelper.createInputRequiredRun();
    expect(run.status).toBe('input_required');
  });

  test('extracts input request', () => {
    const run = HITLTestHelper.createInputRequiredRun();

    const inputRequests = run.output
      .flatMap(msg => msg.contents)
      .filter(content => content.kind === 'userInputRequest');

    expect(inputRequests).toHaveLength(1);
    const request = inputRequests[0];
    expect(request.requestId).toBe('input_001');
    expect(request.inputType).toBe('choice');
    expect(request.choices).toHaveLength(3);
  });

  test('submits choice input', () => {
    const run = HITLTestHelper.createInputRequiredRun();
    const request = run.output[0].contents[0];

    const submission = {
      requestId: request.requestId,
      value: 'Option B'
    };

    expect(request.choices).toContain(submission.value);
  });
});

describe('Authentication Workflow', () => {
  test('run enters auth_required state', () => {
    const run = HITLTestHelper.createAuthRequiredRun();

    expect(run.status).toBe('auth_required');
    expect(run).toHaveProperty('requiredAuth');
  });

  test('extracts auth requirements', () => {
    const run = HITLTestHelper.createAuthRequiredRun();
    const auth = run.requiredAuth;

    expect(auth.provider).toBe('gmail');
    expect(auth.scopes[0]).toContain('gmail.send');
    expect(auth).toHaveProperty('authUrl');
  });

  test('submits OAuth token', () => {
    const run = HITLTestHelper.createAuthRequiredRun();

    const submission = {
      token: 'ya29.a0AfH6SMBx...',
      tokenType: 'Bearer'
    };

    expect(submission.tokenType).toBe('Bearer');
    expect(submission.token.length).toBeGreaterThan(0);
  });
});

describe('HITL Timeout', () => {
  test('timeout during tool approval', () => {
    const run = HITLTestHelper.createToolApprovalRun();
    const timeElapsed = 601; // 10 minutes + 1 second

    if (timeElapsed > 600) {
      run.status = 'timeout';
      run.error = {
        code: 'tool_response_timeout',
        message: 'No tool outputs submitted within 10 minutes'
      };
    }

    expect(run.status).toBe('timeout');
    expect(run.error.code).toBe('tool_response_timeout');
  });
});

describe('HITL Escalation', () => {
  test('escalates after timeout', () => {
    const run = HITLTestHelper.createToolApprovalRun();
    run.status = 'timeout';

    const escalation = {
      originalRunId: run.runId,
      escalatedTo: 'manager@example.com',
      reason: 'Original approver did not respond within timeout',
      urgency: 'high'
    };

    expect(escalation.originalRunId).toBe('run_hitl_001');
    expect(escalation.urgency).toBe('high');
  });

  test('conditional escalation for critical paths', () => {
    const run = HITLTestHelper.createToolApprovalRun();
    const toolCall = run.output[0].contents[0];
    const path = toolCall.arguments.path;

    const requiresEscalation = ['/production/', '/important/', '/system/']
      .some(critical => path.includes(critical));

    expect(requiresEscalation).toBe(true); // /important/ is in path
  });
});
```

### Pattern 5: Testing Multi-Agent Handoffs

Test agent handoffs and multi-agent coordination patterns.

#### Python Implementation

```python
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch

class MultiAgentTestHelper:
    """Helper for testing multi-agent scenarios."""

    @staticmethod
    def create_triage_agent() -> Dict[str, Any]:
        """Create triage agent configuration."""
        return {
            "kind": "prompt",
            "agentId": "agent_triage",
            "name": "Triage Agent",
            "model": "gpt-4o",
            "instructions": """You route requests to specialists.
            Use transfer_to_billing for billing questions.
            Use transfer_to_technical for technical issues.""",
            "tools": [
                {
                    "name": "transfer_to_billing",
                    "description": "Transfer to billing specialist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "transfer_to_technical",
                    "description": "Transfer to technical specialist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string"}
                        }
                    }
                }
            ]
        }

    @staticmethod
    def create_billing_agent() -> Dict[str, Any]:
        """Create billing specialist agent."""
        return {
            "kind": "prompt",
            "agentId": "agent_billing",
            "name": "Billing Agent",
            "model": "gpt-4o",
            "instructions": "You handle billing questions.",
            "tools": [
                {
                    "name": "lookup_invoice",
                    "description": "Find invoice details"
                }
            ]
        }


class TestAgentHandoff:
    """Test agent handoff patterns."""

    def test_handoff_tool_call(self):
        """Test agent generates handoff tool call."""
        triage_agent = MultiAgentTestHelper.create_triage_agent()

        # Verify handoff tools exist
        tool_names = [t["name"] for t in triage_agent["tools"]]
        assert "transfer_to_billing" in tool_names
        assert "transfer_to_technical" in tool_names

    def test_handoff_detection(self):
        """Test detecting handoff from tool call."""
        # Simulate run with handoff
        run = {
            "runId": "run_handoff_001",
            "status": "requires_action",
            "agentId": "agent_triage",
            "output": [{
                "role": "assistant",
                "contents": [{
                    "kind": "functionCall",
                    "callId": "call_001",
                    "name": "transfer_to_billing",
                    "arguments": {"reason": "User has billing question"}
                }]
            }]
        }

        # Extract handoff
        tool_call = run["output"][0]["contents"][0]
        is_handoff = tool_call["name"].startswith("transfer_to_")

        assert is_handoff is True

        # Extract target agent
        target = tool_call["name"].replace("transfer_to_", "")
        assert target == "billing"

    def test_handoff_execution(self):
        """Test executing handoff."""
        # Start with triage agent
        thread_id = "thread_001"
        current_agent_id = "agent_triage"

        # Detect handoff tool call
        tool_call = {
            "name": "transfer_to_billing",
            "arguments": {"reason": "Billing question"}
        }

        # Execute handoff
        if tool_call["name"].startswith("transfer_to_"):
            target = tool_call["name"].replace("transfer_to_", "")
            new_agent_id = f"agent_{target}"

            # Create new run with target agent
            new_run = {
                "threadId": thread_id,
                "agentId": new_agent_id,
                "input": []  # Reads from thread
            }

            assert new_run["agentId"] == "agent_billing"
            assert new_run["threadId"] == thread_id

    def test_handoff_history(self):
        """Test tracking handoff history."""
        handoff_history = []

        # Handoff 1: Triage → Billing
        handoff_history.append({
            "from": "agent_triage",
            "to": "agent_billing",
            "reason": "Billing question"
        })

        # Handoff 2: Billing → Manager
        handoff_history.append({
            "from": "agent_billing",
            "to": "agent_manager",
            "reason": "Requires manager approval"
        })

        assert len(handoff_history) == 2
        assert handoff_history[0]["from"] == "agent_triage"
        assert handoff_history[1]["to"] == "agent_manager"

    def test_prevent_handoff_loops(self):
        """Test detecting and preventing handoff loops."""
        handoff_history = [
            {"from": "agent_a", "to": "agent_b"},
            {"from": "agent_b", "to": "agent_c"},
            {"from": "agent_c", "to": "agent_a"}  # Loop!
        ]

        # Detect loop
        agents_visited = [h["from"] for h in handoff_history] + [handoff_history[-1]["to"]]
        has_loop = len(agents_visited) != len(set(agents_visited))

        assert has_loop is True

    def test_max_handoffs_limit(self):
        """Test enforcing max handoffs limit."""
        max_handoffs = 5
        handoff_count = 6

        if handoff_count > max_handoffs:
            error = {
                "code": "MAX_HANDOFFS_EXCEEDED",
                "message": f"Exceeded maximum handoffs ({max_handoffs})"
            }

            assert error["code"] == "MAX_HANDOFFS_EXCEEDED"


class TestMultiAgentCoordination:
    """Test multi-agent coordination patterns."""

    @patch('requests.post')
    def test_parallel_agent_execution(self, mock_post):
        """Test executing multiple agents in parallel."""
        # Mock API responses
        mock_post.return_value.json.side_effect = [
            {"runId": "run_1", "status": "completed", "output": [{"text": "Result 1"}]},
            {"runId": "run_2", "status": "completed", "output": [{"text": "Result 2"}]},
            {"runId": "run_3", "status": "completed", "output": [{"text": "Result 3"}]}
        ]

        # Execute agents in parallel (simulated)
        agents = ["agent_search", "agent_academic", "agent_news"]
        results = []

        for agent_id in agents:
            import requests
            response = requests.post(
                "https://api.example.com/v1/runs",
                json={"agentId": agent_id, "input": []}
            )
            results.append(response.json())

        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

    def test_sequential_agent_pipeline(self):
        """Test sequential agent execution."""
        # Pipeline: Research → Analyze → Summarize
        pipeline = [
            {"agentId": "agent_research", "name": "Research Agent"},
            {"agentId": "agent_analyze", "name": "Analyze Agent"},
            {"agentId": "agent_summarize", "name": "Summarize Agent"}
        ]

        execution_log = []

        # Simulate execution
        current_input = "Initial query"
        for agent in pipeline:
            execution_log.append({
                "agent": agent["agentId"],
                "input": current_input
            })
            # In real test, would execute run and get output
            current_input = f"Output from {agent['name']}"

        assert len(execution_log) == 3
        assert execution_log[0]["agent"] == "agent_research"
        assert execution_log[2]["agent"] == "agent_summarize"

    def test_consensus_building(self):
        """Test consensus from multiple agents."""
        # Multiple agents vote
        votes = [
            {"agent": "agent_legal", "decision": "yes", "confidence": 0.8},
            {"agent": "agent_finance", "decision": "yes", "confidence": 0.9},
            {"agent": "agent_technical", "decision": "no", "confidence": 0.6},
            {"agent": "agent_security", "decision": "yes", "confidence": 0.7}
        ]

        # Calculate consensus
        yes_votes = sum(1 for v in votes if v["decision"] == "yes")
        no_votes = sum(1 for v in votes if v["decision"] == "no")
        total_votes = len(votes)

        consensus_reached = yes_votes / total_votes >= 0.75

        assert yes_votes == 3
        assert no_votes == 1
        assert consensus_reached is True  # 75% yes


class TestSharedThreadState:
    """Test agents sharing thread state."""

    def test_agents_read_shared_thread(self):
        """Test multiple agents reading from same thread."""
        thread_id = "thread_shared_001"

        # Agent A writes to thread
        run_a = {
            "agentId": "agent_a",
            "threadId": thread_id,
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "Question"}]}],
            "store": True  # Store in thread
        }

        # Agent B reads from thread
        run_b = {
            "agentId": "agent_b",
            "threadId": thread_id,
            "input": [],  # Reads from thread
            "store": True
        }

        assert run_a["threadId"] == run_b["threadId"]
        assert len(run_b["input"]) == 0  # Reads from thread

    def test_message_visibility_across_agents(self):
        """Test messages visible to all agents in thread."""
        thread_messages = [
            {"role": "user", "contents": [{"kind": "text", "text": "Hello"}]},
            {"role": "assistant", "agentId": "agent_a", "contents": [{"kind": "text", "text": "Response from A"}]},
            {"role": "assistant", "agentId": "agent_b", "contents": [{"kind": "text", "text": "Response from B"}]}
        ]

        # Agent C can see all messages
        agent_c_context = thread_messages

        assert len(agent_c_context) == 3
        # Verify messages from different agents
        agent_ids = [m.get("agentId") for m in agent_c_context if m["role"] == "assistant"]
        assert "agent_a" in agent_ids
        assert "agent_b" in agent_ids
```

#### JavaScript Implementation

```javascript
// test/integration/multiAgent.test.js

class MultiAgentTestHelper {
  static createTriageAgent() {
    return {
      kind: 'prompt',
      agentId: 'agent_triage',
      name: 'Triage Agent',
      model: 'gpt-4o',
      instructions: `You route requests to specialists.
        Use transfer_to_billing for billing questions.
        Use transfer_to_technical for technical issues.`,
      tools: [
        {
          name: 'transfer_to_billing',
          description: 'Transfer to billing specialist',
          parameters: {
            type: 'object',
            properties: {
              reason: { type: 'string' }
            }
          }
        },
        {
          name: 'transfer_to_technical',
          description: 'Transfer to technical specialist',
          parameters: {
            type: 'object',
            properties: {
              reason: { type: 'string' }
            }
          }
        }
      ]
    };
  }

  static createBillingAgent() {
    return {
      kind: 'prompt',
      agentId: 'agent_billing',
      name: 'Billing Agent',
      model: 'gpt-4o',
      instructions: 'You handle billing questions.',
      tools: [{
        name: 'lookup_invoice',
        description: 'Find invoice details'
      }]
    };
  }
}

describe('Agent Handoff', () => {
  test('agent has handoff tools', () => {
    const triageAgent = MultiAgentTestHelper.createTriageAgent();

    const toolNames = triageAgent.tools.map(t => t.name);
    expect(toolNames).toContain('transfer_to_billing');
    expect(toolNames).toContain('transfer_to_technical');
  });

  test('detects handoff from tool call', () => {
    const run = {
      runId: 'run_handoff_001',
      status: 'requires_action',
      agentId: 'agent_triage',
      output: [{
        role: 'assistant',
        contents: [{
          kind: 'functionCall',
          callId: 'call_001',
          name: 'transfer_to_billing',
          arguments: { reason: 'User has billing question' }
        }]
      }]
    };

    const toolCall = run.output[0].contents[0];
    const isHandoff = toolCall.name.startsWith('transfer_to_');

    expect(isHandoff).toBe(true);

    const target = toolCall.name.replace('transfer_to_', '');
    expect(target).toBe('billing');
  });

  test('executes handoff', () => {
    const threadId = 'thread_001';
    let currentAgentId = 'agent_triage';

    const toolCall = {
      name: 'transfer_to_billing',
      arguments: { reason: 'Billing question' }
    };

    if (toolCall.name.startsWith('transfer_to_')) {
      const target = toolCall.name.replace('transfer_to_', '');
      const newAgentId = `agent_${target}`;

      const newRun = {
        threadId,
        agentId: newAgentId,
        input: []
      };

      expect(newRun.agentId).toBe('agent_billing');
      expect(newRun.threadId).toBe(threadId);
    }
  });

  test('tracks handoff history', () => {
    const handoffHistory = [];

    handoffHistory.push({
      from: 'agent_triage',
      to: 'agent_billing',
      reason: 'Billing question'
    });

    handoffHistory.push({
      from: 'agent_billing',
      to: 'agent_manager',
      reason: 'Requires manager approval'
    });

    expect(handoffHistory).toHaveLength(2);
    expect(handoffHistory[0].from).toBe('agent_triage');
    expect(handoffHistory[1].to).toBe('agent_manager');
  });

  test('prevents handoff loops', () => {
    const handoffHistory = [
      { from: 'agent_a', to: 'agent_b' },
      { from: 'agent_b', to: 'agent_c' },
      { from: 'agent_c', to: 'agent_a' } // Loop!
    ];

    const agentsVisited = [
      ...handoffHistory.map(h => h.from),
      handoffHistory[handoffHistory.length - 1].to
    ];

    const hasLoop = agentsVisited.length !== new Set(agentsVisited).size;

    expect(hasLoop).toBe(true);
  });

  test('enforces max handoffs limit', () => {
    const maxHandoffs = 5;
    const handoffCount = 6;

    if (handoffCount > maxHandoffs) {
      const error = {
        code: 'MAX_HANDOFFS_EXCEEDED',
        message: `Exceeded maximum handoffs (${maxHandoffs})`
      };

      expect(error.code).toBe('MAX_HANDOFFS_EXCEEDED');
    }
  });
});

describe('Multi-Agent Coordination', () => {
  test('parallel agent execution', async () => {
    // Mock parallel execution
    const agents = ['agent_search', 'agent_academic', 'agent_news'];
    const results = await Promise.all(
      agents.map(async agentId => ({
        runId: `run_${agentId}`,
        status: 'completed',
        agentId,
        output: [{ text: `Result from ${agentId}` }]
      }))
    );

    expect(results).toHaveLength(3);
    expect(results.every(r => r.status === 'completed')).toBe(true);
  });

  test('sequential agent pipeline', () => {
    const pipeline = [
      { agentId: 'agent_research', name: 'Research Agent' },
      { agentId: 'agent_analyze', name: 'Analyze Agent' },
      { agentId: 'agent_summarize', name: 'Summarize Agent' }
    ];

    const executionLog = [];
    let currentInput = 'Initial query';

    for (const agent of pipeline) {
      executionLog.push({
        agent: agent.agentId,
        input: currentInput
      });
      currentInput = `Output from ${agent.name}`;
    }

    expect(executionLog).toHaveLength(3);
    expect(executionLog[0].agent).toBe('agent_research');
    expect(executionLog[2].agent).toBe('agent_summarize');
  });

  test('consensus building', () => {
    const votes = [
      { agent: 'agent_legal', decision: 'yes', confidence: 0.8 },
      { agent: 'agent_finance', decision: 'yes', confidence: 0.9 },
      { agent: 'agent_technical', decision: 'no', confidence: 0.6 },
      { agent: 'agent_security', decision: 'yes', confidence: 0.7 }
    ];

    const yesVotes = votes.filter(v => v.decision === 'yes').length;
    const noVotes = votes.filter(v => v.decision === 'no').length;
    const totalVotes = votes.length;

    const consensusReached = yesVotes / totalVotes >= 0.75;

    expect(yesVotes).toBe(3);
    expect(noVotes).toBe(1);
    expect(consensusReached).toBe(true);
  });
});

describe('Shared Thread State', () => {
  test('agents read from shared thread', () => {
    const threadId = 'thread_shared_001';

    const runA = {
      agentId: 'agent_a',
      threadId,
      input: [{ role: 'user', contents: [{ kind: 'text', text: 'Question' }] }],
      store: true
    };

    const runB = {
      agentId: 'agent_b',
      threadId,
      input: [],
      store: true
    };

    expect(runA.threadId).toBe(runB.threadId);
    expect(runB.input).toHaveLength(0);
  });

  test('messages visible across agents', () => {
    const threadMessages = [
      { role: 'user', contents: [{ kind: 'text', text: 'Hello' }] },
      { role: 'assistant', agentId: 'agent_a', contents: [{ kind: 'text', text: 'Response from A' }] },
      { role: 'assistant', agentId: 'agent_b', contents: [{ kind: 'text', text: 'Response from B' }] }
    ];

    const agentCContext = threadMessages;

    expect(agentCContext).toHaveLength(3);

    const agentIds = agentCContext
      .filter(m => m.role === 'assistant')
      .map(m => m.agentId);

    expect(agentIds).toContain('agent_a');
    expect(agentIds).toContain('agent_b');
  });
});
```

### Pattern 6: Testing ThreadWatch and Auto-Response

Test ThreadWatch activation and auto-response conditions.

#### Python Implementation

```python
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch

class ThreadWatchTestHelper:
    """Helper for testing ThreadWatch patterns."""

    @staticmethod
    def create_watch(agent_id: str, thread_id: str, condition: Dict = None) -> Dict[str, Any]:
        """Create ThreadWatch registration."""
        return {
            "watchId": f"watch_{agent_id}_{thread_id}",
            "threadId": thread_id,
            "agentId": agent_id,
            "active": True,
            "condition": condition or {"kind": "roles", "roles": ["user"]},
            "createdAt": "2026-02-07T10:00:00Z",
            "activationCount": 0
        }

    @staticmethod
    def create_auto_response_agent(condition: Dict) -> Dict[str, Any]:
        """Create agent with auto-response config."""
        return {
            "kind": "prompt",
            "agentId": "agent_auto",
            "name": "Auto Response Agent",
            "model": "gpt-4o",
            "instructions": "You respond automatically.",
            "autoResponseConfig": {
                "runCondition": condition,
                "maxConsecutiveRuns": 1,
                "threadCleanup": "keep"
            }
        }


class TestThreadWatchActivation:
    """Test ThreadWatch activation patterns."""

    def test_watch_creation(self):
        """Test creating ThreadWatch."""
        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_support",
            thread_id="thread_001"
        )

        assert watch["agentId"] == "agent_support"
        assert watch["threadId"] == "thread_001"
        assert watch["active"] is True

    def test_watch_with_roles_condition(self):
        """Test watch with roles condition."""
        condition = {
            "kind": "roles",
            "roles": ["user"]
        }

        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_support",
            thread_id="thread_001",
            condition=condition
        )

        assert watch["condition"]["kind"] == "roles"
        assert "user" in watch["condition"]["roles"]

    def test_watch_with_mention_condition(self):
        """Test watch with mention condition."""
        condition = {
            "kind": "mention",
            "requireExplicitMention": True
        }

        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_supervisor",
            thread_id="thread_001",
            condition=condition
        )

        assert watch["condition"]["kind"] == "mention"
        assert watch["condition"]["requireExplicitMention"] is True

    def test_watch_with_content_condition(self):
        """Test watch with content type condition."""
        condition = {
            "kind": "content",
            "contentTypes": ["video"]
        }

        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_video",
            thread_id="thread_001",
            condition=condition
        )

        assert watch["condition"]["kind"] == "content"
        assert "video" in watch["condition"]["contentTypes"]

    def test_evaluate_roles_condition(self):
        """Test evaluating roles condition."""
        condition = {
            "kind": "roles",
            "roles": ["user"]
        }

        # Test user message
        message = {"role": "user", "contents": []}
        should_activate = message["role"] in condition["roles"]
        assert should_activate is True

        # Test assistant message
        message = {"role": "assistant", "contents": []}
        should_activate = message["role"] in condition["roles"]
        assert should_activate is False

    def test_evaluate_mention_condition(self):
        """Test evaluating mention condition."""
        condition = {
            "kind": "mention",
            "requireExplicitMention": True
        }

        # Message with mention
        message = {
            "role": "user",
            "contents": [{
                "kind": "text",
                "text": "Hey @AgentSupport can you help?"
            }]
        }

        text = message["contents"][0]["text"]
        has_mention = "@AgentSupport" in text
        assert has_mention is True

        # Message without mention
        message = {
            "role": "user",
            "contents": [{
                "kind": "text",
                "text": "I need help with this"
            }]
        }

        text = message["contents"][0]["text"]
        has_mention = "@AgentSupport" in text
        assert has_mention is False

    def test_evaluate_content_condition(self):
        """Test evaluating content type condition."""
        condition = {
            "kind": "content",
            "contentTypes": ["image", "video"]
        }

        # Message with image
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Check this out"},
                {"kind": "image", "uri": "https://example.com/photo.jpg"}
            ]
        }

        content_types = [c["kind"] for c in message["contents"]]
        should_activate = any(ct in condition["contentTypes"] for ct in content_types)
        assert should_activate is True

        # Message with only text
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Just text"}
            ]
        }

        content_types = [c["kind"] for c in message["contents"]]
        should_activate = any(ct in condition["contentTypes"] for ct in content_types)
        assert should_activate is False

    def test_watch_activation_count(self):
        """Test tracking watch activation count."""
        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_support",
            thread_id="thread_001"
        )

        # Simulate activations
        watch["activationCount"] = 0

        # Message 1
        watch["activationCount"] += 1
        watch["lastActivatedAt"] = "2026-02-07T10:01:00Z"

        # Message 2
        watch["activationCount"] += 1
        watch["lastActivatedAt"] = "2026-02-07T10:02:00Z"

        assert watch["activationCount"] == 2
        assert watch["lastActivatedAt"] == "2026-02-07T10:02:00Z"

    def test_deactivate_watch(self):
        """Test deactivating watch."""
        watch = ThreadWatchTestHelper.create_watch(
            agent_id="agent_support",
            thread_id="thread_001"
        )

        # Deactivate
        watch["active"] = False

        assert watch["active"] is False

        # Watch should not trigger when inactive
        if not watch["active"]:
            should_trigger = False
        else:
            should_trigger = True

        assert should_trigger is False


class TestAutoResponse:
    """Test auto-response patterns."""

    def test_auto_response_config(self):
        """Test auto-response configuration."""
        condition = {
            "kind": "roles",
            "roles": ["user"]
        }

        agent = ThreadWatchTestHelper.create_auto_response_agent(condition)

        assert "autoResponseConfig" in agent
        assert agent["autoResponseConfig"]["runCondition"]["kind"] == "roles"
        assert agent["autoResponseConfig"]["maxConsecutiveRuns"] == 1

    def test_max_consecutive_runs(self):
        """Test maxConsecutiveRuns enforcement."""
        max_consecutive = 2
        consecutive_count = 0

        # User message → Agent runs (count = 1)
        consecutive_count += 1
        can_run = consecutive_count <= max_consecutive
        assert can_run is True

        # Agent response → triggers another run (count = 2)
        consecutive_count += 1
        can_run = consecutive_count <= max_consecutive
        assert can_run is True

        # Would trigger third run (count = 3) → blocked
        consecutive_count += 1
        can_run = consecutive_count <= max_consecutive
        assert can_run is False

        # User message resets counter
        consecutive_count = 0

    def test_always_condition(self):
        """Test AlwaysCondition (dangerous - always activates)."""
        condition = {"kind": "always"}

        # Always returns True
        should_activate = True  # AlwaysCondition always activates

        assert should_activate is True

    def test_expression_condition(self):
        """Test ExpressionCondition with CEL."""
        condition = {
            "kind": "expression",
            "expression": "message.role == 'user' && message.text.contains('urgent')"
        }

        # Simulate evaluation
        message = {
            "role": "user",
            "text": "This is urgent!"
        }

        # Would be evaluated by CEL engine
        # Simplified evaluation for test
        matches_role = message["role"] == "user"
        contains_urgent = "urgent" in message["text"].lower()
        should_activate = matches_role and contains_urgent

        assert should_activate is True

    def test_multiple_watches_same_thread(self):
        """Test multiple agents watching same thread."""
        thread_id = "thread_multi_001"

        watches = [
            ThreadWatchTestHelper.create_watch(
                agent_id="agent_support",
                thread_id=thread_id,
                condition={"kind": "roles", "roles": ["user"]}
            ),
            ThreadWatchTestHelper.create_watch(
                agent_id="agent_supervisor",
                thread_id=thread_id,
                condition={"kind": "mention", "requireExplicitMention": True}
            ),
            ThreadWatchTestHelper.create_watch(
                agent_id="agent_video",
                thread_id=thread_id,
                condition={"kind": "content", "contentTypes": ["video"]}
            )
        ]

        assert len(watches) == 3
        assert all(w["threadId"] == thread_id for w in watches)
        assert len(set(w["agentId"] for w in watches)) == 3  # All different agents

    def test_watch_priority(self):
        """Test watch priority/ordering."""
        # User message arrives
        message = {
            "role": "user",
            "contents": [{"kind": "text", "text": "Hello"}]
        }

        # Multiple watches match
        watches = [
            {"agentId": "agent_support", "priority": 1},
            {"agentId": "agent_triage", "priority": 2},
            {"agentId": "agent_qa", "priority": 3}
        ]

        # Sort by priority
        sorted_watches = sorted(watches, key=lambda w: w["priority"])

        assert sorted_watches[0]["agentId"] == "agent_support"  # Highest priority


class TestAutoResponseIntegration:
    """Test auto-response integration scenarios."""

    @patch('requests.post')
    def test_auto_response_creates_run(self, mock_post):
        """Test auto-response automatically creates run."""
        # Mock run creation
        mock_post.return_value.json.return_value = {
            "runId": "run_auto_001",
            "status": "in_progress",
            "agentId": "agent_support",
            "triggeredBy": "threadwatch:watch_123"
        }

        # Simulate ThreadWatch activation
        import requests
        response = requests.post(
            "https://api.example.com/v1/runs",
            json={
                "agentId": "agent_support",
                "threadId": "thread_001",
                "triggeredBy": "threadwatch:watch_123"
            }
        )

        result = response.json()
        assert result["status"] == "in_progress"
        assert result["triggeredBy"] == "threadwatch:watch_123"

    def test_auto_response_tiered_support(self):
        """Test tiered support with auto-response."""
        # Tier 1: Responds to all user messages
        tier1_condition = {
            "kind": "roles",
            "roles": ["user"]
        }

        # Tier 2: Responds when mentioned
        tier2_condition = {
            "kind": "mention",
            "requireExplicitMention": True
        }

        # User message → Tier 1 activates
        message = {
            "role": "user",
            "contents": [{"kind": "text", "text": "I need help"}]
        }

        tier1_activates = message["role"] in tier1_condition["roles"]
        tier2_activates = "@Tier2" in message["contents"][0]["text"]

        assert tier1_activates is True
        assert tier2_activates is False

        # Tier 1 mentions Tier 2
        message = {
            "role": "assistant",
            "contents": [{"kind": "text", "text": "@Tier2 please assist"}]
        }

        tier1_activates = message["role"] in tier1_condition["roles"]
        tier2_activates = "@Tier2" in message["contents"][0]["text"]

        assert tier1_activates is False  # Not user role
        assert tier2_activates is True  # Has mention

    def test_content_based_routing(self):
        """Test content-based agent routing."""
        # Text agent: Responds to user messages without media
        text_condition = {
            "kind": "roles",
            "roles": ["user"]
        }

        # Image agent: Responds to images
        image_condition = {
            "kind": "content",
            "contentTypes": ["image"]
        }

        # Video agent: Responds to videos
        video_condition = {
            "kind": "content",
            "contentTypes": ["video"]
        }

        # User sends text → Text agent activates
        message = {
            "role": "user",
            "contents": [{"kind": "text", "text": "Hello"}]
        }

        text_activates = message["role"] == "user"
        image_activates = any(c["kind"] == "image" for c in message["contents"])
        video_activates = any(c["kind"] == "video" for c in message["contents"])

        assert text_activates is True
        assert image_activates is False
        assert video_activates is False

        # User sends image → Image agent activates
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "What's this?"},
                {"kind": "image", "uri": "https://example.com/photo.jpg"}
            ]
        }

        image_activates = any(c["kind"] == "image" for c in message["contents"])

        assert image_activates is True
```

Due to the length of this comprehensive guide, I'll create a separate script to append the remaining sections including the JavaScript implementation continuation and all other remaining patterns.


#### JavaScript Implementation (continued)

```javascript
// test/integration/threadWatch.test.js

class ThreadWatchTestHelper {
  static createWatch(agentId, threadId, condition = null) {
    return {
      watchId: `watch_${agentId}_${threadId}`,
      threadId,
      agentId,
      active: true,
      condition: condition || { kind: 'roles', roles: ['user'] },
      createdAt: '2026-02-07T10:00:00Z',
      activationCount: 0
    };
  }

  static createAutoResponseAgent(condition) {
    return {
      kind: 'prompt',
      agentId: 'agent_auto',
      name: 'Auto Response Agent',
      model: 'gpt-4o',
      instructions: 'You respond automatically.',
      autoResponseConfig: {
        runCondition: condition,
        maxConsecutiveRuns: 1,
        threadCleanup: 'keep'
      }
    };
  }
}

describe('ThreadWatch Activation', () => {
  test('creates thread watch', () => {
    const watch = ThreadWatchTestHelper.createWatch('agent_support', 'thread_001');

    expect(watch.agentId).toBe('agent_support');
    expect(watch.threadId).toBe('thread_001');
    expect(watch.active).toBe(true);
  });

  test('watch with roles condition', () => {
    const condition = {
      kind: 'roles',
      roles: ['user']
    };

    const watch = ThreadWatchTestHelper.createWatch('agent_support', 'thread_001', condition);

    expect(watch.condition.kind).toBe('roles');
    expect(watch.condition.roles).toContain('user');
  });

  test('evaluates roles condition', () => {
    const condition = {
      kind: 'roles',
      roles: ['user']
    };

    // User message
    let message = { role: 'user', contents: [] };
    let shouldActivate = condition.roles.includes(message.role);
    expect(shouldActivate).toBe(true);

    // Assistant message
    message = { role: 'assistant', contents: [] };
    shouldActivate = condition.roles.includes(message.role);
    expect(shouldActivate).toBe(false);
  });

  test('evaluates mention condition', () => {
    const condition = {
      kind: 'mention',
      requireExplicitMention: true
    };

    // Message with mention
    let message = {
      role: 'user',
      contents: [{
        kind: 'text',
        text: 'Hey @AgentSupport can you help?'
      }]
    };

    let hasMention = message.contents[0].text.includes('@AgentSupport');
    expect(hasMention).toBe(true);

    // Message without mention
    message = {
      role: 'user',
      contents: [{
        kind: 'text',
        text: 'I need help with this'
      }]
    };

    hasMention = message.contents[0].text.includes('@AgentSupport');
    expect(hasMention).toBe(false);
  });

  test('evaluates content condition', () => {
    const condition = {
      kind: 'content',
      contentTypes: ['image', 'video']
    };

    // Message with image
    let message = {
      role: 'user',
      contents: [
        { kind: 'text', text: 'Check this out' },
        { kind: 'image', uri: 'https://example.com/photo.jpg' }
      ]
    };

    let contentTypes = message.contents.map(c => c.kind);
    let shouldActivate = condition.contentTypes.some(ct => contentTypes.includes(ct));
    expect(shouldActivate).toBe(true);

    // Message with only text
    message = {
      role: 'user',
      contents: [
        { kind: 'text', text: 'Just text' }
      ]
    };

    contentTypes = message.contents.map(c => c.kind);
    shouldActivate = condition.contentTypes.some(ct => contentTypes.includes(ct));
    expect(shouldActivate).toBe(false);
  });

  test('tracks activation count', () => {
    const watch = ThreadWatchTestHelper.createWatch('agent_support', 'thread_001');

    watch.activationCount = 0;

    // Activation 1
    watch.activationCount += 1;
    watch.lastActivatedAt = '2026-02-07T10:01:00Z';

    // Activation 2
    watch.activationCount += 1;
    watch.lastActivatedAt = '2026-02-07T10:02:00Z';

    expect(watch.activationCount).toBe(2);
    expect(watch.lastActivatedAt).toBe('2026-02-07T10:02:00Z');
  });

  test('deactivates watch', () => {
    const watch = ThreadWatchTestHelper.createWatch('agent_support', 'thread_001');

    watch.active = false;

    expect(watch.active).toBe(false);

    const shouldTrigger = watch.active;
    expect(shouldTrigger).toBe(false);
  });
});

describe('Auto-Response', () => {
  test('configures auto-response', () => {
    const condition = {
      kind: 'roles',
      roles: ['user']
    };

    const agent = ThreadWatchTestHelper.createAutoResponseAgent(condition);

    expect(agent).toHaveProperty('autoResponseConfig');
    expect(agent.autoResponseConfig.runCondition.kind).toBe('roles');
    expect(agent.autoResponseConfig.maxConsecutiveRuns).toBe(1);
  });

  test('enforces maxConsecutiveRuns', () => {
    const maxConsecutive = 2;
    let consecutiveCount = 0;

    // Run 1
    consecutiveCount += 1;
    expect(consecutiveCount <= maxConsecutive).toBe(true);

    // Run 2
    consecutiveCount += 1;
    expect(consecutiveCount <= maxConsecutive).toBe(true);

    // Run 3 - blocked
    consecutiveCount += 1;
    expect(consecutiveCount <= maxConsecutive).toBe(false);

    // User message resets
    consecutiveCount = 0;
  });

  test('multiple watches on same thread', () => {
    const threadId = 'thread_multi_001';

    const watches = [
      ThreadWatchTestHelper.createWatch(
        'agent_support',
        threadId,
        { kind: 'roles', roles: ['user'] }
      ),
      ThreadWatchTestHelper.createWatch(
        'agent_supervisor',
        threadId,
        { kind: 'mention', requireExplicitMention: true }
      ),
      ThreadWatchTestHelper.createWatch(
        'agent_video',
        threadId,
        { kind: 'content', contentTypes: ['video'] }
      )
    ];

    expect(watches).toHaveLength(3);
    expect(watches.every(w => w.threadId === threadId)).toBe(true);

    const agentIds = new Set(watches.map(w => w.agentId));
    expect(agentIds.size).toBe(3);
  });
});

describe('Auto-Response Scenarios', () => {
  test('tiered support activation', () => {
    const tier1Condition = {
      kind: 'roles',
      roles: ['user']
    };

    const tier2Condition = {
      kind: 'mention',
      requireExplicitMention: true
    };

    // User message → Tier 1 activates
    let message = {
      role: 'user',
      contents: [{ kind: 'text', text: 'I need help' }]
    };

    let tier1Activates = tier1Condition.roles.includes(message.role);
    let tier2Activates = message.contents[0].text.includes('@Tier2');

    expect(tier1Activates).toBe(true);
    expect(tier2Activates).toBe(false);

    // Tier 1 mentions Tier 2
    message = {
      role: 'assistant',
      contents: [{ kind: 'text', text: '@Tier2 please assist' }]
    };

    tier1Activates = tier1Condition.roles.includes(message.role);
    tier2Activates = message.contents[0].text.includes('@Tier2');

    expect(tier1Activates).toBe(false);
    expect(tier2Activates).toBe(true);
  });

  test('content-based routing', () => {
    const textCondition = { kind: 'roles', roles: ['user'] };
    const imageCondition = { kind: 'content', contentTypes: ['image'] };
    const videoCondition = { kind: 'content', contentTypes: ['video'] };

    // Text only
    let message = {
      role: 'user',
      contents: [{ kind: 'text', text: 'Hello' }]
    };

    let textActivates = message.role === 'user';
    let imageActivates = message.contents.some(c => c.kind === 'image');
    let videoActivates = message.contents.some(c => c.kind === 'video');

    expect(textActivates).toBe(true);
    expect(imageActivates).toBe(false);
    expect(videoActivates).toBe(false);

    // With image
    message = {
      role: 'user',
      contents: [
        { kind: 'text', text: "What's this?" },
        { kind: 'image', uri: 'https://example.com/photo.jpg' }
      ]
    };

    imageActivates = message.contents.some(c => c.kind === 'image');

    expect(imageActivates).toBe(true);
  });
});
```

## Test Fixtures and Factories

### Reusable Test Data

#### Python Fixtures

```python
# tests/fixtures/agents.py

import pytest
from typing import Dict, Any
from datetime import datetime, timedelta

@pytest.fixture
def agent_factory():
    """Factory for creating agent configurations."""
    def create_agent(
        agent_id: str = "agent_test",
        model: str = "gpt-4o",
        tools: list = None,
        auto_response: Dict = None
    ) -> Dict[str, Any]:
        agent = {
            "kind": "prompt",
            "agentId": agent_id,
            "name": f"Test Agent {agent_id}",
            "model": model,
            "instructions": "You are a test agent."
        }

        if tools:
            agent["tools"] = tools

        if auto_response:
            agent["autoResponseConfig"] = auto_response

        return agent

    return create_agent


@pytest.fixture
def run_factory():
    """Factory for creating run objects."""
    def create_run(
        status: str = "completed",
        agent_id: str = "agent_test",
        thread_id: str = None
    ) -> Dict[str, Any]:
        return {
            "runId": f"run_{datetime.now().timestamp()}",
            "agentId": agent_id,
            "threadId": thread_id or f"thread_{datetime.now().timestamp()}",
            "status": status,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "input": [],
            "output": []
        }

    return create_run


@pytest.fixture
def message_factory():
    """Factory for creating message objects."""
    def create_message(
        role: str = "user",
        text: str = "Test message",
        message_id: str = None
    ) -> Dict[str, Any]:
        return {
            "messageId": message_id or f"msg_{datetime.now().timestamp()}",
            "role": role,
            "contents": [{
                "kind": "text",
                "text": text
            }],
            "createdAt": datetime.now().isoformat()
        }

    return create_message


@pytest.fixture
def tool_call_factory():
    """Factory for creating tool calls."""
    def create_tool_call(
        name: str = "test_tool",
        arguments: Dict = None,
        call_id: str = None
    ) -> Dict[str, Any]:
        return {
            "kind": "functionCall",
            "callId": call_id or f"call_{datetime.now().timestamp()}",
            "name": name,
            "arguments": arguments or {}
        }

    return create_tool_call


@pytest.fixture
def thread_factory():
    """Factory for creating threads."""
    def create_thread(
        thread_id: str = None,
        participants: list = None
    ) -> Dict[str, Any]:
        return {
            "threadId": thread_id or f"thread_{datetime.now().timestamp()}",
            "status": "active",
            "participants": participants or [
                {"id": "user_1", "role": "user"}
            ],
            "messages": [],
            "createdAt": datetime.now().isoformat(),
            "metadata": {}
        }

    return create_thread


# tests/fixtures/mocks.py

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response."""
    def create_response(
        text: str = "Mock response",
        tool_calls: list = None
    ) -> Dict[str, Any]:
        contents = [{"kind": "text", "text": text}]

        if tool_calls:
            contents.extend(tool_calls)

        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "contents": contents
                },
                "finishReason": "stop"
            }],
            "usage": {
                "promptTokens": 10,
                "completionTokens": 20,
                "totalTokens": 30
            }
        }

    return create_response


@pytest.fixture
def mock_api_client():
    """Mock Agent Runtime API client."""
    class MockAPIClient:
        def __init__(self):
            self.runs = {}
            self.threads = {}
            self.watches = {}

        def create_run(self, request: Dict) -> Dict:
            run_id = f"run_{len(self.runs) + 1}"
            run = {
                "runId": run_id,
                "status": "queued",
                **request
            }
            self.runs[run_id] = run
            return run

        def get_run(self, run_id: str) -> Dict:
            return self.runs.get(run_id)

        def create_thread(self, request: Dict) -> Dict:
            thread_id = f"thread_{len(self.threads) + 1}"
            thread = {
                "threadId": thread_id,
                "status": "active",
                "messages": [],
                **request
            }
            self.threads[thread_id] = thread
            return thread

        def create_watch(self, thread_id: str, request: Dict) -> Dict:
            watch_id = f"watch_{len(self.watches) + 1}"
            watch = {
                "watchId": watch_id,
                "threadId": thread_id,
                "active": True,
                **request
            }
            self.watches[watch_id] = watch
            return watch

    return MockAPIClient()
```

#### JavaScript Fixtures

```javascript
// test/fixtures/factories.js

export class AgentFactory {
  static create({
    agentId = 'agent_test',
    model = 'gpt-4o',
    tools = null,
    autoResponse = null
  } = {}) {
    const agent = {
      kind: 'prompt',
      agentId,
      name: `Test Agent ${agentId}`,
      model,
      instructions: 'You are a test agent.'
    };

    if (tools) {
      agent.tools = tools;
    }

    if (autoResponse) {
      agent.autoResponseConfig = autoResponse;
    }

    return agent;
  }
}

export class RunFactory {
  static create({
    status = 'completed',
    agentId = 'agent_test',
    threadId = null
  } = {}) {
    return {
      runId: `run_${Date.now()}_${Math.random()}`,
      agentId,
      threadId: threadId || `thread_${Date.now()}`,
      status,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      input: [],
      output: []
    };
  }
}

export class MessageFactory {
  static create({
    role = 'user',
    text = 'Test message',
    messageId = null
  } = {}) {
    return {
      messageId: messageId || `msg_${Date.now()}_${Math.random()}`,
      role,
      contents: [{
        kind: 'text',
        text
      }],
      createdAt: new Date().toISOString()
    };
  }
}

export class ToolCallFactory {
  static create({
    name = 'test_tool',
    arguments: args = {},
    callId = null
  } = {}) {
    return {
      kind: 'functionCall',
      callId: callId || `call_${Date.now()}_${Math.random()}`,
      name,
      arguments: args
    };
  }
}

export class ThreadFactory {
  static create({
    threadId = null,
    participants = null
  } = {}) {
    return {
      threadId: threadId || `thread_${Date.now()}_${Math.random()}`,
      status: 'active',
      participants: participants || [
        { id: 'user_1', role: 'user' }
      ],
      messages: [],
      createdAt: new Date().toISOString(),
      metadata: {}
    };
  }
}

// test/fixtures/mocks.js

export class MockLLMResponse {
  static create({
    text = 'Mock response',
    toolCalls = null
  } = {}) {
    const contents = [{ kind: 'text', text }];

    if (toolCalls) {
      contents.push(...toolCalls);
    }

    return {
      choices: [{
        message: {
          role: 'assistant',
          contents
        },
        finishReason: 'stop'
      }],
      usage: {
        promptTokens: 10,
        completionTokens: 20,
        totalTokens: 30
      }
    };
  }
}

export class MockAPIClient {
  constructor() {
    this.runs = new Map();
    this.threads = new Map();
    this.watches = new Map();
  }

  createRun(request) {
    const runId = `run_${this.runs.size + 1}`;
    const run = {
      runId,
      status: 'queued',
      ...request
    };
    this.runs.set(runId, run);
    return run;
  }

  getRun(runId) {
    return this.runs.get(runId);
  }

  createThread(request) {
    const threadId = `thread_${this.threads.size + 1}`;
    const thread = {
      threadId,
      status: 'active',
      messages: [],
      ...request
    };
    this.threads.set(threadId, thread);
    return thread;
  }

  createWatch(threadId, request) {
    const watchId = `watch_${this.watches.size + 1}`;
    const watch = {
      watchId,
      threadId,
      active: true,
      ...request
    };
    this.watches.set(watchId, watch);
    return watch;
  }
}
```

### Using Fixtures in Tests

```python
# tests/test_with_fixtures.py

def test_create_agent_with_factory(agent_factory):
    """Test agent creation with factory."""
    agent = agent_factory(
        agent_id="agent_custom",
        tools=[{"name": "search", "description": "Search tool"}]
    )

    assert agent["agentId"] == "agent_custom"
    assert len(agent["tools"]) == 1
    assert agent["tools"][0]["name"] == "search"


def test_create_run_with_factory(run_factory):
    """Test run creation with factory."""
    run = run_factory(status="in_progress", agent_id="agent_test")

    assert run["status"] == "in_progress"
    assert run["agentId"] == "agent_test"
    assert "runId" in run


def test_mock_api_client(mock_api_client):
    """Test using mock API client."""
    # Create thread
    thread = mock_api_client.create_thread({
        "participants": [{"id": "user_1", "role": "user"}]
    })

    # Create run
    run = mock_api_client.create_run({
        "threadId": thread["threadId"],
        "agentId": "agent_test"
    })

    # Verify
    assert run["threadId"] == thread["threadId"]
    retrieved_run = mock_api_client.get_run(run["runId"])
    assert retrieved_run["runId"] == run["runId"]
```

## Validation Strategies

### Content Validation

```python
# tests/validators/content_validator.py

class ContentValidator:
    """Validate message content structures."""

    @staticmethod
    def validate_text_content(content: Dict) -> bool:
        """Validate TextContent."""
        required_fields = ["kind", "text"]
        return (
            all(field in content for field in required_fields) and
            content["kind"] == "text" and
            isinstance(content["text"], str)
        )

    @staticmethod
    def validate_function_call_content(content: Dict) -> bool:
        """Validate FunctionCallContent."""
        required_fields = ["kind", "callId", "name"]
        return (
            all(field in content for field in required_fields) and
            content["kind"] == "functionCall" and
            isinstance(content["name"], str) and
            isinstance(content["callId"], str)
        )

    @staticmethod
    def validate_function_result_content(content: Dict) -> bool:
        """Validate FunctionResultContent."""
        required_fields = ["kind", "callId", "name"]
        return (
            all(field in content for field in required_fields) and
            content["kind"] == "functionResult" and
            isinstance(content["name"], str) and
            isinstance(content["callId"], str) and
            ("result" in content or "exception" in content)
        )

    @staticmethod
    def validate_message(message: Dict) -> bool:
        """Validate complete message."""
        required_fields = ["messageId", "role", "contents"]

        if not all(field in message for field in required_fields):
            return False

        valid_roles = ["user", "assistant", "system", "tool", "developer", "channel"]
        if message["role"] not in valid_roles:
            return False

        if not isinstance(message["contents"], list):
            return False

        # Validate all contents
        for content in message["contents"]:
            kind = content.get("kind")
            if kind == "text":
                if not ContentValidator.validate_text_content(content):
                    return False
            elif kind == "functionCall":
                if not ContentValidator.validate_function_call_content(content):
                    return False
            elif kind == "functionResult":
                if not ContentValidator.validate_function_result_content(content):
                    return False

        return True


# Test usage
def test_content_validator():
    """Test content validation."""
    # Valid text content
    content = {"kind": "text", "text": "Hello"}
    assert ContentValidator.validate_text_content(content) is True

    # Invalid text content
    content = {"kind": "text"}
    assert ContentValidator.validate_text_content(content) is False

    # Valid message
    message = {
        "messageId": "msg_1",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello"}
        ]
    }
    assert ContentValidator.validate_message(message) is True
```

### State Transition Validation

```python
# tests/validators/state_validator.py

class StateValidator:
    """Validate run state transitions."""

    VALID_TRANSITIONS = {
        "queued": ["in_progress", "cancelled", "failed"],
        "in_progress": [
            "requires_action", "input_required", "auth_required",
            "completed", "failed", "incomplete", "timeout", "cancelling"
        ],
        "requires_action": ["in_progress", "timeout", "cancelled", "failed"],
        "input_required": ["in_progress", "timeout", "cancelled", "failed"],
        "auth_required": ["in_progress", "timeout", "cancelled", "failed"],
        "cancelling": ["cancelled", "completed"],
        # Terminal states
        "cancelled": [],
        "failed": [],
        "completed": [],
        "incomplete": [],
        "timeout": []
    }

    @staticmethod
    def is_valid_transition(from_state: str, to_state: str) -> bool:
        """Check if state transition is valid."""
        return to_state in StateValidator.VALID_TRANSITIONS.get(from_state, [])

    @staticmethod
    def is_terminal(state: str) -> bool:
        """Check if state is terminal."""
        return len(StateValidator.VALID_TRANSITIONS.get(state, [])) == 0

    @staticmethod
    def validate_run_history(transitions: list) -> bool:
        """Validate complete run transition history."""
        if not transitions:
            return False

        # First state must be queued
        if transitions[0].get("fromState") != "queued":
            return False

        # Validate each transition
        for transition in transitions:
            from_state = transition.get("fromState")
            to_state = transition.get("toState")

            if not StateValidator.is_valid_transition(from_state, to_state):
                return False

        return True


# Test usage
def test_state_validator():
    """Test state transition validation."""
    # Valid transition
    assert StateValidator.is_valid_transition("queued", "in_progress") is True

    # Invalid transition
    assert StateValidator.is_valid_transition("queued", "completed") is False

    # Terminal state
    assert StateValidator.is_terminal("completed") is True
    assert StateValidator.is_terminal("in_progress") is False

    # Valid history
    history = [
        {"fromState": "queued", "toState": "in_progress"},
        {"fromState": "in_progress", "toState": "requires_action"},
        {"fromState": "requires_action", "toState": "in_progress"},
        {"fromState": "in_progress", "toState": "completed"}
    ]
    assert StateValidator.validate_run_history(history) is True
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test-agents.yml

name: Agent Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-python:
    name: Python Tests
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: |
          pytest tests/unit -v --cov=src --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration -v --cov-append --cov=src

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: python

  test-javascript:
    name: JavaScript Tests
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: ['18.x', '20.x']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run integration tests
        run: npm run test:integration

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: javascript

  e2e-tests:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    needs: [test-python, test-javascript]

    steps:
      - uses: actions/checkout@v3

      - name: Set up test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          ./scripts/wait-for-services.sh

      - name: Run E2E tests
        run: |
          npm run test:e2e

      - name: Collect test artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-artifacts
          path: |
            test-results/
            screenshots/

      - name: Teardown test environment
        if: always()
        run: docker-compose -f docker-compose.test.yml down

  performance-tests:
    name: Performance Tests
    runs-on: ubuntu-latest
    needs: [test-python, test-javascript]

    steps:
      - uses: actions/checkout@v3

      - name: Set up test environment
        run: |
          docker-compose -f docker-compose.test.yml up -d
          ./scripts/wait-for-services.sh

      - name: Run load tests
        run: |
          npm run test:load

      - name: Upload performance report
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: performance-report.html
```

### Test Configuration Files

```ini
# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow-running tests
    requires_api: Tests requiring API access
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-branch
    --cov-report=term-missing
```

```json
// jest.config.js

module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '**/tests/**/*.test.js',
    '**/?(*.)+(spec|test).js'
  ],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/**/index.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testTimeout: 10000
};
```

### Test Scripts

```json
// package.json

{
  "scripts": {
    "test": "npm run test:unit && npm run test:integration",
    "test:unit": "jest tests/unit --coverage",
    "test:integration": "jest tests/integration --runInBand",
    "test:e2e": "jest tests/e2e --runInBand --detectOpenHandles",
    "test:watch": "jest --watch",
    "test:load": "k6 run tests/load/agent-load-test.js",
    "test:ci": "jest --ci --coverage --maxWorkers=2"
  }
}
```

```makefile
# Makefile

.PHONY: test test-unit test-integration test-all clean

test: test-unit test-integration

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-all:
	pytest tests/ -v --cov=src

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
```

## Examples

### Complete Test Suite Example

#### Python

```python
# tests/test_complete_workflow.py

import pytest
from typing import Dict, Any
import time

class TestCompleteAgentWorkflow:
    """End-to-end agent workflow tests."""

    @pytest.fixture
    def workflow_context(self, agent_factory, thread_factory, mock_api_client):
        """Setup workflow test context."""
        agent = agent_factory(
            agent_id="agent_workflow",
            tools=[
                {
                    "name": "search_web",
                    "description": "Search the web"
                },
                {
                    "name": "summarize",
                    "description": "Summarize content"
                }
            ]
        )

        thread = thread_factory()

        return {
            "agent": agent,
            "thread": thread,
            "client": mock_api_client
        }

    def test_simple_text_response(self, workflow_context):
        """Test simple text response workflow."""
        ctx = workflow_context

        # Create run
        run = ctx["client"].create_run({
            "agentId": ctx["agent"]["agentId"],
            "threadId": ctx["thread"]["threadId"],
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Hello"}]
            }]
        })

        # Simulate completion
        run["status"] = "completed"
        run["output"] = [{
            "role": "assistant",
            "contents": [{"kind": "text", "text": "Hello! How can I help?"}]
        }]

        assert run["status"] == "completed"
        assert len(run["output"]) == 1

    def test_workflow_with_tool_execution(self, workflow_context):
        """Test workflow with tool execution."""
        ctx = workflow_context

        # Create run
        run = ctx["client"].create_run({
            "agentId": ctx["agent"]["agentId"],
            "threadId": ctx["thread"]["threadId"],
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Search for AI news"}]
            }]
        })

        # Simulate tool call
        run["status"] = "requires_action"
        run["output"] = [{
            "role": "assistant",
            "contents": [{
                "kind": "functionCall",
                "callId": "call_1",
                "name": "search_web",
                "arguments": {"query": "AI news"}
            }]
        }]

        assert run["status"] == "requires_action"

        # Execute tool
        tool_result = {
            "callId": "call_1",
            "result": "Found 10 results about AI news..."
        }

        # Simulate resumption
        run["status"] = "in_progress"

        # Simulate completion
        run["status"] = "completed"
        run["output"].append({
            "role": "assistant",
            "contents": [{
                "kind": "text",
                "text": "Here's a summary of AI news..."
            }]
        })

        assert run["status"] == "completed"

    def test_multi_agent_handoff_workflow(self, workflow_context):
        """Test multi-agent handoff."""
        ctx = workflow_context

        # Create triage agent
        triage_agent = ctx["client"].create_run({
            "agentId": "agent_triage",
            "threadId": ctx["thread"]["threadId"],
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Billing question"}]
            }]
        })

        # Triage agent initiates handoff
        triage_agent["status"] = "requires_action"
        triage_agent["output"] = [{
            "role": "assistant",
            "contents": [{
                "kind": "functionCall",
                "callId": "call_handoff",
                "name": "transfer_to_billing",
                "arguments": {"reason": "Billing inquiry"}
            }]
        }]

        assert triage_agent["status"] == "requires_action"

        # Create billing agent run
        billing_agent = ctx["client"].create_run({
            "agentId": "agent_billing",
            "threadId": ctx["thread"]["threadId"],
            "input": []  # Reads from thread
        })

        billing_agent["status"] = "completed"
        billing_agent["output"] = [{
            "role": "assistant",
            "contents": [{
                "kind": "text",
                "text": "I can help with billing..."
            }]
        }]

        assert billing_agent["agentId"] == "agent_billing"
        assert billing_agent["status"] == "completed"
```

### Load Testing Example

```javascript
// tests/load/agent-load-test.js
// Using k6 for load testing

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '2m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'], // 95% of requests under 2s
    'errors': ['rate<0.1'],              // Error rate under 10%
  },
};

const API_BASE = __ENV.API_BASE || 'https://agents.example.com/v1';
const API_KEY = __ENV.API_KEY;

export default function () {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
  };

  // Create run
  const payload = JSON.stringify({
    agent: {
      kind: 'prompt',
      model: 'gpt-4o',
      instructions: 'You are a helpful assistant.'
    },
    input: [{
      role: 'user',
      contents: [{ kind: 'text', text: 'Hello, how are you?' }]
    }]
  });

  const response = http.post(`${API_BASE}/runs`, payload, { headers });

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has runId': (r) => JSON.parse(r.body).runId !== undefined,
  });

  errorRate.add(!success);

  sleep(1);
}
```

## Troubleshooting

### Common Testing Issues

#### Issue 1: Non-Deterministic Test Failures

**Problem**: Tests pass sometimes but fail randomly.

**Causes**:
- LLM responses vary across runs
- Timing issues with async operations
- Race conditions in parallel tests

**Solutions**:

```python
# Use mocked responses for deterministic behavior
@patch('llm_client.generate')
def test_deterministic_response(mock_generate):
    """Mock LLM for deterministic testing."""
    mock_generate.return_value = {
        "text": "Fixed response",
        "tokenUsage": {"total": 10}
    }

    result = run_agent_with_prompt("Test prompt")
    assert result["text"] == "Fixed response"


# Use retry logic for flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_with_retry():
    """Retry flaky test up to 3 times."""
    result = call_external_service()
    assert result is not None


# Set explicit timeouts
def test_with_timeout():
    """Set explicit timeout for async operations."""
    import asyncio

    async def run_async_test():
        result = await agent.run(timeout=5)
        return result

    result = asyncio.run(asyncio.wait_for(run_async_test(), timeout=10))
    assert result is not None
```

#### Issue 2: Tool Execution Mocking

**Problem**: Difficult to mock external API calls in tools.

**Solutions**:

```python
# Use dependency injection
class ToolExecutor:
    def __init__(self, api_client=None):
        self.api_client = api_client or RealAPIClient()

    def execute(self, tool_name, args):
        return self.api_client.call(tool_name, args)


# In tests
def test_tool_with_mock_api():
    """Use mock API client."""
    mock_api = Mock()
    mock_api.call.return_value = {"data": "mocked"}

    executor = ToolExecutor(api_client=mock_api)
    result = executor.execute("search", {"query": "test"})

    assert result["data"] == "mocked"
    mock_api.call.assert_called_once()
```

#### Issue 3: Thread State Synchronization

**Problem**: Tests fail due to stale thread state.

**Solutions**:

```python
# Always fetch fresh state
def test_thread_state():
    """Fetch fresh thread state."""
    thread_id = create_thread()

    # Don't reuse cached state
    thread_before = get_thread(thread_id)

    # Perform operation
    create_message(thread_id, "Test message")

    # Fetch fresh state
    thread_after = get_thread(thread_id)

    assert len(thread_after["messages"]) > len(thread_before["messages"])


# Use event-driven testing
def test_with_events():
    """Wait for events instead of polling."""
    thread_id = create_thread()

    event_received = threading.Event()

    def on_message(msg):
        event_received.set()

    subscribe_to_thread(thread_id, on_message)

    create_message(thread_id, "Test")

    # Wait for event with timeout
    assert event_received.wait(timeout=5)
```

#### Issue 4: Performance Test Variability

**Problem**: Load test results inconsistent.

**Solutions**:

```python
# Run multiple iterations
def test_performance_averaged():
    """Average results over multiple runs."""
    latencies = []

    for i in range(10):
        start = time.time()
        result = call_agent()
        latency = time.time() - start
        latencies.append(latency)

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 2.0  # Average under 2 seconds

    # Also check p95
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
    assert p95_latency < 3.0
```

### Debugging Strategies

```python
# Enable detailed logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_with_logging():
    """Enable detailed logging for debugging."""
    logger = logging.getLogger(__name__)
    logger.debug("Starting test")

    result = run_agent()

    logger.debug(f"Result: {result}")
    assert result is not None


# Capture HTTP traffic
import requests_mock

def test_with_http_capture():
    """Capture HTTP requests for debugging."""
    with requests_mock.Mocker() as m:
        m.post('/runs', json={'runId': 'run_1'})

        result = create_run()

        # Inspect request history
        assert m.call_count == 1
        assert m.request_history[0].method == 'POST'


# Use test fixtures for reproducibility
@pytest.fixture
def reproducible_scenario():
    """Create reproducible test scenario."""
    # Set random seed
    import random
    random.seed(42)

    # Use fixed timestamps
    from unittest.mock import patch
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 2, 7, 10, 0, 0)
        yield
```

## Best Practices

### Testing Checklist

- [ ] **Unit Tests**: Cover 80%+ of code paths
- [ ] **Integration Tests**: Test agent-tool-state interactions
- [ ] **E2E Tests**: Test complete workflows
- [ ] **Performance Tests**: Load test with realistic traffic
- [ ] **Mock External Dependencies**: Use mocks for APIs, LLMs
- [ ] **Test State Transitions**: Verify all 11 run states
- [ ] **Test Error Handling**: Cover failure scenarios
- [ ] **Test HITL Patterns**: Test all three interruption states
- [ ] **Test Multi-Agent**: Test handoffs and coordination
- [ ] **CI/CD Integration**: Run tests on every commit

### Test Organization

```
tests/
├── unit/
│   ├── test_agent_config.py
│   ├── test_tool_execution.py
│   ├── test_state_machine.py
│   └── test_validators.py
├── integration/
│   ├── test_run_lifecycle.py
│   ├── test_tool_api.py
│   ├── test_multi_agent.py
│   └── test_threadwatch.py
├── e2e/
│   ├── test_workflows.py
│   ├── test_hitl_scenarios.py
│   └── test_multi_agent_scenarios.py
├── load/
│   ├── agent_load_test.js
│   └── multi_agent_load_test.js
├── fixtures/
│   ├── agents.py
│   ├── mocks.py
│   └── factories.js
└── conftest.py
```

### Coverage Goals

| Test Type | Coverage Target | Purpose |
|-----------|----------------|---------|
| Unit Tests | 80-90% | Individual functions |
| Integration Tests | 70-80% | Component interactions |
| E2E Tests | 50-60% | Critical workflows |
| Performance Tests | N/A | Latency benchmarks |

## Related Documentation

- **Multi-Agent Guide**: [../multi-agent.md](../multi-agent.md) - Testing multi-agent coordination
- **Human-in-Loop Guide**: [../human-in-loop.md](../human-in-loop.md) - Testing HITL patterns
- **Tool Execution Spec**: [../specifications/tool-execution.md](../specifications/tool-execution.md) - Tool testing requirements
- **Run Lifecycle Spec**: [../specifications/run-lifecycle.md](../specifications/run-lifecycle.md) - State transition validation
- **TypeSpec Models**: [../../typespec/execution.tsp](../../typespec/execution.tsp) - Run and state models

