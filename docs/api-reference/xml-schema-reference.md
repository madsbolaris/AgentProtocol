# Agent XML Schema Reference

> **Technical reference for the Agent XML serialization format and validation.**

---

## Overview

Agent XML is defined by the Agent Protocol TypeSpec schema and serialized using the `Microsoft.Agents.Xml` SDK. This document provides complete technical details for all message types, content types, validation rules, and schema features.

---

## Message Types

All messages inherit from a base message structure with optional metadata.

### User Messages

Represents input from a human user or system acting on behalf of a user.

```xml
<user
  user-id="string"          <!-- Required: Unique user identifier -->
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
  metadata-key="value"      <!-- Optional: Any custom attributes -->
>
  <!-- Contents: One or more content elements -->
</user>
```

**Example**:
```xml
<user user-id="alice" created-at="2026-02-07T10:30:00Z">
  <text>What's the weather in Seattle?</text>
</user>
```

---

### Agent Messages

Represents output from an AI agent.

```xml
<agent
  agent-id="string"         <!-- Optional: Agent identifier -->
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
  metadata-key="value"      <!-- Optional: Any custom attributes -->
>
  <!-- Contents: One or more content elements -->
</agent>
```

**Example**:
```xml
<agent agent-id="weather-assistant">
  <text>The weather in Seattle is 52°F and cloudy.</text>
</agent>
```

---

### Tool Messages

Represents tool/function execution context.

```xml
<tool
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
>
  <!-- Contents: Typically function-result elements -->
</tool>
```

**Example**:
```xml
<tool>
  <function-result call-id="call_001">
    {"temperature": 52, "conditions": "cloudy"}
  </function-result>
</tool>
```

---

### System Messages

Represents system-level instructions or metadata.

```xml
<system
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
>
  <!-- Contents: Typically text or metadata -->
</system>
```

**Example**:
```xml
<system>
  <text audience="developer">Session started with GPT-4 model</text>
</system>
```

---

### Developer Messages

Represents instructions or context from developers to the agent.

```xml
<developer
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
>
  <!-- Contents: Typically text instructions -->
</developer>
```

**Example**:
```xml
<developer>
  <text>Always respond in a friendly, conversational tone.</text>
</developer>
```

---

### Channel Messages

Represents messages from communication channels (Slack, Teams, etc.).

```xml
<channel
  channel-id="string"       <!-- Required: Channel identifier -->
  source="string"           <!-- Optional: Channel source (e.g., "slack", "teams") -->
  created-at="ISO8601"      <!-- Optional: Message timestamp -->
>
  <!-- Contents: One or more content elements -->
</channel>
```

**Example**:
```xml
<channel channel-id="C12345" source="slack">
  <text>Meeting reminder: 2pm today</text>
</channel>
```

---

## Content Types

Content elements appear within message elements.

### Text Content

Plain text or formatted text content.

```xml
<text
  audience="user|developer|all"     <!-- Optional: Target audience -->
  language="en"                     <!-- Optional: Language code -->
>
  The actual text content
</text>
```

**Example**:
```xml
<text audience="user">Hello! How can I help you today?</text>
```

---

### Thinking Content

Internal reasoning or thought process of the agent.

```xml
<thinking
  exposed="true|false"              <!-- Required: Whether to show thinking -->
  audience="user|developer|all"     <!-- Optional: Target audience -->
>
  The agent's internal reasoning
</thinking>
```

**Example**:
```xml
<thinking exposed="true" audience="developer">
  User asked about weather. I should call the weather API with location "Seattle".
</thinking>
```

---

### Image Content

Image references with optional metadata.

```xml
<image
  uri="https://..."                 <!-- Required: Image URL or data URI -->
  alt-text="string"                 <!-- Optional: Accessibility text -->
  width="number"                    <!-- Optional: Width in pixels -->
  height="number"                   <!-- Optional: Height in pixels -->
  mime-type="image/png"             <!-- Optional: MIME type -->
/>
```

**Example**:
```xml
<image
  uri="https://example.com/chart.png"
  alt-text="Sales chart showing Q4 growth"
  mime-type="image/png"
/>
```

---

### Audio Content

