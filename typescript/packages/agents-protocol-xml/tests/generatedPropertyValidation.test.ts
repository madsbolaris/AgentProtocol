/**
 * Auto-generated property validation tests.
 * Tests that every property serializes and deserializes correctly.
 */

import { describe, it, expect } from '@jest/globals';
import { MessageSerializer } from '../src/serialization/MessageSerializer';
import {
  TextContent,
  FunctionCallContent,
  FunctionResultContent,
  ErrorContent,
  TextReasoningContent,
  DataContent,
  UriContent,
  ImageContent,
  AudioContent,
  TranscriptContent,
  VideoContent,
  FileContent,
  SearchResultContent,
  DocumentContent,
  AdaptiveCardContent,
  RefusalContent,
  ContentFilterResultContent,
  UserInputRequestContent,
  SuggestedActionsContent,
  EventContent,
  TraceContent,
  ActionContent,
  TypingIndicatorContent,
  MessageReactionContent,
  MessageDeleteContent,
  MessageUpdateContent,
  HostedFileContent,
  HostedVectorStoreContent,
} from '../src/models';


describe('TextContent Property Tests', () => {

  it('should deserialize text property correctly', () => {
    // Arrange: XML with text property set
    const xml = `<agent message-id="textContent_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_1">
  <text>test_value</text>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextContent;
    expect(content.text).toBeDefined();
    expect(content.text).toBe(testValue);
  });

});

describe('FunctionCallContent Property Tests', () => {

  it('should deserialize callId property correctly', () => {
    // Arrange: XML with callId property set
    const xml = `<agent message-id="functionCallContent_callId_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_2">
  <function-call call-id="test_id_123" name="test">test</function-call>
</agent>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionCallContent;
    expect(content.callId).toBeDefined();
    expect(content.callId).toBe(testValue);
  });

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<agent message-id="functionCallContent_name_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_3">
  <function-call call-id="test" name="Test Name">test</function-call>
</agent>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionCallContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize arguments property correctly', () => {
    // Arrange: XML with arguments property set
    const xml = `<agent message-id="functionCallContent_arguments_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_4">
  <function-call call-id="test" name="test">test_value</function-call>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionCallContent;
    expect(content.arguments).toBeDefined();
    expect(content.arguments).toBe(testValue);
  });

});

describe('FunctionResultContent Property Tests', () => {

  it('should deserialize callId property correctly', () => {
    // Arrange: XML with callId property set
    const xml = `<tool message-id="functionResultContent_callId_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result call-id="test_id_123">test</function-result>
</tool>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionResultContent;
    expect(content.callId).toBeDefined();
    expect(content.callId).toBe(testValue);
  });

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<tool message-id="functionResultContent_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result name="Test Name">test</function-result>
</tool>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionResultContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize result property correctly', () => {
    // Arrange: XML with result property set
    const xml = `<tool message-id="functionResultContent_result_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test_value</function-result>
</tool>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionResultContent;
    expect(content.result).toBeDefined();
    expect(content.result).toBe(testValue);
  });

});

describe('ErrorContent Property Tests', () => {

  it('should deserialize code property correctly', () => {
    // Arrange: XML with code property set
    const xml = `<agent message-id="errorContent_code_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_8">
  <error code="test_value">
    <message>test</message>
  </error>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ErrorContent;
    expect(content.code).toBeDefined();
    expect(content.code).toBe(testValue);
  });

  it('should deserialize message property correctly', () => {
    // Arrange: XML with message property set
    const xml = `<agent message-id="errorContent_message_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_9">
  <error>
    <message>test_value</message>
  </error>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ErrorContent;
    expect(content.message).toBeDefined();
    expect(content.message).toBe(testValue);
  });

  it('should deserialize stackTrace property correctly', () => {
    // Arrange: XML with stackTrace property set
    const xml = `<agent message-id="errorContent_stackTrace_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_10">
  <error>
    <message>test</message>
    <stack-trace>test_value</stack-trace>
  </error>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ErrorContent;
    expect(content.stackTrace).toBeDefined();
    expect(content.stackTrace).toBe(testValue);
  });

});

