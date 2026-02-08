using System.Text;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates role-specific TypeScript message interfaces from ChatMessage + ChatRole enum.
/// Creates UserMessage, AgentMessage, ToolMessage, etc. with proper type discrimination.
/// </summary>
public class TypeScriptMessageGenerator
{
    private readonly string _rootNamespace;

    public TypeScriptMessageGenerator(string rootNamespace = "")
    {
        _rootNamespace = rootNamespace;
    }

    /// <summary>
    /// Generates role-specific message interfaces from ChatMessage base model.
    /// </summary>
    public List<string> GenerateRoleMessages(
        ModelDefinition chatMessageModel,
        EnumDefinition chatRoleEnum,
        string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

        // Generate ChatRole enum
        var roleEnumFile = Path.Combine(outputDirectory, "ChatRole.ts");
        var roleEnumCode = GenerateChatRoleEnum(chatRoleEnum);
        File.WriteAllText(roleEnumFile, roleEnumCode);
        generatedFiles.Add(roleEnumFile);

        // Generate base ChatMessage interface
        var baseMessageFile = Path.Combine(outputDirectory, "ChatMessage.ts");
        var baseCode = GenerateBaseChatMessage(chatMessageModel, chatRoleEnum);
        File.WriteAllText(baseMessageFile, baseCode);
        generatedFiles.Add(baseMessageFile);

        // Generate role-specific message interfaces
        foreach (var role in chatRoleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            var filePath = Path.Combine(outputDirectory, $"{roleClassName}.ts");

            var code = GenerateRoleSpecificMessage(
                chatMessageModel,
                role,
                roleClassName,
                chatRoleEnum.Name
            );

            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate message union type and helpers
        var unionFile = Path.Combine(outputDirectory, "Messages.ts");
        var unionCode = GenerateMessageUnionAndHelpers(chatMessageModel, chatRoleEnum);
        File.WriteAllText(unionFile, unionCode);
        generatedFiles.Add(unionFile);

        // Generate index file
        var indexFile = Path.Combine(outputDirectory, "index.ts");
        var indexCode = GenerateIndexFile(chatRoleEnum);
        File.WriteAllText(indexFile, indexCode);
        generatedFiles.Add(indexFile);

        return generatedFiles;
    }

    private string GenerateChatRoleEnum(EnumDefinition chatRoleEnum)
    {
        var sb = new StringBuilder();

        sb.AppendLine("/**");
        sb.AppendLine(" * Message role types");
        sb.AppendLine(" */");
        sb.AppendLine("export type ChatRole =");

        for (int i = 0; i < chatRoleEnum.Members.Count; i++)
        {
            var member = chatRoleEnum.Members[i];
            var value = member.Value ?? NamingConventions.ToCamelCase(member.Name);

            if (i == chatRoleEnum.Members.Count - 1)
            {
                sb.AppendLine($"  | '{value}';");
            }
            else
            {
                sb.AppendLine($"  | '{value}'");
            }
        }

        sb.AppendLine();
        sb.AppendLine("export const ChatRoleValues = {");
        foreach (var member in chatRoleEnum.Members)
        {
            var pascalName = NamingConventions.ToPascalCase(member.Name);
            var value = member.Value ?? NamingConventions.ToCamelCase(member.Name);
            sb.AppendLine($"  {pascalName}: '{value}' as const,");
        }
        sb.AppendLine("} as const;");

        return sb.ToString();
    }

    private string GenerateBaseChatMessage(ModelDefinition model, EnumDefinition roleEnum)
    {
        var sb = new StringBuilder();

        // Import AIContent union
        sb.AppendLine("import { AIContent } from '../content';");
        sb.AppendLine("import { ChatRole } from './ChatRole';");
        sb.AppendLine();

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(model.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {model.Documentation}");
            sb.AppendLine(" */");
        }

        // Generate base interface
        sb.AppendLine("export interface ChatMessage {");

        // Add role property with discriminator
        sb.AppendLine("  /** Message role (discriminator) */");
        sb.AppendLine("  role: ChatRole;");

        // Generate other properties (excluding role)
        foreach (var prop in model.Properties)
        {
            if (prop.Name == "role")
                continue;

            // Add property JSDoc comment
            if (!string.IsNullOrWhiteSpace(prop.Documentation))
            {
                sb.AppendLine();
                sb.AppendLine("  /**");
                sb.AppendLine($"   * {prop.Documentation}");
                sb.AppendLine("   */");
            }

            var tsType = TypeScriptModelGenerator.MapTypeSpecTypeToTypeScript(prop.Type, prop.IsArray);
            var optionalMarker = prop.IsOptional ? "?" : "";
            var propertyName = NamingConventions.ToCamelCase(prop.Name);

            sb.AppendLine($"  {propertyName}{optionalMarker}: {tsType};");
        }

        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateRoleSpecificMessage(
        ModelDefinition model,
        EnumMemberDefinition role,
        string className,
        string enumName)
    {
        var sb = new StringBuilder();

        // Imports
        sb.AppendLine("import { ChatMessage } from './ChatMessage';");
        sb.AppendLine("import { ChatRole } from './ChatRole';");
        sb.AppendLine();

        // JSDoc comment
        var roleValue = role.Value ?? NamingConventions.ToCamelCase(role.Name);
        sb.AppendLine("/**");
        sb.AppendLine($" * Message with role '{roleValue}'");
        if (!string.IsNullOrWhiteSpace(role.Documentation))
        {
            sb.AppendLine($" * {role.Documentation}");
        }
        sb.AppendLine(" */");

        // Generate interface extending base with role discriminator
        sb.AppendLine($"export interface {className} extends ChatMessage {{");
        sb.AppendLine($"  role: '{roleValue}';");

        // Add role-specific properties based on the role
        var roleSpecificProps = GetRoleSpecificProperties(roleValue);
        foreach (var (propName, propType, isOptional, comment) in roleSpecificProps)
        {
            if (comment != null)
            {
                sb.AppendLine();
                sb.AppendLine("  /**");
                sb.AppendLine($"   * {comment}");
                sb.AppendLine("   */");
            }
            var optionalMarker = isOptional ? "?" : "";
            sb.AppendLine($"  {propName}{optionalMarker}: {propType};");
        }

        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateMessageUnionAndHelpers(ModelDefinition model, EnumDefinition roleEnum)
    {
        var sb = new StringBuilder();

        // Import all message types
        foreach (var role in roleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            sb.AppendLine($"import {{ {roleClassName} }} from './{roleClassName}';");
        }
        sb.AppendLine();

        // Generate discriminated union
        sb.AppendLine("/**");
        sb.AppendLine(" * Discriminated union of all message types");
        sb.AppendLine(" */");
        sb.Append("export type Message =");

        for (int i = 0; i < roleEnum.Members.Count; i++)
        {
            var role = roleEnum.Members[i];
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";

            if (i == 0)
            {
                sb.AppendLine($" {roleClassName}");
            }
            else if (i == roleEnum.Members.Count - 1)
            {
                sb.AppendLine($"  | {roleClassName};");
            }
            else
            {
                sb.AppendLine($"  | {roleClassName}");
            }
        }

        sb.AppendLine();
        sb.AppendLine("// Type guards");
        sb.AppendLine();

        // Generate type guards
        foreach (var role in roleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            var roleValue = role.Value ?? NamingConventions.ToCamelCase(role.Name);
            var functionName = $"is{roleClassName}";

            sb.AppendLine("/**");
            sb.AppendLine($" * Type guard to check if message is {roleClassName}");
            sb.AppendLine(" */");
            sb.AppendLine($"export function {functionName}(message: Message): message is {roleClassName} {{");
            sb.AppendLine($"  return message.role === '{roleValue}';");
            sb.AppendLine("}");
            sb.AppendLine();
        }

        // Generate helper functions
        sb.AppendLine("/**");
        sb.AppendLine(" * Filter messages by role");
        sb.AppendLine(" */");
        sb.AppendLine("export function filterMessagesByRole<R extends Message['role']>(");
        sb.AppendLine("  messages: Message[],");
        sb.AppendLine("  role: R");
        sb.AppendLine("): Extract<Message, { role: R }>[] {");
        sb.AppendLine("  return messages.filter((m) => m.role === role) as any;");
        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateIndexFile(EnumDefinition roleEnum)
    {
        var sb = new StringBuilder();

        sb.AppendLine("/**");
        sb.AppendLine(" * Message types - role-based discriminated union");
        sb.AppendLine(" * Generated from TypeSpec definitions");
        sb.AppendLine(" */");
        sb.AppendLine();

        // Export ChatRole
        sb.AppendLine("export * from './ChatRole';");

        // Export base ChatMessage
        sb.AppendLine("export * from './ChatMessage';");

        // Export all role-specific messages
        foreach (var role in roleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            sb.AppendLine($"export * from './{roleClassName}';");
        }

        // Export union and helpers
        sb.AppendLine("export * from './Messages';");

        return sb.ToString();
    }

    /// <summary>
    /// Returns role-specific properties based on the role type.
    /// </summary>
    private List<(string propName, string propType, bool isOptional, string? comment)> GetRoleSpecificProperties(string roleValue)
    {
        return roleValue switch
        {
            "user" => new List<(string, string, bool, string?)>
            {
                ("userId", "string", true, "User identifier")
            },
            "agent" or "assistant" => new List<(string, string, bool, string?)>
            {
                ("agentId", "string", true, "Agent identifier"),
                ("completionId", "string", true, "Completion/run identifier"),
                ("completedAt", "string", true, "When the agent completed this message")
            },
            "tool" => new List<(string, string, bool, string?)>
            {
                ("toolCallId", "string", true, "Tool call identifier this result corresponds to")
            },
            "channel" => new List<(string, string, bool, string?)>
            {
                ("channelId", "string", true, "Channel identifier"),
                ("externalConversationId", "string", true, "External conversation ID from the channel")
            },
            _ => new List<(string, string, bool, string?)>()
        };
    }
}
