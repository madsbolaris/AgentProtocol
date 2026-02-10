"""
Code Generation Utilities

Common utilities for code generation across all generators.
Consolidated to ensure consistency and reduce duplication.
"""

import re


def to_kebab_case(name: str) -> str:
    """
    Convert PascalCase or camelCase to kebab-case.

    Examples:
        >>> to_kebab_case("MessageId")
        'message-id'
        >>> to_kebab_case("userId")
        'user-id'
        >>> to_kebab_case("HTTPResponse")
        'h-t-t-p-response'

    Args:
        name: String in PascalCase or camelCase

    Returns:
        String in kebab-case
    """
    if not name:
        return name

    # Insert hyphen before uppercase letters (except at start)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    # Insert hyphen before uppercase letters followed by lowercase
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1)
    return s2.lower()


def to_pascal_case(name: str) -> str:
    """
    Convert camelCase, snake_case, or kebab-case to PascalCase.

    Examples:
        >>> to_pascal_case("message_id")
        'MessageId'
        >>> to_pascal_case("message-id")
        'MessageId'
        >>> to_pascal_case("messageId")
        'MessageId'

    Args:
        name: String in camelCase, snake_case, or kebab-case

    Returns:
        String in PascalCase
    """
    if not name:
        return name

    # Handle kebab-case and snake_case
    if '-' in name or '_' in name:
        parts = re.split(r'[-_]', name)
        return ''.join(part.capitalize() for part in parts if part)

    # Handle camelCase
    return name[0].upper() + name[1:] if len(name) > 1 else name.upper()


def to_camel_case(name: str) -> str:
    """
    Convert PascalCase, snake_case, or kebab-case to camelCase.

    Examples:
        >>> to_camel_case("MessageId")
        'messageId'
        >>> to_camel_case("message-id")
        'messageId'
        >>> to_camel_case("message_id")
        'messageId'

    Args:
        name: String in PascalCase, snake_case, or kebab-case

    Returns:
        String in camelCase
    """
    if not name:
        return name

    # Handle kebab-case and snake_case
    if '-' in name or '_' in name:
        parts = re.split(r'[-_]', name)
        if not parts:
            return name

        # First part lowercase, rest capitalized
        return parts[0].lower() + ''.join(part.capitalize() for part in parts[1:] if part)

    # Handle PascalCase
    return name[0].lower() + name[1:] if len(name) > 1 else name.lower()


def to_snake_case(name: str) -> str:
    """
    Convert PascalCase or camelCase to snake_case.

    Examples:
        >>> to_snake_case("MessageId")
        'message_id'
        >>> to_snake_case("userId")
        'user_id'

    Args:
        name: String in PascalCase or camelCase

    Returns:
        String in snake_case
    """
    if not name:
        return name

    # Insert underscore before uppercase letters (except at start)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before uppercase letters followed by lowercase
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def escape_python_keyword(name: str) -> str:
    """
    Escape Python reserved keywords by appending underscore.

    Examples:
        >>> escape_python_keyword("from")
        'from_'
        >>> escape_python_keyword("class")
        'class_'
        >>> escape_python_keyword("normal")
        'normal'

    Args:
        name: Property or variable name

    Returns:
        Name with trailing underscore if it's a Python keyword, unchanged otherwise
    """
    # Python 3 reserved keywords
    python_keywords = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield'
    }

    return f"{name}_" if name in python_keywords else name


if __name__ == "__main__":
    # Run doctests
    import doctest
    doctest.testmod()
