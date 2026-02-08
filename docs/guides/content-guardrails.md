# Content Guardrails Guide

**Version**: 1.0

## Overview

This guide explains how to implement content guardrails using the Agent Runtime API's hooks system to filter, modify, approve, and monitor agent content in real-time.

**What You'll Learn:**

- Understand the five hook types (RemoteHook, BlockHook, ModifyHook, TelemetryHook, SendMessageHook)
- Implement PII redaction with predefined and custom patterns
- Build content filtering and blocking workflows
- Create approval workflows for sensitive operations
- Monitor and audit agent behavior with telemetry
- Configure hooks at four lifecycle points (beforeRun, afterRun, beforeToolExecution, afterToolExecution)
- Handle streaming content modification
- Build custom remote hook services
- Implement compliance and governance controls

Content guardrails enable you to:

- **Protect User Privacy**: Automatically redact PII (emails, phone numbers, SSNs) from agent responses
- **Enforce Policies**: Block inappropriate content or prohibited operations
- **Enable Compliance**: Log all interactions for audit trails and regulatory requirements
- **Improve Quality**: Inject feedback to regenerate low-quality responses
- **Control Costs**: Monitor and limit expensive operations

## Prerequisites

- **API Access**: Agent Runtime API endpoint and credentials
- **Programming Language**: Examples in Python and JavaScript
- **HTTP Client**: requests (Python), fetch (JavaScript)
- **Optional**: WebSocket library for real-time hook implementations

## Quick Start

Here's a minimal example showing PII redaction before content reaches users:

```python
import requests

# Configure agent with PII redaction hook
agent_config = {
    "name": "customer-support-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are a helpful customer support agent.",
    "hooks": {
        "afterRun": [
            {
                "kind": "modify",
                "name": "pii-redactor",
                "condition": {
                    "kind": "always"
                },
                "predefinedPatterns": ["email", "phone", "ssn"],
                "replacement": "[REDACTED]"
            }
        ]
    }
}

# Create agent
response = requests.post(
    "https://api.example.com/agents",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json=agent_config
)
agent_id = response.json()["agentId"]

# Run with PII redaction enabled
run_response = requests.post(
    f"https://api.example.com/agents/{agent_id}/runs",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "threadId": "thread_123",
        "message": {
            "role": "user",
            "content": [
                {
                    "kind": "text",
                    "text": "My email is john@example.com and phone is 555-1234"
                }
            ]
        }
    }
)

# Response will have PII redacted: "My email is [REDACTED] and phone is [REDACTED]"
```

## Use Cases

### 1. Privacy Protection

**Scenario**: Prevent PII from reaching users or logs

**Solution**: ModifyHook with predefined patterns

**Example**: Healthcare chatbot that must comply with HIPAA by redacting all patient identifiers

```json
{
  "kind": "modify",
  "name": "hipaa-redactor",
  "predefinedPatterns": ["email", "phone", "ssn", "medical_record_number"],
  "replacement": "[PROTECTED HEALTH INFORMATION]"
}
```

### 2. Content Moderation

**Scenario**: Block inappropriate or harmful content

**Solution**: RemoteHook with content filtering service or BlockHook with conditions

**Example**: Public-facing chatbot that must filter offensive language

```json
{
  "kind": "remote",
  "name": "content-filter",
  "endpoint": "https://hooks.example.com/content-filter",
  "condition": {
    "kind": "content",
    "contentTypes": ["text"]
  }
}
```

### 3. Compliance Auditing

**Scenario**: Log all agent interactions for regulatory compliance

**Solution**: TelemetryHook with audit logging

**Example**: Financial services chatbot with SOX compliance requirements

```json
{
  "kind": "telemetry",
  "name": "sox-audit-logger",
  "event": "agent.interaction",
  "properties": {
    "compliance": "sox",
    "retention": "7-years"
  }
}
```

### 4. Approval Workflows

**Scenario**: Require human approval for high-risk operations

**Solution**: RemoteHook that blocks until approval granted

**Example**: Agent that can execute database operations requires DBA approval

```json
{
  "kind": "remote",
  "name": "db-approval-gateway",
  "endpoint": "https://hooks.example.com/approvals",
  "condition": {
    "kind": "expression",
    "expression": "tool.name == 'execute_sql'"
  }
}
```

### 5. Quality Control

**Scenario**: Regenerate low-quality or incomplete responses

**Solution**: SendMessageHook to inject feedback for regeneration

**Example**: Agent responses must meet minimum length requirements

```json
{
  "kind": "sendMessage",
  "name": "quality-enforcer",
  "condition": {
    "kind": "expression",
    "expression": "len(message.content[0].text) < 100"
  },
  "message": {
    "role": "system",
    "content": [
      {
        "kind": "text",
        "text": "Please provide a more detailed and comprehensive response."
      }
    ]
  }
}
```

### 6. Cost Control

**Scenario**: Monitor and limit expensive operations

**Solution**: BlockHook or RemoteHook with budget checks

**Example**: Block expensive tool calls for non-premium users

```json
{
  "kind": "block",
  "name": "cost-limiter",
  "condition": {
    "kind": "expression",
    "expression": "tool.cost > 5.00 && user.tier != 'premium'"
  },
  "message": "This operation requires a premium subscription"
}
```

## Architecture

### Hook System Overview

The Agent Runtime API provides a comprehensive hooks system that intercepts events at four lifecycle points:

```text
Run Lifecycle with Hooks:

┌─────────────────────────────────────────────────────────────┐
│                         RUN START                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  beforeRun      │ ← Hook Point 1
                    │  hooks evaluate │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  Agent thinking │
                    │  LLM generates  │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  beforeTool     │ ← Hook Point 2
                    │  Execution      │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  Tool executes  │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  afterTool      │ ← Hook Point 3
                    │  Execution      │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  Agent completes│
                    │  response       │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  afterRun       │ ← Hook Point 4
                    │  hooks evaluate │
                    └─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         RUN COMPLETE                        │
└─────────────────────────────────────────────────────────────┘
```

### Hook Types

The API provides five hook types, each optimized for specific use cases:

| Hook Type | Purpose | Blocking | Remote Call | Use Cases |
|-----------|---------|----------|-------------|-----------|
| **RemoteHook** | Delegate to external service | Yes | Yes | Custom logic, complex workflows, integration |
| **BlockHook** | Reject content matching condition | Yes | No | Simple policy enforcement, emergency stops |
| **ModifyHook** | Transform content with patterns | No | No | PII redaction, sanitization |
| **TelemetryHook** | Observe and log events | No | No | Auditing, monitoring, analytics |
| **SendMessageHook** | Inject messages for regeneration | No | No | Quality control, feedback loops |

### Hook Lifecycle Points

Hooks can be attached to four lifecycle points:

#### 1. beforeRun

**Trigger**: Before agent execution starts

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Input validation
- Pre-execution authorization
- User message sanitization
- Rate limiting checks

**Example**:
```json
{
  "beforeRun": [
    {
      "kind": "modify",
      "name": "input-sanitizer",
      "predefinedPatterns": ["email", "phone"],
      "replacement": "[REDACTED]"
    }
  ]
}
```

#### 2. afterRun

**Trigger**: After agent execution completes

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook, SendMessageHook

**Use Cases**:
- Output sanitization
- Quality control
- Response review
- Compliance logging

**Example**:
```json
{
  "afterRun": [
    {
      "kind": "sendMessage",
      "name": "quality-checker",
      "condition": {
        "kind": "expression",
        "expression": "len(message.content[0].text) < 50"
      },
      "message": {
        "role": "system",
        "content": [
          {
            "kind": "text",
            "text": "Response too brief. Please provide more detail."
          }
        ]
      }
    }
  ]
}
```

#### 3. beforeToolExecution

**Trigger**: Before each tool call

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Tool call authorization
- Parameter validation
- Cost control
- Security checks

**Example**:
```json
{
  "beforeToolExecution": [
    {
      "kind": "block",
      "name": "dangerous-tool-blocker",
      "condition": {
        "kind": "expression",
        "expression": "tool.name in ['delete_database', 'drop_table']"
      },
      "message": "This operation is not permitted"
    }
  ]
}
```

#### 4. afterToolExecution

**Trigger**: After each tool call

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Result sanitization
- Output redaction
- Success/failure logging
- Error recovery

**Example**:
```json
{
  "afterToolExecution": [
    {
      "kind": "modify",
      "name": "result-sanitizer",
      "predefinedPatterns": ["email", "phone", "ssn"],
      "replacement": "[REDACTED]"
    }
  ]
}
```

### Hook Evaluation Flow

When an event occurs at a lifecycle point, the runtime processes hooks as follows:

```text
Event Triggered (e.g., content.created)
          ↓
Identify Applicable Hooks
(Hooks configured for this lifecycle point)
          ↓
For Each Hook (in order):
          ↓
    ┌──────────────────┐
    │ Evaluate         │
    │ RunCondition     │
    └──────────────────┘
          ↓
    Condition FALSE? → Skip hook
          ↓
    Condition TRUE? → Continue
          ↓
    ┌──────────────────┐
    │ Execute Hook     │
    │ - Remote: POST   │
    │ - Block: Stop    │
    │ - Modify: Apply  │
    │ - Telemetry: Log │
    │ - SendMsg: Inject│
    └──────────────────┘
          ↓
    ┌──────────────────┐
    │ Process Response │
    │ - Allow: Continue│
    │ - Block: Stop    │
    │ - Modify: Apply  │
    └──────────────────┘
          ↓
All Hooks Complete
          ↓
Continue Run Execution
```

### Conditions System

All hooks support optional `condition` field to control when they evaluate. This enables fine-grained control and reduces unnecessary processing.

**Available Condition Types:**