Audio references with optional metadata.

```xml
<audio
  uri="https://..."                 <!-- Required: Audio URL or data URI -->
  transcript="string"               <!-- Optional: Text transcript -->
  duration="number"                 <!-- Optional: Duration in seconds -->
  mime-type="audio/mp3"             <!-- Optional: MIME type -->
/>
```

**Example**:
```xml
<audio
  uri="https://example.com/recording.mp3"
  transcript="User said: What's the weather like today?"
  duration="3.5"
  mime-type="audio/mp3"
/>
```

---

### Video Content

Video references with optional metadata.

```xml
<video
  uri="https://..."                 <!-- Required: Video URL or data URI -->
  thumbnail="https://..."           <!-- Optional: Thumbnail image URL -->
  duration="number"                 <!-- Optional: Duration in seconds -->
  mime-type="video/mp4"             <!-- Optional: MIME type -->
/>
```

**Example**:
```xml
<video
  uri="https://example.com/demo.mp4"
  thumbnail="https://example.com/demo-thumb.jpg"
  duration="120"
  mime-type="video/mp4"
/>
```

---

### File Content

File references with metadata.

```xml
<file
  uri="https://..."                 <!-- Required: File URL or data URI -->
  name="document.pdf"               <!-- Optional: File name -->
  size="number"                     <!-- Optional: File size in bytes -->
  mime-type="application/pdf"       <!-- Required: MIME type -->
/>
```

**Example**:
```xml
<file
  uri="https://example.com/report.pdf"
  name="Q4_Report.pdf"
  size="1024000"
  mime-type="application/pdf"
/>
```

---

### Document Content

Structured document content with optional pages.

```xml
<document
  uri="https://..."                 <!-- Required: Document URL -->
  title="string"                    <!-- Optional: Document title -->
  mime-type="application/pdf"       <!-- Optional: MIME type -->
>
  Optional text content or summary
</document>
```

**Example**:
```xml
<document
  uri="https://example.com/manual.pdf"
  title="User Manual v2.0"
  mime-type="application/pdf"
>
  Product documentation for version 2.0
</document>
```

---

### Function Call Content

Represents a function/tool invocation.

```xml
<function-call
  call-id="string"                  <!-- Required: Unique call identifier -->
  name="function_name"              <!-- Required: Function name -->
>
  {"arg1": "value1", "arg2": "value2"}
</function-call>
```

**Example**:
```xml
<function-call call-id="call_001" name="get_weather">
  {"location": "Seattle, WA", "units": "fahrenheit"}
</function-call>
```

---

### Function Result Content

Represents the result of a function/tool execution.

```xml
<function-result
  call-id="string"                  <!-- Required: Matches function-call call-id -->
  is-error="true|false"             <!-- Optional: Whether this is an error result -->
>
  {"result": "data"}
</function-result>
```

**Example**:
```xml
<function-result call-id="call_001" is-error="false">
  {"temperature": 52, "conditions": "cloudy", "humidity": 75}
</function-result>
```

**Error Example**:
```xml
<function-result call-id="call_002" is-error="true">
  {"error": "API rate limit exceeded", "code": "RATE_LIMIT"}
</function-result>
```

---

### Adaptive Card Content

Microsoft Adaptive Cards for rich UI rendering.

```xml
<adaptive-card
  card-json='{"type": "AdaptiveCard", ...}'    <!-- Required: JSON string -->
/>
```

**Example**:
```xml
<adaptive-card card-json='{
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "Weather Update",
      "size": "large"
    }
  ]
}' />
```

---

### Action Content

Represents an action or button for user interaction.

```xml
<action
  title="string"                    <!-- Required: Display text -->
  value="string"                    <!-- Optional: Action value/payload -->
  type="button|link|..."            <!-- Optional: Action type -->
  uri="https://..."                 <!-- Optional: Link URL -->
/>
```

**Example**:
```xml
<action title="View Details" value="show_details" type="button" />
```

---

### Suggested Actions Content

Collection of suggested actions for the user.

```xml
<suggested-actions>
  <action title="Option 1" value="opt1" />
  <action title="Option 2" value="opt2" />
  <action title="Option 3" value="opt3" />
</suggested-actions>
```

