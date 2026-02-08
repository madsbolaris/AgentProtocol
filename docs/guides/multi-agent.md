# Multi-Agent Orchestration Guide

**Version**: 2.0
**Last Updated**: 2026-02-07

## Overview

Multi-agent orchestration enables complex workflows by coordinating multiple AI agents working together. Rather than building monolithic agents that try to do everything, you can create specialized agents that collaborate, delegate, and coordinate to solve complex problems.

**What You'll Learn:**
- Multi-agent coordination patterns
- Sequential and parallel agent execution
- Agent handoff and delegation
- Auto-response coordination with ThreadWatch
- Consensus building and voting
- Shared context and state management
- Managing concurrent runs and coordinating results

**Key Concepts:**

- **Agent Specialization**: Each agent has a focused role and expertise
- **Coordination Patterns**: Agents can work sequentially, in parallel, or hierarchically
- **Auto-Response**: Agents automatically participate based on conditions
- **Context Sharing**: Agents pass information through threads and messages
- **State Management**: Track progress across multiple agent runs
- **Error Handling**: Graceful degradation when agents fail

## Use Cases

Multi-agent orchestration is ideal for:

### Task Delegation
- **Customer service routing**: Triage agent → specialist agents (billing, technical, refunds)
- **Document processing**: Extractor → validator → enricher
- **Code review pipeline**: Linter → security scanner → style checker

### Specialized Agents
- **Research aggregation**: Multiple search agents → synthesizer agent
- **Content pipeline**: Writer → editor → fact-checker → publisher
- **Data analysis**: Collector → cleaner → analyzer → reporter

### Complex Workflows
- **Consensus building**: Multiple agents vote on decisions
- **Hierarchical delegation**: Manager agent → team lead agents → worker agents
- **Parallel processing**: Fan-out for speed, fan-in for aggregation

## Architecture

### Agent Coordination Patterns

```
┌─────────────────────────────────────────────────────────┐
│ SEQUENTIAL PIPELINE                                     │
│                                                         │
│  Agent A ──> Agent B ──> Agent C ──> Final Output       │
│  (Research)  (Analyze)   (Summarize)                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PARALLEL EXECUTION                                      │
│                                                         │
│           ┌──> Agent A (Search Google) ──┐              │
│           │                               │             │
│  Input ───┼──> Agent B (Search Papers) ───┼──> Combine  │
│           │                               │             │
│           └──> Agent C (Search Docs) ─────┘             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ HIERARCHICAL DELEGATION                                 │
│                                                         │
│              Manager Agent                              │
│                   │                                     │
│         ┌─────────┼─────────┐                           │
│         ▼         ▼         ▼                           │
│    Specialist  Specialist  Specialist                   │
│       Agent      Agent      Agent                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ AGENT HANDOFF                                           │
│                                                         │
│  Triage ──[handoff]──> Billing ──[handoff]──> Manager   │
│  Agent                  Agent                  Agent    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CONSENSUS BUILDING                                      │
│                                                         │
│           ┌──> Agent A (votes) ───┐                     │
│           │                       │                     │
│  Input ───┼──> Agent B (votes) ───┼──> Aggregator       │
│           │                       │     (consensus)     │
│           └──> Agent C (votes) ───┘                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ AUTO-RESPONSE WITH THREADWATCH                         │
│                                                         │
│  Thread ─┬──> Watched by Agent A (on user messages)    │
│          ├──> Watched by Agent B (on mentions)         │
│          └──> Watched by Agent C (on video content)    │
└─────────────────────────────────────────────────────────┘
```

### Core Models

From TypeSpec `/typespec/execution.tsp` and `/typespec/agents.tsp`:

**Run** - Single agent execution instance
```typescript
model Run {
  runId: string;           // Unique execution identifier
  agentId: string;         // Agent performing the run
  threadId?: string;       // Conversation thread (optional for stateless)
  status: RunStatus;       // queued, in_progress, completed, failed, etc.
  input: ChatMessage[];    // Input messages
  output: ChatMessage[];   // Generated messages
  usage: CompletionUsage;  // Token usage stats
}
```

**Thread** - Conversation context shared across runs
```typescript
model Thread {
  threadId: string;           // Unique thread identifier
  status: ThreadStatus;       // active, closed, archived
  participants: Participant[]; // Conversation participants
  messages: ChatMessage[];    // Full message history
  metadata?: Record<unknown>; // Custom metadata
}
```

**ThreadWatch** - Agent registration for thread monitoring
```typescript
model ThreadWatch {
  watchId: string;          // Unique watch identifier
  threadId: string;         // Thread being watched
  agentId: string;          // Agent watching the thread
  active?: boolean;         // Whether watch is active (default: true)
  createdAt: utcDateTime;   // Creation timestamp
  lastActivatedAt?: utcDateTime;  // Last activation timestamp
  activationCount?: int32;  // Number of runs created by this watch
  metadata?: Record<unknown>; // Custom metadata
}
```

**AutoResponseConfig** - Agent auto-response configuration
```typescript
model AutoResponseConfig {
  runCondition?: RunCondition;      // When agent should participate
  maxConsecutiveRuns?: int32;       // Max runs before requiring user (default: 1)
  threadCleanup?: ThreadCleanup;    // Thread cleanup strategy
}
```

**RunCondition** - Conditions for agent participation
```typescript
union RunCondition {
  AlwaysCondition,          // Always participate
  RolesCondition,           // Match message roles (user, assistant, system)
  ContentCondition,         // Match content types (video, image, file)
  MentionCondition,         // Match explicit @mentions
  ExpressionCondition,      // In-process Power Fx/CEL evaluation
  RemoteCondition,          // Custom logic via remote endpoint
}
```

## Implementation

### Pattern 1: Sequential Agent Pipeline

**Use Case**: Research → Analyze → Summarize

Each agent processes the output of the previous agent in a linear workflow.

**Python Implementation:**

