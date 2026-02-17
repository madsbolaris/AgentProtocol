# Test HashiCorp Admonitions

## Example 1: Note with custom title

!!! note "Default Agent Routing"
    When you don't specify an `agent_id`, requests are automatically routed to the server's **default agent**. This makes simple use cases straightforward while still supporting [multi-agent architectures](#step-6-multi-agent-conversations) when needed.

## Example 2: Warning

!!! warning "API Rate Limits"
    Be aware that API calls are subject to rate limiting. Consider implementing exponential backoff.

## Example 3: Info without title

!!! info
    This is an informational message without a custom title.

## Example 4: Success

!!! success "Configuration Complete"
    Your agent has been successfully configured and is ready to use.
