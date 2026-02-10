using System;
using System.Xml;
using System.Xml.Serialization;
using System.Linq;
using Microsoft.Agents.Protocol.Xml;
using Microsoft.Agents;
using Xunit;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Xml.Tests;

/// <summary>
/// Auto-generated property validation tests.
/// Tests that every property serializes and deserializes correctly.
/// </summary>
public class GeneratedPropertyValidationTests
{
    #region TextContent Property Tests

    [Fact]
    public void Test_TextContent_Text_Property()
    {
        // Arrange: XML with text property set
        var xml = @"<agent message-id=""Test_TextContent_Text_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_1"">
  <text>test_value</text>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Text);
        XunitAssert.Equal(testValue, content.Text);
    }

    #endregion

    #region FunctionCallContent Property Tests

    [Fact]
    public void Test_FunctionCallContent_CallId_Property()
    {
        // Arrange: XML with callId property set
        var xml = @"<agent message-id=""Test_FunctionCallContent_CallId_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_2"">
  <function-call call-id=""test_id_123"" name=""test"">test</function-call>
</agent>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionCallContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.CallId);
        XunitAssert.Equal(testValue, content.CallId);
    }

    [Fact]
    public void Test_FunctionCallContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<agent message-id=""Test_FunctionCallContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_3"">
  <function-call call-id=""test"" name=""Test Name"">test</function-call>
</agent>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionCallContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_FunctionCallContent_Arguments_Property()
    {
        // Arrange: XML with arguments property set
        var xml = @"<agent message-id=""Test_FunctionCallContent_Arguments_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_4"">
  <function-call call-id=""test"" name=""test"">test_value</function-call>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionCallContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Arguments);
        XunitAssert.Equal(testValue, content.Arguments);
    }

    #endregion

    #region FunctionResultContent Property Tests

    [Fact]
    public void Test_FunctionResultContent_CallId_Property()
    {
        // Arrange: XML with callId property set
        var xml = @"<tool message-id=""Test_FunctionResultContent_CallId_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <function-result call-id=""test_id_123"">test</function-result>
</tool>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.CallId);
        XunitAssert.Equal(testValue, content.CallId);
    }

    [Fact]
    public void Test_FunctionResultContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<tool message-id=""Test_FunctionResultContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <function-result name=""Test Name"">test</function-result>