describe('TextReasoningContent Property Tests', () => {

  it('should deserialize text property correctly', () => {
    // Arrange: XML with text property set
    const xml = `<agent message-id="textReasoningContent_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_11">
  <thinking>test_value</thinking>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextReasoningContent;
    expect(content.text).toBeDefined();
    expect(content.text).toBe(testValue);
  });

  it('should deserialize exposed property correctly', () => {
    // Arrange: XML with exposed property set
    const xml = `<agent message-id="textReasoningContent_exposed_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_12">
  <thinking exposed="true">test</thinking>
</agent>
`;
    const testValue = 'true';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextReasoningContent;
    expect(content.exposed).toBeDefined();
    expect(content.exposed).toBe(testValue === 'true');
  });

});

describe('DataContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="dataContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_13">
  <data uri="https://example.com"/>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DataContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="dataContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_14">
  <data mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DataContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize value property correctly', () => {
    // Arrange: XML with value property set
    const xml = `<agent message-id="dataContent_value_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_15">
  <data>test_value</data>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DataContent;
    expect(content.value).toBeDefined();
    expect(content.value).toBe(testValue);
  });

});

describe('UriContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="uriContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_16">
  <uri>https://example.com</uri>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UriContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

});

describe('ImageContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="imageContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_17">
  <image uri="https://example.com"/>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

  it('should deserialize alt property correctly', () => {
    // Arrange: XML with alt property set
    const xml = `<agent message-id="imageContent_alt_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_18">
  <image alt="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.alt).toBeDefined();
    expect(content.alt).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="imageContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_19">
  <image mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize width property correctly', () => {
    // Arrange: XML with width property set
    const xml = `<agent message-id="imageContent_width_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_20">
  <image width="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.width).toBeDefined();
    expect(content.width).toBe(parseInt(testValue));
  });

  it('should deserialize height property correctly', () => {
    // Arrange: XML with height property set
    const xml = `<agent message-id="imageContent_height_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_21">
  <image height="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.height).toBeDefined();
    expect(content.height).toBe(parseInt(testValue));
  });

});

describe('AudioContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="audioContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_22">
  <audio uri="https://example.com"/>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AudioContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="audioContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_23">
  <audio mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AudioContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize duration property correctly', () => {
    // Arrange: XML with duration property set
    const xml = `<agent message-id="audioContent_duration_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_24">
  <audio duration="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AudioContent;
    expect(content.duration).toBeDefined();
    expect(content.duration).toBe(parseInt(testValue));
  });

});

describe('TranscriptContent Property Tests', () => {

  it('should deserialize text property correctly', () => {
    // Arrange: XML with text property set
    const xml = `<agent message-id="transcriptContent_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_25">
  <transcript text="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content.text).toBeDefined();
    expect(content.text).toBe(testValue);
  });

  it('should deserialize language property correctly', () => {
    // Arrange: XML with language property set
    const xml = `<agent message-id="transcriptContent_language_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_26">
  <transcript text="test" language="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content.language).toBeDefined();
    expect(content.language).toBe(testValue);
  });

  it('should deserialize confidence property correctly', () => {
    // Arrange: XML with confidence property set
    const xml = `<agent message-id="transcriptContent_confidence_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_27">
  <transcript text="test" confidence="3.14"/>
</agent>
`;
    const testValue = '3.14';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content.confidence).toBeDefined();
    expect(content.confidence).toBeCloseTo(parseFloat(testValue), 2);
  });

  it('should deserialize speaker property correctly', () => {
    // Arrange: XML with speaker property set
    const xml = `<agent message-id="transcriptContent_speaker_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_28">
  <transcript text="test" speaker="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content.speaker).toBeDefined();
    expect(content.speaker).toBe(testValue);
  });

});

describe('VideoContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="videoContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_29">
  <video uri="https://example.com"/>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="videoContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_30">
  <video mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize width property correctly', () => {
    // Arrange: XML with width property set
    const xml = `<agent message-id="videoContent_width_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_31">
  <video width="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.width).toBeDefined();
    expect(content.width).toBe(parseInt(testValue));
  });

  it('should deserialize height property correctly', () => {
    // Arrange: XML with height property set
    const xml = `<agent message-id="videoContent_height_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_32">
  <video height="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.height).toBeDefined();
    expect(content.height).toBe(parseInt(testValue));
  });

  it('should deserialize duration property correctly', () => {
    // Arrange: XML with duration property set
    const xml = `<agent message-id="videoContent_duration_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_33">
  <video duration="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.duration).toBeDefined();
    expect(content.duration).toBe(parseInt(testValue));
  });

  it('should deserialize frameRate property correctly', () => {
    // Arrange: XML with frameRate property set
    const xml = `<agent message-id="videoContent_frameRate_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_34">
  <video frame-rate="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.frameRate).toBeDefined();
    expect(content.frameRate).toBe(parseInt(testValue));
  });

});

describe('FileContent Property Tests', () => {

  it('should deserialize uri property correctly', () => {
    // Arrange: XML with uri property set
    const xml = `<agent message-id="fileContent_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_35">
  <file uri="https://example.com"/>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content.uri).toBeDefined();
    expect(content.uri).toBe(testValue);
  });

  it('should deserialize filename property correctly', () => {
    // Arrange: XML with filename property set
    const xml = `<agent message-id="fileContent_filename_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_36">
  <file filename="Test Name"/>
</agent>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content.filename).toBeDefined();
    expect(content.filename).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="fileContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_37">
  <file mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize sizeBytes property correctly', () => {
    // Arrange: XML with sizeBytes property set
    const xml = `<agent message-id="fileContent_sizeBytes_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_38">
  <file size-bytes="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content.sizeBytes).toBeDefined();
    expect(content.sizeBytes).toBe(parseInt(testValue));
  });

});