```python
import requests
from typing import List, Dict, Any

API_BASE = "https://agents.example.com/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class SequentialPipeline:
    """Execute agents in sequence, passing output to next agent."""

    def __init__(self, agents: List[Dict[str, Any]]):
        """
        Args:
            agents: List of agent configurations in execution order
        """
        self.agents = agents

    async def run(self, initial_input: str, thread_id: str = None) -> Dict:
        """
        Execute pipeline sequentially.

        Args:
            initial_input: Starting input for first agent
            thread_id: Optional thread for conversation continuity

        Returns:
            Final run result with complete history
        """
        # Create thread if not provided (stores full conversation)
        if not thread_id:
            thread_response = requests.post(
                f"{API_BASE}/threads",
                headers=headers,
                json={
                    "participants": [{"id": "user", "role": "user"}],
                    "metadata": {"pipeline": "sequential"}
                }
            )
            thread_id = thread_response.json()["threadId"]

        # Track all runs for audit trail
        runs = []
        current_input = initial_input

        # Execute each agent in sequence
        for i, agent_config in enumerate(self.agents):
            print(f"Executing agent {i+1}/{len(self.agents)}: {agent_config['name']}")

            # Create run with current input
            run_response = requests.post(
                f"{API_BASE}/runs",
                headers=headers,
                json={
                    "threadId": thread_id,
                    "agent": agent_config,
                    "input": [{
                        "role": "user",
                        "contents": [{
                            "kind": "text",
                            "text": current_input
                        }]
                    }],
                    "store": True  # Persist to thread
                }
            )

            run_result = run_response.json()
            runs.append(run_result)

            # Check status
            if run_result["status"] != "completed":
                raise Exception(
                    f"Agent {agent_config['name']} failed: "
                    f"{run_result.get('error', {}).get('message', 'Unknown error')}"
                )

            # Extract output for next agent
            output_message = run_result["output"][0]
            current_input = output_message["contents"][0]["text"]

        return {
            "threadId": thread_id,
            "runs": runs,
            "finalOutput": current_input,
            "totalUsage": sum(r["usage"]["totalTokens"] for r in runs)
        }


# Example: Content creation pipeline
async def content_pipeline_example():
    """Writer → Editor → Publisher pipeline."""

    pipeline = SequentialPipeline(agents=[
        {
            "kind": "prompt",
            "name": "WriterAgent",
            "model": "gpt-4o",
            "instructions": """You are a content writer. Create engaging blog posts
            based on the topic provided. Focus on clarity and reader engagement."""
        },
        {
            "kind": "prompt",
            "name": "EditorAgent",
            "model": "gpt-4o",
            "instructions": """You are an editor. Review and improve the content
            for grammar, style, and flow. Make it publication-ready."""
        },
        {
            "kind": "prompt",
            "name": "PublisherAgent",
            "model": "gpt-4o",
            "instructions": """You are a publisher. Format the content with proper
            headings, add SEO-friendly metadata, and create a compelling title."""
        }
    ])

    result = await pipeline.run(
        "Write about the future of AI in healthcare"
    )

    print(f"Pipeline completed in {len(result['runs'])} steps")
    print(f"Total tokens: {result['totalUsage']}")
    print(f"Final output:\n{result['finalOutput']}")
```

**JavaScript Implementation:**

```javascript
class SequentialPipeline {
    constructor(agents) {
        this.agents = agents;
    }

    async run(initialInput, threadId = null) {
        // Create thread if not provided
        if (!threadId) {
            const threadRes = await fetch(`${API_BASE}/threads`, {
                method: "POST",
                headers,
                body: JSON.stringify({
                    participants: [{ id: "user", role: "user" }],
                    metadata: { pipeline: "sequential" }
                })
            });
            threadId = (await threadRes.json()).threadId;
        }

        const runs = [];
        let currentInput = initialInput;

        // Execute agents sequentially
        for (const [i, agentConfig] of this.agents.entries()) {
            console.log(`Executing agent ${i+1}/${this.agents.length}: ${agentConfig.name}`);

            const runRes = await fetch(`${API_BASE}/runs`, {
                method: "POST",
                headers,
                body: JSON.stringify({
                    threadId,
                    agent: agentConfig,
                    input: [{
                        role: "user",
                        contents: [{ kind: "text", text: currentInput }]
                    }],
                    store: true
                })
            });

            const runResult = await runRes.json();
            runs.push(runResult);

            if (runResult.status !== "completed") {
                throw new Error(
                    `Agent ${agentConfig.name} failed: ${runResult.error?.message}`
                );
            }

            // Extract output for next agent
            currentInput = runResult.output[0].contents[0].text;
        }

        return {
            threadId,
            runs,
            finalOutput: currentInput,
            totalUsage: runs.reduce((sum, r) => sum + r.usage.totalTokens, 0)
        };
    }
}
```

### Pattern 2: Parallel Agent Execution

**Use Case**: Multiple specialized agents working simultaneously

Execute multiple agents in parallel and aggregate results.

**Python Implementation:**

```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class ParallelAgentExecutor:
    """Execute multiple agents in parallel and aggregate results."""

    def __init__(self, agents: List[Dict[str, Any]]):
        self.agents = agents

    async def run_agent(
        self,
        session: aiohttp.ClientSession,
        agent_config: Dict,
        input_text: str,
        thread_id: str = None
    ) -> Dict:
        """Execute a single agent."""
        async with session.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "threadId": thread_id,
                "agent": agent_config,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": input_text}]
                }],
                "store": thread_id is not None
            }
        ) as response:
            return await response.json()

    async def run_parallel(
        self,
        input_text: str,
        aggregator_agent: Dict = None
    ) -> Dict:
        """
        Execute all agents in parallel, optionally aggregate results.

        Args:
            input_text: Input for all agents
            aggregator_agent: Optional agent to synthesize results

        Returns:
            Dictionary with individual results and optional aggregated output
        """
        async with aiohttp.ClientSession() as session:
            # Launch all agents in parallel
            tasks = [
                self.run_agent(session, agent, input_text)
                for agent in self.agents
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle failures gracefully
            successful_results = []
            failed_results = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_results.append({
                        "agent": self.agents[i]["name"],
                        "error": str(result)
                    })
                elif result.get("status") != "completed":
                    failed_results.append({
                        "agent": self.agents[i]["name"],
                        "error": result.get("error", {}).get("message")
                    })
                else:
                    successful_results.append({
                        "agent": self.agents[i]["name"],
                        "output": result["output"][0]["contents"][0]["text"],
                        "usage": result["usage"]
                    })

            response = {
                "successfulResults": successful_results,
                "failedResults": failed_results,
                "totalAgents": len(self.agents),
                "successCount": len(successful_results)
            }

            # Optionally aggregate with another agent
            if aggregator_agent and successful_results:
                combined_input = "Synthesize these responses:\n\n"
                for r in successful_results:
                    combined_input += f"**{r['agent']}**: {r['output']}\n\n"

                aggregation_result = await self.run_agent(
                    session,
                    aggregator_agent,
                    combined_input
                )

                response["aggregatedOutput"] = (
                    aggregation_result["output"][0]["contents"][0]["text"]
                )

            return response


# Example: Research aggregation from multiple sources
async def research_aggregation_example():
    """Multiple search agents → synthesizer."""

    executor = ParallelAgentExecutor(agents=[
        {
            "kind": "prompt",
            "name": "GoogleSearchAgent",
            "model": "gpt-4o",
            "instructions": "Search Google and summarize top findings.",
            "tools": [{"name": "web_search", "description": "Search the web"}]
        },
        {
            "kind": "prompt",
            "name": "AcademicSearchAgent",
            "model": "gpt-4o",
            "instructions": "Search academic papers and summarize key research.",
            "tools": [{"name": "scholar_search", "description": "Search papers"}]
        },
        {
            "kind": "prompt",
            "name": "NewsSearchAgent",
            "model": "gpt-4o",
            "instructions": "Search recent news and summarize developments.",
            "tools": [{"name": "news_search", "description": "Search news"}]
        }
    ])

    synthesizer = {
        "kind": "prompt",
        "name": "SynthesizerAgent",
        "model": "gpt-4o",
        "instructions": """Synthesize the research from multiple sources into
        a cohesive summary. Identify common themes and contradictions."""
    }

    result = await executor.run_parallel(
        input_text="Research the impact of AI on climate change solutions",
        aggregator_agent=synthesizer
    )

    print(f"Successful: {result['successCount']}/{result['totalAgents']}")
    print(f"Aggregated output:\n{result.get('aggregatedOutput', 'N/A')}")
```

