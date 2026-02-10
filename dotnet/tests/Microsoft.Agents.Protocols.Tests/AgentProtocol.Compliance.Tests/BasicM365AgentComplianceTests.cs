extern alias BasicM365Agent;

using System.Threading.Tasks;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Microsoft.Agents.Protocol.Tests.Compliance;

/// <summary>
/// Agent Protocol compliance tests for BasicM365Agent sample.
/// </summary>
public class BasicM365AgentComplianceTests : AgentProtocolComplianceTestsBase, IClassFixture<WebApplicationFactory<BasicM365Agent::Program>>
{
    public BasicM365AgentComplianceTests(WebApplicationFactory<BasicM365Agent::Program> factory)
        : base(factory.CreateClient(), "basic-agent")
    {
    }

    [Fact]
    public async Task BasicM365Agent_ProducesValidXml()
    {
        await AssertAgentProducesValidXml();
    }

    [Fact]
    public async Task BasicM365Agent_SupportsJsonFormat()
    {
        await AssertAgentSupportsJsonFormat();
    }
}