</tool>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_FunctionResultContent_Result_Property()
    {
        // Arrange: XML with result property set
        var xml = @"<tool message-id=""Test_FunctionResultContent_Result_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <function-result>test_value</function-result>
</tool>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Result);
        XunitAssert.Equal(testValue, content.Result);
    }

    #endregion

    #region ErrorContent Property Tests

    [Fact]
    public void Test_ErrorContent_Code_Property()
    {
        // Arrange: XML with code property set
        var xml = @"<agent message-id=""Test_ErrorContent_Code_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_8"">
  <error code=""test_value"">
    <message>test</message>
  </error>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ErrorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Code);
        XunitAssert.Equal(testValue, content.Code);
    }

    [Fact]
    public void Test_ErrorContent_Message_Property()
    {
        // Arrange: XML with message property set
        var xml = @"<agent message-id=""Test_ErrorContent_Message_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_9"">
  <error>
    <message>test_value</message>
  </error>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ErrorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Message);
        XunitAssert.Equal(testValue, content.Message);
    }

    [Fact]
    public void Test_ErrorContent_StackTrace_Property()
    {
        // Arrange: XML with stackTrace property set
        var xml = @"<agent message-id=""Test_ErrorContent_StackTrace_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_10"">
  <error>
    <message>test</message>
    <stack-trace>test_value</stack-trace>
  </error>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ErrorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.StackTrace);
        XunitAssert.Equal(testValue, content.StackTrace);
    }

    #endregion

    #region TextReasoningContent Property Tests

    [Fact]
    public void Test_TextReasoningContent_Text_Property()
    {
        // Arrange: XML with text property set
        var xml = @"<agent message-id=""Test_TextReasoningContent_Text_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_11"">
  <thinking>test_value</thinking>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextReasoningContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Text);
        XunitAssert.Equal(testValue, content.Text);
    }

    [Fact]
    public void Test_TextReasoningContent_Exposed_Property()
    {
        // Arrange: XML with exposed property set
        var xml = @"<agent message-id=""Test_TextReasoningContent_Exposed_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_12"">
  <thinking exposed=""true"">test</thinking>
</agent>
";
        var testValue = "true";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextReasoningContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(bool.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Exposed);
    }

    #endregion

    #region DataContent Property Tests

    [Fact]
    public void Test_DataContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_DataContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_13"">
  <data uri=""https://example.com""/>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DataContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    [Fact]
    public void Test_DataContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_DataContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_14"">
  <data mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DataContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_DataContent_Value_Property()
    {
        // Arrange: XML with value property set
        var xml = @"<agent message-id=""Test_DataContent_Value_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_15"">
  <data>test_value</data>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DataContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Value);
        XunitAssert.Equal(testValue, content.Value);
    }

    #endregion

    #region UriContent Property Tests

    [Fact]
    public void Test_UriContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_UriContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_16"">
  <uri>https://example.com</uri>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UriContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    #endregion

    #region ImageContent Property Tests

    [Fact]
    public void Test_ImageContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_ImageContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_17"">
  <image uri=""https://example.com""/>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    [Fact]
    public void Test_ImageContent_Alt_Property()
    {
        // Arrange: XML with alt property set
        var xml = @"<agent message-id=""Test_ImageContent_Alt_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_18"">
  <image alt=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Alt);
        XunitAssert.Equal(testValue, content.Alt);
    }

    [Fact]
    public void Test_ImageContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_ImageContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_19"">
  <image mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_ImageContent_Width_Property()
    {
        // Arrange: XML with width property set
        var xml = @"<agent message-id=""Test_ImageContent_Width_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_20"">
  <image width=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Width);
    }

    [Fact]
    public void Test_ImageContent_Height_Property()
    {
        // Arrange: XML with height property set
        var xml = @"<agent message-id=""Test_ImageContent_Height_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_21"">
  <image height=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Height);
    }

    #endregion

    #region AudioContent Property Tests

    [Fact]
    public void Test_AudioContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_AudioContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_22"">
  <audio uri=""https://example.com""/>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AudioContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    [Fact]
    public void Test_AudioContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_AudioContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_23"">
  <audio mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AudioContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_AudioContent_Duration_Property()
    {
        // Arrange: XML with duration property set
        var xml = @"<agent message-id=""Test_AudioContent_Duration_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_24"">
  <audio duration=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AudioContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Duration);
    }

    #endregion

    #region TranscriptContent Property Tests

    [Fact]
    public void Test_TranscriptContent_Text_Property()
    {
        // Arrange: XML with text property set
        var xml = @"<agent message-id=""Test_TranscriptContent_Text_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_25"">
  <transcript text=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Text);
        XunitAssert.Equal(testValue, content.Text);
    }

    [Fact]
    public void Test_TranscriptContent_Language_Property()
    {
        // Arrange: XML with language property set
        var xml = @"<agent message-id=""Test_TranscriptContent_Language_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_26"">
  <transcript text=""test"" language=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Language);
        XunitAssert.Equal(testValue, content.Language);
    }

    [Fact]
    public void Test_TranscriptContent_Confidence_Property()
    {
        // Arrange: XML with confidence property set
        var xml = @"<agent message-id=""Test_TranscriptContent_Confidence_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_27"">
  <transcript text=""test"" confidence=""3.14""/>
</agent>
";
        var testValue = "3.14";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(double.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Confidence, 2);
    }

    [Fact]
    public void Test_TranscriptContent_Speaker_Property()
    {
        // Arrange: XML with speaker property set
        var xml = @"<agent message-id=""Test_TranscriptContent_Speaker_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_28"">
  <transcript text=""test"" speaker=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Speaker);
        XunitAssert.Equal(testValue, content.Speaker);
    }

    #endregion

    #region VideoContent Property Tests

    [Fact]
    public void Test_VideoContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_VideoContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_29"">
  <video uri=""https://example.com""/>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    [Fact]
    public void Test_VideoContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_VideoContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_30"">
  <video mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_VideoContent_Width_Property()
    {
        // Arrange: XML with width property set
        var xml = @"<agent message-id=""Test_VideoContent_Width_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_31"">
  <video width=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Width);
    }

    [Fact]
    public void Test_VideoContent_Height_Property()
    {
        // Arrange: XML with height property set
        var xml = @"<agent message-id=""Test_VideoContent_Height_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_32"">
  <video height=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Height);
    }

    [Fact]
    public void Test_VideoContent_Duration_Property()
    {
        // Arrange: XML with duration property set
        var xml = @"<agent message-id=""Test_VideoContent_Duration_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_33"">
  <video duration=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Duration);
    }

    [Fact]
    public void Test_VideoContent_FrameRate_Property()
    {
        // Arrange: XML with frameRate property set
        var xml = @"<agent message-id=""Test_VideoContent_FrameRate_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_34"">
  <video frame-rate=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.FrameRate);
    }

    #endregion

    #region FileContent Property Tests

    [Fact]
    public void Test_FileContent_Uri_Property()
    {
        // Arrange: XML with uri property set
        var xml = @"<agent message-id=""Test_FileContent_Uri_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_35"">
  <file uri=""https://example.com""/>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Uri);
        XunitAssert.Equal(testValue, content.Uri);
    }

    [Fact]
    public void Test_FileContent_Filename_Property()
    {
        // Arrange: XML with filename property set
        var xml = @"<agent message-id=""Test_FileContent_Filename_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_36"">
  <file filename=""Test Name""/>
</agent>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Filename);
        XunitAssert.Equal(testValue, content.Filename);
    }

    [Fact]
    public void Test_FileContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_FileContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_37"">
  <file mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_FileContent_SizeBytes_Property()
    {
        // Arrange: XML with sizeBytes property set
        var xml = @"<agent message-id=""Test_FileContent_SizeBytes_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_38"">
  <file size-bytes=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.SizeBytes);
    }

    #endregion

    #region SearchResultContent Property Tests

    [Fact]
    public void Test_SearchResultContent_Title_Property()
    {
        // Arrange: XML with title property set
        var xml = @"<agent message-id=""Test_SearchResultContent_Title_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_39"">
  <search-result title=""test_value"" url=""test"">
    <snippet>test</snippet>
  </search-result>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Title);
        XunitAssert.Equal(testValue, content.Title);
    }

    [Fact]
    public void Test_SearchResultContent_Url_Property()
    {
        // Arrange: XML with url property set
        var xml = @"<agent message-id=""Test_SearchResultContent_Url_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_40"">
  <search-result title=""test"" url=""https://example.com"">
    <snippet>test</snippet>
  </search-result>
</agent>
";
        var testValue = "https://example.com";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Url);
        XunitAssert.Equal(testValue, content.Url);
    }

    [Fact]
    public void Test_SearchResultContent_Score_Property()
    {
        // Arrange: XML with score property set
        var xml = @"<agent message-id=""Test_SearchResultContent_Score_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_41"">
  <search-result title=""test"" url=""test"" score=""3.14"">
    <snippet>test</snippet>
  </search-result>
</agent>
";
        var testValue = "3.14";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(double.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Score, 2);
    }

    [Fact]
    public void Test_SearchResultContent_Snippet_Property()
    {
        // Arrange: XML with snippet property set
        var xml = @"<agent message-id=""Test_SearchResultContent_Snippet_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_42"">
  <search-result title=""test"" url=""test"">
    <snippet>test_value</snippet>
  </search-result>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Snippet);
        XunitAssert.Equal(testValue, content.Snippet);
    }

    #endregion

    #region DocumentContent Property Tests

    [Fact]
    public void Test_DocumentContent_Title_Property()
    {
        // Arrange: XML with title property set
        var xml = @"<agent message-id=""Test_DocumentContent_Title_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_43"">
  <document title=""test_value"" document-id=""test"" source=""test""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Title);
        XunitAssert.Equal(testValue, content.Title);
    }

    [Fact]
    public void Test_DocumentContent_DocumentId_Property()
    {
        // Arrange: XML with documentId property set
        var xml = @"<agent message-id=""Test_DocumentContent_DocumentId_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_44"">
  <document title=""test"" document-id=""test_id_123"" source=""test""/>
</agent>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.DocumentId);
        XunitAssert.Equal(testValue, content.DocumentId);
    }

    [Fact]
    public void Test_DocumentContent_Source_Property()
    {
        // Arrange: XML with source property set
        var xml = @"<agent message-id=""Test_DocumentContent_Source_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_45"">
  <document title=""test"" document-id=""test"" source=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Source);
        XunitAssert.Equal(testValue, content.Source);
    }

    [Fact]
    public void Test_DocumentContent_MimeType_Property()
    {
        // Arrange: XML with mimeType property set
        var xml = @"<agent message-id=""Test_DocumentContent_MimeType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_46"">
  <document title=""test"" document-id=""test"" source=""test"" mime-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MimeType);
        XunitAssert.Equal(testValue, content.MimeType);
    }

    [Fact]
    public void Test_DocumentContent_Content_Property()
    {
        // Arrange: XML with content property set
        var xml = @"<agent message-id=""Test_DocumentContent_Content_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_47"">
  <document title=""test"" document-id=""test"" source=""test"">
    <content>test_value</content>
  </document>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Content);
        XunitAssert.Equal(testValue, content.Content);
    }

    #endregion

    #region AdaptiveCardContent Property Tests

    [Fact]
    public void Test_AdaptiveCardContent_Version_Property()
    {
        // Arrange: XML with version property set
        var xml = @"<agent message-id=""Test_AdaptiveCardContent_Version_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_48"">
  <adaptive-card version=""test_value"">test</adaptive-card>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AdaptiveCardContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Version);
        XunitAssert.Equal(testValue, content.Version);
    }

    [Fact]
    public void Test_AdaptiveCardContent_FallbackText_Property()
    {
        // Arrange: XML with fallbackText property set
        var xml = @"<agent message-id=""Test_AdaptiveCardContent_FallbackText_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_49"">
  <adaptive-card fallback-text=""test_value"">test</adaptive-card>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AdaptiveCardContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.FallbackText);
        XunitAssert.Equal(testValue, content.FallbackText);
    }

    [Fact]
    public void Test_AdaptiveCardContent_Card_Property()
    {
        // Arrange: XML with card property set
        var xml = @"<agent message-id=""Test_AdaptiveCardContent_Card_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_50"">
  <adaptive-card>test_value</adaptive-card>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AdaptiveCardContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Card);
        XunitAssert.Equal(testValue, content.Card);
    }

    #endregion

    #region RefusalContent Property Tests

    [Fact]
    public void Test_RefusalContent_Reason_Property()
    {
        // Arrange: XML with reason property set
        var xml = @"<agent message-id=""Test_RefusalContent_Reason_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_51"">
  <refusal reason=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<RefusalContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Reason);
        XunitAssert.Equal(testValue, content.Reason);
    }

    #endregion

    #region ContentFilterResultContent Property Tests

    [Fact]
    public void Test_ContentFilterResultContent_Filtered_Property()
    {
        // Arrange: XML with filtered property set
        var xml = @"<agent message-id=""Test_ContentFilterResultContent_Filtered_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_52"">
  <content-filter-result filtered=""true"" category=""test"" severity=""test""/>
</agent>
";
        var testValue = "true";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ContentFilterResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(bool.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Filtered);
    }

    [Fact]
    public void Test_ContentFilterResultContent_Category_Property()
    {
        // Arrange: XML with category property set
        var xml = @"<agent message-id=""Test_ContentFilterResultContent_Category_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_53"">
  <content-filter-result filtered=""true"" category=""test_value"" severity=""test""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ContentFilterResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Category);
        XunitAssert.Equal(testValue, content.Category);
    }

    [Fact]
    public void Test_ContentFilterResultContent_Severity_Property()
    {
        // Arrange: XML with severity property set
        var xml = @"<agent message-id=""Test_ContentFilterResultContent_Severity_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_54"">
  <content-filter-result filtered=""true"" category=""test"" severity=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ContentFilterResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Severity);
        XunitAssert.Equal(testValue, content.Severity);
    }

    #endregion

    #region UserInputRequestContent Property Tests

    [Fact]
    public void Test_UserInputRequestContent_RequestId_Property()
    {
        // Arrange: XML with requestId property set
        var xml = @"<agent message-id=""Test_UserInputRequestContent_RequestId_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_55"">
  <user-input-request request-id=""test_id_123"" prompt=""test""/>
</agent>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.RequestId);
        XunitAssert.Equal(testValue, content.RequestId);
    }

    [Fact]
    public void Test_UserInputRequestContent_Prompt_Property()
    {
        // Arrange: XML with prompt property set
        var xml = @"<agent message-id=""Test_UserInputRequestContent_Prompt_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_56"">
  <user-input-request request-id=""test"" prompt=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Prompt);
        XunitAssert.Equal(testValue, content.Prompt);
    }

    [Fact]
    public void Test_UserInputRequestContent_InputType_Property()
    {
        // Arrange: XML with inputType property set
        var xml = @"<agent message-id=""Test_UserInputRequestContent_InputType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_57"">
  <user-input-request request-id=""test"" prompt=""test"" input-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.InputType);
        XunitAssert.Equal(testValue, content.InputType);
    }

    [Fact]
    public void Test_UserInputRequestContent_Required_Property()
    {
        // Arrange: XML with required property set
        var xml = @"<agent message-id=""Test_UserInputRequestContent_Required_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_58"">
  <user-input-request request-id=""test"" prompt=""test"" required=""true""/>
</agent>
";
        var testValue = "true";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(bool.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.Required);
    }

    #endregion

    #region SuggestedActionsContent Property Tests

    #endregion

    #region EventContent Property Tests

    [Fact]
    public void Test_EventContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<channel message-id=""Test_EventContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <event name=""Test Name""/>
