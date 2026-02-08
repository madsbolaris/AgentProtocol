"""Decorators for marking tests as documentation examples."""

from functools import wraps
from typing import Optional, Dict, Any, Callable
import inspect

# Registry for all doc examples
_doc_examples: Dict[str, Dict[str, Any]] = {}


def doc_example(
    test_id: str,
    title: str,
    description: str = "",
    category: str = "general",
    tags: Optional[list[str]] = None
) -> Callable:
    """
    Mark a test as a documentation example.

    This decorator registers a test function to be extracted for use in documentation.
    The actual code to extract should be wrapped with doc-example-start/doc-example-end
    comments.

    Args:
        test_id: Unique identifier for this example (e.g., "basic-serialization")
        title: Human-readable title for the example
        description: Optional longer description of what the example demonstrates
        category: Category for organization (e.g., "serialization", "deserialization")
        tags: Additional tags for filtering and search

    Returns:
        Decorator function

    Example:
        @doc_example("basic-message", "Create a Basic Message")
        def test_basic_message():
            '''Demonstrates creating a simple message'''

            # doc-example-start
            from microsoft.agents.xml import ChatMessage, TextContent

            message = ChatMessage(
                role="user",
                contents=[TextContent(text="Hello!")]
            )
            # doc-example-end

            assert message is not None
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata
        _doc_examples[test_id] = {
            "test_id": test_id,
            "title": title,
            "description": description,
            "category": category,
            "tags": tags or [],
            "function": func.__name__,
            "module": func.__module__,
            "source_file": inspect.getfile(func),
            "language": "python"
        }

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach metadata to function for introspection
        wrapper._doc_example_metadata = _doc_examples[test_id]  # type: ignore
        return wrapper

    return decorator


def get_all_doc_examples() -> Dict[str, Dict[str, Any]]:
    """
    Get all registered documentation examples.

    Returns:
        Dictionary mapping test IDs to their metadata
    """
    return _doc_examples.copy()
