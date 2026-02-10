using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Core;

namespace Microsoft.Agents.Protocol.Hosting.Examples;

/// <summary>
/// Simple echo agent example (Level 1 - 5 lines of code).
/// Demonstrates the minimal API surface.
/// </summary>
public class EchoAgent : AgentProtocolApplication<EmptyContext>
{
    public EchoAgent(AgentProtocolOptions options) : base(options)
    {
        // This is all you need for a basic echo agent!
        OnUserMessage((context, message, ct) =>
            context.SendTextAsync($"You said: {((UserMessage)message).Text}", ct));
    }
}

/// <summary>
/// Empty context for agents that don't need custom state
/// </summary>
public class EmptyContext
{
}
