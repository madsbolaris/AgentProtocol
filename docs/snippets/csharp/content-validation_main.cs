// using Microsoft.Agents.Xml.Generated.Models;

// Validate required properties
var content = new TextContent { Text = "Hello, world!" };

Assert.NotNull(content.Text); // Text content must have text
Assert.True(content.Text.Length > 0); // Text cannot be empty
Assert.Equal("text", content.Kind); // Kind must match content type

Console.WriteLine($"✓ Content validated: {content.Text}");