1. **AlwaysCondition**: Always evaluates to true
2. **RolesCondition**: Match message roles (user, assistant, system)
3. **ContentCondition**: Match content types (text, image, video)
4. **MentionCondition**: Match explicit @mentions
5. **ExpressionCondition**: Custom logic (Power Fx or CEL)
6. **RemoteCondition**: External evaluation service

**Example - Content Type Filtering:**
```json
{
  "kind": "content",
  "contentTypes": ["image", "video"]
}
```

**Example - Expression-Based Filtering:**
```json
{
  "kind": "expression",
  "expression": "message.role == 'assistant' && len(message.content[0].text) > 1000"
}
```

## Implementation

### Step 1: Understanding Hook Types

Before implementing guardrails, understand which hook type fits your needs:

#### RemoteHook - External Service Integration

**When to use:**
- Complex business logic
- External system integration
- Dynamic decision making
- Approval workflows

**Structure:**
```typescript
{
  kind: "remote",
  name: string,              // Unique hook name
  endpoint: string,          // HTTP or WebSocket URL
  connection?: Connection,   // Authentication
  condition?: RunCondition,  // When to call
  config?: Record<unknown>   // Hook configuration
}
```

**Example:**
```json
{
  "kind": "remote",
  "name": "content-moderation",
  "endpoint": "https://hooks.example.com/moderate",
  "connection": {
    "kind": "key",
    "key": "Bearer hook_secret_abc123",
    "headerName": "Authorization"
  },
  "condition": {
    "kind": "content",
    "contentTypes": ["text"]
  },
  "config": {
    "strictMode": true,
    "categories": ["violence", "hate-speech", "harassment"]
  }
}
```

#### BlockHook - Simple Content Blocking

**When to use:**
- Simple policy enforcement
- Emergency stops
- Testing
- Static rules

**Structure:**
```typescript
{
  kind: "block",
  name: string,              // Unique hook name
  condition?: RunCondition,  // When to block
  message: string            // User-facing message
}
```

**Example:**
```json
{
  "kind": "block",
  "name": "production-environment-guard",
  "condition": {
    "kind": "expression",
    "expression": "environment != 'production' && tool.name.startsWith('prod_')"
  },
  "message": "Production tools cannot be used in non-production environments"
}
```

#### ModifyHook - Pattern-Based Content Transformation

**When to use:**
- PII redaction
- Content sanitization
- Credential removal
- Data masking

**Structure:**
```typescript
{
  kind: "modify",
  name: string,                  // Unique hook name
  condition?: RunCondition,      // When to modify
  predefinedPatterns?: string[], // ["email", "phone", "ssn"]
  regexPatterns?: string[],      // Custom regex patterns
  replacement?: string           // Default: "[REDACTED]"
}
```

**Example:**
```json
{
  "kind": "modify",
  "name": "comprehensive-pii-redactor",
  "condition": {
    "kind": "always"
  },
  "predefinedPatterns": ["email", "phone", "ssn", "credit_card"],
  "regexPatterns": [
    "\\b[A-Z]{2}\\d{6}\\b",
    "\\bAPI[_-]KEY[_-][A-Za-z0-9]{32}\\b"
  ],
  "replacement": "[REDACTED]"
}
```

#### TelemetryHook - Event Observation

**When to use:**
- Compliance logging
- Monitoring and metrics
- Analytics
- Debugging

**Structure:**
```typescript
{
  kind: "telemetry",
  name: string,              // Unique hook name
  condition?: RunCondition,  // When to log
  event: string,             // Event name
  properties?: Record<string> // Event properties
}
```

**Example:**
```json
{
  "kind": "telemetry",
  "name": "compliance-logger",
  "condition": {
    "kind": "always"
  },
  "event": "agent.interaction",
  "properties": {
    "compliance_framework": "SOX",
    "data_classification": "sensitive",
    "retention_period": "7-years"
  }
}
```

#### SendMessageHook - Response Regeneration

**When to use:**
- Quality control
- Response correction
- Additional context
- Feedback loops

**Structure:**
```typescript
{
  kind: "sendMessage",
  name: string,              // Unique hook name
  condition?: RunCondition,  // When to inject
  message: ChatMessage       // Message to inject
}
```

**Note**: Only available in `afterRun` lifecycle point.

**Example:**
```json
{
  "kind": "sendMessage",
  "name": "length-enforcer",
  "condition": {
    "kind": "expression",
    "expression": "len(message.content[0].text) < 100"
  },
  "message": {
    "role": "system",
    "content": [
      {
        "kind": "text",
        "text": "Your response is too brief. Please provide a more comprehensive answer with at least 100 characters, including examples and explanations."
      }
    ]
  }
}
```

### Step 2: Configuring Hooks on Agents

Hooks are configured when creating or updating agents:

**Python Example:**

```python
import requests

def create_agent_with_hooks(api_base_url, token, agent_config):
    """Create agent with configured hooks."""
    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()
    return response.json()

# Agent configuration with multiple hooks
agent_config = {
    "name": "customer-support-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are a helpful customer support agent.",
    "hooks": {
        # Input sanitization before run
        "beforeRun": [
            {
                "kind": "modify",
                "name": "input-pii-redactor",
                "predefinedPatterns": ["email", "phone"],
                "replacement": "[REDACTED]"
            },
            {
                "kind": "telemetry",
                "name": "run-start-logger",
                "event": "run.started",
                "properties": {
                    "agent": "customer-support",
                    "timestamp": "server-time"
                }
            }
        ],
        # Tool authorization before execution
        "beforeToolExecution": [
            {
                "kind": "remote",
                "name": "tool-approval-gateway",
                "endpoint": "https://hooks.example.com/approve-tool",
                "connection": {
                    "kind": "key",
                    "key": "Bearer hook_secret_xyz",
                    "headerName": "Authorization"
                },
                "condition": {
                    "kind": "expression",
                    "expression": "tool.name in ['delete_user', 'refund_payment']"
                }
            }
        ],
        # Result sanitization after tool execution
        "afterToolExecution": [
            {
                "kind": "modify",
                "name": "tool-result-sanitizer",
                "predefinedPatterns": ["email", "phone", "ssn"],
                "replacement": "[REDACTED]"
            }
        ],
        # Output quality control and logging
        "afterRun": [
            {
                "kind": "modify",
                "name": "output-pii-redactor",
                "predefinedPatterns": ["email", "phone", "ssn"],
                "replacement": "[REDACTED]"
            },
            {
                "kind": "sendMessage",
                "name": "quality-enforcer",
                "condition": {
                    "kind": "expression",
                    "expression": "len(message.content[0].text) < 50"
                },
                "message": {
                    "role": "system",
                    "content": [
                        {
                            "kind": "text",
                            "text": "Please provide a more detailed response."
                        }
                    ]
                }
            },
            {
                "kind": "telemetry",
                "name": "run-complete-logger",
                "event": "run.completed",
                "properties": {
                    "agent": "customer-support"
                }
            }
        ]
    }
}

# Create agent
agent = create_agent_with_hooks(
    "https://api.example.com",
    "YOUR_API_TOKEN",
    agent_config
)
print(f"Created agent: {agent['agentId']}")
```

**JavaScript Example:**

```javascript
async function createAgentWithHooks(apiBaseUrl, token, agentConfig) {
    const response = await fetch(`${apiBaseUrl}/agents`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(agentConfig)
    });

    if (!response.ok) {
        throw new Error(`Failed to create agent: ${response.statusText}`);
    }

    return await response.json();
}

// Agent configuration
const agentConfig = {
    name: "customer-support-agent",
    model: "claude-sonnet-4-5-20250929",
    instructions: "You are a helpful customer support agent.",
    hooks: {
        beforeRun: [
            {
                kind: "modify",
                name: "input-pii-redactor",
                predefinedPatterns: ["email", "phone"],
                replacement: "[REDACTED]"
            }
        ],
        afterRun: [
            {
                kind: "modify",
                name: "output-pii-redactor",
                predefinedPatterns: ["email", "phone", "ssn"],
                replacement: "[REDACTED]"
            }
        ]
    }
};

// Create agent
const agent = await createAgentWithHooks(
    "https://api.example.com",
    "YOUR_API_TOKEN",
    agentConfig
);
console.log(`Created agent: ${agent.agentId}`);
```

### Step 3: Implementing PII Redaction

PII redaction is one of the most common use cases. Here's a comprehensive implementation:

**Basic PII Redaction:**

```python
def create_pii_redaction_hook():
    """Create a basic PII redaction hook."""
    return {
        "kind": "modify",
        "name": "pii-redactor",
        "condition": {
            "kind": "always"
        },
        "predefinedPatterns": [
            "email",
            "phone",
            "ssn",
            "credit_card"
        ],
        "replacement": "[REDACTED]"
    }
```

**Predefined Patterns Available:**

| Pattern | Matches | Example |
|---------|---------|---------|
| `email` | Email addresses | `john@example.com` → `[REDACTED]` |
| `phone` | Phone numbers (US/International) | `555-123-4567` → `[REDACTED]` |
| `ssn` | Social Security Numbers | `123-45-6789` → `[REDACTED]` |
| `credit_card` | Credit card numbers | `4532-1234-5678-9010` → `[REDACTED]` |
| `ip_address` | IPv4/IPv6 addresses | `192.168.1.1` → `[REDACTED]` |
| `medical_record_number` | Medical record IDs | `MRN123456` → `[REDACTED]` |

**Advanced PII Redaction with Custom Patterns:**

```python
def create_advanced_pii_redaction_hook():
    """Create advanced PII redaction with custom patterns."""
    return {
        "kind": "modify",
        "name": "advanced-pii-redactor",
        "condition": {
            "kind": "content",
            "contentTypes": ["text"]
        },
        "predefinedPatterns": [
            "email",
            "phone",
            "ssn",
            "credit_card"
        ],
        "regexPatterns": [
            # Employee IDs (format: EMP-123456)
            r"EMP-\d{6}",
            # API Keys (format: api_key_32chars)
            r"api_key_[A-Za-z0-9]{32}",
            # Database connection strings
            r"(?i)(mongodb|postgres|mysql):\/\/[^\s]+",
            # AWS Access Keys
            r"AKIA[0-9A-Z]{16}",
            # Customer IDs (format: CUST-XXXX-XXXX)
            r"CUST-[A-Z0-9]{4}-[A-Z0-9]{4}",
            # Passport numbers (simplified)
            r"\b[A-Z]{1,2}\d{6,9}\b"
        ],
        "replacement": "[REDACTED]"
    }
```