describe('SearchResultContent Property Tests', () => {

  it('should deserialize title property correctly', () => {
    // Arrange: XML with title property set
    const xml = `<agent message-id="searchResultContent_title_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_39">
  <search-result title="test_value" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content.title).toBeDefined();
    expect(content.title).toBe(testValue);
  });

  it('should deserialize url property correctly', () => {
    // Arrange: XML with url property set
    const xml = `<agent message-id="searchResultContent_url_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_40">
  <search-result title="test" url="https://example.com">
    <snippet>test</snippet>
  </search-result>
</agent>
`;
    const testValue = 'https://example.com';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content.url).toBeDefined();
    expect(content.url).toBe(testValue);
  });

  it('should deserialize score property correctly', () => {
    // Arrange: XML with score property set
    const xml = `<agent message-id="searchResultContent_score_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_41">
  <search-result title="test" url="test" score="3.14">
    <snippet>test</snippet>
  </search-result>
</agent>
`;
    const testValue = '3.14';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content.score).toBeDefined();
    expect(content.score).toBeCloseTo(parseFloat(testValue), 2);
  });

  it('should deserialize snippet property correctly', () => {
    // Arrange: XML with snippet property set
    const xml = `<agent message-id="searchResultContent_snippet_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_42">
  <search-result title="test" url="test">
    <snippet>test_value</snippet>
  </search-result>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content.snippet).toBeDefined();
    expect(content.snippet).toBe(testValue);
  });

});

describe('DocumentContent Property Tests', () => {

  it('should deserialize title property correctly', () => {
    // Arrange: XML with title property set
    const xml = `<agent message-id="documentContent_title_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_43">
  <document title="test_value" document-id="test" source="test"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.title).toBeDefined();
    expect(content.title).toBe(testValue);
  });

  it('should deserialize documentId property correctly', () => {
    // Arrange: XML with documentId property set
    const xml = `<agent message-id="documentContent_documentId_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_44">
  <document title="test" document-id="test_id_123" source="test"/>
</agent>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.documentId).toBeDefined();
    expect(content.documentId).toBe(testValue);
  });

  it('should deserialize source property correctly', () => {
    // Arrange: XML with source property set
    const xml = `<agent message-id="documentContent_source_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_45">
  <document title="test" document-id="test" source="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.source).toBeDefined();
    expect(content.source).toBe(testValue);
  });

  it('should deserialize mimeType property correctly', () => {
    // Arrange: XML with mimeType property set
    const xml = `<agent message-id="documentContent_mimeType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_46">
  <document title="test" document-id="test" source="test" mime-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.mimeType).toBeDefined();
    expect(content.mimeType).toBe(testValue);
  });

  it('should deserialize content property correctly', () => {
    // Arrange: XML with content property set
    const xml = `<agent message-id="documentContent_content_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_47">
  <document title="test" document-id="test" source="test">
    <content>test_value</content>
  </document>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.content).toBeDefined();
    expect(content.content).toBe(testValue);
  });

});

describe('AdaptiveCardContent Property Tests', () => {

  it('should deserialize version property correctly', () => {
    // Arrange: XML with version property set
    const xml = `<agent message-id="adaptiveCardContent_version_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_48">
  <adaptive-card version="test_value">test</adaptive-card>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AdaptiveCardContent;
    expect(content.version).toBeDefined();
    expect(content.version).toBe(testValue);
  });

  it('should deserialize fallbackText property correctly', () => {
    // Arrange: XML with fallbackText property set
    const xml = `<agent message-id="adaptiveCardContent_fallbackText_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_49">
  <adaptive-card fallback-text="test_value">test</adaptive-card>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AdaptiveCardContent;
    expect(content.fallbackText).toBeDefined();
    expect(content.fallbackText).toBe(testValue);
  });

  it('should deserialize card property correctly', () => {
    // Arrange: XML with card property set
    const xml = `<agent message-id="adaptiveCardContent_card_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_50">
  <adaptive-card>test_value</adaptive-card>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AdaptiveCardContent;
    expect(content.card).toBeDefined();
    expect(content.card).toBe(testValue);
  });

});

