"""
Thread validator for conversation threads.

Validates that:
- Messages are in chronological order
- Message IDs are unique
- Tool results have matching function calls (call-id validation)
- Function names match between calls and results
- Call-ids are unique within a message
- Call-ids are only fulfilled once
- Messages have non-empty contents
- Messages have valid roles
- Required fields are present
"""

from typing import Set, Dict, Any, Optional
from datetime import datetime

from microsoft.agents.xml.validation.validation_result import ValidationResult


class ThreadValidator:
    """Validates conversation threads."""

    # Valid message roles per spec
    VALID_ROLES = {'user', 'agent', 'system', 'tool', 'developer'}

    def validate(self, thread: Any) -> ValidationResult:
        """
        Validate a conversation thread.

        Args:
            thread: Thread object to validate

        Returns:
            ValidationResult with any errors found
        """
        result = ValidationResult.success()

        # Track state during validation
        message_ids: Set[str] = set()
        function_calls: Dict[str, str] = {}  # call_id -> function_name
        fulfilled_call_ids: Set[str] = set()  # Track which calls have been fulfilled
        last_timestamp: Optional[datetime] = None

        # Validate thread ID
        if not hasattr(thread, 'thread_id') or not thread.thread_id:
            result.add_error("Thread ID is required", field="thread_id", code="THREAD_001")

        # Validate messages
        if not hasattr(thread, 'messages') or not thread.messages:
            # Empty messages list is okay, but attribute should exist
            if not hasattr(thread, 'messages'):
                result.add_error("Thread must have messages attribute", field="messages", code="THREAD_002")
            return result

        for idx, message in enumerate(thread.messages):
            # Validate message role
            self._validate_message_role(message, idx, result)

            # Validate message ID uniqueness
            if hasattr(message, 'message_id') and message.message_id:
                if message.message_id in message_ids:
                    result.add_error(
                        f"Duplicate message ID: {message.message_id}",
                        field=f"messages[{idx}].message_id",
                        code="THREAD_003"
                    )
                message_ids.add(message.message_id)

            # Validate chronological order
            if hasattr(message, 'created_at') and message.created_at:
                if last_timestamp and message.created_at < last_timestamp:
                    result.add_error(
                        f"Messages not in chronological order at index {idx}",
                        field=f"messages[{idx}].created_at",
                        code="THREAD_004"
                    )
                last_timestamp = message.created_at

            # Validate message contents and track function calls
            self._validate_message_contents(
                message, idx, function_calls, fulfilled_call_ids, result
            )

        return result

    def _validate_message_role(self, message: Any, message_idx: int,
                               result: ValidationResult) -> None:
        """
        Validate message has a valid role.

        Args:
            message: Message to validate
            message_idx: Index of message in thread
            result: Validation result to add errors to
        """
        if not hasattr(message, 'role'):
            return  # Role might be inferred from message type

        role = message.role
        if role and role not in self.VALID_ROLES:
            result.add_error(
                f"Invalid message role '{role}'. Valid roles are: {', '.join(sorted(self.VALID_ROLES))}",
                field=f"messages[{message_idx}].role",
                code="MSG_002",
                context={"role": role, "valid_roles": list(self.VALID_ROLES)}
            )

    def _validate_message_contents(self, message: Any, message_idx: int,
                                   function_calls: Dict[str, str],
                                   fulfilled_call_ids: Set[str],
                                   result: ValidationResult) -> None:
        """
        Validate message contents and track function calls.

        Args:
            message: Message to validate
            message_idx: Index of message in thread
            function_calls: Dict mapping call_id -> function_name for pending calls
            fulfilled_call_ids: Set of call_ids that have been fulfilled
            result: Validation result to add errors to
        """
        # Validate non-empty contents
        if not hasattr(message, 'contents'):
            return

        if not message.contents or len(message.contents) == 0:
            result.add_error(
                "Message must have non-empty contents",
                field=f"messages[{message_idx}].contents",
                code="MSG_001"
            )
            return

        # Track call-ids within this message to detect duplicates
        message_call_ids: Set[str] = set()

        for content_idx, content in enumerate(message.contents):
            content_type = type(content).__name__

            # Validate function calls
            if content_type == 'FunctionCallContent':
                self._validate_function_call(
                    content, message_idx, content_idx, message_call_ids,
                    function_calls, result
                )

            # Validate function results
            elif content_type == 'FunctionResultContent':
                self._validate_function_result(
                    content, message_idx, content_idx, function_calls,
                    fulfilled_call_ids, result
                )

    def _validate_function_call(self, content: Any, message_idx: int,
                               content_idx: int, message_call_ids: Set[str],
                               function_calls: Dict[str, str],
                               result: ValidationResult) -> None:
        """
        Validate a function call content.

        Args:
            content: Function call content to validate
            message_idx: Index of message in thread
            content_idx: Index of content in message
            message_call_ids: Set of call_ids seen in this message
            function_calls: Dict to store call_id -> function_name
            result: Validation result to add errors to
        """
        # Validate required field: call_id
        if not hasattr(content, 'call_id') or not content.call_id:
            result.add_error(
                "Function call must have call_id",
                field=f"messages[{message_idx}].contents[{content_idx}].call_id",
                code="TOOL_005"
            )
            return

        call_id = content.call_id

        # Check for duplicate call-id within message
        if call_id in message_call_ids:
            result.add_error(
                f"Duplicate call-id '{call_id}' within message",
                field=f"messages[{message_idx}].contents[{content_idx}].call_id",
                code="TOOL_002",
                context={"call_id": call_id, "message_index": message_idx}
            )
        else:
            message_call_ids.add(call_id)

        # Validate required field: name
        if not hasattr(content, 'name') or not content.name:
            result.add_error(
                "Function call must have name",
                field=f"messages[{message_idx}].contents[{content_idx}].name",
                code="TOOL_005"
            )
            return

        # Track this function call
        function_calls[call_id] = content.name

    def _validate_function_result(self, content: Any, message_idx: int,
                                  content_idx: int, function_calls: Dict[str, str],
                                  fulfilled_call_ids: Set[str],
                                  result: ValidationResult) -> None:
        """
        Validate a function result content.

        Args:
            content: Function result content to validate
            message_idx: Index of message in thread
            content_idx: Index of content in message
            function_calls: Dict of call_id -> function_name for pending calls
            fulfilled_call_ids: Set of call_ids that have been fulfilled
            result: Validation result to add errors to
        """
        # Validate required field: call_id
        if not hasattr(content, 'call_id') or not content.call_id:
            result.add_error(
                "Function result must have call_id",
                field=f"messages[{message_idx}].contents[{content_idx}].call_id",
                code="TOOL_005"
            )
            return

        call_id = content.call_id

        # Check if call_id matches a pending function call
        if call_id not in function_calls:
            result.add_error(
                f"Tool result call-id '{call_id}' does not match any "
                f"preceding function call",
                field=f"messages[{message_idx}].contents[{content_idx}].call_id",
                code="TOOL_001",
                context={
                    "call_id": call_id,
                    "known_call_ids": list(function_calls.keys())
                }
            )
            return

        # Check if call_id already fulfilled
        if call_id in fulfilled_call_ids:
            result.add_error(
                f"Call-id '{call_id}' already submitted. Each function call can only be fulfilled once.",
                field=f"messages[{message_idx}].contents[{content_idx}].call_id",
                code="TOOL_004",
                context={"call_id": call_id}
            )
            return

        # Validate required field: name
        if not hasattr(content, 'name') or not content.name:
            result.add_error(
                "Function result must have name",
                field=f"messages[{message_idx}].contents[{content_idx}].name",
                code="TOOL_005"
            )
            # Still mark as fulfilled even if name is missing to avoid cascading errors
            fulfilled_call_ids.add(call_id)
            return

        # Validate name matches function call name
        expected_name = function_calls[call_id]
        if content.name != expected_name:
            result.add_error(
                f"Function result name '{content.name}' does not match "
                f"function call name '{expected_name}'",
                field=f"messages[{message_idx}].contents[{content_idx}].name",
                code="TOOL_003",
                context={
                    "call_id": call_id,
                    "result_name": content.name,
                    "expected_name": expected_name
                }
            )

        # Mark this call as fulfilled
        fulfilled_call_ids.add(call_id)
