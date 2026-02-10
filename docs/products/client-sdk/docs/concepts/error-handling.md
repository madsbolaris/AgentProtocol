# Error Handling

Robust error handling ensures your agent applications gracefully handle failures and provide clear feedback to users.

## Error Types

The SDK raises different exceptions for different failure scenarios:

### Network Errors

Connection and timeout issues:

=== "Python"
    ```python
    from microsoft.agents.protocol import AgentProtocolClient
    from microsoft.agents.protocol.exceptions import (
        ConnectionError,
        TimeoutError,
        NetworkError
    )

    client = AgentProtocolClient("http://localhost:3978")

    try:
        response = await client.complete_chat("Hello")
    except ConnectionError:
        print("Cannot connect to agent server")
    except TimeoutError:
        print("Request timed out")
    except NetworkError as e:
        print(f"Network error: {e}")
    ```

=== "TypeScript"
    ```typescript
    import { AgentProtocolClient, ConnectionError, TimeoutError } from '@microsoft/agents-protocol';

    const client = new AgentProtocolClient("http://localhost:3978");

    try {
        const response = await client.completeChat("Hello");
    } catch (error) {
        if (error instanceof ConnectionError) {
            console.error("Cannot connect to agent server");
        } else if (error instanceof TimeoutError) {
            console.error("Request timed out");
        } else {
            console.error("Network error:", error);
        }
    }
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol.Client;
    using Microsoft.Agents.Protocol.Exceptions;

    var client = new AgentProtocolClient("http://localhost:3978");

    try
    {
        var response = await client.CompleteChatAsync("Hello");
    }
    catch (ConnectionException ex)
    {
        Console.WriteLine("Cannot connect to agent server");
    }
    catch (TimeoutException ex)
    {
        Console.WriteLine("Request timed out");
    }
    catch (NetworkException ex)
    {
        Console.WriteLine($"Network error: {ex.Message}");
    }
    ```

### Authentication Errors

API key and authorization failures:

=== "Python"
    ```python
    from microsoft.agents.protocol.exceptions import AuthenticationError

    try:
        response = await client.complete_chat("Hello")
    except AuthenticationError:
        print("Invalid API key or unauthorized")
        # Prompt user to check credentials
    ```

=== "TypeScript"
    ```typescript
    try {
        const response = await client.completeChat("Hello");
    } catch (error) {
        if (error instanceof AuthenticationError) {
            console.error("Invalid API key or unauthorized");
        }
    }
    ```

=== "C#"
    ```csharp
    try
    {
        var response = await client.CompleteChatAsync("Hello");
    }
    catch (AuthenticationException ex)
    {
        Console.WriteLine("Invalid API key or unauthorized");
    }
    ```

### Validation Errors

Invalid input or configuration:

=== "Python"
    ```python
    from microsoft.agents.protocol.exceptions import ValidationError

    try:
        # Empty message
        response = await client.complete_chat("")
    except ValidationError as e:
        print(f"Invalid input: {e.message}")
        print(f"Field: {e.field}")
    ```

=== "TypeScript"
    ```typescript
    try {
        const response = await client.completeChat("");
    } catch (error) {
        if (error instanceof ValidationError) {
            console.error(`Invalid input: ${error.message}`);
            console.error(`Field: ${error.field}`);
        }
    }
    ```

=== "C#"
    ```csharp
    try
    {
        var response = await client.CompleteChatAsync("");
    }
    catch (ValidationException ex)
    {
        Console.WriteLine($"Invalid input: {ex.Message}");
        Console.WriteLine($"Field: {ex.Field}");
    }
    ```

### Rate Limit Errors

Too many requests:

=== "Python"
    ```python
    from microsoft.agents.protocol.exceptions import RateLimitError
    import asyncio

    try:
        response = await client.complete_chat("Hello")
    except RateLimitError as e:
        # Wait and retry
        retry_after = e.retry_after  # Seconds to wait
        print(f"Rate limited. Retry after {retry_after}s")
        await asyncio.sleep(retry_after)
        response = await client.complete_chat("Hello")
    ```

=== "TypeScript"
    ```typescript
    try {
        const response = await client.completeChat("Hello");
    } catch (error) {
        if (error instanceof RateLimitError) {
            const retryAfter = error.retryAfter;
            console.log(`Rate limited. Retry after ${retryAfter}s`);
            await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
            // Retry request
        }
    }
    ```

