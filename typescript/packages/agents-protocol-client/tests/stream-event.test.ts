/**
 * Tests for StreamEvent classes
 */

import { StreamEventImpl, createStreamEvent } from '../src/stream-event';

describe('StreamEvent', () => {
  describe('StreamEventImpl', () => {
    it('should create event with type and data', () => {
      const data = { message: 'Hello' };
      const event = new StreamEventImpl('message.created', data);

      expect(event.eventType).toBe('message.created');
      expect(event.data).toEqual(data);
    });

    it('should extract data with getDataAs', () => {
      interface TestData {
        value: number;
      }

      const data: TestData = { value: 42 };
      const event = new StreamEventImpl('test.event', data);

      class TestClass {
        value: number = 0;
      }

      const extracted = event.getDataAs(TestClass);
      expect(extracted).toEqual(data);
    });

    it('should get data with getData', () => {
      interface CustomData {
        id: string;
        name: string;
      }

      const data: CustomData = { id: 'test-123', name: 'Test' };
      const event = new StreamEventImpl('custom.event', data);

      const result = event.getData<CustomData>();
      expect(result).toEqual(data);
      expect(result.id).toBe('test-123');
      expect(result.name).toBe('Test');
    });

    it('should handle complex nested data', () => {
      const data = {
        user: {
          id: 'user-123',
          profile: {
            name: 'Alice',
            age: 30,
          },
        },
        timestamp: '2024-01-15T10:00:00Z',
      };

      const event = new StreamEventImpl('user.updated', data);

      expect(event.data).toEqual(data);
      expect(event.getData()).toEqual(data);
    });

    it('should handle null data', () => {
      const event = new StreamEventImpl('null.event', null);

      expect(event.eventType).toBe('null.event');
      expect(event.data).toBeNull();
    });

    it('should handle undefined data', () => {
      const event = new StreamEventImpl('undefined.event', undefined);

      expect(event.eventType).toBe('undefined.event');
      expect(event.data).toBeUndefined();
    });

    it('should handle array data', () => {
      const data = [1, 2, 3, 4, 5];
      const event = new StreamEventImpl('array.event', data);

      expect(event.data).toEqual(data);
      expect(event.getData<number[]>()).toEqual(data);
    });

    it('should handle primitive data types', () => {
      const stringEvent = new StreamEventImpl('string.event', 'test string');
      expect(stringEvent.data).toBe('test string');

      const numberEvent = new StreamEventImpl('number.event', 42);
      expect(numberEvent.data).toBe(42);

      const booleanEvent = new StreamEventImpl('boolean.event', true);
      expect(booleanEvent.data).toBe(true);
    });
  });

  describe('createStreamEvent', () => {
    it('should create StreamEvent with type and data', () => {
      const data = { status: 'active' };
      const event = createStreamEvent('status.changed', data);

      expect(event.eventType).toBe('status.changed');
      expect(event.data).toEqual(data);
    });

    it('should create event with complex data', () => {
      const data = {
        runId: 'run-123',
        status: 'in_progress',
        metadata: {
          startTime: Date.now(),
          agentId: 'agent-456',
        },
      };

      const event = createStreamEvent('run.started', data);

      expect(event.eventType).toBe('run.started');
      expect(event.data).toEqual(data);
    });

    it('should return StreamEvent interface', () => {
      const event = createStreamEvent('test.event', { test: true });

      expect(event).toHaveProperty('eventType');
      expect(event).toHaveProperty('data');
      expect(event).toHaveProperty('getDataAs');
    });

    it('should create event with typed data', () => {
      interface MessageData {
        messageId: string;
        content: string;
      }

      const data: MessageData = {
        messageId: 'msg-789',
        content: 'Hello world',
      };

      const event = createStreamEvent<MessageData>('message.created', data);

      expect(event.eventType).toBe('message.created');
      expect(event.data.messageId).toBe('msg-789');
      expect(event.data.content).toBe('Hello world');
    });

    it('should handle empty data object', () => {
      const event = createStreamEvent('empty.event', {});

      expect(event.eventType).toBe('empty.event');
      expect(event.data).toEqual({});
    });

    it('should handle null data', () => {
      const event = createStreamEvent('null.event', null);

      expect(event.eventType).toBe('null.event');
      expect(event.data).toBeNull();
    });

    it('should create multiple independent events', () => {
      const event1 = createStreamEvent('event1', { id: 1 });
      const event2 = createStreamEvent('event2', { id: 2 });

      expect(event1.eventType).toBe('event1');
      expect(event2.eventType).toBe('event2');
      expect(event1.data).not.toEqual(event2.data);
    });
  });
});
