/**
 * Contains constant error codes for all validation rules.
 */
export class ValidationErrorCode {
  // Category A: Message Structure Validations (12 rules)
  static readonly MSG_001 = 'MSG-001'; // message-id must be non-empty string
  static readonly MSG_002 = 'MSG-002'; // message-id must be unique within a thread
  static readonly MSG_003 = 'MSG-003'; // created-at must be valid ISO 8601 datetime
  static readonly MSG_004 = 'MSG-004'; // created-at must not be in the future
  static readonly MSG_005 = 'MSG-005'; // author-name must not exceed 100 characters
  static readonly MSG_006 = 'MSG-006'; // parent-message-id must reference existing message in thread
  static readonly MSG_007 = 'MSG-007'; // parent-message-id must not create cycles (DAG validation)
  static readonly MSG_008 = 'MSG-008'; // SystemMessage content must be non-empty
  static readonly MSG_009 = 'MSG-009'; // DeveloperMessage content must be non-empty
  static readonly MSG_010 = 'MSG-010'; // UserMessage must have at least one content item
  static readonly MSG_011 = 'MSG-011'; // AgentMessage must have at least one content item
  static readonly MSG_012 = 'MSG-012'; // ToolMessage must have call-id and name

  // Category B: Relationship Validations (14 rules)
  static readonly REL_001 = 'REL-001'; // FunctionCallContent call-id must be unique within message
  static readonly REL_002 = 'REL-002'; // FunctionResultContent call-id must match a FunctionCallContent call-id
  static readonly REL_003 = 'REL-003'; // One FunctionCallContent per call-id (no duplicates)
  static readonly REL_004 = 'REL-004'; // One FunctionResultContent per call-id (no duplicates)
  static readonly REL_005 = 'REL-005'; // ToolMessage call-id must match FunctionCallContent in preceding AgentMessage
  static readonly REL_006 = 'REL-006'; // FunctionResultContent call-id must match FunctionCallContent
  static readonly REL_007 = 'REL-007'; // FunctionResultContent name must match FunctionCallContent name
  static readonly REL_008 = 'REL-008'; // ToolMessage name must match FunctionCallContent name
  static readonly REL_009 = 'REL-009'; // AgentMessage completion-id must be valid format (run_*)
  static readonly REL_010 = 'REL-010'; // AgentMessage agent-id must be non-empty when present
  static readonly REL_011 = 'REL-011'; // UserMessage user-id must be non-empty when present
  static readonly REL_012 = 'REL-012'; // parent-message-id references must form valid DAG
  static readonly REL_013 = 'REL-013'; // MessageReactionContent referenced-message-id must exist
  static readonly REL_014 = 'REL-014'; // MessageDeleteContent/MessageUpdateContent message-id must exist

  // Category C: Content Type Validations (15 rules)
  static readonly CNT_001 = 'CNT-001'; // TextContent text must be non-empty
  static readonly CNT_002 = 'CNT-002'; // TextContent text must not exceed 100,000 characters
  static readonly CNT_003 = 'CNT-003'; // FunctionCallContent name must be valid identifier ([a-zA-Z0-9_-]+)
  static readonly CNT_004 = 'CNT-004'; // FunctionCallContent arguments must be valid JSON
  static readonly CNT_005 = 'CNT-005'; // FunctionResultContent result must be valid JSON
  static readonly CNT_006 = 'CNT-006'; // ImageContent must have uri OR data (at least one)
  static readonly CNT_007 = 'CNT-007'; // ImageContent width/height must be positive integers
  static readonly CNT_008 = 'CNT-008'; // ImageContent mime-type must be valid (image/*)
  static readonly CNT_009 = 'CNT-009'; // AudioContent duration must be positive
  static readonly CNT_010 = 'CNT-010'; // VideoContent frame-rate must be positive
  static readonly CNT_011 = 'CNT-011'; // ErrorContent message must be non-empty
  static readonly CNT_012 = 'CNT-012'; // SearchResultContent url must be valid URI
  static readonly CNT_013 = 'CNT-013'; // DocumentContent document-id must be non-empty
  static readonly CNT_014 = 'CNT-014'; // AdaptiveCardContent card must be valid JSON
  static readonly CNT_015 = 'CNT-015'; // EventContent name must be non-empty

  // Category D: Role-Specific Content Validations (8 rules)
  static readonly ROLE_001 = 'ROLE-001'; // SystemMessage can only contain TextContent
  static readonly ROLE_002 = 'ROLE-002'; // DeveloperMessage can only contain TextContent
  static readonly ROLE_003 = 'ROLE-003'; // AgentMessage can contain FunctionCallContent, TextContent, TextReasoningContent
  static readonly ROLE_004 = 'ROLE-004'; // ToolMessage can only contain FunctionResultContent, ErrorContent
  static readonly ROLE_005 = 'ROLE-005'; // UserMessage cannot contain FunctionCallContent
  static readonly ROLE_006 = 'ROLE-006'; // ChannelMessage can contain EventContent, TraceContent, ActionContent
  static readonly ROLE_007 = 'ROLE-007'; // FunctionCallContent can only appear in AgentMessage
  static readonly ROLE_008 = 'ROLE-008'; // FunctionResultContent can only appear in ToolMessage

  // Category E: Thread-Level Validations (7 rules)
  static readonly THR_001 = 'THR-001'; // Thread must have unique message-ids
  static readonly THR_002 = 'THR-002'; // Thread status must be valid enum (active, closed, archived)
  static readonly THR_003 = 'THR-003'; // Thread created-at must be before or equal to last-message-at
  static readonly THR_004 = 'THR-004'; // Thread unread-count must be non-negative
  static readonly THR_005 = 'THR-005'; // All parent-message-id references must exist in thread
  static readonly THR_006 = 'THR-006'; // Thread must not have circular parent-message-id references
  static readonly THR_007 = 'THR-007'; // Thread participants list must not be empty

  // Category F: Business Logic Validations (5 rules)
  static readonly BIZ_001 = 'BIZ-001'; // AgentMessage with FunctionCallContent must be followed by ToolMessage
  static readonly BIZ_002 = 'BIZ-002'; // ToolMessage must follow AgentMessage with matching call-id
  static readonly BIZ_003 = 'BIZ-003'; // completed-at must be after created-at
  static readonly BIZ_004 = 'BIZ-004'; // Message sequence must follow valid conversation pattern
  static readonly BIZ_005 = 'BIZ-005'; // Audience attribute must be comma-separated valid roles

  // Category G: XML Schema Validations (8 rules)
  static readonly XML_001 = 'XML-001'; // Root element must be valid message type
  static readonly XML_002 = 'XML-002'; // All required attributes must be present
  static readonly XML_003 = 'XML-003'; // Attribute values must match expected types
  static readonly XML_004 = 'XML-004'; // Nested content elements must be valid AIContent types
  static readonly XML_005 = 'XML-005'; // XML must be well-formed
  static readonly XML_006 = 'XML-006'; // Namespaces must be correct (if used)
  static readonly XML_007 = 'XML-007'; // Element ordering must follow schema
  static readonly XML_008 = 'XML-008'; // Unknown attributes/elements must be rejected
}
