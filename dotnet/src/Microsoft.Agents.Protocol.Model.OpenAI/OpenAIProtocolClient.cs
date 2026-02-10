using Microsoft.Agents;
using Microsoft.Agents.Protocol.Model;
using OpenAI;
using OpenAI.Chat;
using System.Runtime.CompilerServices;
using System.Text.Json;
using OpenAIChatMessage = OpenAI.Chat.ChatMessage;
using ProtocolChatMessage = Microsoft.Agents.ChatMessage;

namespace Microsoft.Agents.Protocol.Model.OpenAI;

/// <summary>
/// OpenAI implementation of IProtocolLLMClient that returns Agent Protocol types directly.
/// </summary>
public class OpenAIProtocolClient : IProtocolLLMClient
{
    private readonly ChatClient _client;
    private readonly string _model;
    private readonly OpenAIProtocolClientOptions _options;

    /// <summary>
    /// Creates a new OpenAI protocol client.
    /// </summary>
    /// <param name="apiKey">OpenAI API key</param>
    /// <param name="model">Model identifier (default: gpt-4o)</param>
    /// <param name="options">Optional client configuration</param>
    public OpenAIProtocolClient(
        string apiKey,
        string model = "gpt-4o",
        OpenAIProtocolClientOptions? options = null)
    {
        ArgumentNullException.ThrowIfNull(apiKey);
        ArgumentNullException.ThrowIfNull(model);

        _model = model;
        _options = options ?? new OpenAIProtocolClientOptions();

        var openAIClient = new OpenAIClient(apiKey);
        _client = openAIClient.GetChatClient(_model);
    }

    /// <summary>
    /// Creates a new OpenAI protocol client with custom base URL (for Azure, Foundry, etc.).
    /// </summary>
    /// <param name="apiKey">API key</param>
    /// <param name="baseUrl">Custom base URL</param>
    /// <param name="model">Model identifier</param>
    /// <param name="options">Optional client configuration</param>
    public OpenAIProtocolClient(
        string apiKey,
        Uri baseUrl,
        string model,
        OpenAIProtocolClientOptions? options = null)
    {
        ArgumentNullException.ThrowIfNull(apiKey);
        ArgumentNullException.ThrowIfNull(baseUrl);
        ArgumentNullException.ThrowIfNull(model);

        _model = model;
        _options = options ?? new OpenAIProtocolClientOptions();

        var openAIClient = new OpenAIClient(new System.ClientModel.ApiKeyCredential(apiKey), new OpenAIClientOptions
        {
            Endpoint = baseUrl
        });
        _client = openAIClient.GetChatClient(_model);
    }

    public LLMProviderInfo ProviderInfo => new()
    {
        Provider = "OpenAI",
        Model = _model,
        SupportsStreaming = true,
        SupportsFunctionCalling = true,
        SupportsVision = _model.Contains("vision") || _model.Contains("4o") || _model.Contains("gpt-4"),
        SupportsMultimodal = _model.Contains("4o")
    };

    public async Task<AgentMessage> GenerateAsync(
        List<ProtocolChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default)
    {
        var openAIMessages = ConvertToOpenAIMessages(conversationHistory);
        var openAITools = ConvertToOpenAITools(availableTools);

        var chatOptions = new ChatCompletionOptions();

        if (openAITools != null && openAITools.Count > 0)
        {
            foreach (var tool in openAITools)
            {
                chatOptions.Tools.Add(tool);
            }
        }

        chatOptions.Temperature = (float)_options.Temperature;

        if (_options.MaxTokens.HasValue)
        {
            chatOptions.MaxOutputTokenCount = _options.MaxTokens.Value;
        }

        if (_options.TopP.HasValue)
        {
            chatOptions.TopP = (float)_options.TopP.Value;
        }

        if (_options.FrequencyPenalty.HasValue)
        {
            chatOptions.FrequencyPenalty = (float)_options.FrequencyPenalty.Value;
        }

        if (_options.PresencePenalty.HasValue)
        {
            chatOptions.PresencePenalty = (float)_options.PresencePenalty.Value;
        }

        var completion = await _client.CompleteChatAsync(openAIMessages, chatOptions, cancellationToken);

        return ConvertToAgentMessage(completion.Value);
    }

