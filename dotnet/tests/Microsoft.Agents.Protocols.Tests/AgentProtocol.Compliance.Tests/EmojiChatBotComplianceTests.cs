extern alias EmojiChatBot;

using System.Threading.Tasks;
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

namespace Microsoft.Agents.Protocol.Tests.Compliance;

/// <summary>
/// Agent Protocol compliance tests for EmojiChatBot sample.
/// </summary>
public class EmojiChatBotComplianceTests : AgentProtocolComplianceTestsBase, IClassFixture<WebApplicationFactory<EmojiChatBot::Program>>
{
    public EmojiChatBotComplianceTests(WebApplicationFactory<EmojiChatBot::Program> factory)
        : base(factory.CreateClient(), "emoji-agent")
    {
    }

    [Fact]
    public async Task EmojiChatBot_ProducesValidXml()
    {
        await AssertAgentProducesValidXml();
    }

    [Fact]
    public async Task EmojiChatBot_SupportsJsonFormat()
    {
        await AssertAgentSupportsJsonFormat();
    }
}
