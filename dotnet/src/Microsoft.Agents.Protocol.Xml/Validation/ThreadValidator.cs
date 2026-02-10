using System;
using System.Collections.Generic;
using System.Linq;

namespace Microsoft.Agents.Protocol.Xml.Validation;

/// <summary>
/// Thread validator for conversation threads.
///
/// Validates that:
/// - Messages are in chronological order
/// - Message IDs are unique
/// - Tool results have matching function calls (call-id validation)
/// - Function names match between calls and results
/// - Call-ids are unique within a message
/// - Call-ids are only fulfilled once
/// - Messages have non-empty contents
/// - Messages have valid roles
/// - Required fields are present
/// </summary>
public class ThreadValidator
{
    /// <summary>
    /// Valid message roles per spec.
    /// </summary>
    private static readonly HashSet<string> ValidRoles = new()
    {
        "user", "agent", "system", "tool", "developer", "channel"
    };

    /// <summary>
    /// Validate a conversation thread.
    /// </summary>
    public ValidationResult Validate(object thread)
    {
        var result = ValidationResult.Success();

        // Use reflection to access thread properties dynamically
        var threadType = thread.GetType();

        // Validate thread ID
        var threadIdProp = threadType.GetProperty("ThreadId") ?? threadType.GetProperty("thread_id");
        var threadId = threadIdProp?.GetValue(thread) as string;
        if (string.IsNullOrEmpty(threadId))
        {
            result.AddError("Thread ID is required", field: "threadId", code: "THREAD_001");
        }

        // Validate messages
        var messagesProp = threadType.GetProperty("Messages") ?? threadType.GetProperty("messages");
        if (messagesProp == null)
        {
            result.AddError("Thread must have messages attribute", field: "messages", code: "THREAD_002");
            return result;
        }

        var messages = messagesProp.GetValue(thread) as System.Collections.IEnumerable;
        if (messages == null)
        {
            result.AddError("Thread messages must be enumerable", field: "messages", code: "THREAD_002");
            return result;
        }

        // Track state during validation
        var messageIds = new HashSet<string>();
        var functionCalls = new Dictionary<string, string>(); // call_id -> function_name
        var fulfilledCallIds = new HashSet<string>();
        DateTime? lastTimestamp = null;

        int idx = 0;
        foreach (var message in messages)
        {
            // Validate message role
            ValidateMessageRole(message, idx, result);

            // Validate message ID uniqueness
            var messageIdProp = message.GetType().GetProperty("MessageId") ?? message.GetType().GetProperty("message_id");
            var messageId = messageIdProp?.GetValue(message) as string;
            if (!string.IsNullOrEmpty(messageId))
            {
                if (messageIds.Contains(messageId))
                {
                    result.AddError(
                        $"Duplicate message ID: {messageId}",
                        field: $"messages[{idx}].messageId",
                        code: "THREAD_003"
                    );
                }
                messageIds.Add(messageId);
            }

            // Validate chronological order
            var createdAtProp = message.GetType().GetProperty("CreatedAt") ?? message.GetType().GetProperty("created_at");
            var createdAt = createdAtProp?.GetValue(message);
            if (createdAt != null)
            {
                DateTime timestamp;
                if (createdAt is DateTime dt)
                {
                    timestamp = dt;
                }
                else if (createdAt is string dateStr && DateTime.TryParse(dateStr, out var parsed))
                {
                    timestamp = parsed;
                }
                else
                {
                    idx++;
                    continue;
                }

                if (lastTimestamp.HasValue && timestamp < lastTimestamp.Value)
                {
                    result.AddError(
                        $"Messages not in chronological order at index {idx}",
                        field: $"messages[{idx}].createdAt",
                        code: "THREAD_004"
                    );
                }
                lastTimestamp = timestamp;
            }

            // Validate message contents
            ValidateMessageContents(message, idx, functionCalls, fulfilledCallIds, result);

            idx++;
        }

        // Check for unfulfilled function calls
        var unfulfilledCalls = functionCalls.Keys.Except(fulfilledCallIds).ToList();
        if (unfulfilledCalls.Any())
        {
            result.AddWarning(
                $"{unfulfilledCalls.Count} function call(s) without matching result: {string.Join(", ", unfulfilledCalls)}"
            );
        }

        return result;
    }

    private void ValidateMessageRole(object message, int messageIdx, ValidationResult result)
    {
        var roleProp = message.GetType().GetProperty("Role") ?? message.GetType().GetProperty("role");
        var role = roleProp?.GetValue(message) as string;

        if (string.IsNullOrEmpty(role))
        {
            return; // Role might be inferred from message type
        }

        if (!ValidRoles.Contains(role.ToLowerInvariant()))
        {
            result.AddError(
                $"Invalid message role: {role}. Must be one of: {string.Join(", ", ValidRoles)}",
                field: $"messages[{messageIdx}].role",
                code: "THREAD_005"
            );
        }
    }

