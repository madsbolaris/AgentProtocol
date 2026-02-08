using System.CommandLine;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.RoslynGenerator;

namespace Microsoft.Agents.CodeGen;

/// <summary>
/// Entry point for the Agents code generator.
/// Generates C# models and serialization code from TypeSpec definitions.
/// </summary>
public class Program
{
    public static async Task<int> Main(string[] args)
    {
        var typeSpecFileOption = new Option<FileInfo>(
            name: "--typespec",
            description: "Path to TypeSpec file (e.g., ../typespec/messages.tsp)")
        {
            IsRequired = true
        };
        typeSpecFileOption.AddAlias("-t");

        var outputDirOption = new Option<DirectoryInfo>(
            name: "--output",
            description: "Output directory for generated code",
            getDefaultValue: () => new DirectoryInfo("./Generated"));
        outputDirOption.AddAlias("-o");

        var namespaceOption = new Option<string>(
            name: "--namespace",
            description: "Root namespace for generated code",
            getDefaultValue: () => "AgentXml.Generated");
        namespaceOption.AddAlias("-n");

        var languageOption = new Option<string>(
            name: "--language",
            description: "Target language (csharp, typescript, or python)",
            getDefaultValue: () => "csharp");
        languageOption.AddAlias("-l");

        var rootCommand = new RootCommand("Agents Code Generator - Generate C#, TypeScript, or Python models from TypeSpec")
        {
            typeSpecFileOption,
            outputDirOption,
            namespaceOption,
            languageOption
        };

        rootCommand.SetHandler(async (typeSpecFile, outputDir, rootNamespace, language) =>
        {
            // Always generate both XML and JSON serialization
            await GenerateCode(typeSpecFile, outputDir, rootNamespace, language, SerializationMode.Both);
        }, typeSpecFileOption, outputDirOption, namespaceOption, languageOption);

        return await rootCommand.InvokeAsync(args);
    }

    static async Task GenerateCode(FileInfo typeSpecFile, DirectoryInfo outputDir, string rootNamespace, string language, SerializationMode serialization)
    {
        Console.WriteLine($"Agents Code Generator");
        Console.WriteLine($"=====================");
        Console.WriteLine($"TypeSpec:  {typeSpecFile.FullName}");
        Console.WriteLine($"Output:    {outputDir.FullName}");
        Console.WriteLine($"Namespace: {rootNamespace}");
        Console.WriteLine($"Language:  {language}");
        Console.WriteLine($"Note:      Generates both XML and JSON serialization attributes");
        Console.WriteLine();

        // Step 1: Parse TypeSpec file
        Console.WriteLine("📖 Parsing TypeSpec...");
        var parser = new TypeSpecReader();
        var typeSpecModel = await parser.ParseFileAsync(typeSpecFile.FullName);
        Console.WriteLine($"   ✓ Found {typeSpecModel.Models.Count} models");
        Console.WriteLine($"   ✓ Found {typeSpecModel.Enums.Count} enums");
        Console.WriteLine($"   ✓ Found {typeSpecModel.Unions.Count} unions");
        Console.WriteLine();

        // Step 2: Generate code based on target language
        var generatedFiles = new List<string>();

        if (language.ToLower() == "python")
        {
            Console.WriteLine("🔧 Generating Python code...");
            generatedFiles = await GeneratePython(typeSpecModel, outputDir.FullName, rootNamespace);
        }
        else if (language.ToLower() == "typescript")
        {
            Console.WriteLine("🔧 Generating TypeScript code...");
            generatedFiles = await GenerateTypeScript(typeSpecModel, outputDir.FullName, rootNamespace);
        }
        else
        {
            Console.WriteLine("🔧 Generating C# code with Roslyn...");
            generatedFiles = GenerateCSharp(typeSpecModel, outputDir.FullName, rootNamespace, serialization);
        }

        Console.WriteLine($"   ✓ Total: {generatedFiles.Count} files generated");
        Console.WriteLine();

        // Step 3: Generate XML schema (XSD)
        Console.WriteLine("📝 Generating XML schema...");
        var schemaGenerator = new XmlSchemaGenerator.XsdGenerator();
        var schemaFile = schemaGenerator.GenerateSchema(typeSpecModel, outputDir.FullName);
        Console.WriteLine($"   ✓ Generated {Path.GetFileName(schemaFile)}");
        Console.WriteLine();

        Console.WriteLine("✅ Code generation complete!");
    }