**Domain-Specific PII Redaction:**

```python
def create_healthcare_pii_redaction():
    """Healthcare-specific PII redaction (HIPAA compliance)."""
    return {
        "kind": "modify",
        "name": "hipaa-pii-redactor",
        "predefinedPatterns": [
            "email",
            "phone",
            "ssn",
            "medical_record_number"
        ],
        "regexPatterns": [
            # Health Plan Beneficiary Numbers
            r"\b\d{3}-\d{2}-\d{4}-[A-Z]\d\b",
            # Device IDs
            r"\bDEV-\d{8}\b",
            # Provider IDs
            r"\bNPI-\d{10}\b"
        ],
        "replacement": "[PHI REDACTED]"
    }

def create_financial_pii_redaction():
    """Financial services PII redaction (PCI DSS compliance)."""
    return {
        "kind": "modify",
        "name": "pci-pii-redactor",
        "predefinedPatterns": [
            "credit_card",
            "ssn"
        ],
        "regexPatterns": [
            # Bank account numbers
            r"\b\d{8,17}\b",
            # Routing numbers
            r"\b\d{9}\b",
            # CVV codes (3-4 digits)
            r"\b\d{3,4}\b"
        ],
        "replacement": "[FINANCIAL DATA REDACTED]"
    }
```

**Multi-Stage PII Redaction:**

```python
# Configure PII redaction at multiple lifecycle points
agent_config = {
    "name": "secure-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are a secure assistant.",
    "hooks": {
        # Redact PII from user input
        "beforeRun": [
            create_pii_redaction_hook()
        ],
        # Redact PII from tool results
        "afterToolExecution": [
            create_pii_redaction_hook()
        ],
        # Redact PII from agent output
        "afterRun": [
            create_pii_redaction_hook()
        ]
    }
}
```

### Step 4: Implementing Content Blocking

Content blocking prevents inappropriate or prohibited content from being processed or delivered.

**Simple Keyword Blocking:**

```python
def create_keyword_blocker():
    """Block content containing prohibited keywords."""
    return {
        "kind": "block",
        "name": "keyword-blocker",
        "condition": {
            "kind": "expression",
            "expression": """
                any([
                    'prohibited_word_1' in message.content[0].text.lower(),
                    'prohibited_word_2' in message.content[0].text.lower(),
                    'prohibited_word_3' in message.content[0].text.lower()
                ])
            """
        },
        "message": "Content contains prohibited keywords and cannot be processed"
    }
```

**Tool-Based Blocking:**

```python
def create_dangerous_tool_blocker():
    """Block dangerous tool calls."""
    return {
        "kind": "block",
        "name": "dangerous-tool-blocker",
        "condition": {
            "kind": "expression",
            "expression": """
                tool.name in [
                    'delete_database',
                    'drop_table',
                    'execute_system_command',
                    'delete_all_users'
                ]
            """
        },
        "message": "This tool is not permitted due to security policy"
    }
```

**Conditional Blocking Based on User Tier:**

```python
def create_tier_based_blocker():
    """Block expensive operations for free-tier users."""
    return {
        "kind": "block",
        "name": "tier-blocker",
        "condition": {
            "kind": "expression",
            "expression": """
                user.tier == 'free' && (
                    tool.name in ['generate_video', 'train_model'] ||
                    tool.estimated_cost > 1.00
                )
            """
        },
        "message": "This operation requires a premium subscription. Please upgrade to continue."
    }
```

**Environment-Based Blocking:**

```python
def create_environment_blocker():
    """Block production operations in non-production environments."""
    return {
        "kind": "block",
        "name": "environment-guard",
        "condition": {
            "kind": "expression",
            "expression": """
                environment != 'production' &&
                tool.name.startsWith('prod_')
            """
        },
        "message": "Production tools cannot be executed in non-production environments"
    }
```

**Time-Based Blocking:**

```python
def create_time_based_blocker():
    """Block operations outside business hours."""
    return {
        "kind": "block",
        "name": "business-hours-guard",
        "condition": {
            "kind": "expression",
            "expression": """
                (now().hour < 9 || now().hour >= 17) &&
                tool.category == 'financial'
            """
        },
        "message": "Financial operations are only permitted during business hours (9 AM - 5 PM)"
    }
```

### Step 5: Building Remote Hooks

Remote hooks delegate decision-making to external services. This is the most flexible hook type.

**Remote Hook Service Architecture:**

```text
Agent Runtime                Remote Hook Service
      |                              |
      | Event: content.created       |
      |----------------------------->|
      |                              |
      |                         Evaluate:
      |                         - Content filter
      |                         - Business rules
      |                         - External APIs
      |                              |
      | Response: allow/block/modify |
      |<-----------------------------|
      |                              |
   Continue/Block/Modify             |
```

**HTTP-Based Remote Hook Service (Python/Flask):**

```python
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/content-filter', methods=['POST'])
def content_filter():
    """
    Remote hook endpoint for content filtering.

    Request body contains:
    - eventSeq: Event sequence number
    - event: Event type (e.g., "content.created")
    - content: Content data
    - context: Run context
    """
    data = request.json

    # Extract event information
    event_seq = data['eventSeq']
    event_type = data['event']
    content = data.get('content', {})

    # Content filtering logic
    if content.get('kind') == 'text':
        text = content.get('text', '')

        # Check for prohibited content
        prohibited_patterns = [
            r'offensive_word_1',
            r'offensive_word_2',
            r'prohibited_pattern'
        ]

        for pattern in prohibited_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return jsonify({
                    "kind": "block",
                    "eventSeqs": [event_seq],
                    "message": "Content violates community guidelines"
                })

        # Check for PII that needs redaction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            # Redact emails
            redacted_text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
            return jsonify({
                "kind": "modify",
                "eventSeqs": [event_seq],
                "contentIndex": 0,
                "modifiedContent": {
                    "kind": "text",
                    "text": redacted_text
                }
            })

    # Allow content by default
    return jsonify({
        "kind": "allow",
        "eventSeqs": [event_seq]
    })

@app.route('/approve-tool', methods=['POST'])
def approve_tool():
    """
    Remote hook endpoint for tool approval workflow.

    This would integrate with an approval system to pause
    until a human approves the operation.
    """
    data = request.json

    event_seq = data['eventSeq']
    tool_call = data.get('content', {})
    tool_name = tool_call.get('name', '')
    tool_args = tool_call.get('arguments', {})

    # Check if tool requires approval
    requires_approval = tool_name in [
        'delete_user',
        'refund_payment',
        'execute_sql'
    ]

    if requires_approval:
        # In a real implementation, this would:
        # 1. Create approval request in database
        # 2. Send notification to approver
        # 3. Wait for approval (via webhook or polling)
        # 4. Return response based on approval decision

        # For this example, we'll simulate approval check
        approval_status = check_approval_status(tool_name, tool_args)

        if approval_status == 'approved':
            return jsonify({
                "kind": "allow",
                "eventSeqs": [event_seq]
            })
        elif approval_status == 'rejected':
            return jsonify({
                "kind": "block",
                "eventSeqs": [event_seq],
                "message": "Operation rejected by approver"
            })
        else:  # pending
            return jsonify({
                "kind": "block",
                "eventSeqs": [event_seq],
                "message": "Operation pending approval"
            }), 202  # Accepted but not complete

    # Allow tool by default
    return jsonify({
        "kind": "allow",
        "eventSeqs": [event_seq]
    })

def check_approval_status(tool_name, tool_args):
    """
    Check approval status from approval system.
    In production, this would query a database or approval service.
    """
    # Placeholder implementation
    return "approved"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**JavaScript/Express Remote Hook Service:**

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// Content filtering endpoint
app.post('/content-filter', async (req, res) => {
    const { eventSeq, event, content, context } = req.body;

    // Content filtering logic
    if (content?.kind === 'text') {
        const text = content.text || '';

        // Check for prohibited content
        const prohibitedPatterns = [
            /offensive_word_1/i,
            /offensive_word_2/i,
            /prohibited_pattern/i
        ];

        for (const pattern of prohibitedPatterns) {
            if (pattern.test(text)) {
                return res.json({
                    kind: 'block',
                    eventSeqs: [eventSeq],
                    message: 'Content violates community guidelines'
                });
            }
        }

        // Check for PII
        const emailPattern = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
        if (emailPattern.test(text)) {
            const redactedText = text.replace(emailPattern, '[EMAIL REDACTED]');
            return res.json({
                kind: 'modify',
                eventSeqs: [eventSeq],
                contentIndex: 0,
                modifiedContent: {
                    kind: 'text',
                    text: redactedText
                }
            });
        }
    }

    // Allow by default
    res.json({
        kind: 'allow',
        eventSeqs: [eventSeq]
    });
});

// Tool approval endpoint
app.post('/approve-tool', async (req, res) => {
    const { eventSeq, content } = req.body;

    const toolName = content?.name || '';
    const toolArgs = content?.arguments || {};

    // Check if tool requires approval
    const requiresApproval = [
        'delete_user',
        'refund_payment',
        'execute_sql'
    ].includes(toolName);

    if (requiresApproval) {
        // Check approval status
        const approvalStatus = await checkApprovalStatus(toolName, toolArgs);

        if (approvalStatus === 'approved') {
            return res.json({
                kind: 'allow',
                eventSeqs: [eventSeq]
            });
        } else if (approvalStatus === 'rejected') {
            return res.json({
                kind: 'block',
                eventSeqs: [eventSeq],
                message: 'Operation rejected by approver'
            });
        } else {
            return res.status(202).json({
                kind: 'block',
                eventSeqs: [eventSeq],
                message: 'Operation pending approval'
            });
        }
    }

    // Allow by default
    res.json({
        kind: 'allow',
        eventSeqs: [eventSeq]
    });
});

async function checkApprovalStatus(toolName, toolArgs) {
    // In production, query approval system
    return 'approved';
}

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Remote hook service running on port ${PORT}`);
});
```

**WebSocket-Based Remote Hook Service (Python):**

WebSocket-based hooks provide lower latency and support bidirectional communication:

```python
import asyncio
import websockets
import json

