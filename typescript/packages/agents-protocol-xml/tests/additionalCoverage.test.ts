/**
 * Additional tests to reach 90%+ coverage on TypeScript XML SDK.
 */

import { describe, test, expect } from '@jest/globals';
import { preprocess } from '../src/evalXmlPreprocessor';
import { ValidationResult } from '../src/validation/ValidationResult';
import { ThreadValidator } from '../src/validation/ThreadValidator';

describe('EvalXmlPreprocessor Additional Coverage', () => {
  test('text content after last tag', () => {
    // This tests lines 35-36: the break when no more tags are found
    // Input has a tag followed by plain text with no more tags
    const input = '<assert>x == 5</assert>Some plain text after the tag with no more tags < or > characters here.';
    const result = preprocess(input);

    // The assert should be wrapped, and the trailing text preserved
    expect(result).toContain('<![CDATA[x == 5]]>');
    expect(result).toContain('Some plain text after the tag');
  });

  test('text with isolated less-than not part of tag', () => {
    // This tests lines 46-48: when '<' is found but doesn't match TAG_REGEX
    // A '<' that is not followed by a valid tag name
    const input = '<assert>value</assert> Text with < 5 comparison < another one';
    const result = preprocess(input);

    // Should handle the '<' characters that aren't part of tags
    expect(result).toContain('<![CDATA[value]]>');
    expect(result).toContain(' Text with < 5 comparison < another one');
  });

  test('less-than at end of string', () => {
    // Edge case: input ends with '<' that doesn't form a tag
    const input = '<metric>x > 0</metric> Final text <';
    const result = preprocess(input);

    expect(result).toContain('<![CDATA[x > 0]]>');
    expect(result).toContain('Final text <');
  });

  test('multiple isolated less-than characters', () => {
    // Multiple '<' characters that don't form tags
    const input = 'Start << middle < < end';
    const result = preprocess(input);

    // Should preserve all the '<' characters since they're not tags
    expect(result).toBe('Start << middle < < end');
  });

  test('less-than followed by space', () => {
    // '<' followed by space doesn't match TAG_REGEX
    const input = '<args>test</args> Value < 10 and < 20';
    const result = preprocess(input);

    expect(result).toContain('<![CDATA[test]]>');
    expect(result).toContain('Value < 10 and < 20');
  });

  test('less-than followed by number', () => {
    // '<' followed by number doesn't match TAG_REGEX (tag names start with letter)
    const input = 'Check if x <5 or y <10';
    const result = preprocess(input);

    expect(result).toBe('Check if x <5 or y <10');
  });
});

describe('ValidationResult Additional Coverage', () => {
  test('error with field in toString', () => {
    // Test that toString properly formats errors with field names
    const result = ValidationResult.failure('Invalid value', { field: 'testField', code: 'TEST_001' });
    const str = result.toString();

    expect(str).toContain('testField: Invalid value');
  });

  test('multiple errors in toString', () => {
    // Test toString with multiple errors
    const result = ValidationResult.success();
    result.addError('First error', { field: 'field1', code: 'ERR_001' });
    result.addError('Second error', { field: 'field2', code: 'ERR_002' });
    result.addError('Third error'); // No field

    const str = result.toString();
    expect(str).toContain('3 error(s)');
    expect(str).toContain('field1: First error');
    expect(str).toContain('field2: Second error');
    expect(str).toContain('Third error');
  });

  test('addError with context', () => {
    // Test that addError properly handles context
    const result = ValidationResult.success();
    result.addError('Error with context', {
      field: 'testField',
      code: 'TEST_001',
      context: { key1: 'value1', key2: 123 }
    });

    expect(result.isValid).toBe(false);
    expect(result.errors[0].context).toEqual({ key1: 'value1', key2: 123 });
  });

  test('constructor with explicit parameters', () => {
    // Test constructor with explicit errors and warnings arrays
    const errors = [{ message: 'Error 1', code: 'ERR_001' }];
    const warnings = ['Warning 1'];
    const result = new ValidationResult(false, errors, warnings);

    expect(result.isValid).toBe(false);
    expect(result.errors).toEqual(errors);
    expect(result.warnings).toEqual(warnings);
  });

  test('constructor with partial parameters', () => {
    // Test constructor with only isValid parameter (defaults for rest)
    const result = new ValidationResult(false);

    expect(result.isValid).toBe(false);
    expect(result.errors).toEqual([]);
    expect(result.warnings).toEqual([]);
  });
});