describe('RefusalContent Property Tests', () => {

  it('should deserialize reason property correctly', () => {
    // Arrange: XML with reason property set
    const xml = `<agent message-id="refusalContent_reason_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_51">
  <refusal reason="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as RefusalContent;
    expect(content.reason).toBeDefined();
    expect(content.reason).toBe(testValue);
  });

});

describe('ContentFilterResultContent Property Tests', () => {

  it('should deserialize filtered property correctly', () => {
    // Arrange: XML with filtered property set
    const xml = `<agent message-id="contentFilterResultContent_filtered_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_52">
  <content-filter-result filtered="true" category="test" severity="test"/>
</agent>
`;
    const testValue = 'true';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ContentFilterResultContent;
    expect(content.filtered).toBeDefined();
    expect(content.filtered).toBe(testValue === 'true');
  });

  it('should deserialize category property correctly', () => {
    // Arrange: XML with category property set
    const xml = `<agent message-id="contentFilterResultContent_category_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_53">
  <content-filter-result filtered="true" category="test_value" severity="test"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ContentFilterResultContent;
    expect(content.category).toBeDefined();
    expect(content.category).toBe(testValue);
  });

  it('should deserialize severity property correctly', () => {
    // Arrange: XML with severity property set
    const xml = `<agent message-id="contentFilterResultContent_severity_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_54">
  <content-filter-result filtered="true" category="test" severity="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ContentFilterResultContent;
    expect(content.severity).toBeDefined();
    expect(content.severity).toBe(testValue);
  });

});

describe('UserInputRequestContent Property Tests', () => {

  it('should deserialize requestId property correctly', () => {
    // Arrange: XML with requestId property set
    const xml = `<agent message-id="userInputRequestContent_requestId_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_55">
  <user-input-request request-id="test_id_123" prompt="test"/>
</agent>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content.requestId).toBeDefined();
    expect(content.requestId).toBe(testValue);
  });

  it('should deserialize prompt property correctly', () => {
    // Arrange: XML with prompt property set
    const xml = `<agent message-id="userInputRequestContent_prompt_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_56">
  <user-input-request request-id="test" prompt="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content.prompt).toBeDefined();
    expect(content.prompt).toBe(testValue);
  });

  it('should deserialize inputType property correctly', () => {
    // Arrange: XML with inputType property set
    const xml = `<agent message-id="userInputRequestContent_inputType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_57">
  <user-input-request request-id="test" prompt="test" input-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content.inputType).toBeDefined();
    expect(content.inputType).toBe(testValue);
  });

  it('should deserialize required property correctly', () => {
    // Arrange: XML with required property set
    const xml = `<agent message-id="userInputRequestContent_required_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_58">
  <user-input-request request-id="test" prompt="test" required="true"/>
</agent>
`;
    const testValue = 'true';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content.required).toBeDefined();
    expect(content.required).toBe(testValue === 'true');
  });

});

describe('SuggestedActionsContent Property Tests', () => {

});