</channel>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<EventContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_EventContent_Value_Property()
    {
        // Arrange: XML with value property set
        var xml = @"<channel message-id=""Test_EventContent_Value_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <event name=""test"">test_value</event>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<EventContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Value);
        XunitAssert.Equal(testValue, content.Value);
    }

    #endregion

    #region TraceContent Property Tests

    [Fact]
    public void Test_TraceContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<channel message-id=""Test_TraceContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""Test Name""/>
</channel>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_TraceContent_Label_Property()
    {
        // Arrange: XML with label property set
        var xml = @"<channel message-id=""Test_TraceContent_Label_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""test"" label=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Label);
        XunitAssert.Equal(testValue, content.Label);
    }

    [Fact]
    public void Test_TraceContent_Severity_Property()
    {
        // Arrange: XML with severity property set
        var xml = @"<channel message-id=""Test_TraceContent_Severity_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""test"" severity=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Severity);
        XunitAssert.Equal(testValue, content.Severity);
    }

    [Fact]
    public void Test_TraceContent_Value_Property()
    {
        // Arrange: XML with value property set
        var xml = @"<channel message-id=""Test_TraceContent_Value_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""test"">test_value</trace>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Value);
        XunitAssert.Equal(testValue, content.Value);
    }

    #endregion

    #region ActionContent Property Tests

    [Fact]
    public void Test_ActionContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<channel message-id=""Test_ActionContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <action name=""Test Name""/>
