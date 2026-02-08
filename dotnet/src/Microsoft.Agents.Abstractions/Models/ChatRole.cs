using System;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    public enum ChatRole
    {
        System,
        Developer,
        Agent,
        User,
        Tool,
        Channel
    }
}