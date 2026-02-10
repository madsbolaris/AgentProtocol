# Events

**Events** are notifications about things that happen in the Agent Protocol. They enable reactive, event-driven architectures.

## What are Events?

Events inform you when something occurs:
- Run started/completed
- Message created
- Thread archived
- Agent enabled/disabled
- Error occurred

Instead of constantly checking status (polling), events notify you when changes happen.

## Why Use Events?

### Real-time Notifications
Know immediately when something happens:
```
Run completes → Event fired → Your code reacts
```

### Decoupled Architecture
Components react to events without tight coupling:
```
Agent creates message → Event → Multiple listeners react
```

### Audit Trail
Events provide a history of what happened:
```
Thread created → User joined → Message sent → Run completed
```

## Event Types

### Run Events
Track run lifecycle:
- **run_created** - New run initialized
- **run_started** - Run began executing
- **run_in_progress** - Run is processing
- **run_requires_action** - Run needs input (tool approval, etc.)
- **run_completed** - Run finished successfully
- **run_failed** - Run encountered error
- **run_cancelled** - Run was stopped
- **run_timeout** - Run exceeded time limit

### Message Events
Track message lifecycle:
- **message_created** - New message added
- **message_updated** - Message modified
- **message_completed** - Message fully processed
- **message_deleted** - Message removed

### Thread Events
Track thread lifecycle:
- **thread_created** - New thread initialized
- **thread_reopened** - Archived thread reactivated
- **thread_closed** - Thread marked inactive
- **thread_archived** - Thread moved to archive
- **thread_deleted** - Thread permanently removed

### Agent Events
Track agent changes:
- **agent_created** - New agent defined
- **agent_updated** - Agent configuration changed
- **agent_enabled** - Agent activated
- **agent_disabled** - Agent deactivated
- **agent_deleted** - Agent removed
- **agent_error** - Agent encountered error

### Participant Events
Track conversation participants:
- **participant_added** - New participant joined
- **participant_removed** - Participant left

## Event Structure

Every event contains:

```json
{
  "type": "run_completed",
  "id": "evt_123",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "run_id": "run_456",
    "thread_id": "thread_789",
    "status": "completed",
    "output": [...]
  }
}
```

### Common Fields
- **type** - Event type identifier
- **id** - Unique event ID
- **created_at** - When event occurred
- **data** - Event-specific payload

## Consuming Events

### Webhooks
Receive HTTP callbacks when events occur:

```javascript
// Your webhook endpoint
app.post('/webhooks/agent-protocol', (req, res) => {
  const event = req.body;

  switch (event.type) {
    case 'run_completed':
      handleRunCompleted(event.data);
      break;
    case 'message_created':
      handleMessageCreated(event.data);
      break;
  }

  res.status(200).send();
});
```

### Polling
Check for new events periodically:

```python
while True:
    events = client.list_events(since=last_event_id)
    for event in events:
        handle_event(event)
    time.sleep(5)
```

### Server-Sent Events (SSE)
Maintain open connection for real-time events:

```typescript
const eventSource = new EventSource('/api/events');

eventSource.addEventListener('run_completed', (e) => {
  const event = JSON.parse(e.data);
  handleRunCompleted(event);
});
```

## Event Patterns

### React to Completion
```
run_completed → Send notification
              → Update database
              → Trigger next step
```

### Chain Operations
```
thread_created → message_created → run_completed → thread_archived
```

### Fan-out
```
run_completed → Analytics service
              → Notification service
              → Billing service
              → Audit logger
```

### Error Handling
```
run_failed → Log error
           → Alert admin
           → Retry or rollback
```

## Event Filtering

Subscribe to specific events:

```javascript
// Only run events
webhooks.subscribe({
  events: ['run.*']
});

// Only completed runs
webhooks.subscribe({
  events: ['run_completed']
});

// Multiple specific events
webhooks.subscribe({
  events: ['run_completed', 'run_failed', 'run_timeout']
});
```

## Event Ordering

Events are ordered by creation time:
```
event_1 (10:30:00) → event_2 (10:30:01) → event_3 (10:30:02)
```

For related events, order is guaranteed:
```
run_created → run_started → run_completed
```

## Related Concepts

- **[Runs](runs.md)** - Generate run events
- **[Messages](messages.md)** - Generate message events
- **[Threads](threads.md)** - Generate thread events
- **[Agents](agents.md)** - Generate agent events

## Best Practices

✅ **Do:**
- Handle all event types gracefully
- Implement retry logic for webhooks
- Store event IDs to prevent duplicates
- Log events for debugging
- Use event filtering to reduce noise

❌ **Don't:**
- Assume event order across unrelated entities
- Block webhook handlers (return fast)
- Ignore error events
- Skip idempotency checks
- Process same event twice

## Event Delivery

### Webhook Delivery
- **At-least-once** - Events may be delivered multiple times
- **Best-effort ordering** - Usually in order, not guaranteed
- **Retry logic** - Failed deliveries are retried

### SSE Delivery
- **Real-time** - Events delivered as they occur
- **Ordered** - Events arrive in order
- **Reconnection** - Clients can reconnect and resume

## Debugging Events

### Event Logs
View recent events:
```bash
curl /api/events?limit=50
```

### Event Replay
Replay events for testing:
```bash
curl -X POST /api/webhooks/replay \
  -d '{"event_id": "evt_123"}'
```

### Event Inspector
Monitor live events:
```bash
# Stream events to console
sse-client /api/events/stream
```

## Next Steps

- Configure webhooks in your [Hosting SDK](../products/hosting-sdk/) application
- Learn about [Runs](runs.md) that generate events
- Explore event handling in SDK documentation