describe('EventContent Property Tests', () => {

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<channel message-id="eventContent_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <event name="Test Name"/>
</channel>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as EventContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize value property correctly', () => {
    // Arrange: XML with value property set
    const xml = `<channel message-id="eventContent_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test">test_value</event>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as EventContent;
    expect(content.value).toBeDefined();
    expect(content.value).toBe(testValue);
  });

});

describe('TraceContent Property Tests', () => {

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<channel message-id="traceContent_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="Test Name"/>
</channel>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize label property correctly', () => {
    // Arrange: XML with label property set
    const xml = `<channel message-id="traceContent_label_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test" label="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content.label).toBeDefined();
    expect(content.label).toBe(testValue);
  });

  it('should deserialize severity property correctly', () => {
    // Arrange: XML with severity property set
    const xml = `<channel message-id="traceContent_severity_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test" severity="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content.severity).toBeDefined();
    expect(content.severity).toBe(testValue);
  });

  it('should deserialize value property correctly', () => {
    // Arrange: XML with value property set
    const xml = `<channel message-id="traceContent_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test">test_value</trace>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content.value).toBeDefined();
    expect(content.value).toBe(testValue);
  });

});

describe('ActionContent Property Tests', () => {

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<channel message-id="actionContent_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="Test Name"/>
</channel>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ActionContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize text property correctly', () => {
    // Arrange: XML with text property set
    const xml = `<channel message-id="actionContent_text_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test" text="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ActionContent;
    expect(content.text).toBeDefined();
    expect(content.text).toBe(testValue);
  });

  it('should deserialize value property correctly', () => {
    // Arrange: XML with value property set
    const xml = `<channel message-id="actionContent_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test">test_value</action>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ActionContent;
    expect(content.value).toBeDefined();
    expect(content.value).toBe(testValue);
  });

});

describe('TypingIndicatorContent Property Tests', () => {

  it('should deserialize from property correctly', () => {
    // Arrange: XML with from property set
    const xml = `<channel message-id="typingIndicatorContent_from_property_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test_value" status="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TypingIndicatorContent;
    expect(content.from).toBeDefined();
    expect(content.from).toBe(testValue);
  });

});

describe('MessageReactionContent Property Tests', () => {

  it('should deserialize referencedMessageId property correctly', () => {
    // Arrange: XML with referencedMessageId property set
    const xml = `<channel message-id="messageReactionContent_referencedMessageId_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test_id_123"/>
</channel>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageReactionContent;
    expect(content.referencedMessageId).toBeDefined();
    expect(content.referencedMessageId).toBe(testValue);
  });

});

describe('MessageDeleteContent Property Tests', () => {

  it('should deserialize messageId property correctly', () => {
    // Arrange: XML with messageId property set
    const xml = `<channel message-id="messageDeleteContent_messageId_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test_id_123"/>
</channel>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageDeleteContent;
    expect(content.messageId).toBeDefined();
    expect(content.messageId).toBe(testValue);
  });

  it('should deserialize reason property correctly', () => {
    // Arrange: XML with reason property set
    const xml = `<channel message-id="messageDeleteContent_reason_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test" reason="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageDeleteContent;
    expect(content.reason).toBeDefined();
    expect(content.reason).toBe(testValue);
  });

});

describe('MessageUpdateContent Property Tests', () => {

  it('should deserialize messageId property correctly', () => {
    // Arrange: XML with messageId property set
    const xml = `<channel message-id="messageUpdateContent_messageId_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test_id_123"/>
</channel>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageUpdateContent;
    expect(content.messageId).toBeDefined();
    expect(content.messageId).toBe(testValue);
  });

  it('should deserialize reason property correctly', () => {
    // Arrange: XML with reason property set
    const xml = `<channel message-id="messageUpdateContent_reason_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test" reason="test_value"/>
</channel>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageUpdateContent;
    expect(content.reason).toBeDefined();
    expect(content.reason).toBe(testValue);
  });

});

