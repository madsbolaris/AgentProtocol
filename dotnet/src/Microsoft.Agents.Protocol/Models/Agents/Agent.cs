using System.Collections.Generic;
using System.Text.Json.Serialization;
using Microsoft.Agents.Protocol.Models.Common;

namespace Microsoft.Agents.Protocol.Models.Agents;

/// <summary>
/// Agent Definition - Configuration for an agent
/// </summary>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
[JsonDerivedType(typeof(PromptAgent), "prompt")]
public abstract class AgentDefinition
{
    /// <summary>
    /// Agent name
    /// </summary>
    [JsonPropertyName("name")]
    public string? Name { get; set; }

    /// <summary>
    /// Agent description
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Prompt Agent - LLM-based agent with instructions
/// </summary>
public class PromptAgent : AgentDefinition
{
    /// <summary>
    /// Model identifier (e.g., "gpt-4o", "claude-3-sonnet")
    /// </summary>
    [JsonPropertyName("model")]
    public required string Model { get; set; }

    /// <summary>
    /// System instructions for the agent
    /// </summary>
    [JsonPropertyName("instructions")]
    public string? Instructions { get; set; }

    /// <summary>
    /// Tools available to the agent
    /// </summary>
    [JsonPropertyName("tools")]
    public List<AITool>? Tools { get; set; }

    /// <summary>
    /// Temperature for response generation (0.0 to 2.0)
    /// </summary>
    [JsonPropertyName("temperature")]
    public double? Temperature { get; set; }

    /// <summary>
    /// Top P for response generation
    /// </summary>
    [JsonPropertyName("topP")]
    public double? TopP { get; set; }

    /// <summary>
    /// Maximum tokens to generate
    /// </summary>
    [JsonPropertyName("maxTokens")]
    public int? MaxTokens { get; set; }
}

/// <summary>
/// AI Tool - Tool definition for agent capabilities
/// </summary>
public class AITool
{
    /// <summary>
    /// Tool name (unique identifier)
    /// </summary>
    [JsonPropertyName("name")]
    public required string Name { get; set; }

    /// <summary>
    /// Tool description for LLM
    /// </summary>
    [JsonPropertyName("description")]
    public required string Description { get; set; }

    /// <summary>
    /// Tool parameters (JSON Schema)
    /// </summary>
    [JsonPropertyName("parameters")]
    public JSONSchema? Parameters { get; set; }

    /// <summary>
    /// Strict schema validation
    /// </summary>
    [JsonPropertyName("strict")]
    public bool? Strict { get; set; }

    /// <summary>
    /// Execution endpoint for remote tools
    /// </summary>
    [JsonPropertyName("endpoint")]
    public string? Endpoint { get; set; }

    /// <summary>
    /// Authentication for remote endpoint
    /// </summary>
    [JsonPropertyName("connection")]
    public Connection? Connection { get; set; }

    /// <summary>
    /// OAuth2 scopes required for this tool
    /// </summary>
    [JsonPropertyName("scopes")]
    public Dictionary<string, string>? Scopes { get; set; }

    /// <summary>
    /// Requires user approval before execution
    /// </summary>
    [JsonPropertyName("requiresApproval")]
    public bool? RequiresApproval { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// JSON Schema - Parameter schema for tool validation
/// </summary>
public class JSONSchema
{
    /// <summary>
    /// Schema type
    /// </summary>
    [JsonPropertyName("type")]
    public string? SchemaType { get; set; }

    /// <summary>
    /// Object properties
    /// </summary>
    [JsonPropertyName("properties")]
    public Dictionary<string, JSONSchema>? Properties { get; set; }

    /// <summary>
    /// Array item schema
    /// </summary>
    [JsonPropertyName("items")]
    public JSONSchema? Items { get; set; }

    /// <summary>
    /// Required properties
    /// </summary>
    [JsonPropertyName("required")]
    public List<string>? Required { get; set; }

    /// <summary>
    /// Property description
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// Enum values
    /// </summary>
    [JsonPropertyName("enum")]
    public List<object>? Enum { get; set; }

    /// <summary>
    /// Format hint
    /// </summary>
    [JsonPropertyName("format")]
    public string? Format { get; set; }

    /// <summary>
    /// Minimum value
    /// </summary>
    [JsonPropertyName("minimum")]
    public double? Minimum { get; set; }

    /// <summary>
    /// Maximum value
    /// </summary>
    [JsonPropertyName("maximum")]
    public double? Maximum { get; set; }

    /// <summary>
    /// Additional properties
    /// </summary>
    [JsonPropertyName("additionalProperties")]
    public object? AdditionalProperties { get; set; }
}

/// <summary>
/// Agent Card - Discovery/registration metadata
/// </summary>
public class AgentCard
{
    /// <summary>
    /// Agent identifier
    /// </summary>
    [JsonPropertyName("agentId")]
    public string? AgentId { get; set; }

    /// <summary>
    /// Agent name
    /// </summary>
    [JsonPropertyName("name")]
    public required string Name { get; set; }

    /// <summary>
    /// Agent description
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// Agent capabilities
    /// </summary>
    [JsonPropertyName("capabilities")]
    public AgentCapabilities? Capabilities { get; set; }

    /// <summary>
    /// Available tools
    /// </summary>
    [JsonPropertyName("tools")]
    public List<AITool>? Tools { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Agent Capabilities - What the agent can do
/// </summary>
public class AgentCapabilities
{
    /// <summary>
    /// Supports vision/image understanding
    /// </summary>
    [JsonPropertyName("vision")]
    public bool? Vision { get; set; }

    /// <summary>
    /// Supports extended thinking
    /// </summary>
    [JsonPropertyName("thinking")]
    public bool? Thinking { get; set; }

    /// <summary>
    /// Supports tool/function calling
    /// </summary>
    [JsonPropertyName("tools")]
    public bool? Tools { get; set; }

    /// <summary>
    /// Maximum context tokens
    /// </summary>
    [JsonPropertyName("maxTokens")]
    public int? MaxTokens { get; set; }

    /// <summary>
    /// Supported content types
    /// </summary>
    [JsonPropertyName("contentTypes")]
    public List<string>? ContentTypes { get; set; }
}