### Pattern 3: Agent Handoff

**Use Case**: Triage agent → specialist agents

Transfer control from one agent to another based on conversation context. Use Run.agentId to transition between agents within the same thread.

**Implementation:**

```python
class HandoffCoordinator:
    """Coordinate agent handoffs based on conversation needs."""

    def __init__(self, agents: Dict[str, Dict]):
        """
        Args:
            agents: Dictionary mapping agent IDs to configurations
        """
        self.agents = agents
        self.thread_id = None

    def create_handoff_tool(self, target_agent_id: str, target_agent_name: str) -> Dict:
        """Create a handoff tool for transferring to another agent."""
        return {
            "name": f"transfer_to_{target_agent_name}",
            "description": f"Transfer conversation to {target_agent_name} agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for handoff"
                    },
                    "context": {
                        "type": "string",
                        "description": "Context to provide to next agent"
                    }
                },
                "required": ["reason"]
            }
        }

    async def run_with_handoffs(
        self,
        initial_agent_id: str,
        user_input: str,
        max_handoffs: int = 5
    ) -> Dict:
        """
        Run conversation with agent handoffs.

        Args:
            initial_agent_id: Starting agent ID
            user_input: User's initial message
            max_handoffs: Maximum number of handoffs to prevent loops

        Returns:
            Conversation result with handoff history
        """
        # Create thread
        thread_response = requests.post(
            f"{API_BASE}/threads",
            headers=headers,
            json={
                "participants": [{"id": "user", "role": "user"}],
                "metadata": {"pattern": "handoff"}
            }
        )
        self.thread_id = thread_response.json()["threadId"]

        current_agent_id = initial_agent_id
        handoff_history = []

        for handoff_count in range(max_handoffs):
            agent_config = self.agents[current_agent_id].copy()

            # Add handoff tools for available agents
            handoff_tools = [
                self.create_handoff_tool(agent_id, agent["name"])
                for agent_id, agent in self.agents.items()
                if agent_id != current_agent_id
            ]
            agent_config["tools"] = agent_config.get("tools", []) + handoff_tools

            # Run current agent
            run_response = requests.post(
                f"{API_BASE}/runs",
                headers=headers,
                json={
                    "threadId": self.thread_id,
                    "agentId": current_agent_id,  # Use agentId for handoff
                    "agent": agent_config,
                    "input": [{
                        "role": "user",
                        "contents": [{"kind": "text", "text": user_input}]
                    }] if handoff_count == 0 else [],  # Only first agent gets user input
                    "store": True
                }
            )

            run_result = run_response.json()

            # Check for handoff tool calls
            handoff_occurred = False
            for message in run_result.get("output", []):
                for content in message.get("contents", []):
                    if content.get("kind") == "toolCall":
                        tool_name = content.get("name", "")
                        if tool_name.startswith("transfer_to_"):
                            target_agent_name = tool_name.replace("transfer_to_", "")
                            # Find agent ID by name
                            target_agent_id = next(
                                (aid for aid, a in self.agents.items()
                                 if a["name"] == target_agent_name),
                                None
                            )
                            if target_agent_id:
                                handoff_history.append({
                                    "from": current_agent_id,
                                    "to": target_agent_id,
                                    "reason": content.get("input", {}).get("reason")
                                })
                                current_agent_id = target_agent_id
                                handoff_occurred = True
                                break
                if handoff_occurred:
                    break

            # If no handoff, conversation complete
            if not handoff_occurred:
                return {
                    "threadId": self.thread_id,
                    "finalAgentId": current_agent_id,
                    "handoffHistory": handoff_history,
                    "finalOutput": run_result["output"]
                }

            # Continue with next agent (empty input - it reads from thread)
            user_input = ""

        raise Exception(f"Maximum handoffs ({max_handoffs}) exceeded")


# Example: Customer service routing
async def customer_service_example():
    """Triage → Billing/Technical/Refunds specialist."""

    coordinator = HandoffCoordinator(agents={
        "agent-triage-001": {
            "kind": "prompt",
            "name": "TriageAgent",
            "model": "gpt-4o",
            "instructions": """You are a customer service triage agent.
            Determine customer needs and transfer to appropriate specialist:
            - Billing questions → transfer_to_BillingAgent
            - Technical issues → transfer_to_TechnicalAgent
            - Refund requests → transfer_to_RefundsAgent"""
        },
        "agent-billing-001": {
            "kind": "prompt",
            "name": "BillingAgent",
            "model": "gpt-4o",
            "instructions": """You are a billing specialist. Help with invoices,
            payment methods, and billing questions.""",
            "tools": [
                {"name": "lookup_invoice", "description": "Find invoice details"},
                {"name": "update_payment", "description": "Update payment method"}
            ]
        },
        "agent-technical-001": {
            "kind": "prompt",
            "name": "TechnicalAgent",
            "model": "gpt-4o",
            "instructions": """You are a technical support specialist.
            Help troubleshoot product issues.""",
            "tools": [
                {"name": "check_system_status", "description": "Check system health"},
                {"name": "reset_account", "description": "Reset user account"}
            ]
        },
        "agent-refunds-001": {
            "kind": "prompt",
            "name": "RefundsAgent",
            "model": "gpt-4o",
            "instructions": """You are a refunds specialist. Process refund
            requests according to policy.""",
            "tools": [
                {"name": "check_eligibility", "description": "Check refund eligibility"},
                {"name": "process_refund", "description": "Process refund request"}
            ]
        }
    })

    result = await coordinator.run_with_handoffs(
        initial_agent_id="agent-triage-001",
        user_input="I was charged twice for my subscription last month"
    )

    print(f"Conversation handled by: {result['finalAgentId']}")
    print(f"Handoff path: {' → '.join([h['from'] for h in result['handoffHistory']] + [result['finalAgentId']])}")
```

### Pattern 4: Hierarchical Delegation

**Use Case**: Manager agent delegates to team agents

A manager agent coordinates multiple worker agents.

**Implementation:**

