/**
 * XML Serialization Decorators for AgentXml
 *
 * This file defines decorators that map TypeSpec models to XML elements,
 * attributes, and schemas. These decorators are consumed by the AgentXml
 * code generator to produce C# classes with proper XML serialization.
 *
 * USAGE:
 * Import this file in your TypeSpec models:
 * ```
 * import "./xml-decorators.tsp";
 * ```
 */

import "@typespec/http";

using TypeSpec.Http;

namespace AgentXml.Decorators;

/**
 * Marks a model as an XML root element.
 * Generates [XmlRoot] attribute in C#.
 *
 * @param elementName The XML element name (e.g., "agent", "user", "tool")
 *
 * @example
 * ```typescript
 * @xmlRoot("agent")
 * model AgentMessage extends ChatMessage {
 *   // ...
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlRoot("agent")]
 * public partial class AgentMessage : ChatMessage { }
 * ```
 */
extern dec xmlRoot(target: Model, elementName: valueof string);

/**
 * Marks a model as an XML element (non-root).
 * Generates [XmlType] attribute in C#.
 *
 * @param elementName The XML element name
 *
 * @example
 * ```typescript
 * @xmlElement("text")
 * model TextContent {
 *   kind: "text";
 *   text: string;
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlType("text")]
 * public partial class TextContent { }
 * ```
 */
extern dec xmlElement(target: Model, elementName: valueof string);

/**
 * Specifies the XML namespace for an element.
 * Generates [XmlRoot(Namespace = "...")] in C#.
 *
 * @param namespace The XML namespace URI
 *
 * @example
 * ```typescript
 * @xmlRoot("message")
 * @xmlNamespace("http://schemas.agent.ai/messages/v1")
 * model ChatMessage { }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlRoot("message", Namespace = "http://schemas.agent.ai/messages/v1")]
 * public partial class ChatMessage { }
 * ```
 */
extern dec xmlNamespace(target: Model, namespace: valueof string);

/**
 * Marks a property as an XML attribute.
 * Generates [XmlAttribute] in C#.
 *
 * @param attributeName Optional attribute name (defaults to property name in kebab-case)
 *
 * @example
 * ```typescript
 * model ChatMessage {
 *   @xmlAttribute
 *   messageId: string;
 *
 *   @xmlAttribute("created-at")
 *   createdAt: utcDateTime;
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlAttribute("message-id")]
 * public string MessageId { get; set; }
 *
 * [XmlAttribute("created-at")]
 * public DateTime CreatedAt { get; set; }
 * ```
 */
extern dec xmlAttribute(target: ModelProperty, attributeName?: valueof string);

/**
 * Marks a property as an XML element (explicit).
 * Generates [XmlElement] in C#.
 *
 * @param elementName Optional element name (defaults to property name in kebab-case)
 *
 * @example
 * ```typescript
 * model ChatMessage {
 *   @xmlElement("role")
 *   role: ChatRole;
 *
 *   @xmlElement
 *   contents: AIContent[];
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlElement("role")]
 * public ChatRole Role { get; set; }
 *
 * [XmlElement("contents")]
 * public List<AIContent> Contents { get; set; }
 * ```
 */
extern dec xmlElement(target: ModelProperty, elementName?: valueof string);

/**
 * Marks an array property with specific array and item names.
 * Generates [XmlArray] and [XmlArrayItem] in C#.
 *
 * @param arrayName The wrapper element name
 * @param itemName The individual item element name
 *
 * @example
 * ```typescript
 * model ToolDefinition {
 *   @xmlArray("inputs", "input")
 *   inputs: InputParameter[];
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlArray("inputs")]
 * [XmlArrayItem("input")]
 * public List<InputParameter> Inputs { get; set; }
 * ```
 */
extern dec xmlArray(
  target: ModelProperty,
  arrayName: valueof string,
  itemName: valueof string
);

/**
 * Marks content as plain text (inner text node).
 * Generates [XmlText] in C#.
 *
 * @example
 * ```typescript
 * model TextContent {
 *   kind: "text";
 *
 *   @xmlText
 *   text: string;
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlText]
 * public string Text { get; set; }
 * ```
 */
extern dec xmlText(target: ModelProperty);

/**
 * Marks property to be ignored in XML serialization.
 * Generates [XmlIgnore] in C#.
 *
 * @example
 * ```typescript
 * model ChatMessage {
 *   messageId: string;
 *
 *   @xmlIgnore
 *   rawRepresentation?: unknown;
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlIgnore]
 * public object? RawRepresentation { get; set; }
 * ```
 */
extern dec xmlIgnore(target: ModelProperty);