**Example**:
```xml
<suggested-actions>
  <action title="Book a flight" value="book_flight" />
  <action title="Check status" value="check_status" />
  <action title="Cancel booking" value="cancel_booking" />
</suggested-actions>
```

---

### Error Content

Structured error information.

```xml
<error
  code="string"                     <!-- Required: Error code -->
  message="string"                  <!-- Required: Error message -->
  details="string"                  <!-- Optional: Additional details -->
/>
```

**Example**:
```xml
<error
  code="FUNCTION_FAILED"
  message="Weather API returned 500 error"
  details="Service temporarily unavailable"
/>
```

---

### Refusal Content

Indicates the agent refused to comply with a request.

```xml
<refusal
  reason="string"                   <!-- Optional: Reason for refusal -->
>
  I cannot assist with that request.
</refusal>
```

**Example**:
```xml
<refusal reason="policy_violation">
  I cannot provide instructions for illegal activities.
</refusal>
```

---

### Data Content

Arbitrary structured data.

```xml
<data
  content-type="application/json"   <!-- Optional: Data format -->
>
  {"key": "value", "data": [...]}
</data>
```

**Example**:
```xml
<data content-type="application/json">
  {
    "metrics": {"latency": 45, "tokens": 150},
    "metadata": {"model": "gpt-4", "temperature": 0.7}
  }
</data>
```

---

### URI Content

Simple URI reference.

```xml
<uri href="https://example.com/resource" />
```

**Example**:
```xml
<uri href="https://docs.microsoft.com/agent-protocol" />
```

---

### Search Result Content

Represents a search result item.

```xml
<search-result
  title="string"                    <!-- Required: Result title -->
  uri="https://..."                 <!-- Required: Result URL -->
  snippet="string"                  <!-- Optional: Result excerpt -->
>
  Optional detailed content
</search-result>
```

**Example**:
```xml
<search-result
  title="Agent Protocol Documentation"
  uri="https://docs.example.com/agent-protocol"
  snippet="Complete guide to building agents with the Agent Protocol..."
>
  Detailed documentation for implementing agents using the standardized protocol.
</search-result>
```

---

### Event Content

Represents system or application events.

```xml
<event
  event-type="string"               <!-- Required: Event type -->
  timestamp="ISO8601"               <!-- Optional: Event timestamp -->
>
  Event details or payload
</event>
```

**Example**:
```xml
<event event-type="user_joined" timestamp="2026-02-07T14:30:00Z">
  User alice joined the conversation
</event>
```

---

### Trace Content

Debugging and telemetry information.

```xml
<trace
  level="debug|info|warn|error"     <!-- Optional: Log level -->
  category="string"                 <!-- Optional: Trace category -->
>
  Trace message or structured data
</trace>
```

**Example**:
```xml
<trace level="debug" category="function_execution">
  Calling weather API with params: {"location": "Seattle"}
</trace>
```

---

### Content Filter Result Content

Content moderation/safety results.

```xml
<content-filter-result
  filtered="true|false"             <!-- Required: Whether content was filtered -->
  severity="low|medium|high"        <!-- Optional: Severity level -->
  category="hate|violence|..."      <!-- Optional: Filter category -->
>
  Optional explanation
</content-filter-result>
```

**Example**:
```xml
<content-filter-result filtered="true" severity="high" category="violence">
  Content contains descriptions of graphic violence
</content-filter-result>
```

---

### Typing Indicator Content

Indicates agent is processing/typing.

```xml
<typing-indicator active="true|false" />
```

**Example**:
```xml
<typing-indicator active="true" />
```

---

### Message Update/Delete Content

Represents message modification operations.

```xml
<message-update
  message-id="string"               <!-- Required: ID of message to update -->
>
  Updated content
</message-update>

<message-delete
  message-id="string"               <!-- Required: ID of message to delete -->
/>
```

**Example**:
```xml
<message-update message-id="msg_123">
  <text>Corrected: The weather is 52°F (not 45°F)</text>
</message-update>
```

---

### Message Reaction Content

Represents reactions/emoji responses.

