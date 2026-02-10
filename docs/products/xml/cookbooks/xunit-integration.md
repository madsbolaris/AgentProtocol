# xUnit Integration

Use XML serialization and validation in xUnit test suites.

## Overview

This cookbook shows how to integrate XML message validation into xUnit tests for .NET/C# applications.

---

## Test Structure

```
MyApp.Tests/
├── TestData/
│   ├── Input/          # Input XML files
│   └── Expected/       # Expected output XML files
├── Fixtures/
│   └── TestFixture.cs  # Test fixtures
└── MessageTests.cs     # Message tests
```

---

## Installation

```bash
dotnet add package xunit
dotnet add package xunit.runner.visualstudio
dotnet add package Microsoft.Agents.Xml
dotnet add package FluentAssertions  # Optional but recommended
```

---

## Complete Test Example

### Fixtures/TestFixture.cs - Test Fixtures

```csharp
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Agents.Xml;
using Microsoft.Agents.Validation;

namespace Microsoft.Agents.Tests.Fixtures
{
    public class XmlTestFixture : IDisposable
    {
        public MessageSerializer Serializer { get; }
        public ThreadValidator Validator { get; }
        public string TestDataPath { get; }

        public XmlTestFixture()
        {
            Serializer = new MessageSerializer();
            Validator = new ThreadValidator();
            TestDataPath = Path.Combine(
                Directory.GetCurrentDirectory(),
                "TestData"
            );
        }

        public string LoadXml(string filename, string subdir = "Input")
        {
            var filePath = Path.Combine(TestDataPath, subdir, filename);
            return File.ReadAllText(filePath);
        }

        public IEnumerable<TestCase> LoadTestCases()
        {
            var inputDir = Path.Combine(TestDataPath, "Input");
            var expectedDir = Path.Combine(TestDataPath, "Expected");

            foreach (var inputFile in Directory.GetFiles(inputDir, "*.xml"))
            {
                var filename = Path.GetFileName(inputFile);
                var expectedFile = Path.Combine(expectedDir, filename);

                if (File.Exists(expectedFile))
                {
                    yield return new TestCase
                    {
                        Name = Path.GetFileNameWithoutExtension(filename),
                        Input = File.ReadAllText(inputFile),
                        Expected = File.ReadAllText(expectedFile)
                    };
                }
            }
        }

        public void Dispose()
        {
            // Cleanup if needed
        }
    }

    public class TestCase
    {
        public string Name { get; set; }
        public string Input { get; set; }
        public string Expected { get; set; }
    }
}
```

### MessageTests.cs - Message Tests