/**
 * Specifies the content type(s) for syntax highlighting and validation.
 * This is metadata only - it does NOT affect XML serialization.
 * Used by VS Code extensions and other tooling.
 *
 * @param types Single content type or array of accepted types
 *
 * Supported content types:
 * - "text": Plain text
 * - "json": JSON data
 * - "xml": XML data
 * - "yaml": YAML data
 * - "markdown": Markdown text
 * - "powerfx": Microsoft Power Fx formula
 * - "cel": Common Expression Language
 * - "mustache": Mustache template
 * - "sql": SQL query
 * - "python": Python code
 * - "csharp": C# code
 * - "javascript": JavaScript code
 * - "typescript": TypeScript code
 * - And more...
 *
 * @example Single content type with XML text
 * ```typescript
 * model TextContent {
 *   @xmlText
 *   @contentType("text")
 *   text: string;
 * }
 * ```
 *
 * @example JSON content with XML text
 * ```typescript
 * model FunctionCallContent {
 *   @xmlText
 *   @contentType("json")
 *   arguments: string;
 * }
 * ```
 *
 * @example Content type with XML attribute
 * ```typescript
 * model FormulaContent {
 *   @xmlAttribute
 *   @contentType("powerfx")
 *   expression: string;
 * }
 * ```
 *
 * @example Multiple content types (field can be PowerFx OR CEL)
 * ```typescript
 * model ExpressionContent {
 *   @xmlAttribute
 *   @contentType(["powerfx", "cel"])
 *   expression: string;
 * }
 * ```
 *
 * @example Content type with XML element
 * ```typescript
 * model ConfigContent {
 *   @xmlElement
 *   @contentType(["yaml", "json"])
 *   configuration: string;
 * }
 * ```
 *
 * Generates (metadata in XML comments):
 * ```csharp
 * /// <summary>
 * /// Content types: json
 * /// </summary>
 * [XmlText]
 * public string Arguments { get; set; }
 * ```
 *
 * Usage in VS Code Extension:
 * - Enables syntax highlighting based on content type
 * - Provides intellisense and validation
 * - Formats code blocks appropriately
 * - Supports runtime content type detection when multiple types are specified
 */
extern dec contentType(target: ModelProperty, types: valueof string | valueof string[]);

/**
 * Specifies a custom XML type name for enum values.
 * Controls how enum values are serialized to XML.
 *
 * @param typeName The XML type name
 *
 * @example
 * ```typescript
 * @xmlTypeName("chat-role")
 * enum ChatRole {
 *   system,
 *   user,
 *   assistant,
 * }
 * ```
 *
 * Generates:
 * ```csharp
 * [XmlType("chat-role")]
 * public enum ChatRole {
 *   [XmlEnum("system")] System,
 *   [XmlEnum("user")] User,
 *   [XmlEnum("assistant")] Assistant,
 * }
 * ```
 */
extern dec xmlTypeName(target: Enum, typeName: valueof string);

/**
 * Specifies the default value for optional properties in XML.
 * Used for XSD schema generation.
 *
 * @param defaultValue The default value
 *
 * @example
 * ```typescript
 * model TextReasoningContent {
 *   kind: "reasoning";
 *   text: string;
 *
 *   @xmlDefault(false)
 *   exposed?: boolean;
 * }
 * ```
 */
extern dec xmlDefault(target: ModelProperty, defaultValue: unknown);

/**
 * Specifies the default content type when parsing unwrapped content.
 * Used when XML has plain text without explicit content element tags.
 *
 * @param contentType The default content type class name
 *
 * @example System message defaults to TextContent
 * ```typescript
 * @xmlRoot("system")
 * @defaultContentType("TextContent")
 * model SystemMessage extends ChatMessage {
 *   contents: AIContent[];
 * }
 * ```
 *
 * XML Input:
 * ```xml
 * <system>You are a helpful assistant</system>
 * ```
 *
 * Parses as:
 * ```csharp
 * new SystemMessage {
 *   Contents = new List<AIContent> {
 *     new TextContent { Text = "You are a helpful assistant" }
 *   }
 * }
 * ```
 *
 * @example Tool message defaults to FunctionResultContent
 * ```typescript
 * @xmlRoot("tool")
 * @defaultContentType("FunctionResultContent")
 * model ToolMessage extends ChatMessage {
 *   @xmlAttribute("call-id")
 *   callId?: string;
 *   contents: AIContent[];
 * }
 * ```
 *
 * XML Input:
 * ```xml
 * <tool call-id="call_001" name="get_weather">
 *   {"temperature": 72, "conditions": "sunny"}
 * </tool>
 * ```
 *
 * Parses as:
 * ```csharp
 * new ToolMessage {
 *   CallId = "call_001",
 *   Contents = new List<AIContent> {
 *     new FunctionResultContent {
 *       Result = "{\"temperature\": 72, \"conditions\": \"sunny\"}"
 *     }
 *   }
 * }
 * ```
 *
 * Generates C#:
 * ```csharp
 * [XmlRoot("system")]
 * public partial class SystemMessage : ChatMessage {
 *   // When deserializing <system>text</system>, wraps text in TextContent
 *   [XmlText]
 *   public string _InnerText {
 *     get => Contents.OfType<TextContent>().FirstOrDefault()?.Text ?? "";
 *     set => Contents = new List<AIContent> { new TextContent { Text = value } };
 *   }
 *
 *   [XmlIgnore]
 *   public List<AIContent> Contents { get; set; } = new();
 * }
 * ```
 */
extern dec defaultContentType(target: Model, contentType: valueof string);
