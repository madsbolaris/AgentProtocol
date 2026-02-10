using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Abstractions.Serialization;

/// <summary>
/// JSON converter for AIContent polymorphic serialization.
/// </summary>
public class AIContentConverter : JsonConverter<AIContent>
{
    /// <summary>
    /// Reads and converts JSON to an AIContent object.
    /// </summary>
    /// <param name="reader">The JSON reader.</param>
    /// <param name="typeToConvert">The type to convert.</param>
    /// <param name="options">Serializer options.</param>
    /// <returns>The deserialized AIContent object.</returns>
    public override AIContent? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        // Read the JSON into a JsonDocument to inspect it
        using var doc = JsonDocument.ParseValue(ref reader);
        var root = doc.RootElement;

        // Determine the concrete type based on the "kind" property
        AIContent? content = null;

        if (root.TryGetProperty("kind", out var kindElement))
        {
            var kind = kindElement.GetString();

            // Create new options without this converter to avoid recursion
            var newOptions = new JsonSerializerOptions(options);
            newOptions.Converters.Clear();
            foreach (var converter in options.Converters)
            {
                if (converter is not AIContentConverter)
                {
                    newOptions.Converters.Add(converter);
                }
            }

            content = kind switch
            {
                "text" => JsonSerializer.Deserialize<TextContent>(root.GetRawText(), newOptions),
                "function-call" => JsonSerializer.Deserialize<FunctionCallContent>(root.GetRawText(), newOptions),
                "function-result" => JsonSerializer.Deserialize<FunctionResultContent>(root.GetRawText(), newOptions),
                "error" => JsonSerializer.Deserialize<ErrorContent>(root.GetRawText(), newOptions),
                "text-reasoning" => JsonSerializer.Deserialize<TextReasoningContent>(root.GetRawText(), newOptions),
                "data" => JsonSerializer.Deserialize<DataContent>(root.GetRawText(), newOptions),
                "uri" => JsonSerializer.Deserialize<UriContent>(root.GetRawText(), newOptions),
                "image" => JsonSerializer.Deserialize<ImageContent>(root.GetRawText(), newOptions),
                "audio" => JsonSerializer.Deserialize<AudioContent>(root.GetRawText(), newOptions),
                "transcript" => JsonSerializer.Deserialize<TranscriptContent>(root.GetRawText(), newOptions),
                "video" => JsonSerializer.Deserialize<VideoContent>(root.GetRawText(), newOptions),
                "file" => JsonSerializer.Deserialize<FileContent>(root.GetRawText(), newOptions),
                "search-result" => JsonSerializer.Deserialize<SearchResultContent>(root.GetRawText(), newOptions),
                "document" => JsonSerializer.Deserialize<DocumentContent>(root.GetRawText(), newOptions),
                "adaptive-card" => JsonSerializer.Deserialize<AdaptiveCardContent>(root.GetRawText(), newOptions),
                "refusal" => JsonSerializer.Deserialize<RefusalContent>(root.GetRawText(), newOptions),
                "filter-result" => JsonSerializer.Deserialize<ContentFilterResultContent>(root.GetRawText(), newOptions),
                "user-input-request" => JsonSerializer.Deserialize<UserInputRequestContent>(root.GetRawText(), newOptions),
                "suggested-actions" => JsonSerializer.Deserialize<SuggestedActionsContent>(root.GetRawText(), newOptions),
                "event" => JsonSerializer.Deserialize<EventContent>(root.GetRawText(), newOptions),
                "trace" => JsonSerializer.Deserialize<TraceContent>(root.GetRawText(), newOptions),
                "action" => JsonSerializer.Deserialize<ActionContent>(root.GetRawText(), newOptions),
                "typing-indicator" => JsonSerializer.Deserialize<TypingIndicatorContent>(root.GetRawText(), newOptions),
                "message-reaction" => JsonSerializer.Deserialize<MessageReactionContent>(root.GetRawText(), newOptions),
                "message-delete" => JsonSerializer.Deserialize<MessageDeleteContent>(root.GetRawText(), newOptions),
                "message-update" => JsonSerializer.Deserialize<MessageUpdateContent>(root.GetRawText(), newOptions),
                "hosted-file" => JsonSerializer.Deserialize<HostedFileContent>(root.GetRawText(), newOptions),
                "hosted-vector-store" => JsonSerializer.Deserialize<HostedVectorStoreContent>(root.GetRawText(), newOptions),
                _ => null
            };
        }

        return content;
    }

    /// <summary>
    /// Writes an AIContent object to JSON.
    /// </summary>
    /// <param name="writer">The JSON writer.</param>
    /// <param name="value">The AIContent value to serialize.</param>
    /// <param name="options">Serializer options.</param>
    public override void Write(Utf8JsonWriter writer, AIContent value, JsonSerializerOptions options)
    {
        // Create new options without this converter to avoid recursion
        var newOptions = new JsonSerializerOptions(options);
        newOptions.Converters.Clear();
        foreach (var converter in options.Converters)
        {
            if (converter is not AIContentConverter)
            {
                newOptions.Converters.Add(converter);
            }
        }

        // Serialize the concrete type
        JsonSerializer.Serialize(writer, value, value.GetType(), newOptions);
    }
}