async def handle_hook_connection(websocket, path):
    """
    Handle WebSocket connection from Agent Runtime.

    Protocol:
    1. Receive handshake with hook configuration
    2. Process events as they arrive
    3. Send responses for each event
    """
    try:
        # Receive handshake
        handshake = await websocket.recv()
        handshake_data = json.loads(handshake)

        print(f"Hook connected: {handshake_data.get('hookName')}")
        print(f"Config: {handshake_data.get('config')}")

        # Send handshake acknowledgment
        await websocket.send(json.dumps({
            "status": "ready"
        }))

        # Process events
        async for message in websocket:
            event_data = json.loads(message)

            # Process event and generate response
            response = await process_event(event_data)

            # Send response
            await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")

async def process_event(event_data):
    """Process event and return appropriate response."""
    event_seq = event_data.get('eventSeq')
    event_type = event_data.get('event')
    content = event_data.get('content', {})

    # Content filtering
    if content.get('kind') == 'text':
        text = content.get('text', '')

        # Check for violations
        if 'prohibited' in text.lower():
            return {
                "kind": "block",
                "eventSeqs": [event_seq],
                "message": "Content violates policy"
            }

        # Check for PII
        if '@' in text:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            redacted_text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
            return {
                "kind": "modify",
                "eventSeqs": [event_seq],
                "contentIndex": 0,
                "modifiedContent": {
                    "kind": "text",
                    "text": redacted_text
                }
            }

    # Allow by default
    return {
        "kind": "allow",
        "eventSeqs": [event_seq]
    }

