namespace Microsoft.Agents.CodeGen.Utilities;

/// <summary>
/// Provides naming convention utilities for code generation.
/// Consolidated from multiple generators to ensure consistency.
/// </summary>
public static class NamingConventions
{
    /// <summary>
    /// Converts PascalCase or camelCase to kebab-case.
    /// Examples: "MessageId" -> "message-id", "userId" -> "user-id"
    /// </summary>
    /// <param name="input">Input string in PascalCase or camelCase</param>
    /// <returns>String in kebab-case</returns>
    public static string ToKebabCase(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return input;

        // Convert PascalCase/camelCase to kebab-case
        return string.Concat(
            input.Select((c, i) =>
                i > 0 && char.IsUpper(c)
                    ? "-" + char.ToLower(c)
                    : char.ToLower(c).ToString()
            )
        );
    }

    /// <summary>
    /// Converts camelCase or kebab-case to PascalCase.
    /// Examples: "messageId" -> "MessageId", "message-id" -> "MessageId"
    /// </summary>
    /// <param name="input">Input string in camelCase or kebab-case</param>
    /// <returns>String in PascalCase</returns>
    public static string ToPascalCase(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return input;

        // Handle kebab-case
        if (input.Contains('-'))
        {
            var parts = input.Split('-');
            return string.Concat(parts.Select(part =>
                string.IsNullOrEmpty(part) ? "" : char.ToUpper(part[0]) + part.Substring(1).ToLower()
            ));
        }

        // Handle camelCase
        return char.ToUpper(input[0]) + input.Substring(1);
    }

    /// <summary>
    /// Converts PascalCase or kebab-case to camelCase.
    /// Examples: "MessageId" -> "messageId", "message-id" -> "messageId"
    /// </summary>
    /// <param name="input">Input string in PascalCase or kebab-case</param>
    /// <returns>String in camelCase</returns>
    public static string ToCamelCase(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return input;

        // Handle kebab-case
        if (input.Contains('-'))
        {
            var parts = input.Split('-');
            if (parts.Length == 0)
                return input;

            var result = parts[0].ToLower();
            for (int i = 1; i < parts.Length; i++)
            {
                if (!string.IsNullOrEmpty(parts[i]))
                {
                    result += char.ToUpper(parts[i][0]) + parts[i].Substring(1).ToLower();
                }
            }
            return result;
        }

        // Handle PascalCase
        return char.ToLower(input[0]) + input.Substring(1);
    }

    /// <summary>
    /// Converts PascalCase or camelCase to snake_case.
    /// Examples: "MessageId" -> "message_id", "userId" -> "user_id"
    /// </summary>
    /// <param name="input">Input string in PascalCase or camelCase</param>
    /// <returns>String in snake_case</returns>
    public static string ToSnakeCase(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return input;

        // Convert PascalCase/camelCase to snake_case
        return string.Concat(
            input.Select((c, i) =>
                i > 0 && char.IsUpper(c)
                    ? "_" + char.ToLower(c)
                    : char.ToLower(c).ToString()
            )
        );
    }

    /// <summary>
    /// Converts PascalCase or camelCase to UPPER_SNAKE_CASE.
    /// Examples: "MessageId" -> "MESSAGE_ID", "userId" -> "USER_ID"
    /// </summary>
    /// <param name="input">Input string in PascalCase or camelCase</param>
    /// <returns>String in UPPER_SNAKE_CASE</returns>
    public static string ToUpperSnakeCase(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return input;

        // Convert PascalCase/camelCase to UPPER_SNAKE_CASE
        return string.Concat(
            input.Select((c, i) =>
                i > 0 && char.IsUpper(c)
                    ? "_" + char.ToUpper(c)
                    : char.ToUpper(c).ToString()
            )
        );
    }
}