```xml
<message-reaction
  message-id="string"               <!-- Required: ID of message reacted to -->
  reaction="👍"                     <!-- Required: Emoji or reaction string -->
  user-id="string"                  <!-- Optional: User who reacted -->
/>
```

**Example**:
```xml
<message-reaction message-id="msg_456" reaction="👍" user-id="alice" />
```

---

### User Input Request Content

Requests specific input from user.

```xml
<user-input-request
  input-type="text|file|choice"     <!-- Required: Type of input requested -->
  prompt="string"                   <!-- Optional: Prompt text -->
>
  Optional instructions
</user-input-request>
```

**Example**:
```xml
<user-input-request input-type="file" prompt="Please upload your resume">
  Accepted formats: PDF, DOCX. Max size: 5MB.
</user-input-request>
```

---

### Transcript Content

Conversation transcript or summary.

```xml
<transcript
  format="text|xml|json"            <!-- Optional: Transcript format -->
>
  Conversation transcript content
</transcript>
```

**Example**:
```xml
<transcript format="text">
User: Hello
Agent: Hi! How can I help?
User: What's the weather?
Agent: It's 52°F and cloudy.
</transcript>
```

---

### Hosted File/Vector Store Content

References to hosted resources.

```xml
<hosted-file
  file-id="string"                  <!-- Required: Hosted file identifier -->
  name="string"                     <!-- Optional: File name -->
/>

<hosted-vector-store
  store-id="string"                 <!-- Required: Vector store identifier -->
  name="string"                     <!-- Optional: Store name -->
/>
```

**Example**:
```xml
<hosted-file file-id="file_abc123" name="customer_data.csv" />
```

---

## Thread Structure

Threads represent complete conversations.

```xml
<thread
  thread-id="string"                <!-- Required: Unique thread identifier -->
  title="string"                    <!-- Optional: Thread title -->
  created-at="ISO8601"              <!-- Optional: Creation timestamp -->
  metadata-key="value"              <!-- Optional: Custom attributes -->
>
  <!-- Messages: One or more message elements -->
  <user>...</user>
  <agent>...</agent>
  <tool>...</tool>
</thread>
```

**Example**:
```xml
<thread thread-id="conv_001" title="Weather Query" created-at="2026-02-07T10:00:00Z">
  <user user-id="alice">
    <text>What's the weather?</text>
  </user>
  <agent>
    <text>It's 52°F and cloudy in Seattle.</text>
  </agent>
</thread>
```

---

## Validation Rules

### Schema Validation

The XML must conform to the Agent Protocol TypeSpec schema:

```csharp
var serializer = new MessageSerializer(new SerializerOptions
{
    ValidateOnDeserialize = true  // Enable validation
});

try
{
    var message = serializer.Deserialize(xmlString);
}
catch (XmlSchemaException ex)
{
    Console.WriteLine($"Validation error: {ex.Message}");
    Console.WriteLine($"Line: {ex.LineNumber}, Position: {ex.LinePosition}");
}
```

### Common Validation Errors

**Unknown Element**:
```xml
<user user-id="alice">
  <invalid-element>This will fail</invalid-element>
</user>
```
Error: `Unknown element 'invalid-element' in <user> at line 2.`

**Missing Required Attribute**:
```xml
<function-call name="get_weather">
  <!-- Missing required call-id attribute -->
</function-call>
```
Error: `Required attribute 'call-id' missing on <function-call> at line 1.`

**Invalid Attribute Value**:
```xml
<thinking exposed="maybe">
  <!-- 'exposed' must be 'true' or 'false' -->
</thinking>
```
Error: `Invalid value 'maybe' for attribute 'exposed' on <thinking> at line 1.`

---

## Advanced Features

### Custom Attributes

Custom metadata can be added to any message or content element:

```xml
<user user-id="alice" session-id="sess_123" client-version="2.0">
  <text locale="en-US" sentiment="positive">Great, thanks!</text>
</user>
```

Custom attributes are preserved during serialization/deserialization but are not validated against the schema.

---

### Namespaces

The default namespace is the Agent Protocol namespace:

```xml
<thread xmlns="https://schemas.microsoft.com/agent-protocol/2024">
  <user user-id="alice">
    <text>Hello</text>
  </user>
</thread>
```