```csharp
using System;
using System.Linq;
using Xunit;
using FluentAssertions;
using Microsoft.Agents.Xml;
using Microsoft.Agents.Validation;
using Microsoft.Agents.Protocol.Abstractions.Models;
using Microsoft.Agents.Tests.Fixtures;

namespace Microsoft.Agents.Tests
{
    public class XmlMessageSerializationTests : IClassFixture<XmlTestFixture>
    {
        private readonly XmlTestFixture _fixture;

        public XmlMessageSerializationTests(XmlTestFixture fixture)
        {
            _fixture = fixture;
        }

        [Fact]
        public void SerializeUserMessage_ProducesValidXml()
        {
            // Arrange
            var message = new UserMessage
            {
                Role = "user",
                Content = new[] { new TextContent { Text = "Hello, agent!" } }
            };

            // Act
            var xml = _fixture.Serializer.Serialize(message);

            // Assert
            xml.Should().NotBeNull();
            xml.Should().Contain("<?xml");
            xml.Should().Contain("<user-message");
            xml.Should().Contain("Hello, agent!");
        }

        [Fact]
        public void SerializeAgentMessage_ProducesValidXml()
        {
            // Arrange
            var message = new AgentMessage
            {
                Role = "agent",
                Content = new[] { new TextContent { Text = "Hello, user!" } }
            };

            // Act
            var xml = _fixture.Serializer.Serialize(message);

            // Assert
            xml.Should().NotBeNull();
            xml.Should().Contain("<agent-message");
            xml.Should().Contain("Hello, user!");
        }

        [Fact]
        public void RoundtripSerialization_PreservesMessageData()
        {
            // Arrange
            var original = new UserMessage
            {
                Role = "user",
                Content = new[] { new TextContent { Text = "Test message" } }
            };

            // Act
            var xml = _fixture.Serializer.Serialize(original);
            var deserialized = _fixture.Serializer.Deserialize<UserMessage>(xml);

            // Assert
            deserialized.Role.Should().Be(original.Role);
            deserialized.Content.Should().HaveCount(original.Content.Length);
            deserialized.Content[0].Text.Should().Be(original.Content[0].Text);
        }

        [Fact]
        public void SerializeMultimodalContent_IncludesAllContentTypes()
        {
            // Arrange
            var message = new UserMessage
            {
                Role = "user",
                Content = new AIContentBase[]
                {
                    new TextContent { Text = "Look at this:" },
                    new ImageContent { Url = "https://example.com/image.jpg" }
                }
            };

            // Act
            var xml = _fixture.Serializer.Serialize(message);

            // Assert
            xml.Should().Contain("<text>");
            xml.Should().Contain("<image");
            xml.Should().Contain("https://example.com/image.jpg");
        }
    }

    public class XmlValidationTests : IClassFixture<XmlTestFixture>
    {
        private readonly XmlTestFixture _fixture;

        public XmlValidationTests(XmlTestFixture fixture)
        {
            _fixture = fixture;
        }

        [Fact]
        public void ValidateValidXml_ReturnsNoErrors()
        {
            // Arrange
            var validXml = _fixture.LoadXml("basic_message.xml");

            // Act
            var errors = _fixture.Validator.Validate(validXml);

            // Assert
            errors.Should().BeEmpty();
        }

        [Fact]
        public void ValidateInvalidXml_ReturnsErrors()
        {
            // Arrange
            var invalidXml = "<invalid>Not a valid message</invalid>";

            // Act
            var errors = _fixture.Validator.Validate(invalidXml);

            // Assert
            errors.Should().NotBeEmpty();
            errors.First().Message.Should().Contain("schema", 
                Because: "error should reference schema validation");
        }

        [Theory]
        [MemberData(nameof(GetTestDataFiles))]
        public void ValidateTestDataFile_IsValid(string filename)
        {
            // Arrange
            var xml = _fixture.LoadXml(filename);

            // Act
            var errors = _fixture.Validator.Validate(xml);

            // Assert
            errors.Should().BeEmpty($"{filename} should be valid XML");
        }

        public static IEnumerable<object[]> GetTestDataFiles()
        {
            var testDataPath = Path.Combine(
                Directory.GetCurrentDirectory(),
                "TestData", "Input"
            );

            return Directory.GetFiles(testDataPath, "*.xml")
                .Select(f => new object[] { Path.GetFileName(f) });
        }

        [Fact]
        public void ValidationError_ContainsDetailedInformation()
        {
            // Arrange
            var invalidXml = @"
                <?xml version=""1.0""?>
                <thread xmlns=""urn:messages"">
                    <unknown-element>Invalid</unknown-element>
                </thread>
            ";

            // Act
            var errors = _fixture.Validator.Validate(invalidXml);

            // Assert
            errors.Should().NotBeEmpty();
            errors.First().Should().Match<ValidationError>(e =>
                e.Message != null && e.Line > 0
            );
        }
    }

    public class EvalXmlPreprocessingTests
    {
        private readonly EvalXmlPreprocessor _preprocessor;

        public EvalXmlPreprocessingTests()
        {
            _preprocessor = new EvalXmlPreprocessor();
        }

        [Fact]
        public void PreprocessAssertBlock_WrapsInCDATA()
        {
            // Arrange
            var input = "<assert>x == 5</assert>";

            // Act
            var result = _preprocessor.Preprocess(input);

            // Assert
            result.Should().Be("<assert><![CDATA[x == 5]]></assert>");
        }

        [Fact]
        public void PreprocessMetricComparison_ProtectsOperators()
        {
            // Arrange
            var input = "<metric>x > 5 && y < 10</metric>";

            // Act
            var result = _preprocessor.Preprocess(input);

            // Assert
            result.Should().Contain("<![CDATA[");
            result.Should().Contain("x > 5 && y < 10");
            result.Should().Contain("]]>");
        }

        [Theory]
        [InlineData("<assert>x == 1</assert>", "<assert><![CDATA[x == 1]]></assert>")]
        [InlineData("<metric>y > 0</metric>", "<metric><![CDATA[y > 0]]></metric>")]
        [InlineData("<result>true</result>", "<result>true</result>")]
        public void PreprocessVariousBlocks_HandlesCorrectly(string input, string expected)
        {
            // Act
            var result = _preprocessor.Preprocess(input);

            // Assert
            result.Should().Be(expected);
        }

        [Fact]
        public void PreprocessSpecialCharacters_ProtectsXmlEntities()
        {
            // Arrange
            var input = @"<args>{""name"": ""test"", ""value"": ""x < 5 && y > 3""}</args>";

            // Act
            var result = _preprocessor.Preprocess(input);

            // Assert
            result.Should().Contain("<![CDATA[");
            result.Should().Contain("x < 5 && y > 3");
        }
    }

    public class IntegrationTests : IClassFixture<XmlTestFixture>
    {
        private readonly XmlTestFixture _fixture;

        public IntegrationTests(XmlTestFixture fixture)
        {
            _fixture = fixture;
        }

        [Fact]
        public void EndToEndWorkflow_SerializeValidateDeserialize_Works()
        {
            // Arrange
            var message = new UserMessage
            {
                Role = "user",
                Content = new[] { new TextContent { Text = "Integration test" } }
            };

            // Act
            var xml = _fixture.Serializer.Serialize(message);
            var errors = _fixture.Validator.Validate(xml);
            var deserialized = _fixture.Serializer.Deserialize<UserMessage>(xml);

            // Assert
            errors.Should().BeEmpty();
            deserialized.Role.Should().Be(message.Role);
            deserialized.Content[0].Text.Should().Be(message.Content[0].Text);
        }

        [Theory]
        [MemberData(nameof(GetAllTestCases))]
        public void ProcessTestCase_ValidatesCorrectly(TestCase testCase)
        {
            // Act
            var inputErrors = _fixture.Validator.Validate(testCase.Input);
            var expectedErrors = _fixture.Validator.Validate(testCase.Expected);

            // Assert
            inputErrors.Should().BeEmpty($"Input for {testCase.Name} should be valid");
            expectedErrors.Should().BeEmpty($"Expected for {testCase.Name} should be valid");
        }

        public static IEnumerable<object[]> GetAllTestCases()
        {
            var fixture = new XmlTestFixture();
            return fixture.LoadTestCases()
                .Select(tc => new object[] { tc });
        }
    }
}

// Run with: dotnet test
```

