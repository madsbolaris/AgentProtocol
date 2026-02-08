using System;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Thread Status Enum/// RATIONALE: Type-safe status values for thread lifecycle/// ALIGNED WITH: Messaging app conversation states/// - active: Thread is ongoing (like WhatsApp/Teams active chat)/// - closed: Thread is completed but archived (like closed ticket)/// - archived: Thread is hidden from active view (like archived email)/// </summary>
    public enum ThreadStatus
    {
        Active,
        Closed,
        Archived
    }
}