    static List<string> GenerateCSharp(TypeSpecModel typeSpecModel, string outputDir, string rootNamespace, SerializationMode serialization = SerializationMode.Both)
    {
        var generatedFiles = new List<string>();

        // Check if this is a message + content model (has ChatMessage and ChatRole)
        var chatMessageModel = typeSpecModel.Models.FirstOrDefault(m => m.Name == "ChatMessage");
        var chatRoleEnum = typeSpecModel.Enums.FirstOrDefault(e => e.Name == "ChatRole");
        var aiContentUnion = typeSpecModel.Unions.FirstOrDefault(u => u.Name == "AIContent");

        if (chatMessageModel != null && chatRoleEnum != null)
        {
            Console.WriteLine("   📨 Detected message pattern - generating role-specific messages");
            var messageGenerator = new MessageInheritanceGenerator(rootNamespace, serialization);
            var messageFiles = messageGenerator.GenerateRoleMessages(
                chatMessageModel,
                chatRoleEnum,
                outputDir
            );
            generatedFiles.AddRange(messageFiles);
            Console.WriteLine($"   ✓ Generated {messageFiles.Count} message classes");
        }

        if (aiContentUnion != null)
        {
            Console.WriteLine("   📦 Detected content union - generating content types");
            var contentModels = typeSpecModel.Models
                .Where(m => m.Name.EndsWith("Content"))
                .ToList();

            var contentGenerator = new ContentTypeGenerator(rootNamespace, serialization);
            var contentFiles = contentGenerator.GenerateContentTypes(
                aiContentUnion,
                contentModels,
                outputDir
            );
            generatedFiles.AddRange(contentFiles);
            Console.WriteLine($"   ✓ Generated {contentFiles.Count} content types");
        }

        // Generate remaining models (non-message, non-content) and all enums
        var generator = new CSharpModelGenerator(rootNamespace, serialization);
        var remainingModels = new TypeSpecModel
        {
            Namespace = typeSpecModel.Namespace,
            Models = typeSpecModel.Models
                .Where(m => m.Name != "ChatMessage" && !m.Name.EndsWith("Content"))
                .ToList(),
            Enums = typeSpecModel.Enums,  // Include all enums (including ChatRole)
            Unions = typeSpecModel.Unions
                .Where(u => u.Name != "AIContent")
                .ToList()
        };

        if (remainingModels.Models.Any() || remainingModels.Enums.Any())
        {
            var otherFiles = generator.GenerateModels(remainingModels, outputDir);
            generatedFiles.AddRange(otherFiles);
            Console.WriteLine($"   ✓ Generated {otherFiles.Count} additional files");
        }

        return generatedFiles;
    }

    static async Task<List<string>> GenerateTypeScript(TypeSpecModel typeSpecModel, string outputDir, string rootNamespace)
    {
        var generatedFiles = new List<string>();

        // Create output subdirectories
        var contentDir = Path.Combine(outputDir, "content");
        var messageDir = Path.Combine(outputDir, "messages");
        var commonDir = Path.Combine(outputDir, "common");

        Directory.CreateDirectory(contentDir);
        Directory.CreateDirectory(messageDir);
        Directory.CreateDirectory(commonDir);

        // Check for specialized patterns
        var chatMessageModel = typeSpecModel.Models.FirstOrDefault(m => m.Name == "ChatMessage");
        var chatRoleEnum = typeSpecModel.Enums.FirstOrDefault(e => e.Name == "ChatRole");
        var aiContentUnion = typeSpecModel.Unions.FirstOrDefault(u => u.Name == "AIContent");

        if (chatMessageModel != null && chatRoleEnum != null)
        {
            Console.WriteLine("   📨 Detected message pattern - generating role-specific messages");
            var messageGenerator = new TypeScriptMessageGenerator(rootNamespace);
            var messageFiles = messageGenerator.GenerateRoleMessages(
                chatMessageModel,
                chatRoleEnum,
                messageDir
            );
            generatedFiles.AddRange(messageFiles);
            Console.WriteLine($"   ✓ Generated {messageFiles.Count} message types");
        }

        if (aiContentUnion != null)
        {
            Console.WriteLine("   📦 Detected content union - generating content types");
            var contentModels = typeSpecModel.Models
                .Where(m => m.Name.EndsWith("Content"))
                .ToList();

            var contentGenerator = new TypeScriptContentTypeGenerator(rootNamespace);
            var contentFiles = contentGenerator.GenerateContentTypes(
                aiContentUnion,
                contentModels,
                contentDir
            );
            generatedFiles.AddRange(contentFiles);
            Console.WriteLine($"   ✓ Generated {contentFiles.Count} content types");
        }

        // Generate remaining models, enums, and unions
        var generator = new TypeScriptModelGenerator(rootNamespace);
        var remainingModels = new TypeSpecModel
        {
            Namespace = typeSpecModel.Namespace,
            Models = typeSpecModel.Models
                .Where(m => m.Name != "ChatMessage" && !m.Name.EndsWith("Content"))
                .ToList(),
            Enums = typeSpecModel.Enums.Where(e => e.Name != "ChatRole").ToList(),
            Unions = typeSpecModel.Unions.Where(u => u.Name != "AIContent").ToList()
        };

        if (remainingModels.Models.Any() || remainingModels.Enums.Any() || remainingModels.Unions.Any())
        {
            var otherFiles = generator.GenerateModels(remainingModels, commonDir);
            generatedFiles.AddRange(otherFiles);
            Console.WriteLine($"   ✓ Generated {otherFiles.Count} common types");
        }

        // Generate root index.ts
        var rootIndexPath = Path.Combine(outputDir, "index.ts");
        var rootIndexCode = @"/**
 * Generated TypeScript types from TypeSpec definitions
 * DO NOT EDIT MANUALLY
 */

export * from './content';
export * from './messages';
export * from './common';
";
        File.WriteAllText(rootIndexPath, rootIndexCode);
        generatedFiles.Add(rootIndexPath);

        return await Task.FromResult(generatedFiles);
    }