---

## Test Data Organization

### Input XML Files

Create `TestData/Input/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <user-message>
    <text>Hello, agent!</text>
  </user-message>
</thread>
```

### Expected Output Files

Create `TestData/Expected/basic_message.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<thread xmlns="urn:messages">
  <agent-message>
    <text>Hello, user!</text>
  </agent-message>
</thread>
```

---

## Running Tests

### Run All Tests

```bash
dotnet test
```

### Run Specific Test Class

```bash
dotnet test --filter "FullyQualifiedName~XmlMessageSerializationTests"
```

### Run With Coverage

```bash
dotnet test /p:CollectCoverage=true /p:CoverageReporter=html
```

### Run in Parallel

```bash
dotnet test --parallel
```

### Generate Test Report

```bash
dotnet test --logger "trx;LogFileName=test-results.trx"
```

---

## Advanced Patterns

### Custom Assertions

```csharp
public static class XmlAssertions
{
    public static void ShouldBeValidXml(this string xml)
    {
        var validator = new ThreadValidator();
        var errors = validator.Validate(xml);
        
        errors.Should().BeEmpty("XML should be valid");
    }
}

// Usage
xml.ShouldBeValidXml();
```

### Theory Data from Files

```csharp
public class XmlTheoryData : TheoryData<string, string>
{
    public XmlTheoryData()
    {
        var inputDir = Path.Combine("TestData", "Input");
        var expectedDir = Path.Combine("TestData", "Expected");

        foreach (var file in Directory.GetFiles(inputDir, "*.xml"))
        {
            var filename = Path.GetFileName(file);
            var expectedFile = Path.Combine(expectedDir, filename);
            
            if (File.Exists(expectedFile))
            {
                Add(File.ReadAllText(file), File.ReadAllText(expectedFile));
            }
        }
    }
}

[Theory]
[ClassData(typeof(XmlTheoryData))]
public void ValidateTestCases(string input, string expected)
{
    // Test implementation
}
```

### Async Tests

```csharp
[Fact]
public async Task SerializeAsync_ProducesValidXml()
{
    // Arrange
    var message = new UserMessage
    {
        Role = "user",
        Content = new[] { new TextContent { Text = "Async test" } }
    };

    // Act
    var xml = await _fixture.Serializer.SerializeAsync(message);

    // Assert
    xml.Should().NotBeNull();
}
```

---

## See Also

- [pytest Integration](pytest-integration.md)
- [Jest Integration](jest-integration.md)
- [How-To: Validation](../how-to-guides/validation.md)
