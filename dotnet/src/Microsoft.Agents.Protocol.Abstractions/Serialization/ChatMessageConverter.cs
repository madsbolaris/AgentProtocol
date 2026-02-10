using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Abstractions.Serialization;

/// <summary>
/// JSON converter for ChatMessage polymorphic serialization.
/// </summary>
public class ChatMessageConverter : JsonConverter<ChatMessage>
{
    /// <summary>
    /// Reads and converts JSON to a ChatMessage object.
    /// </summary>
    /// <param name="reader">The JSON reader.</param>
    /// <param name="typeToConvert">The type to convert.</param>
    /// <param name="options">Serializer options.</param>
    /// <returns>The deserialized ChatMessage object.</returns>
    public override ChatMessage? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        // Read the JSON into a JsonDocument to inspect it
        using var doc = JsonDocument.ParseValue(ref reader);
        var root = doc.RootElement;

        // Determine the concrete type based on the "role" property
        ChatMessage? message = null;

        if (root.TryGetProperty("role", out var roleElement))
        {
            // Handle role as either string or number (enum value)
            string? role = null;
            if (roleElement.ValueKind == JsonValueKind.String)
            {
                role = roleElement.GetString();
            }
            else if (roleElement.ValueKind == JsonValueKind.Number)
            {
                var roleNum = roleElement.GetInt32();
                role = ((ChatRole)roleNum).ToString().ToLower();
            }

            // Create new options without this converter to avoid recursion
            var newOptions = new JsonSerializerOptions(options);
            newOptions.Converters.Clear();
            foreach (var converter in options.Converters)
            {
                if (converter is not ChatMessageConverter)
                {
                    newOptions.Converters.Add(converter);
                }
            }

            message = role switch
            {
                "system" => JsonSerializer.Deserialize<SystemMessage>(root.GetRawText(), newOptions),
                "developer" => JsonSerializer.Deserialize<DeveloperMessage>(root.GetRawText(), newOptions),
                "agent" => JsonSerializer.Deserialize<AgentMessage>(root.GetRawText(), newOptions),
                "user" => JsonSerializer.Deserialize<UserMessage>(root.GetRawText(), newOptions),
                "tool" => JsonSerializer.Deserialize<ToolMessage>(root.GetRawText(), newOptions),
                "channel" => JsonSerializer.Deserialize<ChannelMessage>(root.GetRawText(), newOptions),
                _ => null
            };
        }

        return message;
    }

    /// <summary>
    /// Writes a ChatMessage object to JSON.
    /// </summary>
    /// <param name="writer">The JSON writer.</param>
    /// <param name="value">The ChatMessage value to serialize.</param>
    /// <param name="options">Serializer options.</param>
    public override void Write(Utf8JsonWriter writer, ChatMessage value, JsonSerializerOptions options)
    {
        // Create new options without this converter to avoid recursion
        var newOptions = new JsonSerializerOptions(options);
        newOptions.Converters.Clear();
        foreach (var converter in options.Converters)
        {
            if (converter is not ChatMessageConverter)
            {
                newOptions.Converters.Add(converter);
            }
        }

        // Add "role" property and serialize the concrete type
        JsonSerializer.Serialize(writer, value, value.GetType(), newOptions);
    }
}