=== "C#"
    ```csharp
    try
    {
        var response = await client.CompleteChatAsync("Hello");
    }
    catch (RateLimitException ex)
    {
        var retryAfter = ex.RetryAfter;
        Console.WriteLine($"Rate limited. Retry after {retryAfter}s");
        await Task.Delay(TimeSpan.FromSeconds(retryAfter));
        // Retry request
    }
    ```

### Agent Errors

Errors from the agent itself:

=== "Python"
    ```python
    from microsoft.agents.protocol.exceptions import AgentError

    try:
        response = await client.complete_chat("Hello")
    except AgentError as e:
        print(f"Agent error: {e.message}")
        print(f"Error code: {e.code}")
        # Check if retryable
        if e.is_retryable:
            # Retry with backoff
            pass
    ```

=== "TypeScript"
    ```typescript
    try {
        const response = await client.completeChat("Hello");
    } catch (error) {
        if (error instanceof AgentError) {
            console.error(`Agent error: ${error.message}`);
            console.error(`Error code: ${error.code}`);
            if (error.isRetryable) {
                // Retry with backoff
            }
        }
    }
    ```

=== "C#"
    ```csharp
    try
    {
        var response = await client.CompleteChatAsync("Hello");
    }
    catch (AgentException ex)
    {
        Console.WriteLine($"Agent error: {ex.Message}");
        Console.WriteLine($"Error code: {ex.Code}");
        if (ex.IsRetryable)
        {
            // Retry with backoff
        }
    }
    ```

## Retry Strategies

### Exponential Backoff

Implement retry logic with increasing delays:

=== "Python"
    ```python
    import asyncio
    from typing import TypeVar, Callable

    T = TypeVar('T')

    async def retry_with_backoff(
        func: Callable[[], T],
        max_attempts: int = 3,
        base_delay: float = 1.0
    ) -> T:
        """Retry function with exponential backoff."""
        for attempt in range(max_attempts):
            try:
                return await func()
            except (NetworkError, TimeoutError) as e:
                if attempt == max_attempts - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed. Retrying in {delay}s...")
                await asyncio.sleep(delay)

    # Usage
    response = await retry_with_backoff(
        lambda: client.complete_chat("Hello"),
        max_attempts=3
    )
    ```