async def main():
    """Start WebSocket server."""
    async with websockets.serve(
        handle_hook_connection,
        "0.0.0.0",
        8765
    ):
        print("WebSocket hook service running on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

**Configuring Remote Hook with WebSocket:**

```json
{
  "kind": "remote",
  "name": "websocket-content-filter",
  "endpoint": "wss://hooks.example.com/filter",
  "connection": {
    "kind": "key",
    "key": "Bearer ws_secret_xyz",
    "headerName": "Authorization"
  },
  "condition": {
    "kind": "content",
    "contentTypes": ["text"]
  },
  "config": {
    "strictMode": true,
    "realtime": true
  }
}
```

### Step 6: Implementing Telemetry and Monitoring

Telemetry hooks enable comprehensive monitoring and auditing without affecting run execution.

**Basic Telemetry:**

```python
def create_basic_telemetry_hook():
    """Create basic telemetry hook for all events."""
    return {
        "kind": "telemetry",
        "name": "basic-telemetry",
        "condition": {
            "kind": "always"
        },
        "event": "agent.event",
        "properties": {
            "source": "agent-runtime",
            "environment": "production"
        }
    }
```

**Compliance Audit Logging:**

```python
def create_compliance_audit_hook():
    """Create comprehensive compliance audit logging."""
    return {
        "kind": "telemetry",
        "name": "compliance-audit",
        "condition": {
            "kind": "always"
        },
        "event": "compliance.audit",
        "properties": {
            "compliance_framework": "SOX",
            "audit_category": "financial_transaction",
            "retention_period": "7_years",
            "data_classification": "confidential",
            "requires_encryption": True
        }
    }
```

**Performance Monitoring:**

```python
def create_performance_telemetry():
    """Monitor agent performance metrics."""
    return {
        "kind": "telemetry",
        "name": "performance-monitor",
        "condition": {
            "kind": "always"
        },
        "event": "agent.performance",
        "properties": {
            "metric_type": "latency",
            "track_tokens": True,
            "track_cost": True
        }
    }
```

**Security Audit Logging:**

```python
def create_security_audit_hook():
    """Log security-relevant events."""
    return {
        "kind": "telemetry",
        "name": "security-audit",
        "condition": {
            "kind": "expression",
            "expression": """
                tool.category == 'security' ||
                tool.name.startsWith('admin_') ||
                user.role == 'administrator'
            """
        },
        "event": "security.audit",
        "properties": {
            "audit_type": "privileged_access",
            "requires_review": True,
            "alert_security_team": True
        }
    }
```

**Multi-Stage Telemetry Configuration:**

```python
agent_config = {
    "name": "monitored-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are a monitored assistant.",
    "hooks": {
        "beforeRun": [
            {
                "kind": "telemetry",
                "name": "run-start",
                "event": "run.started",
                "properties": {
                    "stage": "beforeRun"
                }
            }
        ],
        "beforeToolExecution": [
            {
                "kind": "telemetry",
                "name": "tool-start",
                "event": "tool.started",
                "properties": {
                    "stage": "beforeToolExecution"
                }
            }
        ],
        "afterToolExecution": [
            {
                "kind": "telemetry",
                "name": "tool-complete",
                "event": "tool.completed",
                "properties": {
                    "stage": "afterToolExecution",
                    "measure_duration": True
                }
            }
        ],
        "afterRun": [
            {
                "kind": "telemetry",
                "name": "run-complete",
                "event": "run.completed",
                "properties": {
                    "stage": "afterRun",
                    "measure_total_duration": True
                }
            }
        ]
    }
}
```

### Step 7: Implementing Approval Workflows

Approval workflows require human authorization before proceeding with sensitive operations.

**Basic Approval Workflow:**

```python
import requests
import time

class ApprovalWorkflow:
    """Manage approval workflows for sensitive operations."""

    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        self.token = token
        self.approval_service_url = "https://approvals.example.com"

    def create_approval_hook(self):
        """Create hook that requires approval for sensitive tools."""
        return {
            "kind": "remote",
            "name": "approval-gateway",
            "endpoint": f"{self.approval_service_url}/approve",
            "connection": {
                "kind": "key",
                "key": f"Bearer {self.token}",
                "headerName": "Authorization"
            },
            "condition": {
                "kind": "expression",
                "expression": """
                    tool.name in [
                        'delete_user',
                        'refund_payment',
                        'execute_sql',
                        'send_email_campaign'
                    ]
                """
            }
        }

    def request_approval(self, tool_name, tool_args, approver_id):
        """Request approval for tool execution."""
        response = requests.post(
            f"{self.approval_service_url}/requests",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={
                "toolName": tool_name,
                "toolArguments": tool_args,
                "approverId": approver_id,
                "requestedAt": time.time()
            }
        )
        response.raise_for_status()
        return response.json()["requestId"]

    def check_approval_status(self, request_id):
        """Check if approval has been granted."""
        response = requests.get(
            f"{self.approval_service_url}/requests/{request_id}",
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        response.raise_for_status()
        return response.json()["status"]

    def wait_for_approval(self, request_id, timeout=300):
        """Wait for approval with timeout."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.check_approval_status(request_id)

            if status == "approved":
                return True
            elif status == "rejected":
                return False

            time.sleep(5)  # Poll every 5 seconds

        raise TimeoutError("Approval request timed out")

# Usage
workflow = ApprovalWorkflow("https://api.example.com", "YOUR_TOKEN")

agent_config = {
    "name": "approval-required-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are an assistant with approval workflows.",
    "hooks": {
        "beforeToolExecution": [
            workflow.create_approval_hook()
        ]
    }
}
```

**Multi-Level Approval Workflow:**

```python
class MultiLevelApprovalWorkflow:
    """Implement sequential multi-level approvals."""

    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        self.token = token

    def create_tiered_approval_hooks(self):
        """
        Create approval hooks for different tiers:
        - Tier 1: Manager approval for < $1000
        - Tier 2: Director approval for $1000-$10000
        - Tier 3: VP approval for > $10000
        """
        return [
            # Tier 1: Manager approval
            {
                "kind": "remote",
                "name": "manager-approval",
                "endpoint": "https://approvals.example.com/manager",
                "condition": {
                    "kind": "expression",
                    "expression": """
                        tool.name == 'process_refund' &&
                        tool.arguments.amount < 1000
                    """
                }
            },
            # Tier 2: Director approval
            {
                "kind": "remote",
                "name": "director-approval",
                "endpoint": "https://approvals.example.com/director",
                "condition": {
                    "kind": "expression",
                    "expression": """
                        tool.name == 'process_refund' &&
                        tool.arguments.amount >= 1000 &&
                        tool.arguments.amount < 10000
                    """
                }
            },
            # Tier 3: VP approval
            {
                "kind": "remote",
                "name": "vp-approval",
                "endpoint": "https://approvals.example.com/vp",
                "condition": {
                    "kind": "expression",
                    "expression": """
                        tool.name == 'process_refund' &&
                        tool.arguments.amount >= 10000
                    """
                }
            }
        ]

# Usage
workflow = MultiLevelApprovalWorkflow("https://api.example.com", "YOUR_TOKEN")

agent_config = {
    "name": "financial-agent",
    "model": "claude-sonnet-4-5-20250929",
    "instructions": "You are a financial operations assistant.",
    "hooks": {
        "beforeToolExecution": workflow.create_tiered_approval_hooks()
    }
}
```

### Step 8: Handling Streaming Content

When working with streaming responses, hooks need to handle partial content and make decisions based on complete context.

**Streaming Content Handling:**

```python
class StreamingHookHandler:
    """Handle hooks for streaming content."""

    def __init__(self):
        self.content_buffer = {}

    async def handle_streaming_event(self, event):
        """
        Handle streaming events and make decisions.

        Events for streaming content:
        - content.created: Initial content piece
        - content.updated: Partial content updates (streaming)
        - content.completed: Final content piece
        """
        event_seq = event['eventSeq']
        event_type = event['event']
        content = event.get('content', {})

        if event_type == 'content.created':
            # Initialize buffer for this content piece
            content_id = content.get('contentId')
            self.content_buffer[content_id] = ""

        elif event_type == 'content.updated':
            # Accumulate streaming chunks
            content_id = content.get('contentId')
            delta = content.get('delta', '')
            self.content_buffer[content_id] += delta

            # Can optionally check partial content
            partial_text = self.content_buffer[content_id]

            # Example: Block if prohibited content detected early
            if 'prohibited_keyword' in partial_text.lower():
                return {
                    "kind": "block",
                    "eventSeqs": [event_seq],
                    "message": "Content blocked due to policy violation"
                }

        elif event_type == 'content.completed':
            # Make final decision on complete content
            content_id = content.get('contentId')
            complete_text = self.content_buffer[content_id]

            # Perform final content filtering
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            if re.search(email_pattern, complete_text):
                # Redact emails from complete content
                redacted_text = re.sub(email_pattern, '[EMAIL REDACTED]', complete_text)

                return {
                    "kind": "modify",
                    "eventSeqs": [event_seq],
                    "contentIndex": 0,
                    "modifiedContent": {
                        "kind": "text",
                        "text": redacted_text
                    }
                }

            # Clean up buffer
            del self.content_buffer[content_id]

        # Allow by default
        return {
            "kind": "allow",
            "eventSeqs": [event_seq]
        }
```

**Important Notes for Streaming:**

1. **Buffer Management**: Accumulate streaming chunks to make informed decisions
2. **Early Termination**: Can block content before streaming completes if violation detected
3. **Complete Context**: Wait for `content.completed` event for final modifications
4. **Event Sequences**: Modifications must reference all relevant eventSeqs

## Examples

### Example 1: Healthcare Chatbot with HIPAA Compliance

A healthcare chatbot that must redact all Protected Health Information (PHI):

```python
import requests

def create_hipaa_compliant_agent(api_base_url, token):
    """Create HIPAA-compliant healthcare chatbot."""

    agent_config = {
        "name": "healthcare-assistant",
        "model": "claude-sonnet-4-5-20250929",
        "instructions": """
            You are a healthcare assistant helping patients with general
            health information. You must protect patient privacy at all times.
        """,
        "hooks": {
            # Redact PHI from user input
            "beforeRun": [
                {
                    "kind": "modify",
                    "name": "input-phi-redactor",
                    "predefinedPatterns": [
                        "email",
                        "phone",
                        "ssn",
                        "medical_record_number"
                    ],
                    "regexPatterns": [
                        # Health Plan Beneficiary Numbers
                        r"\b\d{3}-\d{2}-\d{4}-[A-Z]\d\b",
                        # Provider NPI numbers
                        r"\bNPI-\d{10}\b",
                        # Dates of birth
                        r"\b\d{1,2}/\d{1,2}/\d{4}\b"
                    ],
                    "replacement": "[PHI REDACTED]"
                },
                {
                    "kind": "telemetry",
                    "name": "hipaa-audit-input",
                    "event": "hipaa.user_input",
                    "properties": {
                        "compliance": "HIPAA",
                        "audit_level": "required"
                    }
                }
            ],
            # Block tools that could expose PHI
            "beforeToolExecution": [
                {
                    "kind": "block",
                    "name": "phi-tool-blocker",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.name in [
                                'query_patient_records',
                                'access_medical_history',
                                'view_lab_results'
                            ] && user.role != 'healthcare_provider'
                        """
                    },
                    "message": "Access to patient records requires healthcare provider credentials"
                }
            ],
            # Redact PHI from agent output
            "afterRun": [
                {
                    "kind": "modify",
                    "name": "output-phi-redactor",
                    "predefinedPatterns": [
                        "email",
                        "phone",
                        "ssn",
                        "medical_record_number"
                    ],
                    "regexPatterns": [
                        r"\b\d{3}-\d{2}-\d{4}-[A-Z]\d\b",
                        r"\bNPI-\d{10}\b",
                        r"\b\d{1,2}/\d{1,2}/\d{4}\b"
                    ],
                    "replacement": "[PHI REDACTED]"
                },
                {
                    "kind": "telemetry",
                    "name": "hipaa-audit-output",
                    "event": "hipaa.agent_response",
                    "properties": {
                        "compliance": "HIPAA",
                        "audit_level": "required",
                        "retention": "6_years"
                    }
                }
            ]
        }
    }

    # Create agent
    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()

    return response.json()

# Usage
agent = create_hipaa_compliant_agent(
    "https://api.example.com",
    "YOUR_API_TOKEN"
)

print(f"Created HIPAA-compliant agent: {agent['agentId']}")

# Test with patient query
run_response = requests.post(
    f"https://api.example.com/agents/{agent['agentId']}/runs",
    headers={
        "Authorization": "Bearer YOUR_API_TOKEN",
        "Content-Type": "application/json"
    },
    json={
        "threadId": "thread_patient_123",
        "message": {
            "role": "user",
            "content": [
                {
                    "kind": "text",
                    "text": "My name is John Doe, SSN 123-45-6789, and my email is john@example.com. Can you help me understand my lab results?"
                }
            ]
        }
    }
)

# Response will have all PHI redacted
print(run_response.json())
```

### Example 2: Financial Services Agent with Multi-Level Approvals

A financial services agent that requires different approval levels based on transaction amounts:

```python
import requests

def create_financial_agent_with_approvals(api_base_url, token):
    """Create financial agent with tiered approval workflows."""

    agent_config = {
        "name": "financial-operations-agent",
        "model": "claude-sonnet-4-5-20250929",
        "instructions": """
            You are a financial operations assistant. You can help process
            refunds, payments, and account adjustments. All operations
            require appropriate approval levels.
        """,
        "tools": [
            {
                "kind": "function",
                "name": "process_refund",
                "description": "Process a refund for a customer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerId": {"type": "string"},
                        "amount": {"type": "number"},
                        "reason": {"type": "string"}
                    },
                    "required": ["customerId", "amount", "reason"]
                }
            },
            {
                "kind": "function",
                "name": "adjust_account_balance",
                "description": "Adjust customer account balance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "accountId": {"type": "string"},
                        "adjustment": {"type": "number"},
                        "notes": {"type": "string"}
                    },
                    "required": ["accountId", "adjustment", "notes"]
                }
            }
        ],
        "hooks": {
            # PII redaction for all input/output
            "beforeRun": [
                {
                    "kind": "modify",
                    "name": "financial-pii-redactor-input",
                    "predefinedPatterns": [
                        "credit_card",
                        "ssn",
                        "email",
                        "phone"
                    ],
                    "regexPatterns": [
                        # Bank account numbers
                        r"\b\d{8,17}\b",
                        # Routing numbers
                        r"\b\d{9}\b"
                    ],
                    "replacement": "[FINANCIAL DATA REDACTED]"
                }
            ],
            # Multi-tier approval system
            "beforeToolExecution": [
                # Small transactions: Manager approval
                {
                    "kind": "remote",
                    "name": "manager-approval",
                    "endpoint": "https://approvals.example.com/financial/manager",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.name == 'process_refund' &&
                            tool.arguments.amount > 0 &&
                            tool.arguments.amount <= 1000
                        """
                    },
                    "config": {
                        "approvalLevel": "manager",
                        "maxAmount": 1000
                    }
                },
                # Medium transactions: Director approval
                {
                    "kind": "remote",
                    "name": "director-approval",
                    "endpoint": "https://approvals.example.com/financial/director",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.name == 'process_refund' &&
                            tool.arguments.amount > 1000 &&
                            tool.arguments.amount <= 10000
                        """
                    },
                    "config": {
                        "approvalLevel": "director",
                        "maxAmount": 10000
                    }
                },
                # Large transactions: VP approval
                {
                    "kind": "remote",
                    "name": "vp-approval",
                    "endpoint": "https://approvals.example.com/financial/vp",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.name == 'process_refund' &&
                            tool.arguments.amount > 10000
                        """
                    },
                    "config": {
                        "approvalLevel": "vp",
                        "requiresSecondary": True
                    }
                },
                # Audit all financial operations
                {
                    "kind": "telemetry",
                    "name": "financial-audit",
                    "event": "financial.operation.requested",
                    "properties": {
                        "compliance": "SOX",
                        "audit_category": "financial_transaction",
                        "requires_retention": True
                    }
                }
            ],
            # Log operation results
            "afterToolExecution": [
                {
                    "kind": "telemetry",
                    "name": "operation-complete-audit",
                    "event": "financial.operation.completed",
                    "properties": {
                        "compliance": "SOX",
                        "audit_category": "financial_transaction"
                    }
                }
            ],
            # Redact PII from output
            "afterRun": [
                {
                    "kind": "modify",
                    "name": "financial-pii-redactor-output",
                    "predefinedPatterns": [
                        "credit_card",
                        "ssn",
                        "email",
                        "phone"
                    ],
                    "regexPatterns": [
                        r"\b\d{8,17}\b",
                        r"\b\d{9}\b"
                    ],
                    "replacement": "[FINANCIAL DATA REDACTED]"
                }
            ]
        }
    }

    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()

    return response.json()

# Usage
agent = create_financial_agent_with_approvals(
    "https://api.example.com",
    "YOUR_API_TOKEN"
)

print(f"Created financial agent with approvals: {agent['agentId']}")
```

### Example 3: Content Moderation for Public Chatbot

A public-facing chatbot with comprehensive content moderation:

```python
import requests

def create_moderated_public_chatbot(api_base_url, token):
    """Create public chatbot with content moderation."""

    agent_config = {
        "name": "public-chatbot",
        "model": "claude-sonnet-4-5-20250929",
        "instructions": """
            You are a helpful public-facing chatbot. You should be friendly,
            professional, and appropriate for all ages.
        """,
        "hooks": {
            # Input moderation
            "beforeRun": [
                # Remote content filter for user input
                {
                    "kind": "remote",
                    "name": "input-content-filter",
                    "endpoint": "https://moderation.example.com/filter",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "content",
                        "contentTypes": ["text"]
                    },
                    "config": {
                        "categories": [
                            "violence",
                            "hate-speech",
                            "harassment",
                            "sexual-content",
                            "self-harm"
                        ],
                        "threshold": "medium"
                    }
                },
                # Log all user inputs
                {
                    "kind": "telemetry",
                    "name": "input-logger",
                    "event": "user.input",
                    "properties": {
                        "source": "public-chatbot",
                        "moderation_enabled": True
                    }
                }
            ],
            # Output moderation
            "afterRun": [
                # Remote content filter for agent output
                {
                    "kind": "remote",
                    "name": "output-content-filter",
                    "endpoint": "https://moderation.example.com/filter",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "content",
                        "contentTypes": ["text"]
                    },
                    "config": {
                        "categories": [
                            "violence",
                            "hate-speech",
                            "harassment",
                            "sexual-content",
                            "self-harm"
                        ],
                        "threshold": "low"  # Stricter for output
                    }
                },
                # Ensure responses meet quality standards
                {
                    "kind": "sendMessage",
                    "name": "quality-enforcer",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            len(message.content[0].text) < 50
                        """
                    },
                    "message": {
                        "role": "system",
                        "content": [
                            {
                                "kind": "text",
                                "text": "Your response is too brief. Please provide a more helpful and detailed response."
                            }
                        ]
                    }
                },
                # Block responses that might be harmful
                {
                    "kind": "block",
                    "name": "safety-blocker",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            any([
                                'disclaimer: i am not a' in message.content[0].text.lower(),
                                'i cannot provide' in message.content[0].text.lower(),
                                'harmful' in message.content[0].text.lower()
                            ])
                        """
                    },
                    "message": "I apologize, but I cannot provide that information."
                },
                # Log all outputs
                {
                    "kind": "telemetry",
                    "name": "output-logger",
                    "event": "agent.output",
                    "properties": {
                        "source": "public-chatbot",
                        "moderation_enabled": True
                    }
                }
            ]
        }
    }

    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()

    return response.json()

# Usage
agent = create_moderated_public_chatbot(
    "https://api.example.com",
    "YOUR_API_TOKEN"
)

print(f"Created moderated public chatbot: {agent['agentId']}")
```

### Example 4: Enterprise Agent with Comprehensive Governance

An enterprise agent with complete governance controls:

```python
import requests

def create_enterprise_governed_agent(api_base_url, token):
    """Create enterprise agent with comprehensive governance."""

    agent_config = {
        "name": "enterprise-agent",
        "model": "claude-sonnet-4-5-20250929",
        "instructions": """
            You are an enterprise AI assistant with strict governance controls.
            All operations are logged, monitored, and subject to approval workflows.
        """,
        "hooks": {
            "beforeRun": [
                # Environment validation
                {
                    "kind": "block",
                    "name": "environment-validator",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            environment not in ['production', 'staging']
                        """
                    },
                    "message": "Agent can only run in authorized environments"
                },
                # Authentication check
                {
                    "kind": "remote",
                    "name": "authentication-validator",
                    "endpoint": "https://auth.example.com/validate",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    }
                },
                # Input sanitization
                {
                    "kind": "modify",
                    "name": "input-sanitizer",
                    "predefinedPatterns": ["email", "phone", "ssn", "credit_card"],
                    "regexPatterns": [
                        r"(?i)(password|api[_-]?key|secret|token)[\s:=]+[^\s]+",
                        r"(?i)(mongodb|postgres|mysql):\/\/[^\s]+"
                    ],
                    "replacement": "[SENSITIVE DATA REDACTED]"
                },
                # Start audit trail
                {
                    "kind": "telemetry",
                    "name": "audit-run-start",
                    "event": "enterprise.run.started",
                    "properties": {
                        "governance": "enabled",
                        "compliance": ["SOX", "GDPR", "SOC2"],
                        "retention": "7_years"
                    }
                }
            ],
            "beforeToolExecution": [
                # Tool authorization
                {
                    "kind": "remote",
                    "name": "tool-authorization",
                    "endpoint": "https://authz.example.com/authorize-tool",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    }
                },
                # Block dangerous operations
                {
                    "kind": "block",
                    "name": "dangerous-operation-blocker",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.category in ['destructive', 'admin'] &&
                            user.role not in ['admin', 'super_admin']
                        """
                    },
                    "message": "Insufficient permissions for this operation"
                },
                # Cost control
                {
                    "kind": "remote",
                    "name": "cost-controller",
                    "endpoint": "https://billing.example.com/check-budget",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "expression",
                        "expression": "tool.estimated_cost > 0"
                    }
                },
                # Approval workflow
                {
                    "kind": "remote",
                    "name": "approval-workflow",
                    "endpoint": "https://approvals.example.com/approve",
                    "connection": {
                        "kind": "key",
                        "key": f"Bearer {token}",
                        "headerName": "Authorization"
                    },
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.requires_approval == true ||
                            tool.estimated_cost > 10.00
                        """
                    }
                },
                # Audit tool execution
                {
                    "kind": "telemetry",
                    "name": "audit-tool-start",
                    "event": "enterprise.tool.started",
                    "properties": {
                        "governance": "enabled",
                        "track_duration": True,
                        "track_cost": True
                    }
                }
            ],
            "afterToolExecution": [
                # Result sanitization
                {
                    "kind": "modify",
                    "name": "result-sanitizer",
                    "predefinedPatterns": ["email", "phone", "ssn", "credit_card"],
                    "regexPatterns": [
                        r"(?i)(password|api[_-]?key|secret|token)[\s:=]+[^\s]+",
                        r"(?i)(mongodb|postgres|mysql):\/\/[^\s]+"
                    ],
                    "replacement": "[SENSITIVE DATA REDACTED]"
                },
                # Audit tool completion
                {
                    "kind": "telemetry",
                    "name": "audit-tool-complete",
                    "event": "enterprise.tool.completed",
                    "properties": {
                        "governance": "enabled"
                    }
                }
            ],
            "afterRun": [
                # Output sanitization
                {
                    "kind": "modify",
                    "name": "output-sanitizer",
                    "predefinedPatterns": ["email", "phone", "ssn", "credit_card"],
                    "regexPatterns": [
                        r"(?i)(password|api[_-]?key|secret|token)[\s:=]+[^\s]+",
                        r"(?i)(mongodb|postgres|mysql):\/\/[^\s]+"
                    ],
                    "replacement": "[SENSITIVE DATA REDACTED]"
                },
                # Quality validation
                {
                    "kind": "sendMessage",
                    "name": "quality-validator",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            len(message.content[0].text) < 100 ||
                            'error' in message.content[0].text.lower()
                        """
                    },
                    "message": {
                        "role": "system",
                        "content": [
                            {
                                "kind": "text",
                                "text": "Please provide a more comprehensive and error-free response."
                            }
                        ]
                    }
                },
                # Final audit
                {
                    "kind": "telemetry",
                    "name": "audit-run-complete",
                    "event": "enterprise.run.completed",
                    "properties": {
                        "governance": "enabled",
                        "compliance": ["SOX", "GDPR", "SOC2"]
                    }
                }
            ]
        }
    }

    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()

    return response.json()

# Usage
agent = create_enterprise_governed_agent(
    "https://api.example.com",
    "YOUR_API_TOKEN"
)

print(f"Created enterprise governed agent: {agent['agentId']}")
```

### Example 5: Development vs Production Hooks

Different hook configurations for different environments:

```python
import requests

def create_environment_specific_hooks(environment):
    """Create hooks appropriate for the environment."""

    if environment == "development":
        return {
            "beforeRun": [
                # Development: Log everything
                {
                    "kind": "telemetry",
                    "name": "dev-logger",
                    "event": "dev.run.started",
                    "properties": {
                        "environment": "development",
                        "verbose": True
                    }
                }
            ],
            "afterRun": [
                {
                    "kind": "telemetry",
                    "name": "dev-logger-end",
                    "event": "dev.run.completed",
                    "properties": {
                        "environment": "development"
                    }
                }
            ]
        }

    elif environment == "staging":
        return {
            "beforeRun": [
                # Staging: Basic PII redaction
                {
                    "kind": "modify",
                    "name": "staging-pii-redactor",
                    "predefinedPatterns": ["email", "phone"],
                    "replacement": "[REDACTED]"
                },
                {
                    "kind": "telemetry",
                    "name": "staging-logger",
                    "event": "staging.run.started",
                    "properties": {
                        "environment": "staging"
                    }
                }
            ],
            "beforeToolExecution": [
                # Staging: Block production tools
                {
                    "kind": "block",
                    "name": "prod-tool-blocker",
                    "condition": {
                        "kind": "expression",
                        "expression": "tool.name.startsWith('prod_')"
                    },
                    "message": "Production tools not available in staging"
                }
            ],
            "afterRun": [
                {
                    "kind": "modify",
                    "name": "staging-output-redactor",
                    "predefinedPatterns": ["email", "phone"],
                    "replacement": "[REDACTED]"
                }
            ]
        }

    elif environment == "production":
        return {
            "beforeRun": [
                # Production: Comprehensive PII redaction
                {
                    "kind": "modify",
                    "name": "prod-pii-redactor-input",
                    "predefinedPatterns": [
                        "email",
                        "phone",
                        "ssn",
                        "credit_card"
                    ],
                    "replacement": "[REDACTED]"
                },
                # Production: Audit logging
                {
                    "kind": "telemetry",
                    "name": "prod-audit-start",
                    "event": "production.run.started",
                    "properties": {
                        "environment": "production",
                        "compliance": "enabled"
                    }
                }
            ],
            "beforeToolExecution": [
                # Production: Tool approval
                {
                    "kind": "remote",
                    "name": "prod-tool-approval",
                    "endpoint": "https://approvals.example.com/prod",
                    "condition": {
                        "kind": "expression",
                        "expression": """
                            tool.category in ['destructive', 'financial']
                        """
                    }
                },
                # Production: Cost control
                {
                    "kind": "remote",
                    "name": "prod-cost-control",
                    "endpoint": "https://billing.example.com/check",
                    "condition": {
                        "kind": "expression",
                        "expression": "tool.estimated_cost > 5.00"
                    }
                }
            ],
            "afterToolExecution": [
                {
                    "kind": "modify",
                    "name": "prod-result-sanitizer",
                    "predefinedPatterns": [
                        "email",
                        "phone",
                        "ssn",
                        "credit_card"
                    ],
                    "replacement": "[REDACTED]"
                }
            ],
            "afterRun": [
                # Production: Output sanitization
                {
                    "kind": "modify",
                    "name": "prod-pii-redactor-output",
                    "predefinedPatterns": [
                        "email",
                        "phone",
                        "ssn",
                        "credit_card"
                    ],
                    "replacement": "[REDACTED]"
                },
                # Production: Quality enforcement
                {
                    "kind": "sendMessage",
                    "name": "prod-quality-enforcer",
                    "condition": {
                        "kind": "expression",
                        "expression": "len(message.content[0].text) < 50"
                    },
                    "message": {
                        "role": "system",
                        "content": [
                            {
                                "kind": "text",
                                "text": "Response too brief. Provide detailed answer."
                            }
                        ]
                    }
                },
                # Production: Final audit
                {
                    "kind": "telemetry",
                    "name": "prod-audit-end",
                    "event": "production.run.completed",
                    "properties": {
                        "environment": "production",
                        "compliance": "enabled"
                    }
                }
            ]
        }

    else:
        raise ValueError(f"Unknown environment: {environment}")

def create_agent_for_environment(api_base_url, token, environment):
    """Create agent with environment-specific hooks."""

    agent_config = {
        "name": f"{environment}-agent",
        "model": "claude-sonnet-4-5-20250929",
        "instructions": f"You are an assistant running in {environment} environment.",
        "hooks": create_environment_specific_hooks(environment)
    }

    response = requests.post(
        f"{api_base_url}/agents",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=agent_config
    )
    response.raise_for_status()

    return response.json()

# Usage
dev_agent = create_agent_for_environment(
    "https://api.example.com",
    "YOUR_API_TOKEN",
    "development"
)

staging_agent = create_agent_for_environment(
    "https://api.example.com",
    "YOUR_API_TOKEN",
    "staging"
)

prod_agent = create_agent_for_environment(
    "https://api.example.com",
    "YOUR_API_TOKEN",
    "production"
)

print(f"Created dev agent: {dev_agent['agentId']}")
print(f"Created staging agent: {staging_agent['agentId']}")
print(f"Created prod agent: {prod_agent['agentId']}")
```

## Troubleshooting

### Problem: Hooks Not Triggering

**Symptoms:**
- Hooks configured but not executing
- Events passing through without modification
- No telemetry logs appearing

**Possible Causes:**

1. **Condition Not Met**
   - Hook condition evaluates to `false`
   - Check condition logic and test with simpler condition

   ```python
   # Debug: Use AlwaysCondition to test
   {
       "kind": "modify",
       "name": "test-hook",
       "condition": {
           "kind": "always"  # Always triggers
       },
       "predefinedPatterns": ["email"],
       "replacement": "[TEST]"
   }
   ```

2. **Wrong Lifecycle Point**
   - Hook attached to wrong lifecycle point
   - Verify lifecycle point matches your use case

   ```python
   # Example: PII redaction should be in afterRun for output
   {
       "hooks": {
           "afterRun": [  # Not beforeRun
               {
                   "kind": "modify",
                   "name": "output-redactor",
                   "predefinedPatterns": ["email"]
               }
           ]
       }
   }
   ```

3. **Content Type Mismatch**
   - Condition checks for content type that doesn't match
   - Verify content types in condition

   ```python
   # Check actual content type
   {
       "condition": {
           "kind": "content",
           "contentTypes": ["text"]  # Only triggers for text
       }
   }
   ```

**Solutions:**

1. **Enable Debug Logging:**
   ```python
   # Add telemetry hook to debug
   {
       "kind": "telemetry",
       "name": "debug-logger",
       "condition": {
           "kind": "always"
       },
       "event": "debug.hook_evaluation",
       "properties": {
           "debug": True
       }
   }
   ```

2. **Test with Simple Hook:**
   ```python
   # Minimal test hook
   {
       "kind": "telemetry",
       "name": "test",
       "event": "test.event"
   }
   ```

3. **Check API Response:**
   ```python
   response = requests.post(...)
   print(response.json())  # Look for hook errors
   ```

### Problem: Remote Hook Timeouts

**Symptoms:**
- Remote hooks timing out
- Hook service receiving requests but not responding in time
- Runs failing with timeout errors

**Possible Causes:**

1. **Slow Hook Service**
   - Hook endpoint taking too long to respond
   - Network latency

2. **Complex Processing**
   - Hook doing expensive operations
   - External API calls taking too long

3. **Database Queries**
   - Slow database lookups
   - Missing indexes

**Solutions:**

1. **Optimize Hook Service:**
   ```python
   # Use async processing for remote hooks
   from flask import Flask, request, jsonify
   import asyncio

   app = Flask(__name__)

   @app.route('/hook', methods=['POST'])
   async def hook_handler():
       data = request.json

       # Fast path: Check cache first
       cached_result = await check_cache(data['eventSeq'])
       if cached_result:
           return jsonify(cached_result)

       # Process and cache
       result = await process_event(data)
       await cache_result(data['eventSeq'], result)

       return jsonify(result)
   ```

2. **Use Client-Side Filtering:**
   ```python
   # Reduce unnecessary remote calls with conditions
   {
       "kind": "remote",
       "name": "expensive-hook",
       "endpoint": "https://hooks.example.com/filter",
       "condition": {
           "kind": "expression",
           "expression": """
               message.role == 'assistant' &&
               len(message.content[0].text) > 100
           """
       }
   }
   ```

3. **Implement Caching:**
   ```python
   import redis

   cache = redis.Redis(host='localhost', port=6379)

   @app.route('/hook', methods=['POST'])
   def hook_handler():
       data = request.json
       event_hash = hash_event(data)

       # Check cache
       cached = cache.get(event_hash)
       if cached:
           return jsonify(json.loads(cached))

       # Process
       result = process_event(data)

       # Cache result
       cache.setex(event_hash, 300, json.dumps(result))

       return jsonify(result)
   ```

4. **Use WebSocket for Long-Running Hooks:**
   ```python
   # WebSocket maintains connection, reducing overhead
   {
       "kind": "remote",
       "name": "realtime-hook",
       "endpoint": "wss://hooks.example.com/filter",
       "connection": {
           "kind": "key",
           "key": "Bearer token",
           "headerName": "Authorization"
       }
   }
   ```

### Problem: PII Still Appearing in Output

**Symptoms:**
- PII not being redacted
- Patterns not matching
- Inconsistent redaction

**Possible Causes:**

1. **Pattern Not Comprehensive**
   - PII in format not covered by pattern
   - Need additional regex patterns

2. **Wrong Lifecycle Point**
   - Redaction happening too early or too late
   - Multiple content pieces not all redacted

3. **Streaming Issues**
   - PII split across multiple chunks
   - Modification not covering all eventSeqs

**Solutions:**

1. **Use Comprehensive Patterns:**
   ```python
   {
       "kind": "modify",
       "name": "comprehensive-pii-redactor",
       "predefinedPatterns": [
           "email",
           "phone",
           "ssn",
           "credit_card",
           "ip_address"
       ],
       "regexPatterns": [
           # International phone numbers
           r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
           # Email variations
           r"\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
           # SSN variations
           r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"
       ],
       "replacement": "[REDACTED]"
   }
   ```

2. **Apply at Multiple Points:**
   ```python
   # Redact at all lifecycle points
   pii_hook = {
       "kind": "modify",
       "name": "pii-redactor",
       "predefinedPatterns": ["email", "phone", "ssn"],
       "replacement": "[REDACTED]"
   }

   agent_config = {
       "hooks": {
           "beforeRun": [pii_hook],
           "afterToolExecution": [pii_hook],
           "afterRun": [pii_hook]
       }
   }
   ```

3. **Handle Streaming Content:**
   ```python
   # For remote hooks handling streaming
   class StreamingPIIRedactor:
       def __init__(self):
           self.buffers = {}

       def handle_event(self, event):
           event_type = event['event']

           if event_type == 'content.completed':
               # Wait for complete content before redacting
               content_id = event['content']['contentId']
               complete_text = self.buffers.get(content_id, '')

               # Apply redaction to complete text
               redacted = redact_pii(complete_text)

               return {
                   "kind": "modify",
                   "eventSeqs": [event['eventSeq']],
                   "contentIndex": 0,
                   "modifiedContent": {
                       "kind": "text",
                       "text": redacted
                   }
               }
   ```

### Problem: Hook Blocking Legitimate Content

**Symptoms:**
- False positives in content filtering
- Legitimate operations being blocked
- Users unable to complete tasks

**Possible Causes:**

1. **Overly Aggressive Conditions**
   - Condition too broad
   - Keywords matching legitimate content

2. **Missing Context**
   - Blocking based on partial information
   - Not considering user role or permissions

**Solutions:**

1. **Refine Conditions:**
   ```python
   # Bad: Too broad
   {
       "kind": "block",
       "name": "keyword-blocker",
       "condition": {
           "kind": "expression",
           "expression": "'admin' in message.content[0].text.lower()"
       },
       "message": "Blocked"
   }

   # Good: More specific
   {
       "kind": "block",
       "name": "keyword-blocker",
       "condition": {
           "kind": "expression",
           "expression": """
               user.role != 'admin' &&
               tool.name == 'admin_panel' &&
               'delete' in tool.arguments.action.lower()
           """
       },
       "message": "Admin privileges required"
   }
   ```

2. **Use Remote Hook for Complex Logic:**
   ```python
   # Remote hook can consider more context
   @app.route('/smart-filter', methods=['POST'])
   def smart_filter():
       data = request.json

       # Consider multiple factors
       content = data.get('content', {})
       user = data.get('context', {}).get('user', {})
       tool = data.get('context', {}).get('tool', {})

       # Complex decision logic
       if should_allow(content, user, tool):
           return jsonify({
               "kind": "allow",
               "eventSeqs": [data['eventSeq']]
           })
       else:
           return jsonify({
               "kind": "block",
               "eventSeqs": [data['eventSeq']],
               "message": "Content filtered"
           })
   ```

3. **Implement Feedback Loop:**
   ```python
   # Allow users to report false positives
   {
       "kind": "remote",
       "name": "adaptive-filter",
       "endpoint": "https://hooks.example.com/adaptive-filter",
       "config": {
           "enable_feedback": True,
           "feedback_url": "https://feedback.example.com"
       }
   }
   ```

### Problem: Hook Responses Not Being Applied

**Symptoms:**
- Hook returns modify response but content unchanged
- Block response not stopping execution
- Allow response but content still filtered

**Possible Causes:**

1. **Invalid EventSeq**
   - EventSeqs don't match events received
   - Non-contiguous eventSeqs
   - EventSeqs out of order

2. **Invalid Response Format**
   - Missing required fields
   - Wrong content type
   - Invalid JSON structure

3. **Content Index Mismatch**
   - Modifying wrong content index
   - Content piece doesn't exist

**Solutions:**

1. **Validate EventSeqs:**
   ```python
   # Ensure contiguous eventSeqs
   @app.route('/hook', methods=['POST'])
   def hook_handler():
       data = request.json
       event_seq = data['eventSeq']

       # Return response with correct eventSeq
       return jsonify({
           "kind": "modify",
           "eventSeqs": [event_seq],  # Must match received event
           "contentIndex": 0,
           "modifiedContent": {
               "kind": "text",
               "text": "Modified content"
           }
       })
   ```

2. **Validate Response Format:**
   ```python
   from jsonschema import validate

   modify_response_schema = {
       "type": "object",
       "properties": {
           "kind": {"const": "modify"},
           "eventSeqs": {
               "type": "array",
               "items": {"type": "integer"}
           },
           "contentIndex": {"type": "integer"},
           "modifiedContent": {
               "type": "object",
               "properties": {
                   "kind": {"type": "string"},
                   "text": {"type": "string"}
               },
               "required": ["kind"]
           }
       },
       "required": ["kind", "eventSeqs", "contentIndex", "modifiedContent"]
   }

   @app.route('/hook', methods=['POST'])
   def hook_handler():
       data = request.json

       response = {
           "kind": "modify",
           "eventSeqs": [data['eventSeq']],
           "contentIndex": 0,
           "modifiedContent": {
               "kind": "text",
               "text": "Modified"
           }
       }

       # Validate before returning
       validate(instance=response, schema=modify_response_schema)

       return jsonify(response)
   ```

3. **Check Content Index:**
   ```python
   @app.route('/hook', methods=['POST'])
   def hook_handler():
       data = request.json
       content = data.get('content', {})

       # Verify content exists
       if 'contentIndex' not in data:
           return jsonify({
               "kind": "allow",
               "eventSeqs": [data['eventSeq']]
           })

       return jsonify({
           "kind": "modify",
           "eventSeqs": [data['eventSeq']],
           "contentIndex": data['contentIndex'],
           "modifiedContent": {
               "kind": "text",
               "text": "Modified"
           }
       })
   ```

### Problem: Telemetry Not Being Logged

**Symptoms:**
- Telemetry hooks configured but no logs
- Events not appearing in monitoring system
- Missing audit trail

**Possible Causes:**

1. **Condition Not Met**
   - Telemetry condition evaluates to false
   - Wrong content type or role

2. **Telemetry Sink Not Configured**
   - Telemetry events not being forwarded
   - Integration with logging system missing

3. **Event Name Mismatch**
   - Monitoring system filtering by event name
   - Event name not recognized

**Solutions:**

1. **Use AlwaysCondition for Testing:**
   ```python
   {
       "kind": "telemetry",
       "name": "test-telemetry",
       "condition": {
           "kind": "always"  # Always logs
       },
       "event": "test.event",
       "properties": {
           "test": True
       }
   }
   ```

2. **Verify Telemetry Integration:**
   ```python
   # Check if telemetry events are being emitted
   import logging

   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)

   # Run agent and check logs
   response = requests.post(...)
   logger.debug(f"Response: {response.json()}")
   ```

3. **Use Standard Event Names:**
   ```python
   # Standard event naming convention
   {
       "kind": "telemetry",
       "name": "audit-logger",
       "event": "agent.run.completed",  # Standard format
       "properties": {
           "source": "agent-runtime",
           "timestamp": "server-time"
       }
   }
   ```

### Problem: Performance Degradation with Many Hooks

**Symptoms:**
- Slow run execution
- Increased latency
- Timeouts

**Possible Causes:**

1. **Too Many Hooks**
   - Too many hooks at each lifecycle point
   - Redundant hooks

2. **Inefficient Conditions**
   - Complex expression conditions
   - Remote condition checks

3. **Remote Hook Latency**
   - Each remote hook adds network round-trip
   - No parallelization

**Solutions:**

1. **Consolidate Hooks:**
   ```python
   # Bad: Multiple similar hooks
   hooks = {
       "afterRun": [
           {"kind": "modify", "name": "email-redactor", "predefinedPatterns": ["email"]},
           {"kind": "modify", "name": "phone-redactor", "predefinedPatterns": ["phone"]},
           {"kind": "modify", "name": "ssn-redactor", "predefinedPatterns": ["ssn"]}
       ]
   }

   # Good: Single comprehensive hook
   hooks = {
       "afterRun": [
           {
               "kind": "modify",
               "name": "pii-redactor",
               "predefinedPatterns": ["email", "phone", "ssn"]
           }
       ]
   }
   ```

2. **Optimize Conditions:**
   ```python
   # Bad: Complex expression evaluated every time
   {
       "condition": {
           "kind": "expression",
           "expression": """
               len(message.content[0].text) > 100 &&
               any([word in message.content[0].text.lower()
                    for word in ['keyword1', 'keyword2', ...]])
           """
       }
   }

   # Good: Simpler condition
   {
       "condition": {
           "kind": "content",
           "contentTypes": ["text"]
       }
   }
   ```

3. **Use WebSocket for Remote Hooks:**
   ```python
   # WebSocket reduces connection overhead
   {
       "kind": "remote",
       "name": "efficient-hook",
       "endpoint": "wss://hooks.example.com/filter"
   }
   ```

4. **Profile Hook Performance:**
   ```python
   # Add timing telemetry
   {
       "kind": "telemetry",
       "name": "performance-monitor",
       "event": "hook.timing",
       "properties": {
           "measure_duration": True,
           "measure_latency": True
       }
   }
   ```

## Best Practices

### 1. Security

- **Encrypt Hook Endpoints**: Always use HTTPS/WSS for remote hooks
- **Authenticate Hooks**: Use Connection types for authentication
- **Validate Input**: Validate all hook responses before applying
- **Limit Hook Scope**: Use conditions to minimize unnecessary hook execution
- **Audit Everything**: Log all hook evaluations for security review

### 2. Performance

- **Consolidate Hooks**: Combine similar hooks to reduce overhead
- **Use Client-Side Filtering**: Apply conditions to reduce remote calls
- **Cache Results**: Cache hook responses when appropriate
- **Optimize Remote Services**: Keep hook services fast (<100ms)
- **Use WebSocket**: For high-frequency hooks, use WebSocket

### 3. Reliability

- **Handle Failures Gracefully**: Implement proper error handling
- **Set Timeouts**: Configure appropriate timeouts for remote hooks
- **Implement Retries**: Retry transient failures with backoff
- **Monitor Hook Health**: Track hook success/failure rates
- **Test Thoroughly**: Test hooks in isolation before production

### 4. Maintainability

- **Use Descriptive Names**: Give hooks clear, descriptive names
- **Document Patterns**: Document custom regex patterns
- **Version Configurations**: Version control hook configurations
- **Separate Concerns**: Keep hooks focused on single responsibility
- **Test Conditions**: Test condition logic separately

### 5. Compliance

- **Document Requirements**: Document compliance requirements met
- **Retain Audit Logs**: Configure appropriate retention periods
- **Review Regularly**: Regularly review hook configurations
- **Test Redaction**: Verify PII redaction is comprehensive
- **Validate Coverage**: Ensure all sensitive data is covered

## Related Documentation

- **[Specifications: Hooks](../specifications/hooks.md)** - Complete hooks specification
- **[TypeSpec: hooks.tsp](../typespec/hooks.tsp)** - Hook type definitions
- **[TypeSpec: conditions.tsp](../typespec/conditions.tsp)** - Condition type definitions
- **[Guide: Human-in-the-Loop](./human-in-loop.md)** - Approval workflows
- **[Specification: Run Lifecycle](../specifications/run-lifecycle.md)** - Run states and lifecycle
- **[Specification: Remote Endpoints](../specifications/remote-endpoints.md)** - RemoteHook protocol
