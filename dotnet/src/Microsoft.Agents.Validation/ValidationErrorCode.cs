namespace Microsoft.Agents.Xml.Validation;

/// <summary>
/// Contains constant error codes for all validation rules.
/// </summary>
public static class ValidationErrorCode
{
    // Category A: Message Structure Validations (12 rules)
    public const string MSG_001 = "MSG-001"; // message-id must be non-empty string
    public const string MSG_002 = "MSG-002"; // message-id must be unique within a thread
    public const string MSG_003 = "MSG-003"; // created-at must be valid ISO 8601 datetime
    public const string MSG_004 = "MSG-004"; // created-at must not be in the future
    public const string MSG_005 = "MSG-005"; // author-name must not exceed 100 characters
    public const string MSG_006 = "MSG-006"; // parent-message-id must reference existing message in thread
    public const string MSG_007 = "MSG-007"; // parent-message-id must not create cycles (DAG validation)
    public const string MSG_008 = "MSG-008"; // SystemMessage content must be non-empty
    public const string MSG_009 = "MSG-009"; // DeveloperMessage content must be non-empty
    public const string MSG_010 = "MSG-010"; // UserMessage must have at least one content item
    public const string MSG_011 = "MSG-011"; // AgentMessage must have at least one content item
    public const string MSG_012 = "MSG-012"; // ToolMessage must have call-id and name

    // Category B: Relationship Validations (14 rules)
    public const string REL_001 = "REL-001"; // FunctionCallContent call-id must be unique within message
    public const string REL_002 = "REL-002"; // FunctionResultContent call-id must match a FunctionCallContent call-id
    public const string REL_003 = "REL-003"; // One FunctionCallContent per call-id (no duplicates)
    public const string REL_004 = "REL-004"; // One FunctionResultContent per call-id (no duplicates)
    public const string REL_005 = "REL-005"; // ToolMessage call-id must match FunctionCallContent in preceding AgentMessage
    public const string REL_006 = "REL-006"; // FunctionResultContent call-id must match FunctionCallContent
    public const string REL_007 = "REL-007"; // FunctionResultContent name must match FunctionCallContent name
    public const string REL_008 = "REL-008"; // ToolMessage name must match FunctionCallContent name
    public const string REL_009 = "REL-009"; // AgentMessage completion-id must be valid format (run_*)
    public const string REL_010 = "REL-010"; // AgentMessage agent-id must be non-empty when present
    public const string REL_011 = "REL-011"; // UserMessage user-id must be non-empty when present
    public const string REL_012 = "REL-012"; // parent-message-id references must form valid DAG
    public const string REL_013 = "REL-013"; // MessageReactionContent referenced-message-id must exist
    public const string REL_014 = "REL-014"; // MessageDeleteContent/MessageUpdateContent message-id must exist

    // Category C: Content Type Validations (15 rules)
    public const string CNT_001 = "CNT-001"; // TextContent text must be non-empty
    public const string CNT_002 = "CNT-002"; // TextContent text must not exceed 100,000 characters
    public const string CNT_003 = "CNT-003"; // FunctionCallContent name must be valid identifier ([a-zA-Z0-9_-]+)
    public const string CNT_004 = "CNT-004"; // FunctionCallContent arguments must be valid JSON
    public const string CNT_005 = "CNT-005"; // FunctionResultContent result must be valid JSON
    public const string CNT_006 = "CNT-006"; // ImageContent must have uri OR data (at least one)
    public const string CNT_007 = "CNT-007"; // ImageContent width/height must be positive integers
    public const string CNT_008 = "CNT-008"; // ImageContent mime-type must be valid (image/*)
    public const string CNT_009 = "CNT-009"; // AudioContent duration must be positive
    public const string CNT_010 = "CNT-010"; // VideoContent frame-rate must be positive
    public const string CNT_011 = "CNT-011"; // ErrorContent message must be non-empty
    public const string CNT_012 = "CNT-012"; // SearchResultContent url must be valid URI
    public const string CNT_013 = "CNT-013"; // DocumentContent document-id must be non-empty
    public const string CNT_014 = "CNT-014"; // AdaptiveCardContent card must be valid JSON
    public const string CNT_015 = "CNT-015"; // EventContent name must be non-empty

    // Category D: Role-Specific Content Validations (8 rules)
    public const string ROLE_001 = "ROLE-001"; // SystemMessage can only contain TextContent
    public const string ROLE_002 = "ROLE-002"; // DeveloperMessage can only contain TextContent
    public const string ROLE_003 = "ROLE-003"; // AgentMessage can contain FunctionCallContent, TextContent, TextReasoningContent
    public const string ROLE_004 = "ROLE-004"; // ToolMessage can only contain FunctionResultContent, ErrorContent
    public const string ROLE_005 = "ROLE-005"; // UserMessage cannot contain FunctionCallContent
    public const string ROLE_006 = "ROLE-006"; // ChannelMessage can contain EventContent, TraceContent, ActionContent
    public const string ROLE_007 = "ROLE-007"; // FunctionCallContent can only appear in AgentMessage
    public const string ROLE_008 = "ROLE-008"; // FunctionResultContent can only appear in ToolMessage

    // Category E: Thread-Level Validations (7 rules)
    public const string THR_001 = "THR-001"; // Thread must have unique message-ids
    public const string THR_002 = "THR-002"; // Thread status must be valid enum (active, closed, archived)
    public const string THR_003 = "THR-003"; // Thread created-at must be before or equal to last-message-at
    public const string THR_004 = "THR-004"; // Thread unread-count must be non-negative
    public const string THR_005 = "THR-005"; // All parent-message-id references must exist in thread
    public const string THR_006 = "THR-006"; // Thread must not have circular parent-message-id references
    public const string THR_007 = "THR-007"; // Thread participants list must not be empty

    // Category F: Business Logic Validations (5 rules)
    public const string BIZ_001 = "BIZ-001"; // AgentMessage with FunctionCallContent must be followed by ToolMessage
    public const string BIZ_002 = "BIZ-002"; // ToolMessage must follow AgentMessage with matching call-id
    public const string BIZ_003 = "BIZ-003"; // completed-at must be after created-at
    public const string BIZ_004 = "BIZ-004"; // Message sequence must follow valid conversation pattern
    public const string BIZ_005 = "BIZ-005"; // Audience attribute must be comma-separated valid roles

    // Category G: XML Schema Validations (8 rules)
    public const string XML_001 = "XML-001"; // Root element must be valid message type (system, user, agent, tool, developer, channel)
    public const string XML_002 = "XML-002"; // All required attributes must be present
    public const string XML_003 = "XML-003"; // Attribute values must match expected types
    public const string XML_004 = "XML-004"; // Nested content elements must be valid AIContent types
    public const string XML_005 = "XML-005"; // XML must be well-formed
    public const string XML_006 = "XML-006"; // Namespaces must be correct (if used)
    public const string XML_007 = "XML-007"; // Element ordering must follow schema
    public const string XML_008 = "XML-008"; // Unknown attributes/elements must be rejected
}