describe('ThreadValidator Additional Coverage', () => {
  const validator = new ThreadValidator();

  test('validates empty messages array', () => {
    // Empty messages list should be valid
    const thread = {
      threadId: 'thread-123',
      messages: []
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('handles snake_case field names', () => {
    // Test thread_id and message_id snake_case variants
    const thread = {
      thread_id: 'thread-123',
      messages: [
        {
          role: 'user',
          message_id: 'msg-1',
          contents: [{ kind: 'text', text: 'Hello' }]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('handles createdAt as Date object', () => {
    // Test created_at with Date objects instead of strings
    const now = new Date();
    const earlier = new Date(now.getTime() - 3600000);

    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          createdAt: earlier,
          contents: [{ kind: 'text', text: 'First' }]
        },
        {
          role: 'agent',
          messageId: 'msg-2',
          createdAt: now,
          contents: [{ kind: 'text', text: 'Second' }]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('detects missing messages attribute', () => {
    // Thread without messages attribute (null/undefined)
    const thread: any = {
      threadId: 'thread-123'
    };
    thread.messages = null;

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_002')).toBe(true);
  });

  test('detects messages not in array format', () => {
    // Messages should be an array
    const thread = {
      threadId: 'thread-123',
      messages: 'not an array'
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_002')).toBe(true);
  });

  test('detects contents not in array format', () => {
    // Contents should be an array
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          contents: 'not an array'
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_006')).toBe(true);
  });

  test('warns about empty contents', () => {
    // Empty contents array should produce warning
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          contents: []
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true); // Valid but has warnings
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  test('validates role channel', () => {
    // 'channel' is a valid role
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'channel',
          messageId: 'msg-1',
          contents: [{ kind: 'text', text: 'Channel message' }]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('handles content field alias', () => {
    // Some messages use 'content' instead of 'contents'
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          content: [{ kind: 'text', text: 'Hello' }]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('handles function_call kind alias', () => {
    // Test snake_case kind aliases
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'function_call', call_id: 'call-1', name: 'test_func', arguments: '{}' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-2',
          contents: [
            { kind: 'function_result', call_id: 'call-1', name: 'test_func', result: 'Success' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
  });

  test('detects function result missing call-id', () => {
    // Function result without call-id
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'tool',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionResult', name: 'test_func', result: 'data' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(false);
    expect(result.errors.some(e => e.code === 'THREAD_010')).toBe(true);
  });

  test('warns about empty text content', () => {
    // Text content with empty or whitespace-only text
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'user',
          messageId: 'msg-1',
          contents: [
            { kind: 'text', text: '   ' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true); // Valid but has warning
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  test('handles missing role gracefully', () => {
    // Message without role (might be inferred)
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          messageId: 'msg-1',
          contents: [{ kind: 'text', text: 'Hello' }]
        }
      ]
    };

    const result = validator.validate(thread);
    // Should be valid - role is optional and might be inferred
    expect(result.isValid).toBe(true);
  });

  test('tracks function call name for validation', () => {
    // Ensure function call name is properly tracked
    const thread = {
      threadId: 'thread-123',
      messages: [
        {
          role: 'agent',
          messageId: 'msg-1',
          contents: [
            { kind: 'functionCall', callId: 'call-1', name: 'get_data', arguments: '{}' }
          ]
        },
        {
          role: 'tool',
          messageId: 'msg-2',
          contents: [
            { kind: 'functionResult', callId: 'call-1', name: 'get_data', result: 'data' }
          ]
        }
      ]
    };

    const result = validator.validate(thread);
    expect(result.isValid).toBe(true);
    expect(result.warnings.length).toBe(0);
  });
});
