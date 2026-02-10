using System;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Marks a test method as a documentation example that can be extracted for docs
/// </summary>
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
public class DocExampleAttribute : Attribute
{
    public string? TestId { get; set; }
    public string? Title { get; set; }
    public string? Description { get; set; }

    public DocExampleAttribute()
    {
    }

    public DocExampleAttribute(string testId, string title)
    {
        TestId = testId;
        Title = title;
    }
}