describe('HostedFileContent Property Tests', () => {

  it('should deserialize fileId property correctly', () => {
    // Arrange: XML with fileId property set
    const xml = `<agent message-id="hostedFileContent_fileId_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_74">
  <hosted-file file-id="test_id_123"/>
</agent>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content.fileId).toBeDefined();
    expect(content.fileId).toBe(testValue);
  });

  it('should deserialize filename property correctly', () => {
    // Arrange: XML with filename property set
    const xml = `<agent message-id="hostedFileContent_filename_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_75">
  <hosted-file file-id="test" filename="Test Name"/>
</agent>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content.filename).toBeDefined();
    expect(content.filename).toBe(testValue);
  });

  it('should deserialize mediaType property correctly', () => {
    // Arrange: XML with mediaType property set
    const xml = `<agent message-id="hostedFileContent_mediaType_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_76">
  <hosted-file file-id="test" media-type="test_value"/>
</agent>
`;
    const testValue = 'test_value';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content.mediaType).toBeDefined();
    expect(content.mediaType).toBe(testValue);
  });

  it('should deserialize sizeBytes property correctly', () => {
    // Arrange: XML with sizeBytes property set
    const xml = `<agent message-id="hostedFileContent_sizeBytes_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_77">
  <hosted-file file-id="test" size-bytes="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content.sizeBytes).toBeDefined();
    expect(content.sizeBytes).toBe(parseInt(testValue));
  });

});

describe('HostedVectorStoreContent Property Tests', () => {

  it('should deserialize vectorStoreId property correctly', () => {
    // Arrange: XML with vectorStoreId property set
    const xml = `<agent message-id="hostedVectorStoreContent_vectorStoreId_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_78">
  <hosted-vector-store vector-store-id="test_id_123"/>
</agent>
`;
    const testValue = 'test_id_123';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedVectorStoreContent;
    expect(content.vectorStoreId).toBeDefined();
    expect(content.vectorStoreId).toBe(testValue);
  });

  it('should deserialize name property correctly', () => {
    // Arrange: XML with name property set
    const xml = `<agent message-id="hostedVectorStoreContent_name_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_79">
  <hosted-vector-store vector-store-id="test" name="Test Name"/>
</agent>
`;
    const testValue = 'Test Name';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedVectorStoreContent;
    expect(content.name).toBeDefined();
    expect(content.name).toBe(testValue);
  });

  it('should deserialize documentCount property correctly', () => {
    // Arrange: XML with documentCount property set
    const xml = `<agent message-id="hostedVectorStoreContent_documentCount_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_80">
  <hosted-vector-store vector-store-id="test" document-count="42"/>
</agent>
`;
    const testValue = '42';

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify property value
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedVectorStoreContent;
    expect(content.documentCount).toBeDefined();
    expect(content.documentCount).toBe(parseInt(testValue));
  });

});

// Discriminator Tests

describe('TextContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with text discriminator
    const xml = `<agent message-id="textContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_81">
  <text>test</text>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextContent;
    expect(content.kind).toBe('text');
  });
});

describe('FunctionCallContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with functionCall discriminator
    const xml = `<agent message-id="functionCallContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_82">
  <function-call call-id="test" name="test">test</function-call>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionCallContent;
    expect(content.kind).toBe('functionCall');
  });
});

describe('FunctionResultContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with functionResult discriminator
    const xml = `<tool message-id="functionResultContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test</function-result>
</tool>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionResultContent;
    expect(content.kind).toBe('functionResult');
  });
});

describe('ErrorContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with error discriminator
    const xml = `<agent message-id="errorContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_84">
  <error>
    <message>test</message>
  </error>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ErrorContent;
    expect(content.kind).toBe('error');
  });
});

describe('TextReasoningContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with reasoning discriminator
    const xml = `<agent message-id="textReasoningContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_85">
  <thinking>test</thinking>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextReasoningContent;
    expect(content.kind).toBe('reasoning');
  });
});

describe('DataContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with data discriminator
    const xml = `<agent message-id="dataContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_86">
  <data/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DataContent;
    expect(content.kind).toBe('data');
  });
});

describe('UriContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with uri discriminator
    const xml = `<agent message-id="uriContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_87">
  <uri>test</uri>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UriContent;
    expect(content.kind).toBe('uri');
  });
});

describe('ImageContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with image discriminator
    const xml = `<agent message-id="imageContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_88">
  <image/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content.kind).toBe('image');
  });
});

describe('AudioContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with audio discriminator
    const xml = `<agent message-id="audioContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_89">
  <audio/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AudioContent;
    expect(content.kind).toBe('audio');
  });
});

describe('TranscriptContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with transcript discriminator
    const xml = `<agent message-id="transcriptContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_90">
  <transcript text="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content.kind).toBe('transcript');
  });
});

describe('VideoContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with video discriminator
    const xml = `<agent message-id="videoContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_91">
  <video/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content.kind).toBe('video');
  });
});

