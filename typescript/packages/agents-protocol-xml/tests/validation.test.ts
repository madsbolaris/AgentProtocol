/**
 * Tests for validation framework
 */

import { describe, test, expect } from '@jest/globals';
import { ValidationResult } from '../src/validation/ValidationResult';
import { ThreadValidator } from '../src/validation/ThreadValidator';

describe('ValidationResult', () => {
  test('success creates valid result', () => {
    const result = ValidationResult.success();
    expect(result.isValid).toBe(true);
    expect(result.errors).toEqual([]);
    expect(result.warnings).toEqual([]);
  });

  test('failure creates invalid result with error', () => {
    const result = ValidationResult.failure('Test error', { field: 'testField', code: 'TEST_001' });
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBe(1);
    expect(result.errors[0].message).toBe('Test error');
    expect(result.errors[0].field).toBe('testField');
    expect(result.errors[0].code).toBe('TEST_001');
  });

  test('addError marks result as invalid', () => {
    const result = ValidationResult.success();
    expect(result.isValid).toBe(true);

    result.addError('Error message');
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBe(1);
  });

  test('addWarning keeps result valid', () => {
    const result = ValidationResult.success();
    result.addWarning('Warning message');
    expect(result.isValid).toBe(true);
    expect(result.warnings.length).toBe(1);
  });

  test('toString shows validation status', () => {
    const successResult = ValidationResult.success();
    expect(successResult.toString()).toBe('Validation passed');

    const failureResult = ValidationResult.failure('Test error');
    expect(failureResult.toString()).toContain('Validation failed');
    expect(failureResult.toString()).toContain('Test error');
  });
});

describe('ThreadValidator', () => {
  const validator = new ThreadValidator();

  test('validates valid thread', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          contents: [{ kind: 'text', text: 'Hello' }]
        },
        {
          role: 'agent',
          messageId: 'msg-2',
          contents: [{ kind: 'text', text: 'Hi there' }]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  test('detects missing thread ID', () => {
    const thread = {
      messages: []
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_001')).toBe(true);
  });

  test('detects duplicate message IDs', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        { role: 'user', messageId: 'msg-1', contents: [{ kind: 'text', text: 'Hello' }] },
        { role: 'agent', messageId: 'msg-1', contents: [{ kind: 'text', text: 'Hi' }] }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_003')).toBe(true);
  });

  test('detects invalid role', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        { role: 'invalid_role', messageId: 'msg-1', contents: [{ kind: 'text', text: 'Hello' }] }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_005')).toBe(true);
  });

  test('detects out of order messages', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        { role: 'user', messageId: 'msg-1', createdAt: '2024-01-01T12:00:00Z', contents: [{ kind: 'text', text: 'First' }] },
        { role: 'agent', messageId: 'msg-2', createdAt: '2024-01-01T11:00:00Z', contents: [{ kind: 'text', text: 'Second' }] }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_004')).toBe(true);
  });

  test('detects function call without result', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'get_weather', arguments: '{}' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true); // Valid but has warnings
    expect(result.warnings.some(w => w.includes('call-1'))).toBe(true);
  });

  test('detects function result without matching call', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'tool',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionResult', callId: 'call-999', result: 'result data' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_011')).toBe(true);
  });

  test('detects duplicate call-id in message', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'func1', arguments: '{}' },
            { kind: 'functionCall', callId: 'call-1', name: 'func2', arguments: '{}' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_008')).toBe(true);
  });

  test('detects function call missing call-id', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', name: 'get_weather', arguments: '{}' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_007')).toBe(true);
  });

  test('detects function call missing name', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', arguments: '{}' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_009')).toBe(true);
  });

  test('validates complete function call-result flow', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'get_weather', arguments: '{"city":"SF"}' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-2',
          contents: [
            { kind: 'functionResult', callId: 'call-1', name: 'get_weather', result: 'Sunny, 72°F' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  test('detects mismatched function names', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'get_weather', arguments: '{}' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-2',
          contents: [
            { kind: 'functionResult', callId: 'call-1', name: 'get_temperature', result: '72°F' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_012')).toBe(true);
  });

  test('detects already fulfilled call-id', () => {
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'get_weather', arguments: '{}' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-2',
          contents: [
            { kind: 'functionResult', callId: 'call-1', result: 'Result 1' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-3',
          contents: [
            { kind: 'functionResult', callId: 'call-1', result: 'Result 2' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_013')).toBe(true);
  });
});