```python
class HierarchicalCoordinator:
    """Manager agent delegates tasks to worker agents."""

    def __init__(
        self,
        manager_agent: Dict,
        worker_agents: List[Dict]
    ):
        self.manager = manager_agent
        self.workers = worker_agents

    def create_delegation_tool(self, worker_name: str) -> Dict:
        """Create delegation tool for assigning work to a worker."""
        return {
            "name": f"delegate_to_{worker_name}",
            "description": f"Delegate task to {worker_name}",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description for worker"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Task priority"
                    }
                },
                "required": ["task"]
            }
        }

    async def coordinate(self, user_request: str) -> Dict:
        """
        Manager coordinates worker agents to complete request.

        Returns:
            Results from all workers plus manager's final synthesis
        """
        # Create thread for coordination
        thread_response = requests.post(
            f"{API_BASE}/threads",
            headers=headers,
            json={
                "participants": [{"id": "user", "role": "user"}],
                "metadata": {"pattern": "hierarchical"}
            }
        )
        thread_id = thread_response.json()["threadId"]

        # Manager plans and delegates
        manager_config = self.manager.copy()
        manager_config["tools"] = manager_config.get("tools", []) + [
            self.create_delegation_tool(w["name"])
            for w in self.workers
        ]

        manager_run = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "threadId": thread_id,
                "agent": manager_config,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": user_request}]
                }],
                "store": True
            }
        ).json()

        # Extract delegations from manager's tool calls
        delegations = []
        for message in manager_run.get("output", []):
            for content in message.get("contents", []):
                if content.get("kind") == "toolCall":
                    tool_name = content.get("name", "")
                    if tool_name.startswith("delegate_to_"):
                        worker_name = tool_name.replace("delegate_to_", "")
                        delegations.append({
                            "worker": worker_name,
                            "task": content.get("input", {}).get("task"),
                            "priority": content.get("input", {}).get("priority", "medium")
                        })

        # Execute worker tasks in parallel
        worker_results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for delegation in delegations:
                # Find worker config
                worker_config = next(
                    (w for w in self.workers if w["name"] == delegation["worker"]),
                    None
                )
                if worker_config:
                    task = self.run_worker(
                        session,
                        worker_config,
                        delegation["task"],
                        thread_id
                    )
                    tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if not isinstance(result, Exception) and result.get("status") == "completed":
                    worker_results.append({
                        "worker": delegations[i]["worker"],
                        "task": delegations[i]["task"],
                        "output": result["output"][0]["contents"][0]["text"]
                    })

        # Manager synthesizes results
        synthesis_input = "Synthesize worker results:\n\n"
        for wr in worker_results:
            synthesis_input += f"**{wr['worker']}**: {wr['output']}\n\n"

        synthesis_run = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "threadId": thread_id,
                "agent": self.manager,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": synthesis_input}]
                }],
                "store": True
            }
        ).json()

        return {
            "threadId": thread_id,
            "delegations": delegations,
            "workerResults": worker_results,
            "finalSynthesis": synthesis_run["output"][0]["contents"][0]["text"]
        }

    async def run_worker(
        self,
        session: aiohttp.ClientSession,
        worker_config: Dict,
        task: str,
        thread_id: str
    ) -> Dict:
        """Execute worker agent task."""
        async with session.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "threadId": thread_id,
                "agent": worker_config,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": task}]
                }],
                "store": True
            }
        ) as response:
            return await response.json()


# Example: Project analysis delegation
async def project_analysis_example():
    """Manager delegates code review, security scan, performance analysis."""

    coordinator = HierarchicalCoordinator(
        manager_agent={
            "kind": "prompt",
            "name": "ProjectManager",
            "model": "gpt-4o",
            "instructions": """You are a project manager. Analyze requests and
            delegate to appropriate specialists. Synthesize their findings."""
        },
        worker_agents=[
            {
                "kind": "prompt",
                "name": "CodeReviewer",
                "model": "gpt-4o",
                "instructions": "Review code quality, patterns, maintainability.",
                "tools": [{"name": "analyze_code", "description": "Analyze code"}]
            },
            {
                "kind": "prompt",
                "name": "SecurityScanner",
                "model": "gpt-4o",
                "instructions": "Scan for security vulnerabilities and risks.",
                "tools": [{"name": "security_scan", "description": "Scan security"}]
            },
            {
                "kind": "prompt",
                "name": "PerformanceAnalyzer",
                "model": "gpt-4o",
                "instructions": "Analyze performance bottlenecks and optimization opportunities.",
                "tools": [{"name": "profile_code", "description": "Profile performance"}]
            }
        ]
    )

    result = await coordinator.coordinate(
        "Analyze the authentication service for production readiness"
    )

    print(f"Delegated to {len(result['delegations'])} workers")
    print(f"Final synthesis:\n{result['finalSynthesis']}")
```

### Pattern 5: Consensus Building

**Use Case**: Multiple agents vote on decisions

Aggregate opinions from multiple agents to reach consensus.

**Implementation:**

```python
class ConsensusBuilder:
    """Multiple agents vote, results aggregated by consensus algorithm."""

    def __init__(self, voting_agents: List[Dict]):
        self.voters = voting_agents

    async def build_consensus(
        self,
        question: str,
        consensus_threshold: float = 0.6
    ) -> Dict:
        """
        Get votes from all agents and determine consensus.

        Args:
            question: Question for agents to vote on
            consensus_threshold: Minimum agreement ratio (0.0-1.0)

        Returns:
            Consensus result with individual votes
        """
        async with aiohttp.ClientSession() as session:
            # Get votes from all agents in parallel
            tasks = [
                self.get_vote(session, agent, question)
                for agent in self.voters
            ]

            votes = await asyncio.gather(*tasks, return_exceptions=True)

            # Process votes
            valid_votes = []
            for i, vote in enumerate(votes):
                if not isinstance(vote, Exception) and vote.get("status") == "completed":
                    vote_text = vote["output"][0]["contents"][0]["text"].lower()

                    # Simple yes/no parsing (could be more sophisticated)
                    decision = None
                    if "yes" in vote_text or "approve" in vote_text:
                        decision = "yes"
                    elif "no" in vote_text or "reject" in vote_text:
                        decision = "no"

                    valid_votes.append({
                        "agent": self.voters[i]["name"],
                        "decision": decision,
                        "reasoning": vote_text
                    })

            # Calculate consensus
            yes_votes = sum(1 for v in valid_votes if v["decision"] == "yes")
            no_votes = sum(1 for v in valid_votes if v["decision"] == "no")
            total_votes = len(valid_votes)

            consensus_reached = False
            final_decision = None

            if total_votes > 0:
                yes_ratio = yes_votes / total_votes
                no_ratio = no_votes / total_votes

                if yes_ratio >= consensus_threshold:
                    consensus_reached = True
                    final_decision = "yes"
                elif no_ratio >= consensus_threshold:
                    consensus_reached = True
                    final_decision = "no"

            return {
                "question": question,
                "votes": valid_votes,
                "yesVotes": yes_votes,
                "noVotes": no_votes,
                "totalVotes": total_votes,
                "consensusReached": consensus_reached,
                "finalDecision": final_decision,
                "threshold": consensus_threshold
            }

    async def get_vote(
        self,
        session: aiohttp.ClientSession,
        agent_config: Dict,
        question: str
    ) -> Dict:
        """Get vote from a single agent."""
        voting_prompt = f"""Vote YES or NO on the following question.
        Provide your reasoning.

        Question: {question}

        Response format:
        Decision: [YES/NO]
        Reasoning: [Your reasoning here]
        """

        async with session.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "agent": agent_config,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": voting_prompt}]
                }],
                "store": False  # Stateless voting
            }
        ) as response:
            return await response.json()


# Example: Content approval voting
async def content_approval_example():
    """Multiple reviewers vote on content publication."""

    builder = ConsensusBuilder(voting_agents=[
        {
            "kind": "prompt",
            "name": "LegalReviewer",
            "model": "gpt-4o",
            "instructions": "Review content for legal compliance and risks."
        },
        {
            "kind": "prompt",
            "name": "BrandReviewer",
            "model": "gpt-4o",
            "instructions": "Review content for brand alignment and messaging."
        },
        {
            "kind": "prompt",
            "name": "TechnicalReviewer",
            "model": "gpt-4o",
            "instructions": "Review content for technical accuracy."
        },
        {
            "kind": "prompt",
            "name": "EditorialReviewer",
            "model": "gpt-4o",
            "instructions": "Review content for quality and readability."
        }
    ])

    result = await builder.build_consensus(
        question="Should we publish this blog post about our new AI product?",
        consensus_threshold=0.75  # Require 75% agreement
    )

    print(f"Consensus: {result['consensusReached']}")
    print(f"Decision: {result['finalDecision']}")
    print(f"Votes: {result['yesVotes']} yes, {result['noVotes']} no")

    for vote in result['votes']:
        print(f"\n{vote['agent']}: {vote['decision']}")
        print(f"  Reasoning: {vote['reasoning']}")
```