describe('FileContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with file discriminator
    const xml = `<agent message-id="fileContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_92">
  <file/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content.kind).toBe('file');
  });
});

describe('SearchResultContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with searchResult discriminator
    const xml = `<agent message-id="searchResultContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_93">
  <search-result title="test" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content.kind).toBe('searchResult');
  });
});

describe('DocumentContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with document discriminator
    const xml = `<agent message-id="documentContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_94">
  <document title="test" document-id="test" source="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content.kind).toBe('document');
  });
});

describe('AdaptiveCardContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with adaptiveCard discriminator
    const xml = `<agent message-id="adaptiveCardContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_95">
  <adaptive-card>test</adaptive-card>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AdaptiveCardContent;
    expect(content.kind).toBe('adaptiveCard');
  });
});

describe('RefusalContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with refusal discriminator
    const xml = `<agent message-id="refusalContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_96">
  <refusal reason="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as RefusalContent;
    expect(content.kind).toBe('refusal');
  });
});

describe('ContentFilterResultContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with contentFilterResult discriminator
    const xml = `<agent message-id="contentFilterResultContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_97">
  <content-filter-result filtered="true" category="test" severity="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ContentFilterResultContent;
    expect(content.kind).toBe('contentFilterResult');
  });
});

describe('UserInputRequestContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with userInputRequest discriminator
    const xml = `<agent message-id="userInputRequestContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_98">
  <user-input-request request-id="test" prompt="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content.kind).toBe('userInputRequest');
  });
});

describe('SuggestedActionsContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with suggestedActions discriminator
    const xml = `<agent message-id="suggestedActionsContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_99">
  <suggested-actions>
    <action>test_value</action>
  </suggested-actions>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SuggestedActionsContent;
    expect(content.kind).toBe('suggestedActions');
  });
});

describe('EventContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with event discriminator
    const xml = `<channel message-id="eventContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as EventContent;
    expect(content.kind).toBe('event');
  });
});

describe('TraceContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with trace discriminator
    const xml = `<channel message-id="traceContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content.kind).toBe('trace');
  });
});

describe('ActionContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with action discriminator
    const xml = `<channel message-id="actionContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ActionContent;
    expect(content.kind).toBe('action');
  });
});

describe('TypingIndicatorContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with typingIndicator discriminator
    const xml = `<channel message-id="typingIndicatorContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TypingIndicatorContent;
    expect(content.kind).toBe('typingIndicator');
  });
});

describe('MessageReactionContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with messageReaction discriminator
    const xml = `<channel message-id="messageReactionContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageReactionContent;
    expect(content.kind).toBe('messageReaction');
  });
});

describe('MessageDeleteContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with messageDelete discriminator
    const xml = `<channel message-id="messageDeleteContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageDeleteContent;
    expect(content.kind).toBe('messageDelete');
  });
});

describe('MessageUpdateContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with messageUpdate discriminator
    const xml = `<channel message-id="messageUpdateContent_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test"/>
</channel>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageUpdateContent;
    expect(content.kind).toBe('messageUpdate');
  });
});

describe('HostedFileContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with hostedFile discriminator
    const xml = `<agent message-id="hostedFileContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_107">
  <hosted-file file-id="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content.kind).toBe('hostedFile');
  });
});

describe('HostedVectorStoreContent Discriminator Test', () => {
  it('should deserialize with correct discriminator', () => {
    // Arrange: XML with hostedVectorStore discriminator
    const xml = `<agent message-id="hostedVectorStoreContent_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_108">
  <hosted-vector-store vector-store-id="test"/>
</agent>
`;

    // Act: Deserialize
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Verify correct type is instantiated
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedVectorStoreContent;
    expect(content.kind).toBe('hostedVectorStore');
  });
});

// Required vs Optional Tests

describe('FunctionResultContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: callId, name
    const xml = `<tool message-id="functionResultContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test</function-result>
</tool>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FunctionResultContent;
    expect(content).toBeDefined();
  });
});

describe('ErrorContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: code, stackTrace
    const xml = `<agent message-id="errorContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_110">
  <error>
    <message>test</message>
  </error>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ErrorContent;
    expect(content).toBeDefined();
  });
});

