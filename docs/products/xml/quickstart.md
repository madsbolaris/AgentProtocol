# XML Quickstart

Get started with XML message serialization and validation in 15 minutes.

## Overview

This quickstart shows you how to serialize Agent Protocol messages to XML, validate them against the schema, and use EvalXML for testing.

---

## Installation

=== "Python"
    ```bash
    pip install microsoft-agents-xml
    ```

=== "TypeScript"
    ```bash
    npm install @microsoft/agents-xml
    ```

=== ".NET"
    ```bash
    dotnet add package Microsoft.Agents.Xml
    ```

---

## Serialize a Message

=== "Python"
    ```python
    from microsoft.agents.xml import MessageSerializer
    from microsoft.agents.models import UserMessage, TextContent
    
    # Create a message
    message = UserMessage(
        role="user",
        content=[TextContent(text="Hello, agent!")]
    )
    
    # Serialize to XML
    serializer = MessageSerializer()
    xml = serializer.serialize(message)
    print(xml)
    ```

=== "TypeScript"
    ```typescript
    import { MessageSerializer } from '@microsoft/agents-xml';
    import { UserMessage, TextContent } from '@microsoft/agents-protocol';
    
    // Create a message
    const message: UserMessage = {
      role: 'user',
      content: [{ type: 'text', text: 'Hello, agent!' }]
    };
    
    // Serialize to XML
    const serializer = new MessageSerializer();
    const xml = serializer.serialize(message);
    console.log(xml);
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Xml;
    using Microsoft.Agents.Protocol.Abstractions.Models;
    
    // Create a message
    var message = new UserMessage
    {
        Role = "user",
        Content = new[] { new TextContent { Text = "Hello, agent!" } }
    };
    
    // Serialize to XML
    var serializer = new MessageSerializer();
    var xml = serializer.Serialize(message);
    Console.WriteLine(xml);
    ```

---

## Validate XML

=== "Python"
    ```python
    from microsoft.agents.validation import ThreadValidator
    
    # Validate XML against schema
    validator = ThreadValidator()
    errors = validator.validate(xml_string)
    
    if errors:
        for error in errors:
            print(f"Error: {error.message} at line {error.line}")
    else:
        print("XML is valid!")
    ```

=== "TypeScript"
    ```typescript
    import { ThreadValidator } from '@microsoft/agents-xml';
    
    // Validate XML against schema
    const validator = new ThreadValidator();
    const errors = validator.validate(xmlString);
    
    if (errors.length > 0) {
        errors.forEach(error => {
            console.log(`Error: ${error.message} at line ${error.line}`);
        });
    } else {
        console.log('XML is valid!');
    }
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Validation;
    
    // Validate XML against schema
    var validator = new ThreadValidator();
    var errors = validator.Validate(xmlString);
    
    if (errors.Any())
    {
        foreach (var error in errors)
        {
            Console.WriteLine($"Error: {error.Message} at line {error.Line}");
        }
    }
    else
    {
        Console.WriteLine("XML is valid!");
    }
    ```

---

## EvalXML for Testing

EvalXML is a special format for writing test cases with expected inputs and outputs.

=== "Python"
    ```python
    from microsoft.agents.xml import EvalXMLPreprocessor
    
    # Preprocess EvalXML file
    preprocessor = EvalXMLPreprocessor()
    thread = preprocessor.process_file("test_cases.evalxml")
    
    # Use in tests
    for message in thread.messages:
        print(f"{message.role}: {message.content}")
    ```

=== "TypeScript"
    ```typescript
    import { EvalXMLPreprocessor } from '@microsoft/agents-xml';
    
    // Preprocess EvalXML file
    const preprocessor = new EvalXMLPreprocessor();
    const thread = preprocessor.processFile('test_cases.evalxml');
    
    // Use in tests
    thread.messages.forEach(message => {
        console.log(`${message.role}: ${message.content}`);
    });
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Xml;
    
    // Preprocess EvalXML file
    var preprocessor = new EvalXMLPreprocessor();
    var thread = preprocessor.ProcessFile("test_cases.evalxml");
    
    // Use in tests
    foreach (var message in thread.Messages)
    {
        Console.WriteLine($"{message.Role}: {message.Content}");
    }
    ```

---

## Next Steps

- [Core Concepts](core-concepts/index.md) - Understand XML format
- [API Reference](api-reference/index.md) - Detailed API docs
- [Cookbooks](cookbooks/index.md) - Practical examples
- [Tutorials](tutorials/index.md) - Step-by-step guides

---

## See Also

- [Getting Started](getting-started.md)
- [How-To Guides](how-to-guides/index.md)