### Pattern 6: Shared Context Collaboration

**Use Case**: Multiple agents collaborate with shared state

Agents work together on a shared thread, building on each other's work.

**Implementation:**

```python
class SharedContextCollaboration:
    """Agents collaborate with shared conversation context."""

    def __init__(self, agents: List[Dict]):
        self.agents = agents

    async def collaborate(
        self,
        initial_task: str,
        max_iterations: int = 10
    ) -> Dict:
        """
        Agents take turns contributing to shared thread.

        Args:
            initial_task: Starting task description
            max_iterations: Maximum conversation turns

        Returns:
            Collaboration result with full thread history
        """
        # Create shared thread
        thread_response = requests.post(
            f"{API_BASE}/threads",
            headers=headers,
            json={
                "participants": [
                    {"id": agent["name"], "role": "assistant"}
                    for agent in self.agents
                ],
                "metadata": {"pattern": "collaboration"}
            }
        )
        thread_id = thread_response.json()["threadId"]

        # Initialize with user task
        requests.post(
            f"{API_BASE}/threads/{thread_id}/messages",
            headers=headers,
            json={
                "role": "user",
                "contents": [{"kind": "text", "text": initial_task}]
            }
        )

        collaboration_log = []

        # Agents take turns (round-robin)
        for iteration in range(max_iterations):
            current_agent = self.agents[iteration % len(self.agents)]

            # Agent reads full thread and contributes
            run_response = requests.post(
                f"{API_BASE}/runs",
                headers=headers,
                json={
                    "threadId": thread_id,
                    "agent": current_agent,
                    "input": [],  # Agent reads from thread
                    "store": True
                }
            )

            run_result = run_response.json()

            if run_result["status"] != "completed":
                collaboration_log.append({
                    "iteration": iteration,
                    "agent": current_agent["name"],
                    "status": "failed",
                    "error": run_result.get("error", {}).get("message")
                })
                continue

            contribution = run_result["output"][0]["contents"][0]["text"]

            collaboration_log.append({
                "iteration": iteration,
                "agent": current_agent["name"],
                "contribution": contribution
            })

            # Check for completion signal
            if "COMPLETE" in contribution.upper() or "FINISHED" in contribution.upper():
                break

        # Get final thread state
        thread_response = requests.get(
            f"{API_BASE}/threads/{thread_id}",
            headers=headers
        )
        thread_state = thread_response.json()

        return {
            "threadId": thread_id,
            "collaborationLog": collaboration_log,
            "finalThread": thread_state,
            "totalTurns": len(collaboration_log)
        }


# Example: Collaborative document creation
async def collaborative_writing_example():
    """Multiple agents collaborate on a document."""

    collaboration = SharedContextCollaboration(agents=[
        {
            "kind": "prompt",
            "name": "OutlineAgent",
            "model": "gpt-4o",
            "instructions": """Create document outlines and structure.
            If outline exists, refine it based on other agents' feedback."""
        },
        {
            "kind": "prompt",
            "name": "ContentAgent",
            "model": "gpt-4o",
            "instructions": """Write content based on the outline.
            Expand sections and add details."""
        },
        {
            "kind": "prompt",
            "name": "ReviewAgent",
            "model": "gpt-4o",
            "instructions": """Review content and provide feedback.
            Suggest improvements. Say COMPLETE when satisfied."""
        }
    ])

    result = await collaboration.collaborate(
        initial_task="Create a technical guide for deploying microservices on Kubernetes",
        max_iterations=9  # 3 rounds (3 agents x 3 rounds)
    )

    print(f"Collaboration completed in {result['totalTurns']} turns")

    for entry in result['collaborationLog']:
        print(f"\n[Turn {entry['iteration']}] {entry['agent']}:")
        print(f"  {entry.get('contribution', entry.get('status'))[:200]}...")
```

### Pattern 7: Auto-Response with ThreadWatch

**Use Case**: Agents automatically participate based on thread activity

Configure agents to automatically respond to thread events using AutoResponseConfig and ThreadWatch. This enables reactive, event-driven coordination without explicit orchestration.

**Key Concepts**:

- **AutoResponseConfig**: Agent-level configuration defining when/how to auto-respond
- **RunCondition**: Defines participation triggers (roles, content types, mentions, etc.)
- **ThreadWatch**: Registration of agent to watch specific thread(s)
- **Loop Prevention**: maxConsecutiveRuns prevents infinite agent-to-agent loops

#### Creating Auto-Response Agents

**Implementation:**