</channel>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ActionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_ActionContent_Text_Property()
    {
        // Arrange: XML with text property set
        var xml = @"<channel message-id=""Test_ActionContent_Text_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <action name=""test"" text=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ActionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Text);
        XunitAssert.Equal(testValue, content.Text);
    }

    [Fact]
    public void Test_ActionContent_Value_Property()
    {
        // Arrange: XML with value property set
        var xml = @"<channel message-id=""Test_ActionContent_Value_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <action name=""test"">test_value</action>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ActionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Value);
        XunitAssert.Equal(testValue, content.Value);
    }

    #endregion

    #region TypingIndicatorContent Property Tests

    [Fact]
    public void Test_TypingIndicatorContent_From_Property()
    {
        // Arrange: XML with from property set
        var xml = @"<channel message-id=""Test_TypingIndicatorContent_From_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <typing-indicator from=""test_value"" status=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TypingIndicatorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.From);
        XunitAssert.Equal(testValue, content.From);
    }

    #endregion

    #region MessageReactionContent Property Tests

    [Fact]
    public void Test_MessageReactionContent_ReferencedMessageId_Property()
    {
        // Arrange: XML with referencedMessageId property set
        var xml = @"<channel message-id=""Test_MessageReactionContent_ReferencedMessageId_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-reaction referenced-message-id=""test_id_123""/>
</channel>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageReactionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.ReferencedMessageId);
        XunitAssert.Equal(testValue, content.ReferencedMessageId);
    }

    #endregion

    #region MessageDeleteContent Property Tests

    [Fact]
    public void Test_MessageDeleteContent_MessageId_Property()
    {
        // Arrange: XML with messageId property set
        var xml = @"<channel message-id=""Test_MessageDeleteContent_MessageId_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-delete message-id=""test_id_123""/>
</channel>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageDeleteContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MessageId);
        XunitAssert.Equal(testValue, content.MessageId);
    }

    [Fact]
    public void Test_MessageDeleteContent_Reason_Property()
    {
        // Arrange: XML with reason property set
        var xml = @"<channel message-id=""Test_MessageDeleteContent_Reason_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-delete message-id=""test"" reason=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageDeleteContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Reason);
        XunitAssert.Equal(testValue, content.Reason);
    }

    #endregion

    #region MessageUpdateContent Property Tests

    [Fact]
    public void Test_MessageUpdateContent_MessageId_Property()
    {
        // Arrange: XML with messageId property set
        var xml = @"<channel message-id=""Test_MessageUpdateContent_MessageId_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-update message-id=""test_id_123""/>
</channel>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageUpdateContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MessageId);
        XunitAssert.Equal(testValue, content.MessageId);
    }

    [Fact]
    public void Test_MessageUpdateContent_Reason_Property()
    {
        // Arrange: XML with reason property set
        var xml = @"<channel message-id=""Test_MessageUpdateContent_Reason_Property_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-update message-id=""test"" reason=""test_value""/>
</channel>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageUpdateContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Reason);
        XunitAssert.Equal(testValue, content.Reason);
    }

    #endregion

    #region HostedFileContent Property Tests

    [Fact]
    public void Test_HostedFileContent_FileId_Property()
    {
        // Arrange: XML with fileId property set
        var xml = @"<agent message-id=""Test_HostedFileContent_FileId_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_74"">
  <hosted-file file-id=""test_id_123""/>
</agent>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.FileId);
        XunitAssert.Equal(testValue, content.FileId);
    }

    [Fact]
    public void Test_HostedFileContent_Filename_Property()
    {
        // Arrange: XML with filename property set
        var xml = @"<agent message-id=""Test_HostedFileContent_Filename_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_75"">
  <hosted-file file-id=""test"" filename=""Test Name""/>
</agent>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Filename);
        XunitAssert.Equal(testValue, content.Filename);
    }

    [Fact]
    public void Test_HostedFileContent_MediaType_Property()
    {
        // Arrange: XML with mediaType property set
        var xml = @"<agent message-id=""Test_HostedFileContent_MediaType_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_76"">
  <hosted-file file-id=""test"" media-type=""test_value""/>
</agent>
";
        var testValue = "test_value";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.MediaType);
        XunitAssert.Equal(testValue, content.MediaType);
    }

    [Fact]
    public void Test_HostedFileContent_SizeBytes_Property()
    {
        // Arrange: XML with sizeBytes property set
        var xml = @"<agent message-id=""Test_HostedFileContent_SizeBytes_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_77"">
  <hosted-file file-id=""test"" size-bytes=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.SizeBytes);
    }

    #endregion

    #region HostedVectorStoreContent Property Tests

    [Fact]
    public void Test_HostedVectorStoreContent_VectorStoreId_Property()
    {
        // Arrange: XML with vectorStoreId property set
        var xml = @"<agent message-id=""Test_HostedVectorStoreContent_VectorStoreId_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_78"">
  <hosted-vector-store vector-store-id=""test_id_123""/>
</agent>
";
        var testValue = "test_id_123";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedVectorStoreContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.VectorStoreId);
        XunitAssert.Equal(testValue, content.VectorStoreId);
    }

    [Fact]
    public void Test_HostedVectorStoreContent_Name_Property()
    {
        // Arrange: XML with name property set
        var xml = @"<agent message-id=""Test_HostedVectorStoreContent_Name_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_79"">
  <hosted-vector-store vector-store-id=""test"" name=""Test Name""/>
</agent>
";
        var testValue = "Test Name";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedVectorStoreContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content.Name);
        XunitAssert.Equal(testValue, content.Name);
    }

    [Fact]
    public void Test_HostedVectorStoreContent_DocumentCount_Property()
    {
        // Arrange: XML with documentCount property set
        var xml = @"<agent message-id=""Test_HostedVectorStoreContent_DocumentCount_Property_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_80"">
  <hosted-vector-store vector-store-id=""test"" document-count=""42""/>
</agent>
";
        var testValue = "42";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify property value
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedVectorStoreContent>(message.Contents.FirstOrDefault());
        XunitAssert.True(int.TryParse(testValue, out var expectedValue));
        XunitAssert.Equal(expectedValue, content.DocumentCount);
    }

    #endregion

    #region Discriminator Tests

    [Fact]
    public void Test_TextContent_Discriminator()
    {
        // Arrange: XML with text discriminator
        var xml = @"<agent message-id=""Test_TextContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_81"">
  <text>test</text>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("text", content.Kind);
    }

    [Fact]
    public void Test_FunctionCallContent_Discriminator()
    {
        // Arrange: XML with functionCall discriminator
        var xml = @"<agent message-id=""Test_FunctionCallContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_82"">
  <function-call call-id=""test"" name=""test"">test</function-call>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionCallContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("functionCall", content.Kind);
    }

    [Fact]
    public void Test_FunctionResultContent_Discriminator()
    {
        // Arrange: XML with functionResult discriminator
        var xml = @"<tool message-id=""Test_FunctionResultContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <function-result>test</function-result>
</tool>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("functionResult", content.Kind);
    }

    [Fact]
    public void Test_ErrorContent_Discriminator()
    {
        // Arrange: XML with error discriminator
        var xml = @"<agent message-id=""Test_ErrorContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_84"">
  <error>
    <message>test</message>
  </error>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ErrorContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("error", content.Kind);
    }

    [Fact]
    public void Test_TextReasoningContent_Discriminator()
    {
        // Arrange: XML with reasoning discriminator
        var xml = @"<agent message-id=""Test_TextReasoningContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_85"">
  <thinking>test</thinking>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextReasoningContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("reasoning", content.Kind);
    }

    [Fact]
    public void Test_DataContent_Discriminator()
    {
        // Arrange: XML with data discriminator
        var xml = @"<agent message-id=""Test_DataContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_86"">
  <data/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DataContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("data", content.Kind);
    }

    [Fact]
    public void Test_UriContent_Discriminator()
    {
        // Arrange: XML with uri discriminator
        var xml = @"<agent message-id=""Test_UriContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_87"">
  <uri>test</uri>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UriContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("uri", content.Kind);
    }

    [Fact]
    public void Test_ImageContent_Discriminator()
    {
        // Arrange: XML with image discriminator
        var xml = @"<agent message-id=""Test_ImageContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_88"">
  <image/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("image", content.Kind);
    }

    [Fact]
    public void Test_AudioContent_Discriminator()
    {
        // Arrange: XML with audio discriminator
        var xml = @"<agent message-id=""Test_AudioContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_89"">
  <audio/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AudioContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("audio", content.Kind);
    }

    [Fact]
    public void Test_TranscriptContent_Discriminator()
    {
        // Arrange: XML with transcript discriminator
        var xml = @"<agent message-id=""Test_TranscriptContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_90"">
  <transcript text=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("transcript", content.Kind);
    }

    [Fact]
    public void Test_VideoContent_Discriminator()
    {
        // Arrange: XML with video discriminator
        var xml = @"<agent message-id=""Test_VideoContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_91"">
  <video/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("video", content.Kind);
    }

    [Fact]
    public void Test_FileContent_Discriminator()
    {
        // Arrange: XML with file discriminator
        var xml = @"<agent message-id=""Test_FileContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_92"">
  <file/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("file", content.Kind);
    }

    [Fact]
    public void Test_SearchResultContent_Discriminator()
    {
        // Arrange: XML with searchResult discriminator
        var xml = @"<agent message-id=""Test_SearchResultContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_93"">
  <search-result title=""test"" url=""test"">
    <snippet>test</snippet>
  </search-result>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("searchResult", content.Kind);
    }

    [Fact]
    public void Test_DocumentContent_Discriminator()
    {
        // Arrange: XML with document discriminator
        var xml = @"<agent message-id=""Test_DocumentContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_94"">
  <document title=""test"" document-id=""test"" source=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("document", content.Kind);
    }

    [Fact]
    public void Test_AdaptiveCardContent_Discriminator()
    {
        // Arrange: XML with adaptiveCard discriminator
        var xml = @"<agent message-id=""Test_AdaptiveCardContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_95"">
  <adaptive-card>test</adaptive-card>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AdaptiveCardContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("adaptiveCard", content.Kind);
    }

    [Fact]
    public void Test_RefusalContent_Discriminator()
    {
        // Arrange: XML with refusal discriminator
        var xml = @"<agent message-id=""Test_RefusalContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_96"">
  <refusal reason=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<RefusalContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("refusal", content.Kind);
    }

    [Fact]
    public void Test_ContentFilterResultContent_Discriminator()
    {
        // Arrange: XML with contentFilterResult discriminator
        var xml = @"<agent message-id=""Test_ContentFilterResultContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_97"">
  <content-filter-result filtered=""true"" category=""test"" severity=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ContentFilterResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("contentFilterResult", content.Kind);
    }

    [Fact]
    public void Test_UserInputRequestContent_Discriminator()
    {
        // Arrange: XML with userInputRequest discriminator
        var xml = @"<agent message-id=""Test_UserInputRequestContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_98"">
  <user-input-request request-id=""test"" prompt=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("userInputRequest", content.Kind);
    }

    [Fact]
    public void Test_SuggestedActionsContent_Discriminator()
    {
        // Arrange: XML with suggestedActions discriminator
        var xml = @"<agent message-id=""Test_SuggestedActionsContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_99"">
  <suggested-actions>
    <action>test_value</action>
  </suggested-actions>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SuggestedActionsContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("suggestedActions", content.Kind);
    }

    [Fact]
    public void Test_EventContent_Discriminator()
    {
        // Arrange: XML with event discriminator
        var xml = @"<channel message-id=""Test_EventContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <event name=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<EventContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("event", content.Kind);
    }

    [Fact]
    public void Test_TraceContent_Discriminator()
    {
        // Arrange: XML with trace discriminator
        var xml = @"<channel message-id=""Test_TraceContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("trace", content.Kind);
    }

    [Fact]
    public void Test_ActionContent_Discriminator()
    {
        // Arrange: XML with action discriminator
        var xml = @"<channel message-id=""Test_ActionContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <action name=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ActionContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("action", content.Kind);
    }

    [Fact]
    public void Test_TypingIndicatorContent_Discriminator()
    {
        // Arrange: XML with typingIndicator discriminator
        var xml = @"<channel message-id=""Test_TypingIndicatorContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <typing-indicator from=""test"" status=""test_value""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TypingIndicatorContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("typingIndicator", content.Kind);
    }

    [Fact]
    public void Test_MessageReactionContent_Discriminator()
    {
        // Arrange: XML with messageReaction discriminator
        var xml = @"<channel message-id=""Test_MessageReactionContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-reaction referenced-message-id=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageReactionContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("messageReaction", content.Kind);
    }

    [Fact]
    public void Test_MessageDeleteContent_Discriminator()
    {
        // Arrange: XML with messageDelete discriminator
        var xml = @"<channel message-id=""Test_MessageDeleteContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-delete message-id=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageDeleteContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("messageDelete", content.Kind);
    }

    [Fact]
    public void Test_MessageUpdateContent_Discriminator()
    {
        // Arrange: XML with messageUpdate discriminator
        var xml = @"<channel message-id=""Test_MessageUpdateContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-update message-id=""test""/>
</channel>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageUpdateContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("messageUpdate", content.Kind);
    }

    [Fact]
    public void Test_HostedFileContent_Discriminator()
    {
        // Arrange: XML with hostedFile discriminator
        var xml = @"<agent message-id=""Test_HostedFileContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_107"">
  <hosted-file file-id=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("hostedFile", content.Kind);
    }

    [Fact]
    public void Test_HostedVectorStoreContent_Discriminator()
    {
        // Arrange: XML with hostedVectorStore discriminator
        var xml = @"<agent message-id=""Test_HostedVectorStoreContent_Discriminator_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_108"">
  <hosted-vector-store vector-store-id=""test""/>
</agent>
";

        // Act: Deserialize
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Verify correct type is instantiated
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedVectorStoreContent>(message.Contents.FirstOrDefault());
        XunitAssert.Equal("hostedVectorStore", content.Kind);
    }

    #endregion

    #region Required vs Optional Tests

    [Fact]
    public void Test_FunctionResultContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: callId, name
        var xml = @"<tool message-id=""Test_FunctionResultContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <function-result>test</function-result>
