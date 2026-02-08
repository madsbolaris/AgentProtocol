using System.Text;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates role-specific Python message classes from ChatMessage + ChatRole enum.
/// Creates UserMessage, AgentMessage, ToolMessage, etc. with proper inheritance.
/// </summary>
public class PythonMessageGenerator
{
    private readonly string _rootNamespace;

    public PythonMessageGenerator(string rootNamespace = "")
    {
        _rootNamespace = rootNamespace;
    }

    /// <summary>
    /// Generates role-specific message classes from ChatMessage base model.
    /// </summary>
    public List<string> GenerateRoleMessages(
        ModelDefinition chatMessageModel,
        EnumDefinition chatRoleEnum,
        string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

        // Generate ChatRole enum
        var roleEnumFile = Path.Combine(outputDirectory, "chat_role.py");
        var roleEnumCode = GenerateChatRoleEnum(chatRoleEnum);
        File.WriteAllText(roleEnumFile, roleEnumCode);
        generatedFiles.Add(roleEnumFile);

        // Generate base ChatMessage class
        var baseMessageFile = Path.Combine(outputDirectory, "chat_message.py");
        var baseCode = GenerateBaseChatMessage(chatMessageModel, chatRoleEnum);
        File.WriteAllText(baseMessageFile, baseCode);
        generatedFiles.Add(baseMessageFile);

        // Generate role-specific message classes
        foreach (var role in chatRoleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            var fileName = NamingConventions.ToSnakeCase(roleClassName);
            var filePath = Path.Combine(outputDirectory, $"{fileName}.py");

            var code = GenerateRoleSpecificMessage(
                chatMessageModel,
                role,
                roleClassName
            );

            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Update __init__.py
        var initFile = Path.Combine(outputDirectory, "__init__.py");
        var initCode = GenerateInitFile(chatRoleEnum);
        File.WriteAllText(initFile, initCode);
        generatedFiles.Add(initFile);

        return generatedFiles;
    }

    private string GenerateChatRoleEnum(EnumDefinition chatRoleEnum)
    {
        var sb = new StringBuilder();

        sb.AppendLine("# Copyright (c) Microsoft Corporation. All rights reserved.");
        sb.AppendLine("# Licensed under the MIT License.");
        sb.AppendLine();
        sb.AppendLine("\"\"\"");
        sb.AppendLine("Generated from TypeSpec definitions.");
        sb.AppendLine("DO NOT EDIT MANUALLY");
        sb.AppendLine("\"\"\"");
        sb.AppendLine();
        sb.AppendLine("from enum import Enum");
        sb.AppendLine("from typing import Literal");
        sb.AppendLine();
        sb.AppendLine();
        sb.AppendLine("class ChatRole(str, Enum):");
        sb.AppendLine("    \"\"\"Message role types.\"\"\"");

        foreach (var member in chatRoleEnum.Members)
        {
            var pythonName = NamingConventions.ToUpperSnakeCase(member.Name);
            var value = member.Value ?? NamingConventions.ToCamelCase(member.Name);
            sb.AppendLine($"    {pythonName} = \"{value}\"");
        }

        sb.AppendLine();
        sb.AppendLine();

        // Generate type alias
        var literalValues = string.Join(", ", chatRoleEnum.Members.Select(m =>
        {
            var value = m.Value ?? NamingConventions.ToCamelCase(m.Name);
            return $"\"{value}\"";
        }));
        sb.AppendLine($"ChatRoleType = Literal[{literalValues}]");

        return sb.ToString();
    }

    private string GenerateBaseChatMessage(ModelDefinition chatMessageModel, EnumDefinition chatRoleEnum)
    {
        var sb = new StringBuilder();

        sb.AppendLine("# Copyright (c) Microsoft Corporation. All rights reserved.");
        sb.AppendLine("# Licensed under the MIT License.");
        sb.AppendLine();
        sb.AppendLine("\"\"\"");
        sb.AppendLine("Generated from TypeSpec definitions.");
        sb.AppendLine("DO NOT EDIT MANUALLY");
        sb.AppendLine("\"\"\"");
        sb.AppendLine();
        sb.AppendLine("from abc import ABC, abstractmethod");
        sb.AppendLine("from dataclasses import dataclass, field");
        sb.AppendLine("from typing import Optional, List, Dict, Any");
        sb.AppendLine("from datetime import datetime");
        sb.AppendLine();
        sb.AppendLine("from .chat_role import ChatRole");
        sb.AppendLine();
        sb.AppendLine();
        sb.AppendLine("@dataclass");
        sb.AppendLine("class ChatMessage(ABC):");

        if (!string.IsNullOrWhiteSpace(chatMessageModel.Documentation))
        {
            sb.AppendLine("    \"\"\"");
            sb.AppendLine($"    {chatMessageModel.Documentation}");
            sb.AppendLine("    \"\"\"");
        }

        // Generate properties
        foreach (var prop in chatMessageModel.Properties)
        {
            // Skip the 'role' property as it will be abstract
            if (prop.Name.Equals("role", StringComparison.OrdinalIgnoreCase))
                continue;

            var pythonType = PythonModelGenerator.MapTypeSpecTypeToPython(prop.Type, prop.IsArray, prop.IsOptional);
            var propertyName = NamingConventions.ToSnakeCase(prop.Name);

            if (prop.IsOptional)
            {
                sb.AppendLine($"    {propertyName}: {pythonType} = None");
            }
            else if (prop.IsArray)
            {
                sb.AppendLine($"    {propertyName}: {pythonType} = field(default_factory=list)");
            }
            else if (pythonType.Contains("Dict"))
            {
                sb.AppendLine($"    {propertyName}: {pythonType} = field(default_factory=dict)");
            }
            else
            {
                sb.AppendLine($"    {propertyName}: {pythonType}");
            }
        }

        sb.AppendLine();
        sb.AppendLine("    @property");
        sb.AppendLine("    @abstractmethod");
        sb.AppendLine("    def role(self) -> ChatRole:");
        sb.AppendLine("        \"\"\"The role of the message sender.\"\"\"");
        sb.AppendLine("        ...");

        return sb.ToString();
    }

    private string GenerateRoleSpecificMessage(
        ModelDefinition chatMessageModel,
        EnumMemberDefinition role,
        string roleClassName)
    {
        var sb = new StringBuilder();

        sb.AppendLine("# Copyright (c) Microsoft Corporation. All rights reserved.");
        sb.AppendLine("# Licensed under the MIT License.");
        sb.AppendLine();
        sb.AppendLine("\"\"\"");
        sb.AppendLine("Generated from TypeSpec definitions.");
        sb.AppendLine("DO NOT EDIT MANUALLY");
        sb.AppendLine("\"\"\"");
        sb.AppendLine();
        sb.AppendLine("from dataclasses import dataclass");
        sb.AppendLine();
        sb.AppendLine("from .chat_message import ChatMessage");
        sb.AppendLine("from .chat_role import ChatRole");
        sb.AppendLine();
        sb.AppendLine();
        sb.AppendLine("@dataclass");
        sb.AppendLine($"class {roleClassName}(ChatMessage):");
        sb.AppendLine($"    \"\"\"");
        sb.AppendLine($"    Message with role '{role.Name}'.\"");
        sb.AppendLine($"    \"\"\"");
        sb.AppendLine();
        sb.AppendLine("    @property");
        sb.AppendLine("    def role(self) -> ChatRole:");

        var rolePythonName = NamingConventions.ToUpperSnakeCase(role.Name);
        sb.AppendLine($"        return ChatRole.{rolePythonName}");

        return sb.ToString();
    }

    private string GenerateInitFile(EnumDefinition chatRoleEnum)
    {
        var sb = new StringBuilder();

        sb.AppendLine("# Copyright (c) Microsoft Corporation. All rights reserved.");
        sb.AppendLine("# Licensed under the MIT License.");
        sb.AppendLine();
        sb.AppendLine("\"\"\"");
        sb.AppendLine("Generated message models from TypeSpec definitions.");
        sb.AppendLine("DO NOT EDIT MANUALLY");
        sb.AppendLine("\"\"\"");
        sb.AppendLine();

        sb.AppendLine("from .chat_role import ChatRole, ChatRoleType");
        sb.AppendLine("from .chat_message import ChatMessage");

        var allExports = new List<string> { "ChatRole", "ChatRoleType", "ChatMessage" };

        foreach (var role in chatRoleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            var fileName = NamingConventions.ToSnakeCase(roleClassName);
            sb.AppendLine($"from .{fileName} import {roleClassName}");
            allExports.Add(roleClassName);
        }

        sb.AppendLine();
        sb.AppendLine("__all__ = [");
        foreach (var export in allExports)
        {
            sb.AppendLine($"    \"{export}\",");
        }
        sb.AppendLine("]");

        return sb.ToString();
    }
}
