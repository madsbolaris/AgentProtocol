# from microsoft.agents.xml.models import ChatMessage, FunctionResultContent
# from microsoft.agents.xml.serialization import MessageSerializer
#
# # Create tool result message
# message = ChatMessage(
#     role="tool",
#     message_id="msg-result-1",
#     contents=[
#         FunctionResultContent(
#             call_id="call_abc123",
#             name="get_weather",
#             content='{"temperature": 55, "conditions": "partly cloudy"}'
#         )
#     ]
# )
#
# serializer = MessageSerializer()
# xml_output = serializer.serialize(message)
# print(xml_output)