=== "TypeScript"
    ```typescript
    async function retryWithBackoff<T>(
        func: () => Promise<T>,
        maxAttempts: number = 3,
        baseDelay: number = 1000
    ): Promise<T> {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                return await func();
            } catch (error) {
                if (attempt === maxAttempts - 1) {
                    throw error;
                }
                const delay = baseDelay * Math.pow(2, attempt);
                console.log(`Attempt ${attempt + 1} failed. Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        throw new Error("Max attempts reached");
    }

    // Usage
    const response = await retryWithBackoff(
        () => client.completeChat("Hello"),
        3
    );
    ```

=== "C#"
    ```csharp
    using Polly;

    // Using Polly library for retry logic
    var retryPolicy = Policy
        .Handle<NetworkException>()
        .Or<TimeoutException>()
        .WaitAndRetryAsync(
            retryCount: 3,
            sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)),
            onRetry: (exception, timeSpan, attempt, context) =>
            {
                Console.WriteLine($"Attempt {attempt} failed. Retrying in {timeSpan.TotalSeconds}s...");
            }
        );

    var response = await retryPolicy.ExecuteAsync(async () =>
        await client.CompleteChatAsync("Hello")
    );
    ```

### Circuit Breaker

Prevent cascading failures:

=== "Python"
    ```python
    from datetime import datetime, timedelta

    class CircuitBreaker:
        def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.failures = 0
            self.last_failure_time = None
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        async def call(self, func):
            if self.state == "OPEN":
                if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func()
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = datetime.now()
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                raise

    # Usage
    breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
    response = await breaker.call(lambda: client.complete_chat("Hello"))
    ```

## Error Recovery

### Graceful Degradation

Provide fallback behavior when errors occur:

=== "Python"
    ```python
    async def get_response_with_fallback(user_message: str) -> str:
        """Get response with fallback to cached or default response."""
        try:
            # Try primary agent
            response = await client.complete_chat(user_message)
            return response
        except NetworkError:
            # Try cached response
            cached = get_cached_response(user_message)
            if cached:
                return cached
            # Use default response
            return "I'm having trouble connecting. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "An error occurred. Please contact support."
    ```

### Error Logging

Log errors for debugging and monitoring:

=== "Python"
    ```python
    import logging

    logger = logging.getLogger(__name__)

    try:
        response = await client.complete_chat("Hello")
    except AgentError as e:
        logger.error(
            "Agent error",
            extra={
                "error_code": e.code,
                "error_message": e.message,
                "user_message": "Hello",
                "is_retryable": e.is_retryable
            }
        )
        raise
    except Exception as e:
        logger.exception("Unexpected error in chat completion")
        raise
    ```

=== "TypeScript"
    ```typescript
    import { logger } from './logger';

    try {
        const response = await client.completeChat("Hello");
    } catch (error) {
        if (error instanceof AgentError) {
            logger.error("Agent error", {
                errorCode: error.code,
                errorMessage: error.message,
                userMessage: "Hello",
                isRetryable: error.isRetryable
            });
        } else {
            logger.error("Unexpected error in chat completion", { error });
        }
        throw error;
    }
    ```

=== "C#"
    ```csharp
    using Microsoft.Extensions.Logging;

    try
    {
        var response = await client.CompleteChatAsync("Hello");
    }
    catch (AgentException ex)
    {
        _logger.LogError(ex,
            "Agent error. Code: {ErrorCode}, Message: {ErrorMessage}, Retryable: {IsRetryable}",
            ex.Code, ex.Message, ex.IsRetryable);
        throw;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Unexpected error in chat completion");
        throw;
    }
    ```

## User-Friendly Error Messages

Convert technical errors into user-friendly messages:

=== "Python"
    ```python
    def get_user_friendly_error(error: Exception) -> str:
        """Convert exception to user-friendly message."""
        error_messages = {
            ConnectionError: "Cannot connect to the service. Please check your internet connection.",
            TimeoutError: "The request took too long. Please try again.",
            AuthenticationError: "Authentication failed. Please check your credentials.",
            ValidationError: "Invalid input. Please check your message and try again.",
            RateLimitError: "Too many requests. Please wait a moment and try again.",
        }

        for error_type, message in error_messages.items():
            if isinstance(error, error_type):
                return message

        return "An unexpected error occurred. Please try again or contact support."

    # Usage
    try:
        response = await client.complete_chat(user_input)
    except Exception as e:
        user_message = get_user_friendly_error(e)
        print(user_message)
    ```

## Best Practices

### Do:
- ✅ Catch specific exceptions before generic ones
- ✅ Log errors with context for debugging
- ✅ Implement retry logic for transient failures
- ✅ Provide user-friendly error messages
- ✅ Use circuit breakers for external dependencies
- ✅ Set appropriate timeouts
- ✅ Monitor error rates and patterns

### Don't:
- ❌ Catch all exceptions silently
- ❌ Expose internal error details to users
- ❌ Retry indefinitely without backoff
- ❌ Ignore error types (treat all errors the same)
- ❌ Skip logging critical errors
- ❌ Use errors for control flow

## Testing Error Handling

Test error scenarios:

=== "Python"
    ```python
    import pytest
    from unittest.mock import patch, AsyncMock

    @pytest.mark.asyncio
    async def test_connection_error_handling():
        """Test handling of connection errors."""
        client = AgentProtocolClient("http://localhost:3978")

        with patch.object(client, 'complete_chat', side_effect=ConnectionError()):
            with pytest.raises(ConnectionError):
                await client.complete_chat("Hello")

    @pytest.mark.asyncio
    async def test_retry_with_backoff():
        """Test retry logic with exponential backoff."""
        mock_func = AsyncMock(side_effect=[
            TimeoutError(),
            TimeoutError(),
            "Success"
        ])

        result = await retry_with_backoff(mock_func, max_attempts=3)
        assert result == "Success"
        assert mock_func.call_count == 3
    ```

## Next Steps

- [Streaming](streaming.md) - Handle errors during streaming
- [Tool Execution](tools.md) - Error handling in tools
- [Debugging](../debugging.md) - Debug errors in production
- [Observability](../deployment/observability.md) - Monitor errors in production