</tool>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FunctionResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_ErrorContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: code, stackTrace
        var xml = @"<agent message-id=""Test_ErrorContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_110"">
  <error>
    <message>test</message>
  </error>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ErrorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_TextReasoningContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: exposed
        var xml = @"<agent message-id=""Test_TextReasoningContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_111"">
  <thinking>test</thinking>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TextReasoningContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_DataContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: uri, mimeType, value
        var xml = @"<agent message-id=""Test_DataContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_112"">
  <data/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DataContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_ImageContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: uri, alt, mimeType
        var xml = @"<agent message-id=""Test_ImageContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_113"">
  <image/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ImageContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_AudioContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: uri, mimeType, duration
        var xml = @"<agent message-id=""Test_AudioContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_114"">
  <audio/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AudioContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_TranscriptContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: language, confidence, speaker
        var xml = @"<agent message-id=""Test_TranscriptContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_115"">
  <transcript text=""test""/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TranscriptContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_VideoContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: uri, mimeType, width
        var xml = @"<agent message-id=""Test_VideoContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_116"">
  <video/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<VideoContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_FileContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: uri, filename, mimeType
        var xml = @"<agent message-id=""Test_FileContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_117"">
  <file/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<FileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_SearchResultContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: score
        var xml = @"<agent message-id=""Test_SearchResultContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_118"">
  <search-result title=""test"" url=""test"">
    <snippet>test</snippet>
  </search-result>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<SearchResultContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_DocumentContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: mimeType, content
        var xml = @"<agent message-id=""Test_DocumentContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_119"">
  <document title=""test"" document-id=""test"" source=""test""/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<DocumentContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_AdaptiveCardContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: version, fallbackText
        var xml = @"<agent message-id=""Test_AdaptiveCardContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_120"">
  <adaptive-card>test</adaptive-card>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<AdaptiveCardContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_UserInputRequestContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: inputType, required
        var xml = @"<agent message-id=""Test_UserInputRequestContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_121"">
  <user-input-request request-id=""test"" prompt=""test""/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<UserInputRequestContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_EventContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: timestamp, value
        var xml = @"<channel message-id=""Test_EventContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <event name=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<EventContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_TraceContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: label, severity, timestamp
        var xml = @"<channel message-id=""Test_TraceContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <trace name=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TraceContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_ActionContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: text, timestamp, value
        var xml = @"<channel message-id=""Test_ActionContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <action name=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<ActionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_TypingIndicatorContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: timestamp
        var xml = @"<channel message-id=""Test_TypingIndicatorContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <typing-indicator from=""test"" status=""test_value""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<TypingIndicatorContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_MessageReactionContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: reactionsAdded, reactionsRemoved
        var xml = @"<channel message-id=""Test_MessageReactionContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-reaction referenced-message-id=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageReactionContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_MessageDeleteContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: reason
        var xml = @"<channel message-id=""Test_MessageDeleteContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-delete message-id=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageDeleteContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_MessageUpdateContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: reason
        var xml = @"<channel message-id=""Test_MessageUpdateContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"">
  <message-update message-id=""test""/>
</channel>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<MessageUpdateContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_HostedFileContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: filename, mediaType, sizeBytes
        var xml = @"<agent message-id=""Test_HostedFileContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_129"">
  <hosted-file file-id=""test""/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedFileContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    [Fact]
    public void Test_HostedVectorStoreContent_OptionalFieldsCanBeOmitted()
    {
        // Arrange: XML omitting optional fields: name, documentCount
        var xml = @"<agent message-id=""Test_HostedVectorStoreContent_OptionalFieldsCanBeOmitted_msg"" created-at=""2026-02-07T10:00:00Z"" agent-id=""agent_test_130"">
  <hosted-vector-store vector-store-id=""test""/>
</agent>
";

        // Act: Deserialize (should succeed)
        var serializer = new MessageSerializer();
        var message = serializer.Deserialize(xml);

        // Assert: Message deserializes successfully
        XunitAssert.NotNull(message);
        var content = XunitAssert.IsType<HostedVectorStoreContent>(message.Contents.FirstOrDefault());
        XunitAssert.NotNull(content);
    }

    #endregion

}