```python
class AutoResponseCoordinator:
    """Coordinate agents using auto-response and ThreadWatch."""

    async def create_support_agent(self) -> str:
        """
        Create support agent that auto-responds to user messages.

        Responds to all user messages with maxConsecutiveRuns=1.
        """
        agent_response = requests.post(
            f"{API_BASE}/agents",
            headers=headers,
            json={
                "kind": "prompt",
                "name": "Support Agent",
                "model": "gpt-4o",
                "instructions": """You are a customer support agent.
                Help users with their questions and issues.""",
                "autoResponseConfig": {
                    "runCondition": {
                        "kind": "roles",
                        "roles": ["user"]
                    },
                    "maxConsecutiveRuns": 1,
                    "threadCleanup": "keep"
                }
            }
        )
        return agent_response.json()["agentId"]

    async def create_supervisor_agent(self) -> str:
        """
        Create supervisor agent that responds only when mentioned.

        Requires explicit @mention to participate.
        """
        agent_response = requests.post(
            f"{API_BASE}/agents",
            headers=headers,
            json={
                "kind": "prompt",
                "name": "Support Supervisor",
                "model": "gpt-4o",
                "instructions": """You are a senior support supervisor.
                Provide expert guidance when explicitly mentioned.""",
                "autoResponseConfig": {
                    "runCondition": {
                        "kind": "mention",
                        "requireExplicitMention": True
                    },
                    "maxConsecutiveRuns": 1,
                    "threadCleanup": "keep"
                }
            }
        )
        return agent_response.json()["agentId"]

    async def create_video_analysis_agent(self) -> str:
        """
        Create agent that auto-responds to video content.

        Only participates when video content is uploaded.
        """
        agent_response = requests.post(
            f"{API_BASE}/agents",
            headers=headers,
            json={
                "kind": "prompt",
                "name": "Video Analyzer",
                "model": "gpt-4o",
                "instructions": """You are a video analysis agent.
                Analyze video content and provide insights.""",
                "autoResponseConfig": {
                    "runCondition": {
                        "kind": "content",
                        "contentTypes": ["video"]
                    },
                    "maxConsecutiveRuns": 1,
                    "threadCleanup": "keep"
                }
            }
        )
        return agent_response.json()["agentId"]

    async def create_qa_agent(self, monitored_agent_id: str) -> str:
        """
        Create QA agent that reviews another agent's responses.

        Uses ExpressionCondition to match specific agent's messages.
        """
        agent_response = requests.post(
            f"{API_BASE}/agents",
            headers=headers,
            json={
                "kind": "prompt",
                "name": "Quality Assurance",
                "model": "gpt-4o",
                "instructions": """You review responses for quality and accuracy.
                Provide feedback if improvements needed.""",
                "autoResponseConfig": {
                    "runCondition": {
                        "kind": "expression",
                        "expression": f"message.role == 'assistant' && message.agentId == '{monitored_agent_id}'"
                    },
                    "maxConsecutiveRuns": 1,
                    "threadCleanup": "keep"
                }
            }
        )
        return agent_response.json()["agentId"]


# Example: Register ThreadWatch
async def register_thread_watches(thread_id: str, agent_ids: List[str]):
    """
    Register agents to watch a specific thread.

    Args:
        thread_id: Thread to watch
        agent_ids: List of agent IDs to register as watchers
    """
    watches = []

    for agent_id in agent_ids:
        watch_response = requests.post(
            f"{API_BASE}/threads/{thread_id}/watches",
            headers=headers,
            json={
                "agentId": agent_id,
                "active": True,
                "metadata": {
                    "purpose": "multi-agent coordination",
                    "registeredAt": datetime.now().isoformat()
                }
            }
        )
        watches.append(watch_response.json())

    return watches


# Example: Multi-agent support system
async def multi_agent_support_example():
    """Setup multi-agent support with auto-response."""

    coordinator = AutoResponseCoordinator()

    # Create agents with auto-response
    support_id = await coordinator.create_support_agent()
    supervisor_id = await coordinator.create_supervisor_agent()
    video_id = await coordinator.create_video_analysis_agent()
    qa_id = await coordinator.create_qa_agent(monitored_agent_id=support_id)

    print(f"Created support agent: {support_id}")
    print(f"Created supervisor: {supervisor_id}")
    print(f"Created video analyzer: {video_id}")
    print(f"Created QA agent: {qa_id}")

    # Create thread
    thread_response = requests.post(
        f"{API_BASE}/threads",
        headers=headers,
        json={
            "participants": [{"id": "user", "role": "user"}],
            "metadata": {"type": "customer_support"}
        }
    )
    thread_id = thread_response.json()["threadId"]

    # Register all agents to watch the thread
    watches = await register_thread_watches(
        thread_id,
        [support_id, supervisor_id, video_id, qa_id]
    )

    print(f"\nRegistered {len(watches)} thread watches")

    # Now agents will automatically respond based on their conditions:
    # - Support agent: responds to all user messages
    # - Supervisor: responds only when @mentioned
    # - Video analyzer: responds only to video uploads
    # - QA agent: reviews support agent's responses

    return {
        "threadId": thread_id,
        "agentIds": {
            "support": support_id,
            "supervisor": supervisor_id,
            "video": video_id,
            "qa": qa_id
        },
        "watches": watches
    }
```

#### Multi-Agent Coordination Patterns

**1. Tiered Support with Auto-Response**:

```python
async def tiered_support_example():
    """
    Tier 1 (user messages) → Tier 2 (on mention) → Supervisor (on mention)
    """

    # Tier 1: Always responds to users
    tier1_agent = {
        "kind": "prompt",
        "name": "Tier 1 Support",
        "model": "gpt-4o",
        "instructions": "Handle basic customer inquiries. Mention @Tier2 for complex issues.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "roles",
                "roles": ["user"]
            },
            "maxConsecutiveRuns": 1
        }
    }

    # Tier 2: Responds when mentioned
    tier2_agent = {
        "kind": "prompt",
        "name": "Tier 2 Support",
        "model": "gpt-4o",
        "instructions": "Handle complex issues. Mention @Supervisor for escalation.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "mention",
                "requireExplicitMention": True
            },
            "maxConsecutiveRuns": 1
        }
    }

    # Supervisor: Responds when mentioned
    supervisor_agent = {
        "kind": "prompt",
        "name": "Supervisor",
        "model": "gpt-4o",
        "instructions": "Handle escalated issues and provide expert guidance.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "mention",
                "requireExplicitMention": True
            },
            "maxConsecutiveRuns": 1
        }
    }
```

**2. Content-Based Routing**:

```python
async def content_routing_example():
    """
    Different agents handle different content types automatically.
    """

    # Text specialist
    text_agent = {
        "kind": "prompt",
        "name": "Text Specialist",
        "model": "gpt-4o",
        "instructions": "Process text inquiries.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "roles",
                "roles": ["user"]
            },
            "maxConsecutiveRuns": 1
        }
    }

    # Image analyst
    image_agent = {
        "kind": "prompt",
        "name": "Image Analyst",
        "model": "gpt-4o",
        "instructions": "Analyze images and provide insights.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "content",
                "contentTypes": ["image"]
            },
            "maxConsecutiveRuns": 1
        }
    }

    # Video analyst
    video_agent = {
        "kind": "prompt",
        "name": "Video Analyst",
        "model": "gpt-4o",
        "instructions": "Analyze videos and provide insights.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "content",
                "contentTypes": ["video"]
            },
            "maxConsecutiveRuns": 1
        }
    }
```

**3. Observer Pattern with QA**:

```python
async def observer_qa_example():
    """
    QA agent observes primary agent's responses using ExpressionCondition.
    """

    # Primary agent
    primary_agent_response = requests.post(
        f"{API_BASE}/agents",
        headers=headers,
        json={
            "kind": "prompt",
            "name": "Primary Agent",
            "model": "gpt-4o",
            "instructions": "Handle customer requests.",
            "autoResponseConfig": {
                "runCondition": {
                    "kind": "roles",
                    "roles": ["user"]
                },
                "maxConsecutiveRuns": 1
            }
        }
    )
    primary_id = primary_agent_response.json()["agentId"]

    # QA agent that watches primary agent
    qa_agent = {
        "kind": "prompt",
        "name": "QA Observer",
        "model": "gpt-4o",
        "instructions": "Review responses for quality. Provide private feedback if needed.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "expression",
                "expression": f"message.role == 'assistant' && message.agentId == '{primary_id}'"
            },
            "maxConsecutiveRuns": 1
        }
    }
```