describe('TextReasoningContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: exposed
    const xml = `<agent message-id="textReasoningContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_111">
  <thinking>test</thinking>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TextReasoningContent;
    expect(content).toBeDefined();
  });
});

describe('DataContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: uri, mimeType, value
    const xml = `<agent message-id="dataContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_112">
  <data/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DataContent;
    expect(content).toBeDefined();
  });
});

describe('ImageContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: uri, alt, mimeType
    const xml = `<agent message-id="imageContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_113">
  <image/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ImageContent;
    expect(content).toBeDefined();
  });
});

describe('AudioContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: uri, mimeType, duration
    const xml = `<agent message-id="audioContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_114">
  <audio/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AudioContent;
    expect(content).toBeDefined();
  });
});

describe('TranscriptContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: language, confidence, speaker
    const xml = `<agent message-id="transcriptContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_115">
  <transcript text="test"/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TranscriptContent;
    expect(content).toBeDefined();
  });
});

describe('VideoContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: uri, mimeType, width
    const xml = `<agent message-id="videoContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_116">
  <video/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as VideoContent;
    expect(content).toBeDefined();
  });
});

describe('FileContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: uri, filename, mimeType
    const xml = `<agent message-id="fileContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_117">
  <file/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as FileContent;
    expect(content).toBeDefined();
  });
});

describe('SearchResultContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: score
    const xml = `<agent message-id="searchResultContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_118">
  <search-result title="test" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as SearchResultContent;
    expect(content).toBeDefined();
  });
});

describe('DocumentContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: mimeType, content
    const xml = `<agent message-id="documentContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_119">
  <document title="test" document-id="test" source="test"/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as DocumentContent;
    expect(content).toBeDefined();
  });
});

describe('AdaptiveCardContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: version, fallbackText
    const xml = `<agent message-id="adaptiveCardContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_120">
  <adaptive-card>test</adaptive-card>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as AdaptiveCardContent;
    expect(content).toBeDefined();
  });
});

describe('UserInputRequestContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: inputType, required
    const xml = `<agent message-id="userInputRequestContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_121">
  <user-input-request request-id="test" prompt="test"/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as UserInputRequestContent;
    expect(content).toBeDefined();
  });
});

describe('EventContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: timestamp, value
    const xml = `<channel message-id="eventContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as EventContent;
    expect(content).toBeDefined();
  });
});

describe('TraceContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: label, severity, timestamp
    const xml = `<channel message-id="traceContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TraceContent;
    expect(content).toBeDefined();
  });
});

describe('ActionContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: text, timestamp, value
    const xml = `<channel message-id="actionContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as ActionContent;
    expect(content).toBeDefined();
  });
});

describe('TypingIndicatorContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: timestamp
    const xml = `<channel message-id="typingIndicatorContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as TypingIndicatorContent;
    expect(content).toBeDefined();
  });
});

describe('MessageReactionContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: reactionsAdded, reactionsRemoved
    const xml = `<channel message-id="messageReactionContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageReactionContent;
    expect(content).toBeDefined();
  });
});

describe('MessageDeleteContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: reason
    const xml = `<channel message-id="messageDeleteContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageDeleteContent;
    expect(content).toBeDefined();
  });
});

describe('MessageUpdateContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: reason
    const xml = `<channel message-id="messageUpdateContent_optional_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test"/>
</channel>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as MessageUpdateContent;
    expect(content).toBeDefined();
  });
});

describe('HostedFileContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: filename, mediaType, sizeBytes
    const xml = `<agent message-id="hostedFileContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_129">
  <hosted-file file-id="test"/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedFileContent;
    expect(content).toBeDefined();
  });
});

describe('HostedVectorStoreContent Optional Fields Test', () => {
  it('should allow optional fields to be omitted', () => {
    // Arrange: XML omitting optional fields: name, documentCount
    const xml = `<agent message-id="hostedVectorStoreContent_optional_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_130">
  <hosted-vector-store vector-store-id="test"/>
</agent>
`;

    // Act: Deserialize (should succeed)
    const serializer = new MessageSerializer();
    const message = serializer.deserialize(xml);

    // Assert: Message deserializes successfully
    expect(message).toBeDefined();
    expect(message.contents).toBeDefined();
    expect(message.contents.length).toBeGreaterThan(0);
    const content = message.contents[0] as HostedVectorStoreContent;
    expect(content).toBeDefined();
  });
});
