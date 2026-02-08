using System;

namespace Microsoft.Agents.Testing
{
    /// <summary>
    /// Marks a test method as a documentation example.
    ///
    /// Tests marked with this attribute can be extracted for use in documentation.
    /// The actual code to extract should be wrapped with doc-example-start/doc-example-end
    /// comments.
    /// </summary>
    /// <example>
    /// <code>
    /// [Fact]
    /// [DocExample("basic-message", "Create a Basic Message",
    ///     Description = "Demonstrates creating a simple message",
    ///     Category = "serialization")]
    /// public void TestBasicMessage()
    /// {
    ///     // doc-example-start
    ///     var message = new ChatMessage
    ///     {
    ///         Role = "user",
    ///         Contents = new List&lt;Content&gt;
    ///         {
    ///             new TextContent { Text = "Hello!" }
    ///         }
    ///     };
    ///     // doc-example-end
    ///
    ///     message.Should().NotBeNull();
    /// }
    /// </code>
    /// </example>
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = false)]
    public class DocExampleAttribute : Attribute
    {
        /// <summary>
        /// Gets the unique identifier for this example.
        /// </summary>
        /// <value>
        /// A unique ID used to reference this example (e.g., "basic-serialization").
        /// Must match the test ID used in output capture.
        /// </value>
        public string TestId { get; }

        /// <summary>
        /// Gets the human-readable title for this example.
        /// </summary>
        /// <value>
        /// A short, descriptive title for the example.
        /// </value>
        public string Title { get; }

        /// <summary>
        /// Gets or sets the longer description of what this example demonstrates.
        /// </summary>
        /// <value>
        /// An optional longer description of the example's purpose and what it teaches.
        /// </value>
        public string Description { get; set; } = "";

        /// <summary>
        /// Gets or sets the category for organization.
        /// </summary>
        /// <value>
        /// Category name for grouping examples (e.g., "serialization", "deserialization").
        /// Default is "general".
        /// </value>
        public string Category { get; set; } = "general";

        /// <summary>
        /// Gets or sets additional tags for filtering and search.
        /// </summary>
        /// <value>
        /// Array of tag strings for categorization and filtering.
        /// </value>
        public string[] Tags { get; set; } = Array.Empty<string>();

        /// <summary>
        /// Initializes a new instance of the <see cref="DocExampleAttribute"/> class.
        /// </summary>
        /// <param name="testId">Unique identifier for this example.</param>
        /// <param name="title">Human-readable title for this example.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="testId"/> or <paramref name="title"/> is null.
        /// </exception>
        public DocExampleAttribute(string testId, string title)
        {
            TestId = testId ?? throw new ArgumentNullException(nameof(testId));
            Title = title ?? throw new ArgumentNullException(nameof(title));
        }
    }
}