    static async Task<List<string>> GeneratePython(TypeSpecModel typeSpecModel, string outputDir, string rootNamespace)
    {
        var generatedFiles = new List<string>();

        // Python doesn't use subdirectories like TypeScript - all files go in the models directory
        Directory.CreateDirectory(outputDir);

        // Check for specialized patterns
        var chatMessageModel = typeSpecModel.Models.FirstOrDefault(m => m.Name == "ChatMessage");
        var chatRoleEnum = typeSpecModel.Enums.FirstOrDefault(e => e.Name == "ChatRole");
        var aiContentUnion = typeSpecModel.Unions.FirstOrDefault(u => u.Name == "AIContent");

        if (chatMessageModel != null && chatRoleEnum != null)
        {
            Console.WriteLine("   📨 Detected message pattern - generating role-specific messages");
            var messageGenerator = new PythonMessageGenerator(rootNamespace);
            var messageFiles = messageGenerator.GenerateRoleMessages(
                chatMessageModel,
                chatRoleEnum,
                outputDir
            );
            generatedFiles.AddRange(messageFiles);
            Console.WriteLine($"   ✓ Generated {messageFiles.Count} message classes");
        }

        if (aiContentUnion != null)
        {
            Console.WriteLine("   📦 Detected content union - generating content types");
            var contentModels = typeSpecModel.Models
                .Where(m => m.Name.EndsWith("Content"))
                .ToList();

            var contentGenerator = new PythonContentTypeGenerator(rootNamespace);
            var contentFiles = contentGenerator.GenerateContentTypes(
                aiContentUnion,
                contentModels,
                outputDir
            );
            generatedFiles.AddRange(contentFiles);
            Console.WriteLine($"   ✓ Generated {contentFiles.Count} content types");
        }

        // Generate remaining models, enums, and unions
        var generator = new PythonModelGenerator(rootNamespace);
        var remainingModels = new TypeSpecModel
        {
            Namespace = typeSpecModel.Namespace,
            Models = typeSpecModel.Models
                .Where(m => m.Name != "ChatMessage" && !m.Name.EndsWith("Content"))
                .ToList(),
            Enums = typeSpecModel.Enums.Where(e => e.Name != "ChatRole").ToList(),
            Unions = typeSpecModel.Unions.Where(u => u.Name != "AIContent").ToList()
        };

        if (remainingModels.Models.Any() || remainingModels.Enums.Any() || remainingModels.Unions.Any())
        {
            var otherFiles = generator.GenerateModels(remainingModels, outputDir);
            generatedFiles.AddRange(otherFiles);
            Console.WriteLine($"   ✓ Generated {otherFiles.Count} common types");
        }

        return await Task.FromResult(generatedFiles);
    }
}
