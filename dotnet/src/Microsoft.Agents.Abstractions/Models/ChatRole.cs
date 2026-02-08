using System;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
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