Custom namespaces can be used for extensions:

```xml
<thread xmlns="https://schemas.microsoft.com/agent-protocol/2024"
        xmlns:custom="https://example.com/custom">
  <user user-id="alice">
    <text>Hello</text>
    <custom:metadata>Custom data</custom:metadata>
  </user>
</thread>
```

---

### Comments

XML comments are preserved and can be used for documentation:

```xml
<thread thread-id="test_001">
  <!-- This is a test scenario for weather queries -->
  <user user-id="alice">
    <text>What's the weather?</text>
  </user>
  <!-- Agent should call get_weather function -->
  <agent>
    <function-call call-id="call_001" name="get_weather">
      {"location": "Seattle"}
    </function-call>
  </agent>
</thread>
```

---

### CDATA Sections

Use CDATA for content containing special characters:

```xml
<text><![CDATA[
  The formula is: if (x < 10 && y > 5) { return true; }
]]></text>
```

---

### Entity References

Standard XML entity references are supported:

```xml
<text>Price: $5 &lt; $10 &amp; quality &gt; 8/10</text>
<!-- Renders as: Price: $5 < $10 & quality > 8/10 -->
```

---

## Serialization Options

### Pretty Print

```csharp
var serializer = new MessageSerializer(new SerializerOptions
{
    Indent = true,
    IndentChars = "  "  // Two spaces
});

var xml = serializer.Serialize(message);
// Output is formatted with indentation
```

### Namespace Handling

```csharp
var serializer = new MessageSerializer(new SerializerOptions
{
    OmitXmlDeclaration = false,  // Include <?xml version="1.0"?>
    NamespacePrefix = "agent"     // Use <agent:user> instead of <user>
});
```

### Validation Options

```csharp
var serializer = new MessageSerializer(new SerializerOptions
{
    ValidateOnSerialize = true,    // Validate before serializing
    ValidateOnDeserialize = true,  // Validate after deserializing
    StrictMode = true              // Reject unknown elements/attributes
});
```

---

## Best Practices

### Use Meaningful IDs

```xml
<!-- Good -->
<user user-id="alice_2026-02-07">
<function-call call-id="weather_seattle_001">

<!-- Bad -->
<user user-id="u1">
<function-call call-id="1">
```

### Add Timestamps

```xml
<user user-id="alice" created-at="2026-02-07T10:30:45Z">
  <text>What's the weather?</text>
</user>
```

### Use Comments for Context

```xml
<!-- Test case: Multi-turn conversation with function calling -->
<thread thread-id="test_multimodal_001">
  <!-- User provides image and text -->
  <user user-id="test_user">
    <text>What's in this image?</text>
    <image uri="test-images/photo.jpg" />
  </user>
</thread>
```

### Group Related Content

```xml
<agent>
  <!-- Show reasoning first -->
  <thinking exposed="true">Need to call weather API</thinking>

  <!-- Then the function call -->
  <function-call call-id="call_001" name="get_weather">
    {"location": "Seattle"}
  </function-call>
</agent>
```

---

## Migration Guide

### From JSON to XML

**JSON**:
```json
{
  "role": "user",
  "userId": "alice",
  "content": [
    {"type": "text", "text": "Hello"}
  ]
}
```

**XML**:
```xml
<user user-id="alice">
  <text>Hello</text>
</user>
```

### From Other Formats

Most serialization formats can be converted using the SDK:

```csharp
// From custom format
var customMessage = LoadFromCustomFormat("message.json");

// Convert to Agent Protocol message
var message = new UserMessage
{
    UserId = customMessage.UserId,
    Contents = customMessage.Contents.Select(c => ConvertContent(c)).ToList()
};

// Serialize to XML
var xml = serializer.Serialize(message);
```

---

## Reference Implementation

For complete implementation details, see:

- **Source Code**: `/dotnet/src/Microsoft.Agents.Xml/`
- **Test Suite**: `/dotnet/tests/Microsoft.Agents.Xml.Tests/`
- **Test Data**: `/test-data/input/` (400+ examples)
- **TypeSpec Schema**: `/specs/agent-protocol.tsp`

---

*Last Updated: 2026-02-08*