**4. Loop Prevention Example**:

```python
async def loop_prevention_example():
    """
    Demonstrate maxConsecutiveRuns to prevent infinite loops.
    """

    # Agent A: Can respond twice in a row
    agent_a = {
        "kind": "prompt",
        "name": "Agent A",
        "model": "gpt-4o",
        "instructions": "First responder. Can hand off to Agent B.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "roles",
                "roles": ["user", "assistant"]
            },
            "maxConsecutiveRuns": 2  # Can run twice, then needs user message
        }
    }

    # Agent B: Can respond once
    agent_b = {
        "kind": "prompt",
        "name": "Agent B",
        "model": "gpt-4o",
        "instructions": "Second responder. Provide additional context.",
        "autoResponseConfig": {
            "runCondition": {
                "kind": "roles",
                "roles": ["assistant"]
            },
            "maxConsecutiveRuns": 1  # Runs once, then needs user message
        }
    }

    # Flow: User → Agent A → Agent B → [STOP - wait for user]
    # Counter resets when user sends another message
```

#### Managing ThreadWatch

**Activate/Deactivate Watches**:

```python
async def manage_thread_watch(watch_id: str, active: bool):
    """
    Toggle thread watch activation without deleting it.
    """
    response = requests.patch(
        f"{API_BASE}/watches/{watch_id}",
        headers=headers,
        json={"active": active}
    )
    return response.json()


async def get_thread_watches(thread_id: str):
    """
    List all agents watching a thread.
    """
    response = requests.get(
        f"{API_BASE}/threads/{thread_id}/watches",
        headers=headers
    )
    return response.json()


async def remove_thread_watch(watch_id: str):
    """
    Remove agent from watching thread.
    """
    response = requests.delete(
        f"{API_BASE}/watches/{watch_id}",
        headers=headers
    )
    return response.status_code == 204
```

#### Use Cases for Auto-Response Coordination

**1. Customer Support Tiers**:
- Tier 1 auto-responds to all user messages
- Tier 2 responds when mentioned by Tier 1
- Supervisor responds when mentioned for escalation

**2. Content Moderation**:
- Moderation agent watches all threads
- Auto-responds to inappropriate content
- Uses ExpressionCondition for keyword detection

**3. Specialized Expertise**:
- Image agent responds to image uploads
- Video agent responds to video uploads
- Document agent responds to document uploads

**4. Quality Assurance**:
- QA agent observes primary agent's responses
- Provides feedback on quality issues
- Uses ExpressionCondition to filter by agentId

**5. Multi-Language Support**:
- Language detection agent responds first
- Routes to language-specific agents
- Uses RemoteCondition for language detection

#### Comparison: Orchestration vs Auto-Response

| Pattern | Orchestration (Patterns 1-6) | Auto-Response (Pattern 7) |
|---------|------------------------------|---------------------------|
| **Control** | Explicit run creation | Automatic run creation |
| **Coordination** | Orchestrator code required | Configuration-based |
| **Scalability** | Manual scaling | Automatic scaling |
| **Use Case** | Deterministic workflows | Reactive, event-driven |
| **Complexity** | More orchestration code | Less orchestration code |
| **Thread Scope** | Single or multiple threads | Single thread per watch |

**When to Use Auto-Response**:
- Reactive agent participation
- Event-driven workflows
- Monitoring and supervision
- Content-based routing
- Always-on support agents

**When to Use Orchestration**:
- Deterministic sequences
- Complex state management
- Explicit control flow
- Custom coordination logic
- Multi-thread coordination

---

## Examples

### Complex Scenario 1: Customer Service End-to-End

Combining multiple patterns for a realistic customer service system.

```python
class CustomerServiceOrchestrator:
    """
    Complete customer service system:
    - Triage routes to specialists
    - Specialists can delegate cross-functionally
    - Manager escalation for complex cases
    - Consensus for refund approvals
    """

    async def handle_customer_request(self, request: str) -> Dict:
        # 1. Triage
        triage_result = await self.triage(request)

        # 2. Specialist handles request
        if triage_result["specialist"] == "refunds":
            # Refunds require approval consensus
            specialist_result = await self.handle_refund_with_approval(request)
        else:
            specialist_result = await self.handle_with_specialist(
                triage_result["specialist"],
                request
            )

        # 3. Escalate to manager if needed
        if specialist_result.get("needsEscalation"):
            manager_result = await self.escalate_to_manager(
                request,
                specialist_result
            )
            return manager_result

        return specialist_result
```

### Complex Scenario 2: Multi-Stage Content Pipeline

Research → Draft → Review → Publish with parallel research phase.

```python
class ContentProductionPipeline:
    """
    Complete content production workflow:
    - Parallel research from multiple sources
    - Sequential writing, editing, formatting
    - Consensus-based approval
    - Automated publishing
    """

    async def produce_content(self, topic: str) -> Dict:
        # Phase 1: Parallel research
        research_results = await self.parallel_research(topic)

        # Phase 2: Sequential content creation
        pipeline_result = await self.content_pipeline(research_results)

        # Phase 3: Approval consensus
        approval_result = await self.approval_consensus(
            pipeline_result["finalContent"]
        )

        # Phase 4: Publish if approved
        if approval_result["approved"]:
            publish_result = await self.publish_content(
                pipeline_result["finalContent"]
            )
            return publish_result
        else:
            return {
                "status": "rejected",
                "feedback": approval_result["feedback"]
            }
```

## Troubleshooting

### Managing Concurrent Runs

**Problem**: Multiple runs on same thread cause conflicts

**Solution**: Use run queuing or thread locking

```python
class ThreadLockManager:
    """Prevent concurrent runs on same thread."""

    def __init__(self):
        self.active_runs = {}  # threadId -> runId
        self.lock = asyncio.Lock()

    async def execute_with_lock(
        self,
        thread_id: str,
        agent_config: Dict,
        input_messages: List[Dict]
    ) -> Dict:
        """Execute run with thread-level locking."""
        async with self.lock:
            # Check if thread has active run
            if thread_id in self.active_runs:
                raise Exception(
                    f"Thread {thread_id} has active run: "
                    f"{self.active_runs[thread_id]}"
                )

            # Start run
            run_response = requests.post(
                f"{API_BASE}/runs",
                headers=headers,
                json={
                    "threadId": thread_id,
                    "agent": agent_config,
                    "input": input_messages,
                    "store": True
                }
            )
            run_result = run_response.json()

            # Track active run
            self.active_runs[thread_id] = run_result["runId"]

        try:
            # Wait for completion (poll or stream)
            final_result = await self.wait_for_completion(
                run_result["runId"]
            )
            return final_result
        finally:
            # Release lock
            async with self.lock:
                if thread_id in self.active_runs:
                    del self.active_runs[thread_id]
```

### Handling Agent Failures

**Problem**: One agent failure breaks entire pipeline

**Solution**: Graceful degradation and retry logic