    public async IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        List<ProtocolChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var openAIMessages = ConvertToOpenAIMessages(conversationHistory);
        var openAITools = ConvertToOpenAITools(availableTools);

        var chatOptions = new ChatCompletionOptions();

        if (openAITools != null && openAITools.Count > 0)
        {
            foreach (var tool in openAITools)
            {
                chatOptions.Tools.Add(tool);
            }
        }

        chatOptions.Temperature = (float)_options.Temperature;

        if (_options.MaxTokens.HasValue)
        {
            chatOptions.MaxOutputTokenCount = _options.MaxTokens.Value;
        }

        if (_options.TopP.HasValue)
        {
            chatOptions.TopP = (float)_options.TopP.Value;
        }

        var streamingUpdates = _client.CompleteChatStreamingAsync(openAIMessages, chatOptions, cancellationToken);

        var messageId = $"msg_{Guid.NewGuid():N}";
        var textBuffer = "";
        var toolCallBuffers = new Dictionary<int, ToolCallBuilder>();

        await foreach (var update in streamingUpdates.ConfigureAwait(false))
        {
            cancellationToken.ThrowIfCancellationRequested();

            // Start of message
            if (update.Role.HasValue)
            {
                yield return new AgentMessageDelta
                {
                    MessageId = messageId,
                    Type = DeltaType.MessageStart
                };
            }

            // Text content
            foreach (var contentPart in update.ContentUpdate)
            {
                if (contentPart.Text != null)
                {
                    textBuffer += contentPart.Text;

                    yield return new AgentMessageDelta
                    {
                        MessageId = messageId,
                        Type = DeltaType.TextDelta,
                        Content = new TextContent { Text = textBuffer }
                    };
                }
            }

            // Tool calls
            foreach (var toolCallUpdate in update.ToolCallUpdates)
            {
                var index = toolCallUpdate.Index;

                if (!toolCallBuffers.ContainsKey(index))
                {
                    toolCallBuffers[index] = new ToolCallBuilder
                    {
                        CallId = toolCallUpdate.ToolCallId ?? $"call_{Guid.NewGuid():N}",
                        FunctionName = toolCallUpdate.FunctionName ?? ""
                    };

                    yield return new AgentMessageDelta
                    {
                        MessageId = messageId,
                        Type = DeltaType.ToolCallStart,
                        ToolCall = new FunctionCallContent
                        {
                            CallId = toolCallBuffers[index].CallId,
                            Name = toolCallBuffers[index].FunctionName
                        }
                    };
                }

                if (toolCallUpdate.FunctionArgumentsUpdate.ToMemory().Length > 0)
                {
                    toolCallBuffers[index].ArgumentsBuffer += toolCallUpdate.FunctionArgumentsUpdate.ToString();

                    yield return new AgentMessageDelta
                    {
                        MessageId = messageId,
                        Type = DeltaType.ToolCallDelta,
                        ToolCall = new FunctionCallContent
                        {
                            CallId = toolCallBuffers[index].CallId,
                            Name = toolCallBuffers[index].FunctionName,
                            Arguments = toolCallBuffers[index].ArgumentsBuffer
                        }
                    };
                }
            }

            // End of message
            if (update.FinishReason.HasValue)
            {
                // Complete any pending tool calls
                foreach (var builder in toolCallBuffers.Values)
                {
                    yield return new AgentMessageDelta
                    {
                        MessageId = messageId,
                        Type = DeltaType.ToolCallComplete,
                        ToolCall = new FunctionCallContent
                        {
                            CallId = builder.CallId,
                            Name = builder.FunctionName,
                            Arguments = builder.ArgumentsBuffer
                        }
                    };
                }

                yield return new AgentMessageDelta
                {
                    MessageId = messageId,
                    Type = DeltaType.MessageComplete,
                    IsComplete = true
                };
            }
        }
    }

    private AgentMessage ConvertToAgentMessage(ChatCompletion openAICompletion)
    {
        var contents = new List<AIContent>();
        var assistantMessage = openAICompletion.Content;

        // Text content
        foreach (var contentPart in assistantMessage)
        {
            if (contentPart.Text != null)
            {
                contents.Add(new TextContent { Text = contentPart.Text });
            }
        }

        // Function/tool calls
        foreach (var toolCall in openAICompletion.ToolCalls)
        {
            contents.Add(new FunctionCallContent
            {
                CallId = toolCall.Id,
                Name = toolCall.FunctionName,
                Arguments = toolCall.FunctionArguments.ToString()
            });
        }

        return new AgentMessage
        {
            MessageId = $"msg_{openAICompletion.Id ?? Guid.NewGuid().ToString("N")}",
            Contents = contents
        };
    }

    private List<OpenAIChatMessage> ConvertToOpenAIMessages(List<ProtocolChatMessage> protocolMessages)
    {
        var openAIMessages = new List<OpenAIChatMessage>();

        foreach (var msg in protocolMessages)
        {
            switch (msg)
            {
                case SystemMessage system:
                    var systemText = system.Contents.OfType<TextContent>().FirstOrDefault()?.Text;
                    if (systemText != null)
                    {
                        openAIMessages.Add(new SystemChatMessage(systemText));
                    }
                    break;

                case UserMessage user:
                    var userContents = new List<ChatMessageContentPart>();
                    foreach (var content in user.Contents)
                    {
                        if (content is TextContent textContent)
                        {
                            userContents.Add(ChatMessageContentPart.CreateTextPart(textContent.Text));
                        }
                        else if (content is ImageContent imageContent)
                        {
                            // Support image URLs
                            if (!string.IsNullOrEmpty(imageContent.Uri))
                            {
                                userContents.Add(ChatMessageContentPart.CreateImagePart(new Uri(imageContent.Uri)));
                            }
                        }
                    }

                    if (userContents.Count == 1 && userContents[0].Kind == ChatMessageContentPartKind.Text)
                    {
                        openAIMessages.Add(new UserChatMessage(userContents[0].Text));
                    }
                    else if (userContents.Count > 0)
                    {
                        openAIMessages.Add(new UserChatMessage(userContents));
                    }
                    break;

                case AgentMessage agent:
                    var textParts = agent.Contents.OfType<TextContent>().ToList();
                    var toolCalls = agent.Contents.OfType<FunctionCallContent>().ToList();

                    if (toolCalls.Any())
                    {
                        var assistantMessage = new AssistantChatMessage(
                            toolCalls.Select(tc => ChatToolCall.CreateFunctionToolCall(
                                tc.CallId ?? $"call_{Guid.NewGuid():N}",
                                tc.Name ?? "",
                                BinaryData.FromString(tc.Arguments ?? "{}")
                            )).ToList()
                        );

                        if (textParts.Any())
                        {
                            assistantMessage.Content.Add(ChatMessageContentPart.CreateTextPart(
                                string.Join(" ", textParts.Select(t => t.Text))
                            ));
                        }

                        openAIMessages.Add(assistantMessage);
                    }
                    else if (textParts.Any())
                    {
                        openAIMessages.Add(new AssistantChatMessage(
                            string.Join(" ", textParts.Select(t => t.Text))
                        ));
                    }
                    break;

                case ToolMessage tool:
                    foreach (var content in tool.Contents.OfType<FunctionResultContent>())
                    {
                        openAIMessages.Add(new ToolChatMessage(
                            content.CallId ?? $"call_{Guid.NewGuid():N}",
                            content.Result ?? ""
                        ));
                    }
                    break;
            }
        }

        return openAIMessages;
    }

    private List<ChatTool>? ConvertToOpenAITools(ToolDefinition[]? protocolTools)
    {
        if (protocolTools == null || protocolTools.Length == 0)
        {
            return null;
        }

        var tools = new List<ChatTool>();

        foreach (var tool in protocolTools)
        {
            if (tool.Function == null) continue;

            var parametersJson = tool.Function.Parameters.HasValue
                ? BinaryData.FromString(tool.Function.Parameters.Value.GetRawText())
                : BinaryData.FromString("{}");

            tools.Add(ChatTool.CreateFunctionTool(
                tool.Function.Name,
                tool.Function.Description,
                parametersJson
            ));
        }

        return tools;
    }

    private class ToolCallBuilder
    {
        public string CallId { get; set; } = "";
        public string FunctionName { get; set; } = "";
        public string ArgumentsBuffer { get; set; } = "";
    }
}