    private void ValidateMessageContents(
        object message,
        int messageIdx,
        Dictionary<string, string> functionCalls,
        HashSet<string> fulfilledCallIds,
        ValidationResult result)
    {
        var contentsProp = message.GetType().GetProperty("Contents") ??
                          message.GetType().GetProperty("contents") ??
                          message.GetType().GetProperty("Content");

        var contents = contentsProp?.GetValue(message) as System.Collections.IEnumerable;
        if (contents == null)
        {
            result.AddWarning($"Message at index {messageIdx} has no contents");
            return;
        }

        var contentsList = contents.Cast<object>().ToList();
        if (contentsList.Count == 0)
        {
            result.AddWarning($"Message at index {messageIdx} has empty contents");
            return;
        }

        // Track call IDs within this message for uniqueness check
        var callIdsInMessage = new HashSet<string>();

        for (int contentIdx = 0; contentIdx < contentsList.Count; contentIdx++)
        {
            var content = contentsList[contentIdx];
            var contentType = content.GetType();

            var kindProp = contentType.GetProperty("Kind") ?? contentType.GetProperty("kind") ?? contentType.GetProperty("Type");
            var kind = kindProp?.GetValue(content) as string;

            // Validate function calls
            if (kind == "functionCall" || kind == "function_call" || contentType.Name.Contains("FunctionCall"))
            {
                var callIdProp = contentType.GetProperty("CallId") ?? contentType.GetProperty("call_id");
                var nameProp = contentType.GetProperty("Name") ?? contentType.GetProperty("name");

                var callId = callIdProp?.GetValue(content) as string;
                var name = nameProp?.GetValue(content) as string;

                if (string.IsNullOrEmpty(callId))
                {
                    result.AddError(
                        "Function call missing call-id",
                        field: $"messages[{messageIdx}].contents[{contentIdx}].callId",
                        code: "THREAD_007"
                    );
                }
                else
                {
                    if (callIdsInMessage.Contains(callId))
                    {
                        result.AddError(
                            $"Duplicate call-id in message: {callId}",
                            field: $"messages[{messageIdx}].contents[{contentIdx}].callId",
                            code: "THREAD_008"
                        );
                    }
                    callIdsInMessage.Add(callId);
                    functionCalls[callId] = name ?? "";
                }

                if (string.IsNullOrEmpty(name))
                {
                    result.AddError(
                        "Function call missing name",
                        field: $"messages[{messageIdx}].contents[{contentIdx}].name",
                        code: "THREAD_009"
                    );
                }
            }

            // Validate function results
            if (kind == "functionResult" || kind == "function_result" || contentType.Name.Contains("FunctionResult"))
            {
                var callIdProp = contentType.GetProperty("CallId") ?? contentType.GetProperty("call_id");
                var nameProp = contentType.GetProperty("Name") ?? contentType.GetProperty("name");

                var callId = callIdProp?.GetValue(content) as string;
                var name = nameProp?.GetValue(content) as string;

                if (string.IsNullOrEmpty(callId))
                {
                    result.AddError(
                        "Function result missing call-id",
                        field: $"messages[{messageIdx}].contents[{contentIdx}].callId",
                        code: "THREAD_010"
                    );
                }
                else
                {
                    if (!functionCalls.ContainsKey(callId))
                    {
                        result.AddError(
                            $"Function result has call-id {callId} but no matching function call",
                            field: $"messages[{messageIdx}].contents[{contentIdx}].callId",
                            code: "THREAD_011"
                        );
                    }
                    else
                    {
                        var expectedName = functionCalls[callId];
                        if (!string.IsNullOrEmpty(name) && !string.IsNullOrEmpty(expectedName) && name != expectedName)
                        {
                            result.AddError(
                                $"Function result name '{name}' does not match function call name '{expectedName}' for call-id {callId}",
                                field: $"messages[{messageIdx}].contents[{contentIdx}].name",
                                code: "THREAD_012"
                            );
                        }

                        if (fulfilledCallIds.Contains(callId))
                        {
                            result.AddError(
                                $"Function result has call-id {callId} which was already fulfilled",
                                field: $"messages[{messageIdx}].contents[{contentIdx}].callId",
                                code: "THREAD_013"
                            );
                        }
                        fulfilledCallIds.Add(callId);
                    }
                }
            }

            // Validate text content
            if (kind == "text" || contentType.Name.Contains("TextContent"))
            {
                var textProp = contentType.GetProperty("Text") ?? contentType.GetProperty("text") ?? contentType.GetProperty("Content");
                var text = textProp?.GetValue(content) as string;

                if (string.IsNullOrWhiteSpace(text))
                {
                    result.AddWarning($"Text content at messages[{messageIdx}].contents[{contentIdx}] is empty");
                }
            }
        }
    }
}