```python
class ResilientPipeline:
    """Pipeline with retry and fallback handling."""

    async def run_with_retry(
        self,
        agent_config: Dict,
        input_text: str,
        max_retries: int = 3,
        fallback_agent: Dict = None
    ) -> Dict:
        """Execute agent with retry and fallback."""
        last_error = None

        for attempt in range(max_retries):
            try:
                result = await self.execute_agent(agent_config, input_text)

                if result["status"] == "completed":
                    return result

                last_error = result.get("error", {}).get("message")

            except Exception as e:
                last_error = str(e)

            # Exponential backoff
            await asyncio.sleep(2 ** attempt)

        # Try fallback agent
        if fallback_agent:
            try:
                return await self.execute_agent(fallback_agent, input_text)
            except Exception as e:
                last_error = f"Fallback also failed: {e}"

        raise Exception(
            f"Agent failed after {max_retries} retries. "
            f"Last error: {last_error}"
        )
```

### Token Limit Management

**Problem**: Long multi-agent conversations exceed context limits

**Solution**: Summarization and context pruning

```python
class ContextManager:
    """Manage context window for long conversations."""

    async def summarize_thread(
        self,
        thread_id: str,
        summarizer_agent: Dict
    ) -> str:
        """Summarize thread history."""
        # Get thread messages
        thread = requests.get(
            f"{API_BASE}/threads/{thread_id}",
            headers=headers
        ).json()

        # Combine messages
        history = "\n\n".join([
            f"{msg['role']}: {msg['contents'][0]['text']}"
            for msg in thread["messages"]
        ])

        # Summarize
        summary_run = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "agent": summarizer_agent,
                "input": [{
                    "role": "user",
                    "contents": [{
                        "kind": "text",
                        "text": f"Summarize this conversation:\n\n{history}"
                    }]
                }],
                "store": False
            }
        ).json()

        return summary_run["output"][0]["contents"][0]["text"]

    async def prune_thread(
        self,
        thread_id: str,
        max_messages: int = 20
    ):
        """Keep only recent messages, summarize old ones."""
        thread = requests.get(
            f"{API_BASE}/threads/{thread_id}",
            headers=headers
        ).json()

        if len(thread["messages"]) <= max_messages:
            return  # No pruning needed

        # Summarize old messages
        old_messages = thread["messages"][:-max_messages]
        summary = await self.summarize_thread_subset(old_messages)

        # Keep recent + summary
        # (Implementation depends on API support for message deletion)
```

### Debugging Multi-Agent Flows

**Problem**: Hard to trace errors across multiple agents

**Solution**: Comprehensive logging and tracing

```python
import logging
from typing import Optional
from datetime import datetime
import json

class AgentTracer:
    """Trace agent execution for debugging."""

    def __init__(self):
        self.logger = logging.getLogger("agent_tracer")
        self.traces = []

    def trace_run(
        self,
        agent_name: str,
        run_id: str,
        thread_id: Optional[str],
        status: str,
        input_preview: str,
        output_preview: str,
        error: Optional[str] = None
    ):
        """Record run trace."""
        trace = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "runId": run_id,
            "threadId": thread_id,
            "status": status,
            "inputPreview": input_preview[:100],
            "outputPreview": output_preview[:100] if output_preview else None,
            "error": error
        }

        self.traces.append(trace)
        self.logger.info(f"[{agent_name}] {status}: {run_id}")

        if error:
            self.logger.error(f"[{agent_name}] Error: {error}")

    def export_traces(self, format: str = "json") -> str:
        """Export traces for analysis."""
        if format == "json":
            return json.dumps(self.traces, indent=2)
        elif format == "markdown":
            md = "# Agent Execution Trace\n\n"
            for trace in self.traces:
                md += f"## {trace['timestamp']} - {trace['agent']}\n"
                md += f"- Status: {trace['status']}\n"
                md += f"- Run ID: {trace['runId']}\n"
                if trace['error']:
                    md += f"- Error: {trace['error']}\n"
                md += "\n"
            return md
```

### Preventing Auto-Response Loops

**Problem**: Agents with auto-response create infinite loops

**Solution**: Use maxConsecutiveRuns and proper conditions

```python
# INCORRECT: Can create infinite loops
bad_agent_a = {
    "autoResponseConfig": {
        "runCondition": {
            "kind": "always"  # Always responds!
        },
        "maxConsecutiveRuns": 0  # Unlimited runs!
    }
}

# CORRECT: Loop prevention
good_agent_a = {
    "autoResponseConfig": {
        "runCondition": {
            "kind": "roles",
            "roles": ["user"]  # Only respond to users
        },
        "maxConsecutiveRuns": 1  # Stop after one run
    }
}

good_agent_b = {
    "autoResponseConfig": {
        "runCondition": {
            "kind": "mention",
            "requireExplicitMention": True  # Only when mentioned
        },
        "maxConsecutiveRuns": 1
    }
}
```

## Best Practices

### 1. Design Patterns Selection

- **Sequential**: When each step depends on previous output
- **Parallel**: When agents can work independently
- **Handoff**: When specialized expertise needed at different stages
- **Hierarchical**: When coordination and synthesis required
- **Consensus**: When multiple perspectives needed for decisions
- **Auto-Response**: When reactive, event-driven behavior needed

### 2. Error Handling

- Always implement retry logic with exponential backoff
- Use fallback agents for critical paths
- Log all agent interactions for debugging
- Validate agent outputs before passing to next stage
- Handle partial failures gracefully in parallel execution

### 3. Performance Optimization

- Run independent agents in parallel
- Use streaming for real-time feedback
- Implement caching for repeated queries
- Monitor token usage and costs
- Use ThreadWatch for reactive patterns instead of polling

### 4. State Management

- Use threads for conversation continuity
- Store metadata for tracking agent progression
- Implement checkpointing for long workflows
- Clean up old threads to manage storage
- Use ThreadWatch for cross-thread coordination

### 5. Auto-Response Configuration

- Always set maxConsecutiveRuns to prevent loops (default: 1)
- Use specific RunConditions (avoid AlwaysCondition)
- Test auto-response behavior before production
- Monitor activationCount on ThreadWatch
- Use active flag to temporarily disable watches

### 6. Testing Multi-Agent Systems

- Test each agent independently first
- Test pairwise handoffs before full pipeline
- Use mock agents for integration testing
- Monitor for infinite loops in handoff chains
- Test auto-response activation/deactivation
- Verify maxConsecutiveRuns prevents loops

## Related Documentation

- **TypeSpec Reference**: `/typespec/execution.tsp` - Run, Thread, and ThreadWatch models
- **TypeSpec Reference**: `/typespec/agents.tsp` - AgentCard, AgentDefinition, and AutoResponseConfig
- **TypeSpec Reference**: `/typespec/conditions.tsp` - RunCondition types
- **Getting Started Guide**: `/guides/getting-started.md` - Basic API usage
- **API Reference**: `/api-reference/models/threadwatch.md` - ThreadWatch API details
- **API Reference**: `/api-reference/models/expressioncondition.md` - Expression syntax
