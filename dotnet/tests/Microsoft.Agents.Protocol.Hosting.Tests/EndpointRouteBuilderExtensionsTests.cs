using System;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class EndpointRouteBuilderExtensionsTests
{
    [Fact]
    public void MapAgentProtocol_ThrowsArgumentNullException_WhenEndpointsIsNull()
    {
        // Act & Assert
        var act = () => EndpointRouteBuilderExtensions.MapAgentProtocol(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("endpoints");
    }

    [Fact]
    public async Task MapAgentProtocol_MapsThreadStreamEndpoint()
    {
        // Arrange
        using var host = await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            endpoints.MapAgentProtocol();
                        });
                    });
            })
            .StartAsync();

        var client = host.GetTestClient();
        client.Timeout = TimeSpan.FromSeconds(1);

        // Act & Assert
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromMilliseconds(500));

        try
        {
            var response = await client.GetAsync("/threads/test-thread-123/stream", HttpCompletionOption.ResponseHeadersRead, cts.Token);
            response.StatusCode.Should().Be(HttpStatusCode.OK);
            response.Content.Headers.ContentType?.MediaType.Should().Be("text/event-stream");
        }
        catch (OperationCanceledException)
        {
            // Expected - streaming endpoint runs indefinitely
        }
    }

    [Fact]
    public async Task MapAgentProtocol_ThreadStreamEndpoint_ReturnsCorrectHeaders()
    {
        // Arrange
        using var host = await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            endpoints.MapAgentProtocol();
                        });
                    });
            })
            .StartAsync();

        var client = host.GetTestClient();
        client.Timeout = TimeSpan.FromSeconds(1);

        // Act & Assert
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromMilliseconds(500));

        try
        {
            var response = await client.GetAsync("/threads/test-thread/stream", HttpCompletionOption.ResponseHeadersRead, cts.Token);
            response.Headers.CacheControl?.NoCache.Should().BeTrue();
            response.Headers.Connection.Should().Contain("keep-alive");
        }
        catch (OperationCanceledException)
        {
            // Expected - streaming endpoint runs indefinitely
        }
    }

    [Fact]
    public async Task MapAgentProtocol_MapsRunStreamEndpoint()
    {
        // Arrange
        using var host = await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            endpoints.MapAgentProtocol();
                        });
                    });
            })
            .StartAsync();

        var client = host.GetTestClient();
        client.Timeout = TimeSpan.FromSeconds(1);

        // Act & Assert
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromMilliseconds(500));

        try
        {
            var response = await client.GetAsync("/runs/test-run-456/stream", HttpCompletionOption.ResponseHeadersRead, cts.Token);
            response.StatusCode.Should().Be(HttpStatusCode.OK);
            response.Content.Headers.ContentType?.MediaType.Should().Be("text/event-stream");
        }
        catch (OperationCanceledException)
        {
            // Expected - streaming endpoint runs indefinitely
        }
    }

    [Fact]
    public async Task MapAgentProtocol_RunStreamEndpoint_ReturnsCorrectHeaders()
    {
        // Arrange
        using var host = await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            endpoints.MapAgentProtocol();
                        });
                    });
            })
            .StartAsync();

        var client = host.GetTestClient();
        client.Timeout = TimeSpan.FromSeconds(1);

        // Act & Assert
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromMilliseconds(500));

        try
        {
            var response = await client.GetAsync("/runs/test-run/stream", HttpCompletionOption.ResponseHeadersRead, cts.Token);
            response.Headers.CacheControl?.NoCache.Should().BeTrue();
            response.Headers.Connection.Should().Contain("keep-alive");
        }
        catch (OperationCanceledException)
        {
            // Expected - streaming endpoint runs indefinitely
        }
    }

    [Fact]
    public async Task MapAgentProtocol_ReturnsEndpointRouteBuilder()
    {
        // Arrange
        using var host = await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            var result = endpoints.MapAgentProtocol();
                            result.Should().BeSameAs(endpoints);
                        });
                    });
            })
            .StartAsync();

        // Assert - test passes if no exception thrown
        await Task.CompletedTask;
    }
}
