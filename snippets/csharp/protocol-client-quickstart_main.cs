using Microsoft.Agents.Protocol;
using Microsoft.Agents.Protocol.Models.Execution;
using System.Collections.Generic;
using System.Threading.Tasks;

// Create a client
var client = new AgentProtocolClient("https://agents.example.com/v1");

// Create and execute a run
var run = new Run
{
    AgentId = "agent_001",
    Input = new List<object>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<AIContentBase>
            {
                new TextContent { Text = "Hello! Can you help me?" }
            }
        }
    }
};

// Wait for completion
var result = await client.Runs.CreateAndWaitAsync(run);

Console.WriteLine($"Status: {result.Status}");
Console.WriteLine($"Messages: {result.Messages.Count}");
