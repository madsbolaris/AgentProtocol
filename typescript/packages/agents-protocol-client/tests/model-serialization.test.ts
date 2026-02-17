/**
 * Tests for JSON serialization/deserialization of model classes
 * Validates that the models serialize correctly for the Agent Protocol API
 *
 * TypeScript equivalent of ModelSerializationTests.cs
 */

import type {
  ChatMessage,
  ChatRole,
  Run,
  RunStatus,
  Thread,
  ThreadStatus,
  ThreadCleanup,
  PromptAgent,
  AgentCard,
  RunError,
  CompletionUsage,
  Participant,
  AITool,
  JSONSchema,
  TextContent,
  ImageContent,
  AudioContent,
  VideoContent,
  FileContent,
  FunctionCallContent,
  FunctionResultContent,
} from '@microsoft/agents-protocol-abstractions';

describe('ModelSerializationTests', () => {
  describe('Run serialization', () => {
    it('should serialize and deserialize Run correctly', () => {
      // Arrange
      const run: Run = {
        runId: 'run_123',
        agentId: 'agent_001',
        threadId: 'thread_456',
        status: 'completed' as RunStatus,
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg_input',
            contents: [
              {
                kind: 'text',
                text: 'Hello',
              } as TextContent,
            ],
          },
        ],
        output: [
          {
            role: 'assistant' as ChatRole,
            messageId: 'msg_output',
            contents: [
              {
                kind: 'text',
                text: 'Hi there!',
              } as TextContent,
            ],
          },
        ],
        usage: {
          inputTokens: 10,
          outputTokens: 5,
          totalTokens: 15,
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        threadCleanup: 'keep' as ThreadCleanup,
      };

      // Act
      const json = JSON.stringify(run);
      const deserialized = JSON.parse(json) as Run;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.runId).toBe(run.runId);
      expect(deserialized.agentId).toBe(run.agentId);
      expect(deserialized.threadId).toBe(run.threadId);
      expect(deserialized.status).toBe(run.status);
      expect(deserialized.threadCleanup).toBe(run.threadCleanup);
      expect(deserialized.input).toHaveLength(1);
      expect(deserialized.output).toHaveLength(1);
    });

    it('should omit null/undefined fields in serialization', () => {
      // Arrange - Test that null fields are not included in JSON
      const run: Run = {
        runId: 'run_123',
        agentId: 'agent_001',
        input: [],
        output: [],
        status: 'completed' as RunStatus,
        usage: {
          inputTokens: 0,
          outputTokens: 0,
          totalTokens: 0,
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        // threadId, journalId, metadata intentionally omitted
      };

      // Act
      const json = JSON.stringify(run);

      // Assert
      expect(json).toContain('agentId');
      expect(json).toContain('input');
      expect(json).not.toContain('threadId');
      expect(json).not.toContain('journalId');
      expect(json).not.toContain('metadata');
    });
  });

  describe('ChatMessage with multiple content types', () => {
    it('should serialize ChatMessage with polymorphic content types', () => {
      // Arrange - Test polymorphic content types with 'kind' discriminator
      const message: ChatMessage = {
        messageId: 'msg_001',
        role: 'user' as ChatRole,
        contents: [
          {
            kind: 'text',
            text: "What's in this image?",
          } as TextContent,
          {
            kind: 'image',
            uri: 'https://example.com/image.jpg',
            alt: 'Test image',
            mimeType: 'image/jpeg',
          } as ImageContent,
          {
            kind: 'functionCall',
            callId: 'call_123',
            name: 'analyze_image',
            arguments: '{"url":"https://example.com/image.jpg"}',
          } as FunctionCallContent,
        ],
      };

      // Act
      const json = JSON.stringify(message);
      const deserialized = JSON.parse(json) as ChatMessage;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.contents).toHaveLength(3);

      // Validate TextContent
      const textContent = deserialized.contents[0] as TextContent;
      expect(textContent.kind).toBe('text');
      expect(textContent.text).toBe("What's in this image?");

      // Validate ImageContent
      const imageContent = deserialized.contents[1] as ImageContent;
      expect(imageContent.kind).toBe('image');
      expect(imageContent.uri).toBe('https://example.com/image.jpg');
      expect(imageContent.mimeType).toBe('image/jpeg');

      // Validate FunctionCallContent
      const functionCall = deserialized.contents[2] as FunctionCallContent;
      expect(functionCall.kind).toBe('functionCall');
      expect(functionCall.callId).toBe('call_123');
      expect(functionCall.name).toBe('analyze_image');
    });

    it('should handle all content types correctly', () => {
      // Arrange - Test all major content types
      const message: ChatMessage = {
        messageId: 'msg_multi',
        role: 'user' as ChatRole,
        contents: [
          { kind: 'text', text: 'Text content' } as TextContent,
          { kind: 'image', uri: 'https://example.com/img.jpg' } as ImageContent,
          { kind: 'audio', uri: 'https://example.com/audio.mp3', duration: 60 } as AudioContent,
          { kind: 'video', uri: 'https://example.com/video.mp4', duration: 120 } as VideoContent,
          { kind: 'file', uri: 'https://example.com/doc.pdf', filename: 'doc.pdf' } as FileContent,
        ],
      };

      // Act
      const json = JSON.stringify(message);
      const deserialized = JSON.parse(json) as ChatMessage;

      // Assert
      expect(deserialized.contents).toHaveLength(5);
      expect(deserialized.contents[0].kind).toBe('text');
      expect(deserialized.contents[1].kind).toBe('image');
      expect(deserialized.contents[2].kind).toBe('audio');
      expect(deserialized.contents[3].kind).toBe('video');
      expect(deserialized.contents[4].kind).toBe('file');

      // Validate specific properties
      const audioContent = deserialized.contents[2] as AudioContent;
      expect(audioContent.duration).toBe(60);

      const videoContent = deserialized.contents[3] as VideoContent;
      expect(videoContent.duration).toBe(120);

      const fileContent = deserialized.contents[4] as FileContent;
      expect(fileContent.filename).toBe('doc.pdf');
    });
  });

  describe('PromptAgent with tools', () => {
    it('should serialize PromptAgent with tools correctly', () => {
      // Arrange
      const agent: PromptAgent = {
        kind: 'promptAgent',
        name: 'weather-agent',
        displayName: 'Weather Assistant',
        description: 'You are a helpful assistant',
        tools: [
          {
            name: 'get_weather',
            description: 'Get weather information',
            parameters: {
              schemaType: 'object',
              properties: {
                location: {
                  schemaType: 'string',
                  description: 'City name',
                  format: 'city',
                },
                units: {
                  schemaType: 'string',
                  enum: ['celsius', 'fahrenheit'],
                },
              },
              required: ['location'],
            } as JSONSchema,
            requiresApproval: false,
          } as AITool,
        ],
      };

      // Act
      const json = JSON.stringify(agent);
      const deserialized = JSON.parse(json) as PromptAgent;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.kind).toBe('promptAgent');
      expect(deserialized.name).toBe('weather-agent');
      expect(deserialized.displayName).toBe('Weather Assistant');
      expect(deserialized.description).toBe('You are a helpful assistant');
      expect(deserialized.tools).toHaveLength(1);
      expect(deserialized.tools![0].name).toBe('get_weather');
      expect(deserialized.tools![0].parameters).toBeDefined();
      expect(deserialized.tools![0].parameters!.properties).toBeDefined();
      expect(Object.keys(deserialized.tools![0].parameters!.properties!)).toHaveLength(2);
    });
  });

  describe('Thread with participants', () => {
    it('should serialize Thread with participants correctly', () => {
      // Arrange
      const thread: Thread = {
        threadId: 'thread_123',
        status: 'active' as ThreadStatus,
        participants: [
          {
            id: 'user_001',
            kind: 'user',
            name: 'John Doe',
            role: 'user',
          } as Participant,
          {
            id: 'agent_001',
            kind: 'agent',
            name: 'Support Bot',
            role: 'assistant',
          } as Participant,
        ],
        messages: [],
        createdAt: new Date().toISOString(),
        unreadCount: 5,
        metadata: {
          priority: 'high',
          department: 'support',
        },
      };

      // Act
      const json = JSON.stringify(thread);
      const deserialized = JSON.parse(json) as Thread;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.threadId).toBe(thread.threadId);
      expect(deserialized.status).toBe(thread.status);
      expect(deserialized.participants).toHaveLength(2);
      expect(deserialized.participants[0].id).toBe('user_001');
      expect(deserialized.participants[1].id).toBe('agent_001');
      expect(deserialized.unreadCount).toBe(5);
      expect(deserialized.metadata).toBeDefined();
      expect(deserialized.metadata!.priority).toBe('high');
    });
  });

  describe('RunError with details', () => {
    it('should serialize RunError with details correctly', () => {
      // Arrange
      const error: RunError = {
        code: 'context_length_exceeded',
        message: 'The conversation exceeded the maximum token limit',
        details: {
          maxTokens: 128000,
          actualTokens: 150000,
          exceeded: true,
        },
      };

      // Act
      const json = JSON.stringify(error);
      const deserialized = JSON.parse(json) as RunError;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.code).toBe(error.code);
      expect(deserialized.message).toBe(error.message);
      expect(deserialized.details).toBeDefined();
      expect(Object.keys(deserialized.details!)).toHaveLength(3);
      expect(deserialized.details!.maxTokens).toBe(128000);
      expect(deserialized.details!.actualTokens).toBe(150000);
      expect(deserialized.details!.exceeded).toBe(true);
    });
  });

  describe('CompletionUsage', () => {
    it('should serialize CompletionUsage correctly', () => {
      // Arrange
      const usage: CompletionUsage = {
        inputTokens: 1000,
        outputTokens: 500,
        totalTokens: 1500,
      };

      // Act
      const json = JSON.stringify(usage);
      const deserialized = JSON.parse(json) as CompletionUsage;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.inputTokens).toBe(1000);
      expect(deserialized.outputTokens).toBe(500);
      expect(deserialized.totalTokens).toBe(1500);
    });
  });

  describe('AgentCard with capabilities', () => {
    it('should serialize AgentCard with capabilities correctly', () => {
      // Arrange
      const card: AgentCard = {
        agentId: 'agent_001',
        name: 'GPT-4o Agent',
        description: 'Advanced AI assistant',
        inputModes: ['text', 'image', 'audio'],
        outputModes: ['text'],
        tags: ['productivity', 'ai'],
      };

      // Act
      const json = JSON.stringify(card);
      const deserialized = JSON.parse(json) as AgentCard;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.agentId).toBe('agent_001');
      expect(deserialized.name).toBe('GPT-4o Agent');
      expect(deserialized.description).toBe('Advanced AI assistant');
      expect(deserialized.inputModes).toEqual(['text', 'image', 'audio']);
      expect(deserialized.outputModes).toEqual(['text']);
      expect(deserialized.tags).toEqual(['productivity', 'ai']);
    });
  });

  describe('RunStatus enum values', () => {
    it('should serialize all RunStatus enum values as strings', () => {
      // Arrange - Test all run status values
      const statuses: RunStatus[] = [
        'queued',
        'in_progress',
        'requires_action',
        'input_required',
        'auth_required',
        'cancelling',
        'cancelled',
        'failed',
        'completed',
        'incomplete',
        'timeout',
      ];

      // Act & Assert
      statuses.forEach((status) => {
        const json = JSON.stringify(status);
        const deserialized = JSON.parse(json) as RunStatus;
        expect(deserialized).toBe(status);
        expect(json).toContain(status); // Ensure it's serialized as string
      });
    });
  });

  describe('FunctionResultContent with error', () => {
    it('should serialize FunctionResultContent with error correctly', () => {
      // Arrange
      const content: FunctionResultContent = {
        kind: 'functionResult',
        callId: 'call_123',
        name: 'delete_file',
        result: 'Error: Permission denied',
      };

      // Act
      const json = JSON.stringify(content);
      const deserialized = JSON.parse(json) as FunctionResultContent;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.kind).toBe('functionResult');
      expect(deserialized.callId).toBe('call_123');
      expect(deserialized.name).toBe('delete_file');
      expect(deserialized.result).toContain('Permission denied');
    });
  });

  describe('Error handling', () => {
    it('should handle invalid JSON gracefully', () => {
      // Arrange
      const invalidJson = '{ "runId": "run_123", invalid }';

      // Act & Assert
      expect(() => JSON.parse(invalidJson)).toThrow(SyntaxError);
    });

    it('should handle missing required fields', () => {
      // Arrange
      const incompleteRun = {
        runId: 'run_123',
        // Missing required fields: agentId, status, input, output, etc.
      };

      // Act
      const json = JSON.stringify(incompleteRun);
      const deserialized = JSON.parse(json);

      // Assert - TypeScript won't enforce at runtime, but we can check
      expect(deserialized.runId).toBe('run_123');
      expect(deserialized.agentId).toBeUndefined();
      expect(deserialized.status).toBeUndefined();
    });

    it('should handle empty arrays correctly', () => {
      // Arrange
      const message: ChatMessage = {
        messageId: 'msg_empty',
        role: 'user' as ChatRole,
        contents: [],
      };

      // Act
      const json = JSON.stringify(message);
      const deserialized = JSON.parse(json) as ChatMessage;

      // Assert
      expect(deserialized.contents).toBeDefined();
      expect(deserialized.contents).toHaveLength(0);
      expect(Array.isArray(deserialized.contents)).toBe(true);
    });

    it('should handle nested objects correctly', () => {
      // Arrange
      const run: Run = {
        runId: 'run_nested',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: {
          inputTokens: 100,
          outputTokens: 50,
          totalTokens: 150,
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        metadata: {
          nested: {
            deeply: {
              value: 'test',
            },
          },
        },
      };

      // Act
      const json = JSON.stringify(run);
      const deserialized = JSON.parse(json) as Run;

      // Assert
      expect(deserialized.metadata).toBeDefined();
      expect((deserialized.metadata as any).nested.deeply.value).toBe('test');
    });
  });

  describe('Type validation', () => {
    it('should preserve content kind discriminators', () => {
      // Arrange
      const contents = [
        { kind: 'text', text: 'Hello' } as TextContent,
        { kind: 'image', uri: 'https://example.com/img.jpg' } as ImageContent,
        { kind: 'audio', uri: 'https://example.com/audio.mp3' } as AudioContent,
        { kind: 'video', uri: 'https://example.com/video.mp4' } as VideoContent,
        { kind: 'file', uri: 'https://example.com/file.pdf' } as FileContent,
        { kind: 'functionCall', callId: 'call_1', name: 'func', arguments: '{}' } as FunctionCallContent,
        { kind: 'functionResult', callId: 'call_1', name: 'func', result: 'ok' } as FunctionResultContent,
      ];

      // Act
      const json = JSON.stringify(contents);
      const deserialized = JSON.parse(json);

      // Assert - Verify each content type preserves its 'kind' discriminator
      expect(deserialized[0].kind).toBe('text');
      expect(deserialized[1].kind).toBe('image');
      expect(deserialized[2].kind).toBe('audio');
      expect(deserialized[3].kind).toBe('video');
      expect(deserialized[4].kind).toBe('file');
      expect(deserialized[5].kind).toBe('functionCall');
      expect(deserialized[6].kind).toBe('functionResult');
    });

    it('should handle special characters in strings', () => {
      // Arrange
      const message: ChatMessage = {
        messageId: 'msg_special',
        role: 'user' as ChatRole,
        contents: [
          {
            kind: 'text',
            text: 'Special chars: "quotes", \'apostrophes\', newlines\n, tabs\t, backslashes\\',
          } as TextContent,
        ],
      };

      // Act
      const json = JSON.stringify(message);
      const deserialized = JSON.parse(json) as ChatMessage;

      // Assert
      const textContent = deserialized.contents[0] as TextContent;
      expect(textContent.text).toContain('quotes');
      expect(textContent.text).toContain('apostrophes');
      expect(textContent.text).toContain('\n');
      expect(textContent.text).toContain('\t');
    });

    it('should handle Unicode characters', () => {
      // Arrange
      const message: ChatMessage = {
        messageId: 'msg_unicode',
        role: 'user' as ChatRole,
        contents: [
          {
            kind: 'text',
            text: 'Unicode: 你好 🌍 café résumé',
          } as TextContent,
        ],
      };

      // Act
      const json = JSON.stringify(message);
      const deserialized = JSON.parse(json) as ChatMessage;

      // Assert
      const textContent = deserialized.contents[0] as TextContent;
      expect(textContent.text).toBe('Unicode: 你好 🌍 café résumé');
    });

    it('should handle numbers as strings in JSON', () => {
      // Arrange
      const usage: CompletionUsage = {
        inputTokens: 1234,
        outputTokens: 5678,
        totalTokens: 6912,
      };

      // Act
      const json = JSON.stringify(usage);
      const deserialized = JSON.parse(json) as CompletionUsage;

      // Assert - Numbers should remain numbers
      expect(typeof deserialized.inputTokens).toBe('number');
      expect(typeof deserialized.outputTokens).toBe('number');
      expect(typeof deserialized.totalTokens).toBe('number');
    });

    it('should handle boolean values correctly', () => {
      // Arrange
      const tool: AITool = {
        name: 'test_tool',
        description: 'A test tool',
        parameters: {} as JSONSchema,
        requiresApproval: true,
      };

      // Act
      const json = JSON.stringify(tool);
      const deserialized = JSON.parse(json) as AITool;

      // Assert
      expect(deserialized.requiresApproval).toBe(true);
      expect(typeof deserialized.requiresApproval).toBe('boolean');
    });
  });

  describe('Complex nested structures', () => {
    it('should handle Run with full nested structure', () => {
      // Arrange - Complex run with all nested structures
      const run: Run = {
        runId: 'run_complex',
        agentId: 'agent_001',
        threadId: 'thread_001',
        status: 'completed' as RunStatus,
        input: [
          {
            messageId: 'msg_in',
            role: 'user' as ChatRole,
            contents: [
              { kind: 'text', text: 'Hello' } as TextContent,
              { kind: 'image', uri: 'https://example.com/img.jpg' } as ImageContent,
            ],
            createdAt: new Date().toISOString(),
          },
        ],
        output: [
          {
            messageId: 'msg_out',
            role: 'assistant' as ChatRole,
            contents: [
              { kind: 'text', text: 'Response' } as TextContent,
              {
                kind: 'functionCall',
                callId: 'call_1',
                name: 'get_weather',
                arguments: '{"location":"London"}',
              } as FunctionCallContent,
            ],
            agentId: 'agent_001',
            createdAt: new Date().toISOString(),
          },
        ],
        usage: {
          inputTokens: 150,
          outputTokens: 75,
          totalTokens: 225,
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
        metadata: {
          requestId: 'req_123',
          sessionId: 'session_456',
          customData: {
            nested: true,
          },
        },
      };

      // Act
      const json = JSON.stringify(run);
      const deserialized = JSON.parse(json) as Run;

      // Assert
      expect(deserialized).toBeDefined();
      expect(deserialized.runId).toBe('run_complex');
      expect(deserialized.input).toHaveLength(1);
      expect(deserialized.input[0].contents).toHaveLength(2);
      expect(deserialized.output).toHaveLength(1);
      expect(deserialized.output[0].contents).toHaveLength(2);
      expect(deserialized.usage.totalTokens).toBe(225);
      expect((deserialized.metadata as any).customData.nested).toBe(true);
    });

    it('should handle Thread with messages and all fields', () => {
      // Arrange
      const thread: Thread = {
        threadId: 'thread_full',
        status: 'active' as ThreadStatus,
        participants: [
          {
            id: 'user_1',
            kind: 'user',
            name: 'Alice',
            role: 'user',
          } as Participant,
        ],
        messages: [
          {
            messageId: 'msg_1',
            role: 'user' as ChatRole,
            contents: [{ kind: 'text', text: 'Hello' } as TextContent],
            userId: 'user_1',
            createdAt: new Date().toISOString(),
          },
          {
            messageId: 'msg_2',
            role: 'assistant' as ChatRole,
            contents: [{ kind: 'text', text: 'Hi' } as TextContent],
            agentId: 'agent_1',
            createdAt: new Date().toISOString(),
          },
        ],
        createdAt: new Date().toISOString(),
        lastMessageAt: new Date().toISOString(),
        lastActivityAt: new Date().toISOString(),
        unreadCount: 1,
        metadata: {
          topic: 'General Discussion',
        },
      };

      // Act
      const json = JSON.stringify(thread);
      const deserialized = JSON.parse(json) as Thread;

      // Assert
      expect(deserialized.threadId).toBe('thread_full');
      expect(deserialized.messages).toHaveLength(2);
      expect(deserialized.participants).toHaveLength(1);
      expect(deserialized.unreadCount).toBe(1);
      expect((deserialized.metadata as any).topic).toBe('General Discussion');
    });
  });

  describe('Date handling', () => {
    it('should serialize ISO date strings correctly', () => {
      // Arrange
      const now = new Date().toISOString();
      const run: Run = {
        runId: 'run_date',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: {},
        createdAt: now,
        updatedAt: now,
        completedAt: now,
      };

      // Act
      const json = JSON.stringify(run);
      const deserialized = JSON.parse(json) as Run;

      // Assert
      expect(deserialized.createdAt).toBe(now);
      expect(deserialized.updatedAt).toBe(now);
      expect(deserialized.completedAt).toBe(now);

      // Verify dates can be parsed back
      expect(new Date(deserialized.createdAt!).toISOString()).toBe(now);
    });
  });

  describe('Array handling', () => {
    it('should handle empty and populated arrays consistently', () => {
      // Arrange
      const emptyRun: Run = {
        runId: 'run_empty',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      const populatedRun: Run = {
        ...emptyRun,
        runId: 'run_populated',
        input: [
          {
            messageId: 'msg_1',
            role: 'user' as ChatRole,
            contents: [{ kind: 'text', text: 'Test' } as TextContent],
          },
        ],
      };

      // Act
      const emptyJson = JSON.stringify(emptyRun);
      const populatedJson = JSON.stringify(populatedRun);
      const emptyDeserialized = JSON.parse(emptyJson) as Run;
      const populatedDeserialized = JSON.parse(populatedJson) as Run;

      // Assert
      expect(emptyDeserialized.input).toHaveLength(0);
      expect(populatedDeserialized.input).toHaveLength(1);
      expect(Array.isArray(emptyDeserialized.input)).toBe(true);
      expect(Array.isArray(populatedDeserialized.input)).toBe(true);
    });
  });
});
