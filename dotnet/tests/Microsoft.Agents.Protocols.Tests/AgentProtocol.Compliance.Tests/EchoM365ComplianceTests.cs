extern alias EchoM365;

using System.Threading.Tasks;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Microsoft.Agents.Protocol.Tests.Compliance;

/// <summary>
/// Agent Protocol compliance tests for EchoM365 sample.
/// </summary>
public class EchoM365ComplianceTests : AgentProtocolComplianceTestsBase, IClassFixture<WebApplicationFactory<EchoM365::Program>>
{
    public EchoM365ComplianceTests(WebApplicationFactory<EchoM365::Program> factory)
        : base(factory.CreateClient(), "echo-agent")
    {
    }

    [Fact]
    public async Task EchoM365_ProducesValidXml()
    {
        await AssertAgentProducesValidXml();
    }

    [Fact]
    public async Task EchoM365_SupportsJsonFormat()
    {
        await AssertAgentSupportsJsonFormat();
    }
}
